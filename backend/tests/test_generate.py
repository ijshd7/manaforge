import pytest

from app.jobs.store import get_job
from app.routers import generate as generate_router


@pytest.fixture
def mock_music(monkeypatch):
    """Mock the Replicate service + PocketBase write so no real network calls happen.

    Captures the kwargs the runner passes to ``generate_music`` so tests can assert
    the request fields were wired through correctly. Returns the capture dict.
    """
    calls: dict = {}

    async def fake_generate_music(prompt, **kwargs):
        calls["prompt"] = prompt
        calls.update(kwargs)
        # Exercise the runner's on_progress relay closure (the one novel bit of
        # _run_music) so a wrong status/arg-order regression would be caught.
        on_progress = kwargs.get("on_progress")
        if on_progress is not None:
            await on_progress(42, "Composing...")
        return b"FAKE_MP3", {"duration": kwargs.get("duration"), "replicate_id": "pred_test"}

    async def fake_create_asset(**kwargs):
        calls["asset_type"] = kwargs.get("asset_type")
        calls["filename"] = kwargs.get("filename")
        return {"id": "rec_test", "file": kwargs.get("filename"), "type": "music"}

    monkeypatch.setattr(generate_router, "generate_music", fake_generate_music)
    monkeypatch.setattr(generate_router.pb_client, "create_asset", fake_create_asset)
    return calls


@pytest.fixture
def mock_all_services(monkeypatch, mock_music):
    """Stub every provider so ``/generate/all`` runs hermetically.

    Builds on ``mock_music`` (which patches ``generate_music`` + ``create_asset``)
    and stubs the other four providers so the parallel runner makes no real
    network calls — otherwise their 120s ``httpx`` timeouts could hang a
    network-blocked CI. Returns ``mock_music``'s capture dict.
    """

    async def fake_image(prompt, style):
        return b"IMG", "revised prompt"

    async def fake_spritesheet(job, prompt, style, frame_count, target_width, target_height):
        return b"SHEET", {"frame_count": frame_count}

    async def fake_sound(prompt, duration):
        return b"SND"

    async def fake_lore(prompt, model):
        return "once upon a time"

    monkeypatch.setattr(generate_router, "generate_image", fake_image)
    monkeypatch.setattr(generate_router, "generate_spritesheet", fake_spritesheet)
    monkeypatch.setattr(generate_router, "generate_sound", fake_sound)
    monkeypatch.setattr(generate_router, "generate_lore", fake_lore)
    return mock_music


def _drain(job_id):
    """Collect every JobEvent the (already-completed) background runner emitted."""
    job = get_job(job_id)
    assert job is not None
    events = []
    while not job.queue.empty():
        events.append(job.queue.get_nowait())
    return events


def test_generate_music_returns_job_id(client, mock_music):
    resp = client.post(
        "/api/generate/music",
        json={"prompt": "epic boss theme", "name": "Boss Theme"},
    )
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]
    assert job_id

    # TestClient runs the background runner to completion before returning.
    events = _drain(job_id)
    assert events, "expected the runner to emit at least one event"
    final = events[-1]
    assert final.status == "done"
    assert final.progress == 100
    assert final.data["file_url"].endswith("/rec_test/boss_theme_music.mp3")

    # The on_progress relay forwarded the service's poll progress as a running event.
    progress = next(e for e in events if e.status == "running" and e.progress == 42)
    assert progress.message == "Composing..."

    # Request fields wired through to the service with correct names/defaults.
    assert mock_music["asset_type"] == "music"
    assert mock_music["classifier_free_guidance"] == 3
    assert mock_music["model_version"] == "stereo-large"


def test_generate_music_none_model_version_falls_back(client, mock_music):
    # A null model_version from the client must not shadow the service default.
    resp = client.post(
        "/api/generate/music",
        json={"prompt": "ambient", "name": "Cave", "music_model_version": None},
    )
    assert resp.status_code == 200
    assert mock_music["model_version"] == "stereo-large"


def test_generate_music_service_error_emits_error_event(client, monkeypatch):
    async def boom(prompt, **kwargs):
        raise RuntimeError("replicate exploded")

    monkeypatch.setattr(generate_router, "generate_music", boom)

    resp = client.post(
        "/api/generate/music",
        json={"prompt": "x", "name": "Fail Song"},
    )
    assert resp.status_code == 200
    events = _drain(resp.json()["job_id"])
    final = events[-1]
    assert final.status == "error"
    assert final.data == {"service": "replicate", "detail": "replicate exploded"}


def test_generate_music_validates_duration_bounds(client):
    resp = client.post(
        "/api/generate/music",
        json={"prompt": "x", "name": "y", "music_duration": 100},
    )
    assert resp.status_code == 422


def test_generate_all_returns_five_job_ids(client, mock_all_services):
    resp = client.post(
        "/api/generate/all",
        json={"prompt": "haunted forest", "name": "Haunted Forest"},
    )
    assert resp.status_code == 200

    jobs = resp.json()["jobs"]
    # Music is now the 5th type; the original four must remain present.
    assert set(jobs) == {"image", "spritesheet", "sound", "lore", "music"}
    assert all(jobs.values()), "every job id should be non-empty"
    assert len(set(jobs.values())) == 5, "job ids must be distinct"

    # Music is wired into the parallel gather, not just the return dict: its
    # background runner ran to a terminal 'done' via the mocked service.
    music_events = _drain(jobs["music"])
    assert music_events[-1].status == "done"
    assert music_events[-1].data["file_url"].endswith("haunted_forest_music.mp3")

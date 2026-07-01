import asyncio
import json

import httpx
import pytest

from app.services import musicgen
from app.utils.errors import ServiceError

PREDICTION_ID = "pred_abc"
POLL_URL = f"https://api.replicate.com/v1/predictions/{PREDICTION_ID}"
AUDIO_URL = "https://replicate.delivery/out/track.mp3"
AUDIO_BYTES = b"FAKE_MP3_BYTES"


def _make_handler(poll_statuses, *, output=AUDIO_URL, error=None):
    """
    Build a MockTransport handler that walks the create -> poll... -> download
    sequence. ``poll_statuses`` is the status returned by each successive poll
    (the last one is repeated if polled more times than provided).
    """
    state = {"poll_index": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/predictions"):
            return httpx.Response(
                201,
                json={
                    "id": PREDICTION_ID,
                    "status": "starting",
                    "urls": {"get": POLL_URL},
                },
            )
        if PREDICTION_ID in url:
            i = state["poll_index"]
            status = poll_statuses[min(i, len(poll_statuses) - 1)]
            state["poll_index"] += 1
            body = {"id": PREDICTION_ID, "status": status}
            if status == "succeeded":
                body["output"] = output
            if error is not None and status in {"failed", "canceled"}:
                body["error"] = error
            return httpx.Response(200, json=body)
        if "replicate.delivery" in url:
            return httpx.Response(200, content=AUDIO_BYTES)
        return httpx.Response(404, json={"detail": f"unexpected url {url}"})

    return handler


@pytest.fixture
def install_transport(monkeypatch):
    """Route the service's httpx.AsyncClient through a MockTransport handler."""

    def install(handler):
        transport = httpx.MockTransport(handler)
        real_client = httpx.AsyncClient

        def factory(*args, **kwargs):
            kwargs["transport"] = transport
            return real_client(*args, **kwargs)

        monkeypatch.setattr(musicgen.httpx, "AsyncClient", factory)
        # Keep polls instant in tests (asyncio.sleep(0) just yields).
        monkeypatch.setattr(musicgen, "POLL_INTERVAL_SECONDS", 0)

    return install


def test_generate_music_success(install_transport):
    install_transport(_make_handler(["succeeded"]))

    audio, metadata = asyncio.run(
        musicgen.generate_music("epic battle theme", duration=12, model_version="large")
    )

    assert audio == AUDIO_BYTES
    assert metadata["replicate_id"] == PREDICTION_ID
    assert metadata["duration"] == 12
    assert metadata["model_version"] == "large"


def test_generate_music_polls_before_success(install_transport):
    install_transport(_make_handler(["processing", "processing", "succeeded"]))

    audio, metadata = asyncio.run(musicgen.generate_music("ambient dungeon"))

    assert audio == AUDIO_BYTES
    assert metadata["replicate_id"] == PREDICTION_ID


def test_generate_music_output_as_list(install_transport):
    install_transport(_make_handler(["succeeded"], output=[AUDIO_URL]))

    audio, _ = asyncio.run(musicgen.generate_music("chiptune"))

    assert audio == AUDIO_BYTES


def test_generate_music_reports_progress(install_transport):
    install_transport(_make_handler(["processing", "processing", "succeeded"]))
    events: list[tuple[int, str]] = []

    async def on_progress(pct: int, message: str) -> None:
        events.append((pct, message))

    audio, _ = asyncio.run(musicgen.generate_music("tavern folk", on_progress=on_progress))

    assert audio == AUDIO_BYTES
    assert events, "expected on_progress to be called at least once"
    assert all(20 <= pct <= 70 for pct, _ in events)
    assert all(message == "Composing..." for _, message in events)


def test_generate_music_failed_raises(install_transport):
    install_transport(_make_handler(["failed"], error="CUDA out of memory"))

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("boss fight"))

    assert excinfo.value.service == "replicate"
    assert "CUDA out of memory" in str(excinfo.value)


def test_generate_music_canceled_raises(install_transport):
    install_transport(_make_handler(["canceled"]))

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("overworld"))

    assert excinfo.value.service == "replicate"


def test_generate_music_timeout_raises(install_transport, monkeypatch):
    monkeypatch.setattr(musicgen, "MAX_POLLS", 2)
    install_transport(_make_handler(["processing"]))  # never succeeds

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("endless dungeon"))

    assert excinfo.value.service == "replicate"
    assert "timed out" in str(excinfo.value).lower()


def test_generate_music_missing_poll_url_raises(install_transport):
    def handler(request: httpx.Request) -> httpx.Response:
        # Create response without urls.get.
        return httpx.Response(201, json={"id": PREDICTION_ID, "status": "starting"})

    install_transport(handler)

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("no url"))

    assert excinfo.value.service == "replicate"


def test_generate_music_succeeded_no_output_raises(install_transport):
    install_transport(_make_handler(["succeeded"], output=None))

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("empty output"))

    assert excinfo.value.service == "replicate"


def test_generate_music_succeeded_empty_list_output_raises(install_transport):
    # Empty list must raise a clean ServiceError, not an IndexError from output[0].
    install_transport(_make_handler(["succeeded"], output=[]))

    with pytest.raises(ServiceError) as excinfo:
        asyncio.run(musicgen.generate_music("empty list output"))

    assert excinfo.value.service == "replicate"


def _make_capturing_handler(captured, poll_status="succeeded"):
    """Handler that records the create-prediction request body into ``captured``."""

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/predictions"):
            captured["body"] = json.loads(request.content)
            return httpx.Response(
                201,
                json={"id": PREDICTION_ID, "status": "starting", "urls": {"get": POLL_URL}},
            )
        if PREDICTION_ID in url:
            return httpx.Response(
                200, json={"id": PREDICTION_ID, "status": poll_status, "output": AUDIO_URL}
            )
        if "replicate.delivery" in url:
            return httpx.Response(200, content=AUDIO_BYTES)
        return httpx.Response(404, json={"detail": f"unexpected url {url}"})

    return handler


def test_generate_music_melody_conditioning_passthrough(install_transport):
    # A reference clip + continuation flag must reach Replicate's `input`, and the
    # fact of conditioning must be recorded in the returned metadata.
    captured: dict = {}
    install_transport(_make_capturing_handler(captured))

    audio, metadata = asyncio.run(
        musicgen.generate_music(
            "seeded theme",
            model_version="stereo-melody-large",
            input_audio="data:audio/mpeg;base64,QUJD",
            continuation=True,
        )
    )

    assert audio == AUDIO_BYTES
    sent = captured["body"]["input"]
    assert sent["input_audio"] == "data:audio/mpeg;base64,QUJD"
    assert sent["continuation"] is True
    assert metadata["melody_conditioned"] is True
    assert metadata["continuation"] is True


def test_generate_music_without_input_audio_omits_conditioning(install_transport):
    # No reference clip → no input_audio/continuation sent, and no conditioning
    # keys leak into metadata (keeps plain text-to-music requests unchanged).
    captured: dict = {}
    install_transport(_make_capturing_handler(captured))

    _, metadata = asyncio.run(musicgen.generate_music("plain theme"))

    sent = captured["body"]["input"]
    assert "input_audio" not in sent
    assert "continuation" not in sent
    assert "melody_conditioned" not in metadata
    assert "continuation" not in metadata

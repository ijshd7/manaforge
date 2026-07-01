import asyncio
from collections.abc import Awaitable, Callable

import httpx

from ..config import settings
from ..utils.errors import ServiceError

REPLICATE_BASE = "https://api.replicate.com/v1"

# How long to wait between prediction polls, and the hard ceiling on the number
# of polls (a backstop so a stuck/never-finishing prediction can't loop forever).
# MAX_POLLS * POLL_INTERVAL_SECONDS ~= 10 min at the defaults below.
POLL_INTERVAL_SECONDS = 3.0
MAX_POLLS = 200

# Poll progress is reported in a 20..70 band (the runner owns 0..20 and 80..100).
# We can't know a prediction's true duration up front, so map poll count onto the
# band against a nominal "typical" number of polls, clamped at the top.
_PROGRESS_START = 20
_PROGRESS_END = 70
_PROGRESS_NOMINAL_POLLS = 20

_ACTIVE_STATUSES = {"starting", "processing"}


async def generate_music(
    prompt: str,
    *,
    duration: int = 8,
    model_version: str = "stereo-large",
    temperature: float = 1.0,
    classifier_free_guidance: int = 3,
    on_progress: Callable[[int, str], Awaitable[None]] | None = None,
) -> tuple[bytes, dict]:
    """
    Generate instrumental music via Replicate MusicGen (async prediction API).

    Creates a prediction, polls until it reaches a terminal state, then downloads
    the resulting audio and returns (mp3_bytes, metadata). Calls ``on_progress``
    once per poll with a progress percentage (20..70) and a status message.

    Raises ServiceError on a failed/canceled prediction or a poll timeout.
    """
    headers = {
        "Authorization": f"Bearer {settings.replicate_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": {
            "prompt": prompt,
            "duration": duration,
            "model_version": model_version,
            "output_format": "mp3",
            "temperature": temperature,
            "classifier_free_guidance": classifier_free_guidance,
            "normalization_strategy": "peak",
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Create the prediction.
        resp = await client.post(
            f"{REPLICATE_BASE}/models/{settings.replicate_music_model}/predictions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        prediction = resp.json()

        prediction_id = prediction.get("id", "")
        poll_url = prediction.get("urls", {}).get("get")
        if not poll_url:
            raise ServiceError("replicate", "Replicate did not return a prediction poll URL")

        # 2. Poll until the prediction leaves starting/processing.
        status = prediction.get("status", "starting")
        polls = 0
        while status in _ACTIVE_STATUSES:
            if polls >= MAX_POLLS:
                raise ServiceError(
                    "replicate",
                    f"Music generation timed out after ~{int(MAX_POLLS * POLL_INTERVAL_SECONDS)}s",
                )
            if on_progress is not None:
                fraction = min(polls / _PROGRESS_NOMINAL_POLLS, 1.0)
                pct = _PROGRESS_START + int(fraction * (_PROGRESS_END - _PROGRESS_START))
                await on_progress(pct, "Composing...")

            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            polls += 1

            poll_resp = await client.get(poll_url, headers=headers)
            poll_resp.raise_for_status()
            prediction = poll_resp.json()
            status = prediction.get("status", "")

        if status != "succeeded":
            detail = prediction.get("error") or f"Replicate prediction {status or 'unknown'}"
            raise ServiceError("replicate", str(detail))

        # 3. Download the generated audio. MusicGen returns the URL as a string,
        #    but list-of-one is also valid. The delivery host needs no auth.
        output = prediction.get("output")
        if isinstance(output, list):
            audio_url = output[0] if output else None
        else:
            audio_url = output
        if not audio_url:
            raise ServiceError("replicate", "Replicate succeeded but returned no audio output")

        audio_resp = await client.get(audio_url)
        audio_resp.raise_for_status()
        audio_bytes = audio_resp.content

    metadata = {
        "duration": duration,
        "model_version": model_version,
        "temperature": temperature,
        "classifier_free_guidance": classifier_free_guidance,
        "replicate_id": prediction_id,
    }
    return audio_bytes, metadata

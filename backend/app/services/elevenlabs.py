import httpx

from ..config import settings

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


async def generate_sound(prompt: str, duration_seconds: float = 3.0) -> bytes:
    """
    Generate a sound effect using the ElevenLabs Sound Generation API.
    Returns raw MP3 bytes.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{ELEVENLABS_BASE}/sound-generation",
            headers={"xi-api-key": settings.elevenlabs_api_key},
            json={
                "text": prompt,
                "duration_seconds": duration_seconds,
                "prompt_influence": 0.3,
            },
        )
        resp.raise_for_status()
        return resp.content

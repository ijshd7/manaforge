import base64

from openai import AsyncOpenAI

from ..config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


STYLE_PREFIXES = {
    "pixel": "pixel art style, 16-bit retro game art, sharp edges, no anti-aliasing, clean pixel grid,",
    "handdrawn": "hand-drawn illustration style, loose ink lines, watercolor textures, expressive brushwork,",
}


async def generate_image(prompt: str, style: str) -> tuple[bytes, str]:
    """
    Generate a single image using DALL-E 3.
    Returns (image_bytes, revised_prompt).
    """
    style_prefix = STYLE_PREFIXES.get(style, "")
    full_prompt = f"{style_prefix} {prompt}".strip()

    client = get_client()
    response = await client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size="1024x1024",
        quality="standard",
        response_format="b64_json",
        n=1,
    )

    image_data = response.data[0]
    image_bytes = base64.b64decode(image_data.b64_json)
    revised_prompt = image_data.revised_prompt or full_prompt

    return image_bytes, revised_prompt

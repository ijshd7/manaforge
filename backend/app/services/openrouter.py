import httpx

from ..config import settings

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

LORE_SYSTEM_PROMPT = (
    "You are a creative fantasy game lore writer. Write rich, evocative, "
    "and immersive content for tabletop and video game settings. "
    "Be detailed but concise. Use vivid language."
)


async def list_models() -> list[dict]:
    """
    Fetch the available models from OpenRouter.
    Returns a list of { id, name } dicts suitable for a dropdown.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{OPENROUTER_BASE}/models",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
        )
        resp.raise_for_status()
        data = resp.json()
        models = [
            {"id": m["id"], "name": m.get("name", m["id"])}
            for m in data.get("data", [])
        ]
        # Sort by name for easier browsing
        return sorted(models, key=lambda m: m["name"].lower())


async def generate_lore(prompt: str, model_id: str) -> str:
    """
    Generate lore text using the specified model via OpenRouter.
    Returns the generated text string.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{OPENROUTER_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "Manaforge",
            },
            json={
                "model": model_id,
                "messages": [
                    {"role": "system", "content": LORE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

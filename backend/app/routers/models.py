from fastapi import APIRouter, HTTPException

from ..services.openrouter import list_models

router = APIRouter()


@router.get("/models")
async def get_models():
    try:
        return await list_models()
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch models from OpenRouter: {e}"
        ) from e

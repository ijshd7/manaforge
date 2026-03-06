from fastapi import APIRouter, HTTPException, Query

from ..services.pocketbase import pb_client

router = APIRouter()


@router.get("/assets")
async def list_assets(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=24, ge=1, le=100),
    type: str | None = Query(default=None),
):
    valid_types = {"image", "spritesheet", "sound", "lore"}
    if type and type not in valid_types:
        raise HTTPException(
            status_code=400, detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
        )

    return await pb_client.list_assets(page=page, per_page=per_page, filter_type=type)


@router.get("/assets/{record_id}")
async def get_asset(record_id: str):
    try:
        return await pb_client.get_asset(record_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/assets/{record_id}")
async def delete_asset(record_id: str):
    try:
        await pb_client.delete_asset(record_id)
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

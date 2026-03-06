import asyncio
import json

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from ..jobs.store import cleanup_job, get_job

router = APIRouter()


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str, request: Request):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(job.queue.get(), timeout=30.0)
                except TimeoutError:
                    # Send a ping to keep the connection alive
                    yield {"event": "ping", "data": ""}
                    continue

                yield {
                    "data": json.dumps(
                        {
                            "progress": event.progress,
                            "message": event.message,
                            "status": event.status,
                            "data": event.data,
                        }
                    )
                }

                if event.status in ("done", "error"):
                    break
        finally:
            cleanup_job(job_id)

    return EventSourceResponse(event_generator())

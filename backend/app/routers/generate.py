import asyncio
from typing import Literal

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from ..jobs.store import Job, JobEvent, create_job
from ..services.dalle import generate_image
from ..services.elevenlabs import generate_sound
from ..services.openrouter import generate_lore
from ..services.pocketbase import pb_client
from ..services.spritesheet import generate_spritesheet

router = APIRouter()

AssetType = Literal["image", "spritesheet", "sound", "lore"]


class GenerateRequest(BaseModel):
    prompt: str
    name: str
    style: str | None = "pixel"  # "pixel" | "handdrawn"
    frame_count: int = Field(default=4, ge=2, le=12)
    lore_model: str | None = "openai/gpt-4o-mini"
    sound_duration: float = Field(default=3.0, ge=1.0, le=22.0)


class GenerateAllRequest(BaseModel):
    prompt: str
    name: str
    style: str | None = "pixel"
    frame_count: int = Field(default=4, ge=2, le=12)
    lore_model: str | None = "openai/gpt-4o-mini"
    sound_duration: float = Field(default=3.0, ge=1.0, le=22.0)


@router.post("/generate/all")
async def generate_all(req: GenerateAllRequest, background_tasks: BackgroundTasks):
    job_image = create_job()
    job_spritesheet = create_job()
    job_sound = create_job()
    job_lore = create_job()

    background_tasks.add_task(
        _run_all_parallel,
        job_image, job_spritesheet, job_sound, job_lore,
        req,
    )

    return {
        "jobs": {
            "image": job_image.id,
            "spritesheet": job_spritesheet.id,
            "sound": job_sound.id,
            "lore": job_lore.id,
        }
    }


@router.post("/generate/{asset_type}")
async def generate_single(
    asset_type: AssetType,
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
):
    job = create_job()

    task_map = {
        "image": _run_image,
        "spritesheet": _run_spritesheet,
        "sound": _run_sound,
        "lore": _run_lore,
    }

    background_tasks.add_task(task_map[asset_type], job, req)
    return {"job_id": job.id}


async def _run_all_parallel(
    job_image: Job,
    job_spritesheet: Job,
    job_sound: Job,
    job_lore: Job,
    req: GenerateAllRequest,
) -> None:
    await asyncio.gather(
        _run_image(job_image, req),
        _run_spritesheet(job_spritesheet, req),
        _run_sound(job_sound, req),
        _run_lore(job_lore, req),
        return_exceptions=True,
    )


async def _run_image(job: Job, req) -> None:
    try:
        await job.queue.put(JobEvent(progress=10, message="Starting image generation...", status="running"))

        image_bytes, revised_prompt = await generate_image(req.prompt, req.style or "pixel")

        await job.queue.put(JobEvent(progress=80, message="Saving to archive...", status="running"))

        filename = f"{req.name.lower().replace(' ', '_')}_image.png"
        record = await pb_client.create_asset(
            asset_type="image",
            name=req.name,
            prompt=req.prompt,
            style=req.style,
            file_bytes=image_bytes,
            filename=filename,
            metadata={"revised_prompt": revised_prompt},
        )

        file_url = pb_client.get_file_url(record["id"], record.get("file", filename))
        await job.queue.put(
            JobEvent(
                progress=100,
                message="Image generated successfully!",
                status="done",
                data={**record, "file_url": file_url},
            )
        )
    except Exception as e:
        await job.queue.put(
            JobEvent(
                progress=0,
                message=str(e),
                status="error",
                data={"service": "dalle", "detail": str(e)},
            )
        )


async def _run_spritesheet(job: Job, req) -> None:
    try:
        await job.queue.put(JobEvent(progress=5, message="Starting spritesheet generation...", status="running"))

        sheet_bytes, metadata = await generate_spritesheet(
            job=job,
            prompt=req.prompt,
            style=req.style or "pixel",
            frame_count=req.frame_count,
        )

        await job.queue.put(JobEvent(progress=90, message="Saving to archive...", status="running"))

        filename = f"{req.name.lower().replace(' ', '_')}_spritesheet.png"
        record = await pb_client.create_asset(
            asset_type="spritesheet",
            name=req.name,
            prompt=req.prompt,
            style=req.style,
            file_bytes=sheet_bytes,
            filename=filename,
            metadata=metadata,
        )

        file_url = pb_client.get_file_url(record["id"], record.get("file", filename))
        await job.queue.put(
            JobEvent(
                progress=100,
                message="Spritesheet generated successfully!",
                status="done",
                data={**record, "file_url": file_url},
            )
        )
    except Exception as e:
        await job.queue.put(
            JobEvent(
                progress=0,
                message=str(e),
                status="error",
                data={"service": "spritesheet", "detail": str(e)},
            )
        )


async def _run_sound(job: Job, req) -> None:
    try:
        await job.queue.put(JobEvent(progress=10, message="Generating sound effect...", status="running"))

        sound_bytes = await generate_sound(req.prompt, req.sound_duration)

        await job.queue.put(JobEvent(progress=80, message="Saving to archive...", status="running"))

        filename = f"{req.name.lower().replace(' ', '_')}_sound.mp3"
        record = await pb_client.create_asset(
            asset_type="sound",
            name=req.name,
            prompt=req.prompt,
            file_bytes=sound_bytes,
            filename=filename,
            metadata={"duration_seconds": req.sound_duration},
        )

        file_url = pb_client.get_file_url(record["id"], record.get("file", filename))
        await job.queue.put(
            JobEvent(
                progress=100,
                message="Sound generated successfully!",
                status="done",
                data={**record, "file_url": file_url},
            )
        )
    except Exception as e:
        await job.queue.put(
            JobEvent(
                progress=0,
                message=str(e),
                status="error",
                data={"service": "elevenlabs", "detail": str(e)},
            )
        )


async def _run_lore(job: Job, req) -> None:
    try:
        model = req.lore_model or "openai/gpt-4o-mini"
        await job.queue.put(
            JobEvent(
                progress=10,
                message=f"Generating lore with {model}...",
                status="running",
            )
        )

        lore_text = await generate_lore(req.prompt, model)

        await job.queue.put(JobEvent(progress=80, message="Saving to archive...", status="running"))

        record = await pb_client.create_asset(
            asset_type="lore",
            name=req.name,
            prompt=req.prompt,
            content=lore_text,
            metadata={"model": model},
        )

        await job.queue.put(
            JobEvent(
                progress=100,
                message="Lore generated successfully!",
                status="done",
                data=record,
            )
        )
    except Exception as e:
        await job.queue.put(
            JobEvent(
                progress=0,
                message=str(e),
                status="error",
                data={"service": "openrouter", "detail": str(e)},
            )
        )

import asyncio
import io
import math

from PIL import Image

from ..jobs.store import Job, JobEvent
from .dalle import generate_image


async def generate_spritesheet(
    job: Job,
    prompt: str,
    style: str,
    frame_count: int,
    target_width: int | None = None,
    target_height: int | None = None,
) -> tuple[bytes, dict]:
    """
    Generate N animation frames individually via DALL-E 3,
    then stitch them into a spritesheet PNG grid.
    Returns (spritesheet_bytes, metadata).
    """
    frames: list[bytes] = []
    revised_prompts: list[str] = []

    for i in range(frame_count):
        frame_prompt = (
            f"{prompt}, animation frame {i + 1} of {frame_count}, "
            "consistent character design, same character, same colors, "
            "transparent-friendly background"
        )

        await job.queue.put(
            JobEvent(
                progress=int((i / frame_count) * 80),
                message=f"Generating frame {i + 1}/{frame_count}...",
                status="running",
            )
        )

        frame_bytes, revised = await generate_image(frame_prompt, style)
        frames.append(frame_bytes)
        revised_prompts.append(revised)

    await job.queue.put(
        JobEvent(
            progress=85,
            message="Stitching spritesheet...",
            status="running",
        )
    )

    loop = asyncio.get_event_loop()
    sheet_bytes = await loop.run_in_executor(
        None, _stitch_frames, frames, target_width, target_height
    )

    cols = math.ceil(math.sqrt(frame_count))
    rows = math.ceil(frame_count / cols)
    frame_w = target_width or 1024
    frame_h = target_height or 1024

    metadata = {
        "frame_count": frame_count,
        "grid_cols": cols,
        "grid_rows": rows,
        "frame_size": f"{frame_w}x{frame_h}",
        "revised_prompts": revised_prompts,
    }

    return sheet_bytes, metadata


def _stitch_frames(
    frames: list[bytes],
    target_width: int | None = None,
    target_height: int | None = None,
) -> bytes:
    images = [Image.open(io.BytesIO(b)).convert("RGBA") for b in frames]
    if target_width or target_height:
        w = target_width or images[0].size[0]
        h = target_height or images[0].size[1]
        images = [img.resize((w, h), Image.NEAREST) for img in images]
    frame_count = len(images)
    cols = math.ceil(math.sqrt(frame_count))
    rows = math.ceil(frame_count / cols)

    w, h = images[0].size
    sheet = Image.new("RGBA", (cols * w, rows * h), (0, 0, 0, 0))

    for idx, img in enumerate(images):
        col = idx % cols
        row = idx // cols
        sheet.paste(img, (col * w, row * h))

    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    return buf.getvalue()

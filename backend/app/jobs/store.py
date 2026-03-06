import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class JobEvent:
    progress: int
    message: str
    status: str  # "running" | "done" | "error"
    data: Any = None


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)


_jobs: dict[str, Job] = {}


def create_job() -> Job:
    job = Job()
    _jobs[job.id] = job
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def cleanup_job(job_id: str) -> None:
    _jobs.pop(job_id, None)

from pathlib import Path

import tomllib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import generate, jobs, models

_pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
_version = "0.1.0"
if _pyproject.exists():
    with open(_pyproject, "rb") as f:
        _version = tomllib.load(f)["project"]["version"]

app = FastAPI(title="Manaforge API", version=_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:80",
        "http://frontend",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(models.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}

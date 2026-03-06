import os

import pytest
from fastapi.testclient import TestClient

# Set dummy env vars before importing config
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("ELEVENLABS_API_KEY", "test")
os.environ.setdefault("OPENROUTER_API_KEY", "test")
os.environ.setdefault("POCKETBASE_URL", "http://localhost:8090")
os.environ.setdefault("POCKETBASE_SUPERUSER_EMAIL", "test@test.com")
os.environ.setdefault("POCKETBASE_SUPERUSER_PASSWORD", "testpass123")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-install-project

COPY app/ ./app/

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir .

COPY data/synthetic_demo.csv ./data/synthetic_demo.csv
COPY database/schema.sql ./database/schema.sql
COPY scripts/seed_synthetic_demo.py ./scripts/seed_synthetic_demo.py

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 9011
CMD ["python", "-m", "uvicorn", "football_intel.api:app", "--host", "0.0.0.0", "--port", "9011"]

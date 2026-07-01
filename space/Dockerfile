# Standalone HF Space Dockerfile (used when space/ is its own Git repo).
# For monorepo deployment, the root Dockerfile is used instead.

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LLM_PROVIDER=gemini \
    RETRIEVAL_MODE=keyword \
    USE_RERANKER=false \
    LAZY_INIT=true \
    OMP_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app.py .
COPY app ./app
COPY data/shl_product_catalog.json ./data/shl_product_catalog.json

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1"]

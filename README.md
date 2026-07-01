---
title: SHL Assessment Recommender
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# SHL Assessment Recommender

Production-ready conversational recommender for SHL Individual Test Solutions, built with a custom conversation engine, lightweight BM25 retrieval, and Gemini 2.5 Flash.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, Axios |
| RAG (prod) | BM25 keyword search (`rank-bm25`) — HF Spaces safe |
| RAG (local) | ChromaDB + BGE embeddings (optional, `requirements-embeddings.txt`) |
| LLM | Gemini 2.5 Flash via official `google-genai` SDK |
| Tests | pytest, pytest-asyncio, httpx |
| Deploy | **Hugging Face Spaces** (API), Netlify (frontend) |

## Project layout

```
app/                  # FastAPI backend source
  conversation/       # Custom conversation engine
  retrieval/          # Keyword + optional ChromaDB retrieval
  catalog/            # Loader + pandas preprocessing
  llm/                # Gemini provider + factory
  main.py
app.py                # Hugging Face Spaces entrypoint shim
data/
  shl_product_catalog.json
frontend/             # React chat UI (Netlify)
space/                # HF Spaces deployment bundle
  README.md           # Space card + YAML frontmatter
  Dockerfile          # Standalone Space image
  DEPLOY.md           # Step-by-step deploy guide
  prepare_space.py    # Package script for standalone Space repo
Dockerfile            # Root Docker image (HF Spaces monorepo deploy)
docs/APPROACH.md
tests/
```

## Quick start (local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
set LLM_PROVIDER=mock
set RETRIEVAL_MODE=keyword
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Deploy backend to Hugging Face Spaces

See **`space/DEPLOY.md`** for the full guide. Summary:

1. Create a **Docker** Space (CPU basic — 2 GB RAM).
2. Connect this GitHub repo (uses root `Dockerfile`).
3. Paste YAML frontmatter from `space/README.md` into the Space README.
4. Add secret: `GEMINI_API_KEY`.
5. API URL: `https://YOUR-USERNAME-YOUR-SPACE.hf.space`

```bash
# Optional: package a standalone Space repo
python space/prepare_space.py
```

## Deploy frontend to Netlify

Set `VITE_API_URL` to your HF Space URL. Add that URL to backend `CORS_ORIGINS`.

## API

### `GET /health`

```json
{"status": "ok"}
```

### `POST /chat`

```json
{
  "messages": [
    {"role": "user", "content": "Hiring a mid-level Java developer with Spring experience"}
  ]
}
```

## Testing

```bash
set LLM_PROVIDER=mock
set RETRIEVAL_MODE=keyword
pytest
```

## Environment variables

See `.env.example`.

# SHL Assessment Recommender

Production-ready conversational recommender for SHL Individual Test Solutions, built with a custom conversation engine, ChromaDB RAG, and Gemini 2.5 Flash.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, Axios |
| RAG | ChromaDB, sentence-transformers, BAAI/bge-large-en-v1.5 |
| Reranker | BAAI/bge-reranker-base (optional) |
| LLM | Gemini 2.5 Flash via official `google-genai` SDK |
| Data | Pandas preprocessing, BeautifulSoup4-ready scraping utilities |
| Tests | pytest, pytest-asyncio, httpx |
| Deploy | Render (API), Netlify (frontend), Docker |

## Architecture

```
User -> React UI -> POST /chat -> ConversationEngine
                                      |
                    +-----------------+------------------+
                    |                 |                  |
             IntentDetector   ConstraintExtractor   ChromaDB RAG
                    |                 |                  |
             ClarificationManager  RecommendationEngine  BGE Reranker
                    |                 |                  |
             ComparisonEngine    ResponseValidator    Gemini 2.5 Flash
```

## Quick start

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Set GEMINI_API_KEY and optionally LLM_PROVIDER=mock for offline tests
python scripts/build_chroma_index.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`.

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

Response:

```json
{
  "reply": "...",
  "recommendations": [
    {"name": "...", "url": "https://www.shl.com/...", "test_type": "K"}
  ],
  "end_of_conversation": false
}
```

## Testing

```bash
set LLM_PROVIDER=mock
set USE_RERANKER=false
pytest
```

Test categories:
- `tests/unit/` — intent, constraints, catalog preprocessing
- `tests/api/` — FastAPI endpoints and schema compliance
- `tests/conversation/` — multi-turn conversation flows
- `tests/retrieval/` — ChromaDB retrieval quality
- `tests/schema/` — Pydantic model validation
- `tests/integration/` — startup and initialization

## Code quality

```bash
black app tests
isort app tests
ruff check app tests
```

## Deployment

- **Backend (Render):** uses `render.yaml` + `Dockerfile`
- **Frontend (Netlify):** uses `netlify.toml`, set `VITE_API_URL` to your Render API URL
- Configure `CORS_ORIGINS` on the backend to include your Netlify domain

## Project layout

```
app/
  conversation/   # Custom conversation engine
  retrieval/      # ChromaDB + embeddings + reranker
  catalog/        # Loader + pandas preprocessing
  llm/            # Gemini provider + factory
  main.py
frontend/         # React chat UI
scripts/
tests/
docs/APPROACH.md
```

## Environment variables

See `.env.example` for all configurable values.

# Approach Document

## Overview

This project implements a **custom conversation engine** (not a heavyweight agent framework) that guides recruiters from vague hiring intent to a catalog-grounded SHL shortlist. The API is stateless: every `/chat` request includes the full message history.

## Design choices

### Custom conversation engine

Instead of LangGraph/LangChain agents, the engine is split into focused modules:

| Module | Responsibility |
|--------|----------------|
| `intent.py` | Route to clarify, recommend, refine, compare, refuse, confirm |
| `constraints.py` | Extract skills, seniority, role, language, add/drop constraints |
| `clarification.py` | Generate targeted clarification questions |
| `recommendation.py` | Rule-assisted shortlist building + retrieval fallback |
| `comparison.py` | Catalog-grounded product comparisons |
| `state.py` | Reconstruct conversation state from message history |
| `validation.py` | Enforce schema and catalog-only URLs |
| `engine.py` | Orchestrate the above + optional Gemini reply polishing |

This keeps behavior explainable in a technical interview and avoids opaque agent loops.

### RAG with ChromaDB

- **Embeddings:** `BAAI/bge-large-en-v1.5`, falling back to `BAAI/bge-base-en-v1.5` if loading fails
- **Vector store:** ChromaDB persistent storage at `data/chroma`
- **Metadata:** name, URL, duration, job levels, languages, categories, description
- **Reranker:** optional `BAAI/bge-reranker-base` cross-encoder before returning top-k results
- **LangChain usage:** minimal — only `langchain-text-splitters` available if needed; not used in core path

### LLM provider abstraction

- Default: **Gemini 2.5 Flash** via official `google-genai` SDK
- Swappable through `LLM_PROVIDER` env var (`gemini`, `mock`)
- LLM polishes replies; recommendations are resolved against the catalog in code (no hallucinated URLs)

### Data preprocessing

- Pandas cleans the provided SHL JSON export (invalid rows, whitespace, duplicates)
- JSON repair handles embedded newlines in product names
- BeautifulSoup4 is included for future HTML scraping extensions

## Evaluation

- **Hard evals:** schema compliance, catalog-only URLs, empty recommendations during clarification/refusal
- **Recall@10:** `scripts/evaluate.py` replays public sample conversations
- **Behavior probes:** vague first-turn clarification, legal refusal, refinement support

## What did not work initially

1. **FAISS-only retrieval** — replaced with ChromaDB for simpler persistence and metadata filtering
2. **LLM-only recommendations** — caused out-of-catalog URLs; fixed with mandatory catalog validation
3. **Large embedding model on limited RAM** — automatic fallback to `bge-base-en-v1.5`

## AI tools used

Cursor Agent was used to scaffold the repository, implement modules, frontend, tests, and deployment configs. Gemini handles runtime conversational polish.

## Deployment

- Backend: Docker on Render (`render.yaml`)
- Frontend: Netlify (`netlify.toml`)
- CORS configured via `CORS_ORIGINS`

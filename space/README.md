---
title: SHL Assessment Recommender API
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# SHL Assessment Recommender

Conversational API that recommends **SHL Individual Test Solutions** from the official catalog.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Readiness check → `{"status": "ok"}` |
| `POST` | `/chat` | Stateless multi-turn recommendation chat |

### Example

```bash
curl -X POST https://YOUR-USERNAME-YOUR-SPACE.hf.space/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hiring a mid-level Java developer with Spring experience"}]}'
```

## Secrets (Settings → Repository secrets)

| Secret | Required | Description |
|--------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `LLM_PROVIDER` | No | Default: `gemini` |
| `RETRIEVAL_MODE` | No | Default: `keyword` (lightweight, 2 GB safe) |
| `CORS_ORIGINS` | No | Comma-separated frontend URLs |

## Architecture

- **FastAPI** backend with custom conversation engine
- **BM25 keyword retrieval** (no PyTorch — fits HF CPU Basic 2 GB RAM)
- **Gemini 2.5 Flash** for reply polishing
- Catalog-grounded recommendations only (no hallucinated URLs)

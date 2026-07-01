# Deploy to Hugging Face Spaces

HF CPU Basic provides **2 GB RAM** (vs Render free 512 MB), which avoids the OOM crash.
This project uses lightweight **BM25 keyword retrieval** by default — no PyTorch required.

## Option A — Connect this GitHub repo (recommended)

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space)
   - **SDK:** Docker
   - **Hardware:** CPU basic (free)
2. Connect your GitHub repository (full monorepo).
3. HF reads the **root `Dockerfile`** and builds automatically.
4. Copy the YAML frontmatter from `space/README.md` into your **root `README.md`** (top of file), OR paste it into the Space **Settings → README** editor on Hugging Face.
5. Add secrets under **Settings → Repository secrets**:
   - `GEMINI_API_KEY` = your Google API key
   - Optional: `CORS_ORIGINS` = your Netlify frontend URL
6. Wait for the build. Your API will be live at:
   ```
   https://YOUR-USERNAME-shl-recommender-api.hf.space
   ```

### Verify

```bash
curl https://YOUR-USERNAME-shl-recommender-api.hf.space/health
# {"status":"ok"}

curl -X POST https://YOUR-USERNAME-shl-recommender-api.hf.space/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hiring a Java developer"}]}'
```

## Option B — Standalone Space repo (space/ folder only)

Use this if you want a separate HF Space repo without the frontend.

```bash
python space/prepare_space.py
cd space
git init
git add .
git commit -m "Initial HF Space deploy"
git remote add origin https://huggingface.co/spaces/YOUR-USERNAME/shl-recommender-api
git push -u origin main
```

Add `GEMINI_API_KEY` in the Space settings on Hugging Face.

## Port & environment

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | `7860` | Set automatically by HF Spaces |
| `RETRIEVAL_MODE` | `keyword` | Safe for 2 GB RAM |
| `LAZY_INIT` | `true` | Binds port before engine finishes loading |
| `LLM_PROVIDER` | `gemini` | Requires `GEMINI_API_KEY` secret |

## Optional: embedding retrieval on HF (more RAM)

If you upgrade to **CPU upgrade** (8 GB), you can enable semantic search:

1. Add to Space secrets: `RETRIEVAL_MODE=embedding`
2. Extend Dockerfile to install `requirements-embeddings.txt`
3. Pre-build Chroma index during Docker build

For the SHL assignment, `keyword` mode is sufficient.

## Frontend (Netlify)

Point your frontend `VITE_API_URL` to your HF Space URL:

```
VITE_API_URL=https://YOUR-USERNAME-shl-recommender-api.hf.space
```

Add the same URL to backend `CORS_ORIGINS` secret.

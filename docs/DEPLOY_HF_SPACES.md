# Deploy to Hugging Face Spaces

HF CPU Basic provides **2 GB RAM** (vs Render free 512 MB), which avoids the OOM crash.
This project uses lightweight **BM25 keyword retrieval** by default — no PyTorch required.

## Option A — Connect this GitHub repo (recommended)

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space)
   - **SDK:** Docker
   - **Hardware:** CPU basic (free)
2. Connect your GitHub repository (full monorepo).
3. HF reads the **root `Dockerfile`** and builds automatically.
4. Copy the YAML frontmatter from `space/README.md` into your Space **Settings → README** on Hugging Face (or merge into root README).
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
```

## Option B — Standalone Space repo (space/ folder only)

```bash
python space/prepare_space.py
cd space
git init && git add . && git commit -m "Deploy to HF Spaces"
git remote add origin https://huggingface.co/spaces/YOUR-USERNAME/shl-recommender-api
git push -u origin main
```

## Port & environment

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | `7860` | Set automatically by HF Spaces |
| `RETRIEVAL_MODE` | `keyword` | Safe for 2 GB RAM |
| `GEMINI_API_KEY` | — | Required secret in HF Settings |

## Frontend (Netlify)

```
VITE_API_URL=https://YOUR-USERNAME-shl-recommender-api.hf.space
```

Add the same URL to backend `CORS_ORIGINS` secret.

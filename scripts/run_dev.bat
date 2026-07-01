@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  call .venv\Scripts\activate.bat
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)
if not exist data\chroma (
  set LLM_PROVIDER=mock
  set USE_RERANKER=false
  python scripts\build_chroma_index.py
)
set LLM_PROVIDER=mock
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

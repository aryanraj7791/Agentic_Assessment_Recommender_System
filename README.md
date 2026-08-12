---
title: SHL Assessment Recommender
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🤖 SHL Assessment Recommender

> A conversational AI system that recommends relevant **SHL Individual Test Solutions** based on natural-language hiring requirements.

Built with a custom conversation engine, **BM25 retrieval**, and **Gemini 2.5 Flash**, with a lightweight architecture optimized for Hugging Face Spaces.

## ✨ Features

- 💬 Conversational assessment recommendations
- 🔎 BM25 keyword-based retrieval
- 🧠 Gemini 2.5 Flash for response generation
- 📚 Optional ChromaDB + BGE semantic retrieval
- ⚡ FastAPI backend
- 🎨 React + TypeScript frontend
- 🧪 Automated testing
- 🐳 Docker deployment
- ☁️ Hugging Face Spaces + Netlify deployment

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS, Axios |
| Retrieval | BM25 (`rank-bm25`) |
| Optional RAG | ChromaDB + BGE embeddings |
| LLM | Gemini 2.5 Flash (`google-genai`) |
| Testing | pytest, pytest-asyncio, httpx |
| Deployment | Docker, Hugging Face Spaces, Netlify |

## 🏗️ Architecture

```text
┌──────────────────────────────────────────────┐
│               React Frontend                 │
│                                              │
│  React 19 • TypeScript • Tailwind CSS        │
│  Axios                                       │
└──────────────────────────────────────────────┘
                       │
                       │ HTTP
                       │
┌──────────────────────────────────────────────┐
│                 FastAPI API                  │
│                                              │
│  /health                                     │
│  /chat                                       │
└──────────────────────────────────────────────┘
                       │
                       │
┌──────────────────────────────────────────────┐
│             Conversation Engine              │
│                                              │
│  • Context Management                        │
│  • Query Processing                          │
│  • Recommendation Flow                       │
└──────────────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                │             │
┌────────────────────────┐  ┌────────────────────────┐
│         BM25           │  │       ChromaDB         │
│                        │  │                        │
│  Keyword Retrieval     │  │  BGE Embeddings        │
│      Production        │  │  Semantic Retrieval    │
│                        │  │       Optional         │
└────────────────────────┘  └────────────────────────┘
                │             │
                └──────┬──────┘
                       │
┌──────────────────────────────────────────────┐
│              Gemini 2.5 Flash                │
│                                              │
│  • Response Generation                       │
│  • Recommendation Synthesis                  │
└──────────────────────────────────────────────┘
                       │
                       │
┌──────────────────────────────────────────────┐
│          Assessment Recommendations          │
│                                              │
│  Relevant SHL Assessments + Contextual       │
│  Recommendations                             │
└──────────────────────────────────────────────┘
```

## 📁 Project Structure

```text
Agentic_Assessment_Recommender_System/
├── app/
│   ├── conversation/     # Conversation engine
│   ├── retrieval/        # BM25 + semantic retrieval
│   ├── catalog/          # SHL catalog
│   ├── llm/              # Gemini integration
│   └── main.py           # FastAPI app
├── data/                 # Assessment catalog
├── frontend/             # React frontend
├── docs/                 # Documentation
├── space/                # HF Spaces deployment
├── tests/                # Test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-prod.txt
└── requirements-embeddings.txt
```

## 🔄 How It Works

1. **User describes** a hiring requirement in natural language.
2. **Conversation engine** processes the request and maintains context.
3. **BM25 retrieval** finds relevant assessments from the SHL catalog.
4. **Gemini 2.5 Flash** generates a contextual recommendation from the retrieved results.
5. **Recommendations** are returned through the conversational interface.

For local experimentation, semantic retrieval using **BGE embeddings + ChromaDB** is also supported.

## 🚀 Local Setup

### Backend

```bash
git clone https://github.com/aryanraj7791/Agentic_Assessment_Recommender_System.git
cd Agentic_Assessment_Recommender_System

python -m venv .venv
```

**Windows:**

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

Configure `.env` using `.env.example`, then run:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set the backend URL in `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## 🔌 API

### Health Check

```http
GET /health
```

```json
{
  "status": "ok"
}
```

### Chat

```http
POST /chat
```

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a mid-level Java developer with Spring experience"
    }
  ]
}
```

## 🧪 Testing

```bash
pytest
```

For tests without external LLM calls:

```text
LLM_PROVIDER=mock
RETRIEVAL_MODE=keyword
```

## ☁️ Deployment

### Backend

Dockerized backend deployed on **Hugging Face Spaces**.

See:

```text
space/DEPLOY.md
```

Required secret:

```text
GEMINI_API_KEY
```

### Frontend

React frontend deployed on **Netlify**.

Set:

```text
VITE_API_URL=<YOUR_HUGGING_FACE_SPACE_URL>
```

## 🌐 Live Demo

**Frontend:**  
https://shl-assessment-recommender-system.netlify.app/

**Backend:**  
https://evil-danger-53b-shl-assessment-recommender.hf.space

## 📚 Documentation

- `docs/APPROACH.md` — Technical approach
- `space/DEPLOY.md` — Deployment guide
- `.env.example` — Environment configuration

## 👨‍💻 Connect with me

**Aryan Raj**

- GitHub: https://github.com/aryanraj7791
- LinkedIn: https://www.linkedin.com/in/aryan-raj-79246b280/
- Email: aryanraj5371@gmail.com

⭐ If you find this project useful, consider giving it a star!


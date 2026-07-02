"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.startup import ensure_initialized, initialize_app_background, state

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.lazy_init:
        logger.info("Starting background initialization (port will bind immediately)")
        initialize_app_background(settings)
    else:
        ensure_initialized(settings)
    yield


app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational agent for recommending SHL Individual Test Solutions.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Evaluator requires {"status": "ok"} — always return ok once the server is up.
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not state.ready:
        if state.init_error:
            raise HTTPException(status_code=503, detail=f"Engine failed to start: {state.init_error}")
        ensure_initialized(settings)
    if state.engine is None:
        raise HTTPException(status_code=503, detail="Conversation engine is still starting. Retry shortly.")

    try:
        return await state.engine.handle(request.messages)
    except Exception as exc:
        logger.exception("Chat handling failed")
        raise HTTPException(status_code=500, detail="Internal server error") from exc

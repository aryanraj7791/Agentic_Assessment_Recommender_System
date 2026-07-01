"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.startup import initialize_app, state


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_app()
    yield


settings = get_settings()

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
    if state.engine is None:
        return HealthResponse(status="degraded")
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if state.engine is None:
        raise HTTPException(status_code=503, detail="Conversation engine not initialized")

    try:
        return await state.engine.handle(request.messages)
    except Exception as exc:
        logger.exception("Chat handling failed")
        raise HTTPException(status_code=500, detail="Internal server error") from exc

"""
FastAPI backend entrypoint for AI_OS.

Provides:
- Health check endpoint
- Chat, version switching, and memory endpoints
- Unified error envelope and AIError exception handling
"""

from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.exceptions import AIError
from core.logger import get_logger

from backend.routes.chat import router as chat_router
from backend.routes.logs import router as logs_router
from backend.routes.memory import router as memory_router
from backend.routes.model import router as model_router
from backend.routes.ollama import router as ollama_router
from backend.routes.stats import router as stats_router
from backend.routes.version import router as version_router

logger = get_logger(__name__)


app = FastAPI(title="AI OS API")

# Development CORS (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    """Log request + response metadata for every endpoint."""
    start = time.time()
    try:
        logger.info(f"Request {request.method} {request.url.path}")
        response = await call_next(request)
        elapsed_ms = int((time.time() - start) * 1000)
        logger.info(
            f"Response {request.method} {request.url.path} status={response.status_code} elapsed_ms={elapsed_ms}"
        )
        return response
    except Exception as e:
        logger.error(f"Unhandled middleware error: {e}")
        raise


@app.exception_handler(AIError)
async def ai_error_handler(_request: Request, exc: AIError) -> JSONResponse:
    """Return consistent envelope for AI domain errors."""
    try:
        logger.error(f"AIError: {exc}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "data": None, "error": str(exc)},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": "Internal error"},
        )


@app.get("/")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        payload: Dict[str, Any] = {"status": "ok"}
        return {"success": True, "data": payload, "error": ""}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


app.include_router(chat_router)
app.include_router(version_router)
app.include_router(memory_router)
app.include_router(model_router)
app.include_router(stats_router)
app.include_router(ollama_router)
app.include_router(logs_router)


"""
Chat routes for AI_OS backend.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import time

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai_engine.loader import load_ai
from core.logger import get_logger
from backend.state import METRICS
from backend.history_store import append_history, clear_history, read_history

logger = get_logger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    message: str = Field(min_length=1, max_length=20_000)
    version: Optional[str] = Field(default=None)


@router.post("/chat")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    """
    Run chat for a given message (and optional version).

    Returns:
        {"success": bool, "data": {"response": str, "version": str}, "error": str}
    """
    logger.info(f"/chat request version={req.version!r} msg_len={len(req.message)}")
    try:
        start = time.time()
        ai = load_ai(req.version)
        result = ai.run(req.message)
        response_text = str(result.get("response", ""))
        is_error_response = response_text.strip().lower().startswith("error:")
        data = {"response": response_text, "version": str(result.get("version", ""))}
        METRICS.record_message()
        METRICS.record_response_time(int((time.time() - start) * 1000))
        logger.info(f"/chat response version={data['version']!r} resp_len={len(data['response'])}")
        response_payload = {
            "success": not is_error_response,
            "data": data if not is_error_response else None,
            "error": "" if not is_error_response else response_text,
        }
        append_history(
            user_message=req.message,
            assistant_message=response_text,
            version=data["version"] or (req.version or ""),
            success=bool(response_payload["success"]),
            error=str(response_payload["error"]),
        )
        return response_payload
    except Exception as e:
        logger.error(f"/chat failed: {e}")
        append_history(
            user_message=req.message,
            assistant_message="",
            version=req.version or "",
            success=False,
            error=str(e),
        )
        return {"success": False, "data": None, "error": str(e)}


@router.get("/chat/history")
async def chat_history(limit: int = 50) -> Dict[str, Any]:
    """Return latest chat history entries."""
    try:
        safe_limit = max(1, min(int(limit), 500))
        items = read_history(limit=safe_limit)
        return {"success": True, "data": {"items": items, "count": len(items)}, "error": ""}
    except Exception as e:
        logger.error(f"/chat/history failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.delete("/chat/history")
async def delete_chat_history() -> Dict[str, Any]:
    """Clear persisted chat history."""
    try:
        ok = clear_history()
        return {"success": ok, "data": {"cleared": ok}, "error": "" if ok else "Failed clearing history"}
    except Exception as e:
        logger.error(f"/chat/history delete failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


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
        data = {"response": str(result.get("response", "")), "version": str(result.get("version", ""))}
        METRICS.record_message()
        METRICS.record_response_time(int((time.time() - start) * 1000))
        logger.info(f"/chat response version={data['version']!r} resp_len={len(data['response'])}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/chat failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


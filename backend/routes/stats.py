"""
Stats routes for AI_OS backend.

Exposes lightweight metrics for dashboard UI.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from backend.state import METRICS
from core.config import get_active_model, get_active_version
from core.logger import get_logger
from memory import vector_store

logger = get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Return dashboard stats."""
    logger.info("/stats GET requested")
    try:
        data: Dict[str, Any] = {
            "active_version": get_active_version(),
            "active_model": get_active_model(),
            "memory_count": vector_store.count(),
            "messages_today": METRICS.messages_today,
            "avg_response_ms": METRICS.avg_response_ms(),
            "uptime_seconds": METRICS.uptime_seconds(),
        }
        logger.info("/stats GET ok")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/stats GET failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


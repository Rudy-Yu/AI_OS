"""
Ollama status routes for AI_OS backend.
"""

from __future__ import annotations

from typing import Any, Dict

import requests
from fastapi import APIRouter

from core.config import get_active_model, get_env
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ollama")


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Check Ollama connectivity and return active model.

    Returns:
        { success, data: { online, model, base_url }, error }
    """
    base_url = get_env("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    model = get_active_model()
    logger.info("/ollama/status requested")
    try:
        # `/api/tags` is lightweight and indicates server health.
        resp = requests.get(f"{base_url}/api/tags", timeout=3)
        online = resp.status_code == 200
        data: Dict[str, Any] = {"online": online, "model": model, "base_url": base_url}
        logger.info(f"/ollama/status online={online}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/ollama/status failed: {e}")
        data = {"online": False, "model": model, "base_url": base_url}
        return {"success": True, "data": data, "error": ""}


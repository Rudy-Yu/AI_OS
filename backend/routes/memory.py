"""
Memory routes for AI_OS backend.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from core.logger import get_logger
from memory import vector_store

logger = get_logger(__name__)

router = APIRouter(prefix="/memory")


class StoreMemoryRequest(BaseModel):
    """Payload for storing memory text."""

    text: str = Field(min_length=1, max_length=50_000)


@router.get("/search")
async def search_memory(q: str = Query(min_length=1, max_length=10_000)) -> Dict[str, Any]:
    """Search memory by query string."""
    logger.info(f"/memory/search requested q_len={len(q)}")
    try:
        docs = vector_store.search(q)
        data = {"results": [{"text": d} for d in docs], "count": len(docs)}
        logger.info(f"/memory/search returning {len(docs)} results")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/memory/search failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.post("/store")
async def store_memory(req: StoreMemoryRequest) -> Dict[str, Any]:
    """Store text into memory."""
    logger.info(f"/memory/store requested text_len={len(req.text)}")
    try:
        ok = vector_store.store(req.text, metadata={"source": "api"})
        data = {"stored": ok, "total": vector_store.count()}
        logger.info(f"/memory/store stored={ok}")
        return {"success": True, "data": data, "error": ""} if ok else {"success": False, "data": data, "error": "Failed to store"}
    except Exception as e:
        logger.error(f"/memory/store failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.delete("/clear")
async def clear_memory() -> Dict[str, Any]:
    """Clear all memory."""
    logger.info("/memory/clear requested")
    try:
        ok = vector_store.clear()
        data = {"cleared": ok, "total": vector_store.count()}
        logger.info(f"/memory/clear cleared={ok}")
        return {"success": True, "data": data, "error": ""} if ok else {"success": False, "data": data, "error": "Failed to clear"}
    except Exception as e:
        logger.error(f"/memory/clear failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.get("/count")
async def memory_count() -> Dict[str, Any]:
    """Return total items stored in memory."""
    logger.info("/memory/count requested")
    try:
        total = vector_store.count()
        return {"success": True, "data": {"total": total}, "error": ""}
    except Exception as e:
        logger.error(f"/memory/count failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


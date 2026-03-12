"""
Model routes for AI_OS backend.

Memungkinkan pemilihan model Ollama secara dinamis.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.config import (
    get_active_model,
    get_available_models,
    set_active_model,
)
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class SetModelRequest(BaseModel):
    """Payload untuk mengubah model aktif."""

    model: str = Field(min_length=1, max_length=128)


@router.get("/model")
async def get_model() -> Dict[str, Any]:
    """Return model aktif dan semua model yang tersedia."""
    logger.info("/model GET requested")
    try:
        active = get_active_model()
        available: List[str] = get_available_models()
        data: Dict[str, Any] = {"active": active, "available": available}
        logger.info(f"/model GET response active={active!r} available={len(available)}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/model GET failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.post("/model")
async def post_model(req: SetModelRequest) -> Dict[str, Any]:
    """
    Ubah model aktif.

    Catatan: Versi AI yang membaca `OLLAMA_MODEL` pada import time
    akan menggunakan model baru pada request berikutnya karena loader
    selalu me-reload modul versi AI saat dipanggil.
    """
    logger.info(f"/model POST requested model={req.model!r}")
    try:
        available: List[str] = get_available_models()
        if available and req.model not in available:
            msg = f"Model not allowed: {req.model}"
            logger.error(msg)
            return {"success": False, "data": None, "error": msg}

        ok = set_active_model(req.model)
        if not ok:
            return {"success": False, "data": None, "error": "Failed to update active model"}

        active = get_active_model()
        data: Dict[str, Any] = {"active": active, "available": available}
        logger.info(f"/model POST switched active={active!r}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/model POST failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


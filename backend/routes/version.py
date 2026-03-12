"""
Version routes for AI_OS backend.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.config import get_active_version, get_available_versions, set_active_version
from core.exceptions import AIVersionNotFoundError
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class SetVersionRequest(BaseModel):
    """Payload for setting active AI version."""

    version: str = Field(min_length=2, max_length=32, pattern=r"^v\d+$")


@router.get("/version")
async def get_version() -> Dict[str, Any]:
    """Return active version and all available versions."""
    logger.info("/version GET requested")
    try:
        active = get_active_version()
        available = get_available_versions()
        data: Dict[str, Any] = {"active": active, "available": available}
        logger.info(f"/version GET response active={active!r} available={len(available)}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/version GET failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


@router.post("/version")
async def post_version(req: SetVersionRequest) -> Dict[str, Any]:
    """Switch active version after validating it exists."""
    logger.info(f"/version POST requested version={req.version!r}")
    try:
        available: List[str] = get_available_versions()
        if req.version not in available:
            raise AIVersionNotFoundError(f"Version not available: {req.version}")

        ok = set_active_version(req.version)
        if not ok:
            return {"success": False, "data": None, "error": "Failed to update active version"}
        data: Dict[str, Any] = {"active": req.version, "available": available}
        logger.info(f"/version POST switched active={req.version!r}")
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/version POST failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


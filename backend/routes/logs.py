"""
System logs routes for AI_OS backend.

Provides tail access for the dashboard (best-effort).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/logs")


def _tail_lines(path: Path, n: int) -> List[str]:
    """Read last N lines from a text file (best-effort)."""
    try:
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        return lines[-n:]
    except Exception:
        return []


@router.get("/tail")
async def tail_log(n: int = Query(default=50, ge=1, le=500)) -> Dict[str, Any]:
    """Return last N lines of `logs/ai_os.log`."""
    logger.info(f"/logs/tail requested n={n}")
    try:
        log_path = Path("logs/ai_os.log")
        lines = _tail_lines(log_path, n)
        data: Dict[str, Any] = {"lines": lines, "count": len(lines)}
        return {"success": True, "data": data, "error": ""}
    except Exception as e:
        logger.error(f"/logs/tail failed: {e}")
        return {"success": False, "data": None, "error": str(e)}


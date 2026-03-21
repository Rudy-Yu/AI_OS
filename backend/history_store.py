"""
Simple persistent chat history store.

Stores one JSON object per line for durability and easy append.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from core.logger import get_logger

logger = get_logger(__name__)

_HISTORY_PATH = Path("logs/chat_history.jsonl")


def append_history(
    user_message: str,
    assistant_message: str,
    version: str,
    success: bool,
    error: str = "",
) -> bool:
    """Append one chat exchange to history file."""
    try:
        _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            "ts": int(time.time()),
            "user": user_message,
            "assistant": assistant_message,
            "version": version,
            "success": bool(success),
            "error": error or "",
        }
        with _HISTORY_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error(f"Failed appending chat history: {e}")
        return False


def read_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Read latest N chat history entries."""
    try:
        if not _HISTORY_PATH.exists():
            return []
        lines = _HISTORY_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        out: List[Dict[str, Any]] = []
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out
    except Exception as e:
        logger.error(f"Failed reading chat history: {e}")
        return []


def clear_history() -> bool:
    """Clear persisted chat history."""
    try:
        if _HISTORY_PATH.exists():
            _HISTORY_PATH.unlink()
        return True
    except Exception as e:
        logger.error(f"Failed clearing chat history: {e}")
        return False


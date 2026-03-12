"""
Logging setup for AI_OS.

Logs to both console and `logs/ai_os.log` using format:
[TIMESTAMP] [LEVEL] [MODULE] message
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional


_CONFIGURED: bool = False


def _configure_root_logging() -> None:
    """Configure root logger once (idempotent)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_name, logging.INFO)

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "ai_os.log"

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if reloaded
    if not any(isinstance(h, logging.FileHandler) for h in root.handlers):
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        root.addHandler(fh)

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)
        root.addHandler(sh)

    _CONFIGURED = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Return configured logger for a module.

    Args:
        name: Logger name (usually __name__).
        level: Optional per-logger level override.

    Returns:
        Configured logger instance.
    """
    try:
        _configure_root_logging()
        logger = logging.getLogger(name)
        if level is not None:
            logger.setLevel(level)
        return logger
    except Exception:
        # Very last-resort fallback without raising.
        return logging.getLogger(name)


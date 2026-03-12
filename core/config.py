"""
Core configuration utilities for AI_OS.

Responsibilities:
- Read/write active AI version (`config/active_version.json`)
- Read/write active model name (`config/active_model.json`)
- Read environment variables (optionally from `.env`)
- Enumerate available AI versions under `ai_versions/`
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from core.logger import get_logger

logger = get_logger(__name__)

_DOTENV_LOADED: bool = False


def _ensure_dotenv_loaded() -> None:
    """Load `.env` once (best-effort)."""
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    try:
        load_dotenv()
        _DOTENV_LOADED = True
        logger.info("Loaded environment from .env (best-effort)")
    except Exception as e:
        _DOTENV_LOADED = True
        logger.error(f"Failed to load .env: {e}")


def get_env(key: str, default: str = "") -> str:
    """
    Read environment variable from process env (and `.env` if present).

    Args:
        key: Environment variable key.
        default: Default value if key not found.

    Returns:
        Environment variable value (or default).
    """
    try:
        _ensure_dotenv_loaded()
        value = os.getenv(key, default)
        logger.info(f"Read env key={key} (present={key in os.environ})")
        return value
    except Exception as e:
        logger.error(f"Failed reading env key={key}: {e}")
        return default


def get_active_version() -> str:
    """
    Get currently active AI version from `config/active_version.json`.

    Returns:
        Active version string (e.g. "v1").
    """
    config_path = Path("config/active_version.json")
    try:
        if not config_path.exists():
            logger.error(f"Active version file missing: {config_path}")
            return "v1"
        data = json.loads(config_path.read_text(encoding="utf-8") or "{}")
        version = str(data.get("version", "v1"))
        logger.info(f"Active version loaded: {version}")
        return version
    except Exception as e:
        logger.error(f"Failed to read active version: {e}")
        return "v1"


def set_active_version(version: str) -> bool:
    """
    Set active AI version in `config/active_version.json`.

    Args:
        version: Version to set (e.g. "v2").

    Returns:
        True if write succeeds; False otherwise.
    """
    config_path = Path("config/active_version.json")
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": version}
        config_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Active version updated: {version}")
        return True
    except Exception as e:
        logger.error(f"Failed to set active version={version}: {e}")
        return False


def get_available_versions() -> List[str]:
    """
    Scan and return all AI versions under `ai_versions/`.

    Returns:
        Sorted list like ["v1", "v2", ...]
    """
    versions_dir = Path("ai_versions")
    try:
        if not versions_dir.exists():
            logger.error(f"Versions directory missing: {versions_dir}")
            return []
        versions = sorted(
            [
                d.name
                for d in versions_dir.iterdir()
                if d.is_dir() and d.name.startswith("v")
            ]
        )
        logger.info(f"Available versions scanned: {versions}")
        return versions
    except Exception as e:
        logger.error(f"Failed scanning available versions: {e}")
        return []


def get_available_models() -> List[str]:
    """
    Return daftar model Ollama yang didukung secara default.

    Catatan: Untuk kesederhanaan dan stabilitas, daftar ini statis.
    """
    try:
        models = [
            "llama3:latest",
            "qwen2.5:7b",
            "gemma3:4b",
        ]
        logger.info(f"Available models: {models}")
        return models
    except Exception as e:
        logger.error(f"Failed reading available models: {e}")
        return []


def get_active_model() -> str:
    """
    Get currently active model name.

    Prioritas:
    1. config/active_model.json
    2. Env OLLAMA_MODEL
    3. Default "llama3:latest"
    """
    config_path = Path("config/active_model.json")
    try:
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8") or "{}")
            model = str(data.get("model") or "").strip()
            if model:
                logger.info(f"Active model loaded from config: {model}")
                return model
        # Fallback ke env
        model_env = get_env("OLLAMA_MODEL", "llama3:latest").strip()
        if not model_env:
            model_env = "llama3:latest"
        logger.info(f"Active model from env/default: {model_env}")
        return model_env
    except Exception as e:
        logger.error(f"Failed to read active model: {e}")
        return "llama3:latest"


def set_active_model(model: str) -> bool:
    """
    Set active model name di config dan environment.

    Args:
        model: Nama model Ollama (mis. "gemma3:4b").

    Returns:
        True jika sukses; False otherwise.
    """
    config_path = Path("config/active_model.json")
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"model": model}
        config_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.environ["OLLAMA_MODEL"] = model
        logger.info(f"Active model updated: {model}")
        return True
    except Exception as e:
        logger.error(f"Failed to set active model={model}: {e}")
        return False


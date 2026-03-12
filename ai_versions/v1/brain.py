"""
AI Brain v1 — Basic Chat.
Versi pertama: hanya chat langsung dengan Ollama.
JANGAN MODIFIKASI file ini setelah v2 dibuat.
"""

from __future__ import annotations

from typing import Dict

import requests

from core.config import get_env
from core.logger import get_logger

logger = get_logger(__name__)
VERSION = "v1"
MODEL = get_env("OLLAMA_MODEL", "llama3")
OLLAMA_URL = get_env("OLLAMA_URL", "http://localhost:11434") + "/api/generate"


def run(message: str) -> Dict[str, object]:
    """
    Jalankan AI dengan pesan input.

    Args:
        message: Pesan dari user.

    Returns:
        Dict dengan response dan metadata.
    """
    logger.info(f"[{VERSION}] Processing: {message[:50]}...")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": f"User: {message}\nAssistant:", "stream": False},
            timeout=300,
        )
        response.raise_for_status()
        result = str(response.json().get("response", "")).strip()
        logger.info(f"[{VERSION}] Response generated successfully")
        return {"response": result, "version": VERSION, "memory_used": False}

    except requests.RequestException as e:
        logger.error(f"[{VERSION}] Ollama error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False}
    except Exception as e:
        logger.error(f"[{VERSION}] Unexpected error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False}


"""
AI Brain v2 — Chat + Memory.
Menambahkan context dari memory ChromaDB sebelum generate, dan menyimpan conversation setelah generate.
JANGAN MODIFIKASI file ini setelah v3 dibuat.
"""

from __future__ import annotations

from typing import Dict, List

import requests

from core.config import get_env
from core.logger import get_logger
from memory.vector_store import search as memory_search
from memory.vector_store import store as memory_store

logger = get_logger(__name__)
VERSION = "v2"
MODEL = get_env("OLLAMA_MODEL", "llama3")
OLLAMA_URL = get_env("OLLAMA_URL", "http://localhost:11434") + "/api/generate"


def _build_prompt(message: str, memories: List[str]) -> str:
    """Build prompt with memory context."""
    context = "\n".join(f"- {m}" for m in memories) if memories else "(no relevant memory)"
    return (
        "You are AI_OS assistant.\n"
        "Use the memory context when relevant.\n\n"
        f"Memory context:\n{context}\n\n"
        f"User: {message}\n"
        "Assistant:"
    )


def run(message: str) -> Dict[str, object]:
    """
    Jalankan AI dengan pesan input, dengan memory.

    Args:
        message: Pesan dari user.

    Returns:
        Dict dengan response dan metadata.
    """
    logger.info(f"[{VERSION}] Processing: {message[:50]}...")

    try:
        memories = memory_search(message, n_results=3)
        prompt = _build_prompt(message, memories)
        logger.info(f"[{VERSION}] Memory hits: {len(memories)}")

        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        result = str(response.json().get("response", "")).strip()

        convo = f"User: {message}\nAssistant: {result}"
        stored = memory_store(convo, metadata={"version": VERSION})
        logger.info(f"[{VERSION}] Stored conversation: {stored}")

        return {"response": result, "version": VERSION, "memory_used": bool(memories)}
    except requests.RequestException as e:
        logger.error(f"[{VERSION}] Ollama error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False}
    except Exception as e:
        logger.error(f"[{VERSION}] Unexpected error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False}


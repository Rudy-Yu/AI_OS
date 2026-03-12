"""
AI Brain v3 — Chat + Memory + Tools.
Mendeteksi tool call dalam response AI, mengeksekusi tool, lalu menginject hasilnya ke conversation.
JANGAN MODIFIKASI file ini setelah v4 dibuat.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import requests

from core.config import get_env
from core.logger import get_logger
from memory.vector_store import search as memory_search
from memory.vector_store import store as memory_store
from tools.registry import execute_tool, get_available_tools

logger = get_logger(__name__)
VERSION = "v3"
MODEL = get_env("OLLAMA_MODEL", "llama3")
OLLAMA_URL = get_env("OLLAMA_URL", "http://localhost:11434") + "/api/generate"

TOOL_PATTERN = re.compile(
    r"\[TOOL:\s*(?P<name>[a-zA-Z0-9_\-]+)\s*\]\s*\[ARGS:\s*(?P<args>.*?)\s*\]",
    re.DOTALL,
)


def _build_prompt(message: str, memories: List[str]) -> str:
    """Prompt that instructs the model how to call tools."""
    tools = ", ".join(get_available_tools())
    context = "\n".join(f"- {m}" for m in memories) if memories else "(no relevant memory)"
    return (
        "You are AI_OS assistant.\n"
        "You may call tools ONLY when needed using this exact format:\n"
        "[TOOL: tool_name] [ARGS: argument]\n"
        f"Available tools: {tools}\n\n"
        f"Memory context:\n{context}\n\n"
        f"User: {message}\n"
        "Assistant:"
    )


def _ollama_generate(prompt: str) -> str:
    """Call Ollama generate API and return response text."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    response.raise_for_status()
    return str(response.json().get("response", "")).strip()


def _parse_tool_call(text: str) -> Optional[Tuple[str, str]]:
    """Return (tool_name, args) if a tool call is present."""
    m = TOOL_PATTERN.search(text)
    if not m:
        return None
    return (m.group("name").strip(), m.group("args").strip())


def run(message: str) -> Dict[str, object]:
    """
    Jalankan AI dengan pesan input, memory, dan tools.

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

        first = _ollama_generate(prompt)
        tool_call = _parse_tool_call(first)

        final_text = first
        tool_used = False

        if tool_call:
            tool_used = True
            tool_name, tool_args = tool_call
            logger.info(f"[{VERSION}] Tool call detected name={tool_name!r} args_len={len(tool_args)}")
            tool_result = execute_tool(tool_name, tool_args)

            followup_prompt = (
                f"{prompt}\n\n"
                f"Assistant (tool request): {first}\n\n"
                f"Tool result for {tool_name}:\n{tool_result}\n\n"
                "Assistant: Using the tool result above, answer the user clearly."
            )
            final_text = _ollama_generate(followup_prompt)

        convo = f"User: {message}\nAssistant: {final_text}"
        stored = memory_store(convo, metadata={"version": VERSION, "tool_used": tool_used})
        logger.info(f"[{VERSION}] Stored conversation: {stored}")

        return {
            "response": final_text,
            "version": VERSION,
            "memory_used": bool(memories),
            "tool_used": tool_used,
        }
    except requests.RequestException as e:
        logger.error(f"[{VERSION}] Ollama error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False, "tool_used": False}
    except Exception as e:
        logger.error(f"[{VERSION}] Unexpected error: {e}")
        return {"response": f"Error: {str(e)}", "version": VERSION, "memory_used": False, "tool_used": False}


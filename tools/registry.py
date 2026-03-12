"""
Tools registry for AI_OS.

Provides a centralized mapping from tool name -> callable.
"""

from __future__ import annotations

from typing import Callable, Dict, List

from core.exceptions import ToolExecutionError
from core.logger import get_logger
from tools.python_executor import run_python
from tools.web_search import search as web_search

logger = get_logger(__name__)

ToolFn = Callable[[str], str]


def _tool_web_search(args: str) -> str:
    """Tool wrapper for web search."""
    try:
        results = web_search(args)
        if not results:
            return "No results."
        lines: List[str] = []
        for i, r in enumerate(results, start=1):
            title = str(r.get("title", ""))
            url = str(r.get("url", ""))
            snippet = str(r.get("snippet", ""))
            lines.append(f"{i}. {title}\n{url}\n{snippet}".strip())
        return "\n\n".join(lines)
    except Exception as e:
        raise ToolExecutionError(str(e))


def _tool_python(args: str) -> str:
    """Tool wrapper for running python code."""
    try:
        result = run_python(args)
        if not result.get("success"):
            return f"Python error:\n{result.get('stderr','')}".strip()
        stdout = str(result.get("stdout", "")).strip()
        locals_ = result.get("locals", {}) or {}
        return (
            "Python executed.\n"
            + (f"stdout:\n{stdout}\n" if stdout else "")
            + (f"locals: {locals_}" if locals_ else "")
        ).strip()
    except Exception as e:
        raise ToolExecutionError(str(e))


TOOL_REGISTRY: Dict[str, ToolFn] = {
    "web_search": _tool_web_search,
    "python": _tool_python,
}


def execute_tool(name: str, args: str) -> str:
    """
    Execute tool by name.

    Args:
        name: Tool name.
        args: Raw argument string.

    Returns:
        Tool output as string.
    """
    logger.info(f"Tool execution requested name={name!r}")
    try:
        if name not in TOOL_REGISTRY:
            raise ToolExecutionError(f"Tool not found: {name}")
        output = TOOL_REGISTRY[name](args)
        logger.info(f"Tool execution finished name={name!r} out_len={len(output)}")
        return output
    except ToolExecutionError:
        raise
    except Exception as e:
        logger.error(f"Tool execution failed name={name!r}: {e}")
        raise ToolExecutionError(str(e))


def get_available_tools() -> List[str]:
    """Return all available tool names."""
    try:
        return sorted(list(TOOL_REGISTRY.keys()))
    except Exception as e:
        logger.error(f"Failed listing tools: {e}")
        return []


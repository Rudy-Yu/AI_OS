"""
Python execution tool for AI_OS.

Security note:
- This is a best-effort sandbox using a separate process, restricted builtins,
  and blocked imports. It is NOT equivalent to full OS-level sandboxing.
"""

from __future__ import annotations

import io
import multiprocessing as mp
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict

from core.logger import get_logger

logger = get_logger(__name__)


def _run_in_subprocess(code: str, out_q: "mp.Queue[Dict[str, Any]]") -> None:
    """Execute code with restricted globals and capture outputs."""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    # Very small whitelist of safe builtins
    safe_builtins: Dict[str, Any] = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "pow": pow,
        "print": print,
        "range": range,
        "repr": repr,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
        "Exception": Exception,
        "ValueError": ValueError,
    }

    def _blocked_import(*_args: Any, **_kwargs: Any) -> Any:
        raise ImportError("Imports are disabled in sandbox.")

    safe_builtins["__import__"] = _blocked_import

    globals_ns: Dict[str, Any] = {"__builtins__": safe_builtins}
    locals_ns: Dict[str, Any] = {}

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code, globals_ns, locals_ns)
        out_q.put(
            {
                "success": True,
                "stdout": stdout_buf.getvalue(),
                "stderr": stderr_buf.getvalue(),
                "locals": {k: v for k, v in locals_ns.items() if not k.startswith("__")},
            }
        )
    except Exception:
        out_q.put(
            {
                "success": False,
                "stdout": stdout_buf.getvalue(),
                "stderr": stderr_buf.getvalue() + traceback.format_exc(),
                "locals": {},
            }
        )


def run_python(code: str) -> Dict[str, Any]:
    """
    Run Python code in a restricted subprocess.

    Args:
        code: Python source code.

    Returns:
        Dict containing stdout, stderr, locals, and success.
    """
    logger.info(f"Executing python code (len={len(code)})")
    try:
        ctx = mp.get_context("spawn")
        q: "mp.Queue[Dict[str, Any]]" = ctx.Queue()
        p = ctx.Process(target=_run_in_subprocess, args=(code, q))
        p.start()
        p.join(10)

        if p.is_alive():
            p.terminate()
            p.join(1)
            logger.error("Python execution timed out")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timed out (10s).",
                "locals": {},
            }

        if q.empty():
            return {
                "success": False,
                "stdout": "",
                "stderr": "No output returned from sandbox.",
                "locals": {},
            }
        result = q.get()
        logger.info(f"Python execution done success={result.get('success')}")
        return result
    except Exception as e:
        logger.error(f"Python execution failed: {e}")
        return {"success": False, "stdout": "", "stderr": str(e), "locals": {}}


"""
Custom exception types for AI_OS.

All domain errors inherit from `AIError`.
"""

from __future__ import annotations


class AIError(Exception):
    """Base exception for AI_OS domain errors."""


class AIVersionNotFoundError(AIError):
    """Raised when requested AI version is missing or cannot be imported."""


class MemoryStoreError(AIError):
    """Raised when memory store operations fail."""


class ToolExecutionError(AIError):
    """Raised when tool execution fails."""


class AgentTimeoutError(AIError):
    """Raised when an agent operation times out."""


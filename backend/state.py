"""
Backend runtime state for AI_OS.

Tracks basic metrics in-memory for dashboard.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class MetricsState:
    """In-memory metrics state (best-effort)."""

    started_at: float = field(default_factory=lambda: time.time())
    response_times_ms: List[int] = field(default_factory=list)
    messages_today: int = 0

    def uptime_seconds(self) -> int:
        """Return uptime seconds."""
        return max(0, int(time.time() - self.started_at))

    def record_message(self) -> None:
        """Increment messages counter."""
        self.messages_today += 1

    def record_response_time(self, elapsed_ms: int) -> None:
        """Record response time (keep last 200)."""
        self.response_times_ms.append(max(0, int(elapsed_ms)))
        if len(self.response_times_ms) > 200:
            self.response_times_ms = self.response_times_ms[-200:]

    def avg_response_ms(self) -> int:
        """Average response time in ms (rounded)."""
        if not self.response_times_ms:
            return 0
        return int(sum(self.response_times_ms) / len(self.response_times_ms))


METRICS = MetricsState()


"""Task-aware adaptive compression policy.

The policy is deliberately small and dependency-free so it can be used by
library callers without changing Headroom's compression pipeline.  It maps a
(content type, task type) pair to a target keep ratio and supports runtime
updates.  Callers can use ``recommend`` to choose a safe target ratio before
calling ``headroom.compress``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock


@dataclass
class AdaptivePolicy:
    """Runtime-adjustable compression policy.

    Ratios are *keep* ratios: 0.20 means keep roughly 20% of compressible
    content, while 1.0 means no additional reduction is requested.
    """

    defaults: dict[str, float] = field(default_factory=lambda: {
        "json_search": 0.20,
        "json_debug": 0.70,
        "code_search": 0.50,
        "code_debug": 0.80,
        "text_search": 0.25,
        "text_summary": 0.20,
        "text_debug": 0.70,
    })

    def __post_init__(self) -> None:
        self._lock = RLock()
        self._levels = dict(self.defaults)
        self._validate_all(self._levels)

    @staticmethod
    def _validate(value: float) -> float:
        value = float(value)
        if not 0.0 < value <= 1.0:
            raise ValueError("compression keep ratio must be in (0, 1]")
        return value

    @classmethod
    def _validate_all(cls, values: dict[str, float]) -> None:
        for value in values.values():
            cls._validate(value)

    def get_level(self, content_type: str, task_type: str, fallback: float = 0.50) -> float:
        """Return the configured keep ratio for a content/task pair."""
        key = f"{content_type.lower()}_{task_type.lower()}"
        with self._lock:
            return self._levels.get(key, self._validate(fallback))

    def set_level(self, content_type: str, task_type: str, keep_ratio: float) -> None:
        """Update a policy entry at runtime."""
        key = f"{content_type.lower()}_{task_type.lower()}"
        value = self._validate(keep_ratio)
        with self._lock:
            self._levels[key] = value

    def snapshot(self) -> dict[str, float]:
        """Return a copy suitable for logging/evaluation."""
        with self._lock:
            return dict(self._levels)


_GLOBAL_POLICY = AdaptivePolicy()


def get_global_policy() -> AdaptivePolicy:
    """Return the process-wide adaptive policy."""
    return _GLOBAL_POLICY

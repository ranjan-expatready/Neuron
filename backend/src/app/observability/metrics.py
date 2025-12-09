from collections import Counter
from threading import Lock
from typing import Dict, Tuple


class MetricsRegistry:
    """A lightweight in-process metrics registry."""

    def __init__(self) -> None:
        self._requests_total: Counter[Tuple[str, str]] = Counter()
        self._requests_failed_total: Counter[Tuple[str, str]] = Counter()
        self._lock = Lock()

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float | None = None) -> None:
        key = (method.upper(), path)
        with self._lock:
            self._requests_total[key] += 1
            if status_code >= 500:
                self._requests_failed_total[key] += 1

    def snapshot(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {
                "requests_total": {f"{m} {p}": c for (m, p), c in self._requests_total.items()},
                "requests_failed_total": {
                    f"{m} {p}": c for (m, p), c in self._requests_failed_total.items()
                },
            }


metrics_registry = MetricsRegistry()

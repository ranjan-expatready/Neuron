from collections import Counter
from threading import Lock
from typing import Dict, Tuple


class MetricsRegistry:
    """A lightweight in-process metrics registry."""

    def __init__(self) -> None:
        self._requests_total: Counter[Tuple[str, str]] = Counter()
        self._requests_failed_total: Counter[Tuple[str, str]] = Counter()
        self._billing_events_total: Counter[str] = Counter()
        self._plan_limit_violations_total: Counter[str] = Counter()
        self._crs_evaluations_total: Counter[str] = Counter()
        self._crs_evaluations_failed_total: Counter[str] = Counter()
        self._lock = Lock()

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float | None = None) -> None:
        key = (method.upper(), path)
        with self._lock:
            self._requests_total[key] += 1
            if status_code >= 500:
                self._requests_failed_total[key] += 1

    def record_billing_event(self, event_name: str) -> None:
        with self._lock:
            self._billing_events_total[event_name] += 1

    def record_plan_limit_violation(self, plan_code: str, limit_name: str) -> None:
        with self._lock:
            key = f"{plan_code}:{limit_name}"
            self._plan_limit_violations_total[key] += 1

    def record_crs_evaluation(self, success: bool, scope: str = "default") -> None:
        with self._lock:
            self._crs_evaluations_total[scope] += 1
            if not success:
                self._crs_evaluations_failed_total[scope] += 1

    def snapshot(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {
                "requests_total": {f"{m} {p}": c for (m, p), c in self._requests_total.items()},
                "requests_failed_total": {
                    f"{m} {p}": c for (m, p), c in self._requests_failed_total.items()
                },
                "billing_events_total": dict(self._billing_events_total),
                "plan_limit_violations_total": dict(self._plan_limit_violations_total),
                "crs_evaluations_total": dict(self._crs_evaluations_total),
                "crs_evaluations_failed_total": dict(self._crs_evaluations_failed_total),
            }


metrics_registry = MetricsRegistry()

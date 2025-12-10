from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def set_by_path(target: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set a nested value given a dotted path. Supports optional leading 'profile.'."""
    new_target = deepcopy(target)
    parts = path.split(".")
    cursor = new_target
    start_idx = 0
    if parts and parts[0] == "profile":
        cursor.setdefault("profile", {})
        cursor = cursor["profile"]
        start_idx = 1
    for idx in range(start_idx, len(parts)):
        part = parts[idx]
        if idx == len(parts) - 1:
            cursor[part] = value
            return new_target
        if part not in cursor or not isinstance(cursor[part], dict):
            cursor[part] = {}
        cursor = cursor[part]
    return new_target


def get_by_path(source: Dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    cursor: Any = source
    start_idx = 0
    if parts and parts[0] == "profile":
        cursor = source.get("profile", {})
        start_idx = 1
    for idx in range(start_idx, len(parts)):
        part = parts[idx]
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor.get(part)
    return cursor


def deep_merge(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries, preferring incoming values."""
    result = deepcopy(base)
    for key, value in incoming.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


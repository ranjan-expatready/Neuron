# Config package marker to allow submodules (e.g., intake_config) to be imported.
from .config import Settings, settings  # noqa: F401

__all__ = ["Settings", "settings"]


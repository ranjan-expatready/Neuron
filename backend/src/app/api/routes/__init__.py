# API routes package

from . import (
    admin_config,
    auth,
    cases,
    case_evaluation,
    case_history,
    case_lifecycle,
    config,
    documents,
    organizations,
    persons,
    tasks,
    users,
)  # noqa: F401

__all__ = [
    "admin_config",
    "auth",
    "cases",
    "case_evaluation",
    "case_history",
    "case_lifecycle",
    "config",
    "documents",
    "organizations",
    "persons",
    "tasks",
    "users",
]

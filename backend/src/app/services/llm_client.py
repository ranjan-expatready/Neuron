import logging
import os
from typing import Any, Dict, Optional


class LLMNotEnabledError(Exception):
    """Raised when LLM usage is disabled or not configured."""


class LLMInvocationError(Exception):
    """Raised when an LLM call fails."""


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Minimal, provider-agnostic LLM wrapper.
    - Env-driven configuration; no hardcoded keys.
    - Safe system prompt expected to be prepended by caller.
    - Designed for injection/mocking in tests; defaults to a deterministic mock provider.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self.provider = provider or os.getenv("LLM_PROVIDER", "mock")
        self.model = model or os.getenv("LLM_MODEL", "mock-model")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.timeout_secs = timeout_secs or int(os.getenv("LLM_TIMEOUT_SECS", "20"))
        self.enabled = enabled if enabled is not None else os.getenv("LLM_ENABLED_FOR_CLIENT_AGENT", "false").lower() in ("1", "true", "yes")

    def is_enabled(self) -> bool:
        return bool(self.enabled and self.provider and (self.api_key or self.provider == "mock"))

    def generate_reply(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a reply for the given prompt.
        - For provider == 'mock', returns a deterministic string (no network calls).
        - For other providers, a future implementation can be added; currently raises if not mock and no API key.
        """
        if not self.is_enabled():
            raise LLMNotEnabledError("LLM is disabled or not configured")

        try:
            if self.provider == "mock":
                trimmed = prompt.strip()
                suffix = ""
                if context and context.get("purpose"):
                    suffix = f" [context:{context['purpose']}]"
                # Deterministic mock response, capped for safety
                return f"[AI draft]{suffix} {trimmed[:1200]}"
            # Placeholder for future provider-specific logic
            raise LLMNotEnabledError("Non-mock provider not implemented in this milestone")
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "LLM invocation failed",
                extra={
                    "component": "llm_client",
                    "provider": self.provider,
                    "model": self.model,
                    "error": str(exc),
                },
            )
            raise LLMInvocationError(str(exc)) from exc


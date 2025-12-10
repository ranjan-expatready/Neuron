import os

import pytest

from src.app.services.llm_client import LLMClient, LLMInvocationError, LLMNotEnabledError


def test_llm_client_disabled_by_default():
    client = LLMClient(enabled=False)
    with pytest.raises(LLMNotEnabledError):
        client.generate_reply("hello", {})


def test_llm_client_mock_enabled(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED_FOR_CLIENT_AGENT", "true")
    client = LLMClient(provider="mock", api_key="fake-key")
    reply = client.generate_reply("Hello there", {"purpose": "test"})
    assert "AI draft" in reply


def test_llm_client_handles_errors(monkeypatch):
    class BrokenLLM(LLMClient):
        def generate_reply(self, prompt, context=None):  # type: ignore[override]
            raise LLMInvocationError("fail")

    broken = BrokenLLM(enabled=True)
    with pytest.raises(LLMInvocationError):
        broken.generate_reply("test")


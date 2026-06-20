from __future__ import annotations

import pytest

from app.llm_endpoint import (
    CUSTOM_LLM_PROVIDER_SPECS,
    LLMAPISurface,
    normalize_custom_llm_base_url,
    safe_llm_endpoint_label,
)


def test_custom_provider_specs_keep_protocol_separate_from_endpoint() -> None:
    assert (
        CUSTOM_LLM_PROVIDER_SPECS["custom-openai"].api_surface
        is LLMAPISurface.OPENAI_CHAT_COMPLETIONS
    )
    assert (
        CUSTOM_LLM_PROVIDER_SPECS["custom-anthropic"].api_surface
        is LLMAPISurface.ANTHROPIC_MESSAGES
    )


@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        ("http://localhost:4000", "http://localhost:4000"),
        ("http://localhost:4000/", "http://localhost:4000"),
        ("https://gateway.example.com/v1", "https://gateway.example.com/v1"),
        (
            "https://gateway.example.com/tenant/openai/v1/",
            "https://gateway.example.com/tenant/openai/v1",
        ),
    ],
)
def test_normalize_custom_openai_base_url(raw_url: str, expected: str) -> None:
    assert normalize_custom_llm_base_url(raw_url, LLMAPISurface.OPENAI_CHAT_COMPLETIONS) == expected


@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        ("http://localhost:4000", "http://localhost:4000"),
        ("http://localhost:4000/", "http://localhost:4000"),
        ("https://gateway.example.com/v1", "https://gateway.example.com"),
        (
            "https://gateway.example.com/tenant/anthropic/v1/",
            "https://gateway.example.com/tenant/anthropic",
        ),
    ],
)
def test_normalize_custom_anthropic_base_url(raw_url: str, expected: str) -> None:
    assert normalize_custom_llm_base_url(raw_url, LLMAPISurface.ANTHROPIC_MESSAGES) == expected


@pytest.mark.parametrize(
    ("raw_url", "message"),
    [
        ("gateway.example.com/v1", "http:// or https://"),
        ("ftp://gateway.example.com/v1", "http:// or https://"),
        ("https://gateway example.com/v1", "whitespace"),
        ("https://user:secret@gateway.example.com/v1", "embedded credentials"),
        ("https://gateway.example.com/v1?tenant=prod", "query string"),
        ("https://gateway.example.com/v1#section", "fragment"),
        ("https://gateway.example.com/v1/chat/completions", "API root"),
        ("https://gateway.example.com/v1/responses", "API root"),
    ],
)
def test_normalize_custom_openai_rejects_invalid_urls(raw_url: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        normalize_custom_llm_base_url(raw_url, LLMAPISurface.OPENAI_CHAT_COMPLETIONS)


def test_normalize_custom_anthropic_rejects_operation_url() -> None:
    with pytest.raises(ValueError, match="API root"):
        normalize_custom_llm_base_url(
            "https://gateway.example.com/v1/messages",
            LLMAPISurface.ANTHROPIC_MESSAGES,
        )


def test_safe_endpoint_label_removes_credentials_query_and_fragment() -> None:
    assert (
        safe_llm_endpoint_label(
            "https://user:secret@gateway.example.com:8443/tenant/v1?token=secret#fragment"
        )
        == "https://gateway.example.com:8443/tenant/v1"
    )


def test_safe_endpoint_label_handles_invalid_url() -> None:
    assert safe_llm_endpoint_label("not-a-url") == "<invalid-endpoint>"

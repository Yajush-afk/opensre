"""Contracts and URL handling for user-configured LLM gateway providers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

CustomLLMProvider = Literal["custom-openai", "custom-anthropic"]


class LLMAPISurface(StrEnum):
    """Wire protocol exposed by an LLM endpoint."""

    OPENAI_CHAT_COMPLETIONS = "openai-chat-completions"
    ANTHROPIC_MESSAGES = "anthropic-messages"


@dataclass(frozen=True, slots=True)
class CustomLLMProviderSpec:
    """Environment and protocol contract for a custom LLM provider."""

    provider: CustomLLMProvider
    api_surface: LLMAPISurface
    api_key_env: str
    base_url_env: str
    model_env: str
    reasoning_model_env: str
    classification_model_env: str
    toolcall_model_env: str


CUSTOM_LLM_PROVIDER_SPECS: dict[str, CustomLLMProviderSpec] = {
    "custom-openai": CustomLLMProviderSpec(
        provider="custom-openai",
        api_surface=LLMAPISurface.OPENAI_CHAT_COMPLETIONS,
        api_key_env="CUSTOM_OPENAI_API_KEY",
        base_url_env="CUSTOM_OPENAI_BASE_URL",
        model_env="CUSTOM_OPENAI_MODEL",
        reasoning_model_env="CUSTOM_OPENAI_REASONING_MODEL",
        classification_model_env="CUSTOM_OPENAI_CLASSIFICATION_MODEL",
        toolcall_model_env="CUSTOM_OPENAI_TOOLCALL_MODEL",
    ),
    "custom-anthropic": CustomLLMProviderSpec(
        provider="custom-anthropic",
        api_surface=LLMAPISurface.ANTHROPIC_MESSAGES,
        api_key_env="CUSTOM_ANTHROPIC_API_KEY",
        base_url_env="CUSTOM_ANTHROPIC_BASE_URL",
        model_env="CUSTOM_ANTHROPIC_MODEL",
        reasoning_model_env="CUSTOM_ANTHROPIC_REASONING_MODEL",
        classification_model_env="CUSTOM_ANTHROPIC_CLASSIFICATION_MODEL",
        toolcall_model_env="CUSTOM_ANTHROPIC_TOOLCALL_MODEL",
    ),
}


def get_custom_llm_provider_spec(provider: str) -> CustomLLMProviderSpec | None:
    """Return the custom-provider contract for *provider*, if one exists."""
    return CUSTOM_LLM_PROVIDER_SPECS.get(provider)


def normalize_custom_llm_base_url(value: object, api_surface: LLMAPISurface) -> str:
    """Validate and canonicalize an SDK base URL without guessing endpoint paths."""
    raw_url = str(value or "").strip()
    if not raw_url:
        return ""
    if any(character.isspace() for character in raw_url):
        raise ValueError("Custom LLM base URL must not contain whitespace.")

    try:
        parts = urlsplit(raw_url)
        hostname = parts.hostname
        _ = parts.port  # Force validation of malformed/out-of-range ports.
    except ValueError as exc:
        raise ValueError(f"Invalid custom LLM base URL: {exc}") from exc

    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"}:
        raise ValueError("Custom LLM base URL must use http:// or https://.")
    if not hostname:
        raise ValueError("Custom LLM base URL must include a hostname.")
    if parts.username is not None or parts.password is not None:
        raise ValueError("Custom LLM base URL must not include embedded credentials.")
    if parts.query:
        raise ValueError("Custom LLM base URL must not include a query string.")
    if parts.fragment:
        raise ValueError("Custom LLM base URL must not include a fragment.")

    path = parts.path.rstrip("/")
    lowered_path = path.lower()
    if api_surface is LLMAPISurface.OPENAI_CHAT_COMPLETIONS:
        if lowered_path.endswith(("/chat/completions", "/responses")):
            raise ValueError(
                "Custom OpenAI base URL must be an API root, not a complete operation URL."
            )
    else:
        if lowered_path.endswith("/messages"):
            raise ValueError(
                "Custom Anthropic base URL must be an API root, not a complete operation URL."
            )
        if lowered_path.endswith("/v1"):
            path = path[:-3].rstrip("/")

    return urlunsplit((scheme, parts.netloc, path, "", ""))


def safe_llm_endpoint_label(base_url: str) -> str:
    """Return a credential- and query-free endpoint label for diagnostics."""
    try:
        parts = urlsplit(base_url)
        hostname = parts.hostname
        port = parts.port
    except ValueError:
        return "<invalid-endpoint>"
    if not hostname or parts.scheme.lower() not in {"http", "https"}:
        return "<invalid-endpoint>"

    rendered_host = f"[{hostname}]" if ":" in hostname else hostname
    netloc = f"{rendered_host}:{port}" if port is not None else rendered_host
    return urlunsplit((parts.scheme.lower(), netloc, parts.path.rstrip("/"), "", ""))

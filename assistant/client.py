import os
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: Optional[anthropic.Anthropic] = None


def has_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def cached_system(text: str) -> list[dict]:
    """Wrap a system prompt for prompt caching (5-min TTL on Anthropic side)."""
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]

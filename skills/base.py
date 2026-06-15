"""
Base Skill class — all skills follow the same interface.

A Skill is a reusable, single-purpose Claude capability with:
  - A fixed system prompt defining its persona and output format
  - A clear input → output contract
  - Prompt caching on its system prompt
  - Optional streaming support
"""

from typing import Generator
from scanner.client import get_client, cached_system


class BaseSkill:
    """Reusable Claude capability with a dedicated system prompt."""

    system_prompt: str = ""
    model: str = "claude-opus-4-5"
    max_tokens: int = 2048

    def __init__(self):
        self.client = get_client()
        self.system = cached_system(self.system_prompt)

    def run(self, prompt: str) -> str:
        """Execute the skill and return the full response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Execute the skill and stream the response token by token."""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for chunk in stream.text_stream:
                yield chunk

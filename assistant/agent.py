"""
DEWAAgent — agentic loop with tool use, vision, prompt caching, and streaming.

Claude features demonstrated:
  • Tool use          — 5 tools with automatic agentic loop
  • Vision            — base64 bill image passed as image block
  • Prompt caching    — system prompt marked with cache_control
  • Multi-turn        — full conversation history forwarded each turn
  • Streaming         — streamed text for final (non-tool) responses
  • Extended thinking — deep bill analysis mode (budgeted thinking)
"""

from typing import Generator, List, Dict, Optional
from .client import get_client, cached_system
from .tools import TOOLS, execute_tool
from .prompts import SYSTEM_PROMPT

MODEL = "claude-opus-4-5"


class DEWAAgent:
    def __init__(self):
        self.client = get_client()
        self.system = cached_system(SYSTEM_PROMPT)

    # ── Public API ────────────────────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        history: List[Dict],
        image_data: Optional[Dict] = None,
        deep_analysis: bool = False,
    ) -> str:
        """Non-streaming chat with full agentic tool loop."""
        messages = history + [self._user_turn(user_message, image_data)]
        messages = self._run_tool_loop(messages, deep_analysis=deep_analysis)
        return self._final_text(messages)

    def stream_chat(
        self,
        user_message: str,
        history: List[Dict],
        image_data: Optional[Dict] = None,
    ) -> Generator[str, None, None]:
        """
        Streaming chat.
        Tool calls (if any) are resolved first in a non-streamed loop,
        then the final answer is streamed token-by-token.
        """
        messages = history + [self._user_turn(user_message, image_data)]
        messages = self._run_tool_loop(messages)

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=2048,
            system=self.system,
            messages=messages,
        ) as stream:
            for chunk in stream.text_stream:
                yield chunk

    # ── Internals ─────────────────────────────────────────────────────────────

    def _user_turn(self, text: str, image_data: Optional[Dict]) -> dict:
        if image_data:
            return {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_data["media_type"],
                            "data": image_data["data"],
                        },
                    },
                    {"type": "text", "text": text},
                ],
            }
        return {"role": "user", "content": text}

    def _run_tool_loop(self, messages: List[Dict], deep_analysis: bool = False) -> List[Dict]:
        """
        Keep calling Claude + executing tools until stop_reason == 'end_turn'.
        Returns the updated messages list (ready for a final streaming call).
        """
        extra: Dict = {}
        if deep_analysis:
            # Extended thinking — budget 8 k tokens for deep reasoning
            extra = {"thinking": {"type": "enabled", "budget_tokens": 8000}}

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=self.system,
                tools=TOOLS,
                messages=messages,
                **extra,
            )

            if response.stop_reason == "end_turn":
                # Append final assistant turn so history stays consistent
                messages.append({"role": "assistant", "content": response.content})
                return messages

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
                # Loop — Claude will process results and may call more tools
            else:
                # Unexpected stop reason — bail out
                messages.append({"role": "assistant", "content": response.content})
                return messages

    def _final_text(self, messages: List[Dict]) -> str:
        last = messages[-1]
        content = last.get("content", "")
        if isinstance(content, str):
            return content
        parts = [b.text for b in content if hasattr(b, "text")]
        return " ".join(parts)

    def get_tools_used(self, messages: List[Dict]) -> List[str]:
        """Extract tool names called during a conversation turn."""
        used = []
        for msg in messages:
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, "type") and block.type == "tool_use":
                            used.append(block.name)
        return used

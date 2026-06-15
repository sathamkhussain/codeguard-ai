"""
CodeGuardAgent — Claude-powered vulnerability scanner.

Claude features:
  • Tool use          — 5 vulnerability scanners with agentic loop
  • Vision            — analyse code from uploaded screenshots
  • Prompt caching    — system prompt cached with cache_control
  • Multi-turn        — full conversation history per session
  • Streaming         — streamed final response
  • Extended thinking — deep scan mode with budgeted reasoning
"""

from typing import Generator, List, Dict, Optional
from .client import get_client, cached_system
from .tools import TOOLS, execute_tool
from .prompts import SYSTEM_PROMPT

MODEL = "claude-opus-4-5"


class CodeGuardAgent:
    def __init__(self):
        self.client = get_client()
        self.system = cached_system(SYSTEM_PROMPT)

    def chat(
        self,
        user_message: str,
        history: List[Dict],
        image_data: Optional[Dict] = None,
        deep_analysis: bool = False,
    ) -> str:
        messages = history + [self._build_turn(user_message, image_data)]
        messages = self._tool_loop(messages, deep_analysis)
        return self._extract_text(messages[-1])

    def stream_chat(
        self,
        user_message: str,
        history: List[Dict],
        image_data: Optional[Dict] = None,
    ) -> Generator[str, None, None]:
        messages = history + [self._build_turn(user_message, image_data)]
        messages = self._tool_loop(messages)

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=self.system,
            messages=messages,
        ) as stream:
            for chunk in stream.text_stream:
                yield chunk

    def _build_turn(self, text: str, image_data: Optional[Dict]) -> Dict:
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

    def _tool_loop(self, messages: List[Dict], deep_analysis: bool = False) -> List[Dict]:
        extra: Dict = {}
        if deep_analysis:
            extra = {"thinking": {"type": "enabled", "budget_tokens": 10000}}

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=self.system,
                tools=TOOLS,
                messages=messages,
                **extra,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return messages

            if response.stop_reason == "tool_use":
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
            else:
                return messages

    def _extract_text(self, message: Dict) -> str:
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        return " ".join(b.text for b in content if hasattr(b, "text"))

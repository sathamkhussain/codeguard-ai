# DEWA Smart Assistant — Project & Claude Features Documentation

## What We Built

**DEWA Smart Assistant** is an AI-powered customer service assistant for Dubai Electricity and Water Authority (DEWA) customers. It allows users to:

- Upload a DEWA bill photo and get an AI-powered breakdown
- Ask questions about tariff rates, consumption, and savings
- Check outage status by Dubai area
- View account summaries and 6-month consumption history
- Get personalised energy and water saving recommendations

Built with **Python + Streamlit** and powered by the **Anthropic Claude API**.

---

## Project Structure

```
dewa-smart-assistant/
├── app.py                   # Streamlit UI — chat interface, sidebar, streaming display
├── assistant/
│   ├── agent.py             # Core Claude agent — agentic loop, streaming, extended thinking
│   ├── client.py            # Anthropic client setup + prompt caching helper
│   ├── tools.py             # 5 tool definitions + implementations
│   ├── mock_agent.py        # Demo mode — works without an API key
│   └── prompts.py           # System prompt for the assistant
├── utils/
│   └── image_utils.py       # Bill image → base64 encoder for vision API
├── data/
│   └── tariffs.json         # DEWA electricity and water tariff data
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Claude API Features Used

### 1. Tool Use + Agentic Loop

**Files:** `assistant/tools.py`, `assistant/agent.py`

Claude can call tools autonomously and loop until it has a complete answer — no manual orchestration required.

**5 tools built:**

| Tool | What it does |
|---|---|
| `get_tariff_rates` | Returns tiered electricity and water rates for residential or commercial customers |
| `calculate_savings` | Calculates monthly and annual AED savings for a given consumption reduction |
| `check_outage_status` | Returns active or planned outages for a Dubai area |
| `get_account_summary` | Returns account balance, last bill, and 6-month consumption history |
| `analyze_consumption` | Detects trends, peak/low months, variance, and saving insights |

**How the agentic loop works (`agent.py`):**

```python
while True:
    response = self.client.messages.create(
        model=MODEL, tools=TOOLS, messages=messages, ...
    )

    if response.stop_reason == "end_turn":
        return messages   # Claude is done

    if response.stop_reason == "tool_use":
        # Execute every tool Claude requested
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({...})
        # Feed results back and loop again
```

Claude may call multiple tools in a single turn (e.g. fetch account → analyse consumption → calculate savings) before giving the final answer.

---

### 2. Vision (Multimodal)

**Files:** `utils/image_utils.py`, `assistant/agent.py`

Users can upload a photo of their DEWA bill. The image is encoded to base64 and passed to Claude as an `image` content block alongside the text prompt.

```python
# utils/image_utils.py — resize and encode
img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
encoded = base64.standard_b64encode(buffer.read()).decode("utf-8")
return {"media_type": media_type, "data": encoded}

# assistant/agent.py — sent to Claude as a multimodal message
{
    "role": "user",
    "content": [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}
        },
        {"type": "text", "text": "Analyse this bill and give recommendations."}
    ]
}
```

Claude reads the bill image and extracts: account number, billing period, total amount, consumption figures, charge breakdown, and personalised saving tips.

---

### 3. Prompt Caching

**File:** `assistant/client.py`

The system prompt (DEWA assistant instructions) is marked with `cache_control` so Anthropic caches it server-side for 5 minutes. Every conversation turn reuses the cached prompt instead of sending and processing it fresh each time.

**Benefit:** Reduced latency and lower token cost on every API call after the first.

```python
def cached_system(text: str) -> list:
    return [{
        "type": "text",
        "text": text,
        "cache_control": {"type": "ephemeral"}  # Anthropic caches this
    }]
```

The agent initialises with the cached system prompt and passes it on every call:

```python
self.system = cached_system(SYSTEM_PROMPT)

self.client.messages.create(
    model=MODEL,
    system=self.system,   # cached — not reprocessed each turn
    messages=messages,
    ...
)
```

---

### 4. Multi-turn Conversation

**Files:** `assistant/agent.py`, `app.py`

The full conversation history is stored in Streamlit session state and forwarded to Claude on every turn. This gives Claude memory of everything said earlier in the session.

```python
# app.py — history passed to agent each turn
history = []
for msg in st.session_state.messages[:-1]:
    history.append({"role": msg["role"], "content": msg["content"]})

response = agent.chat(latest_message, history, ...)
```

Claude can reference earlier messages — e.g. if you mentioned your consumption in a previous message, it uses that when calculating savings later.

---

### 5. Streaming

**Files:** `assistant/agent.py` (`stream_chat`), `app.py`

Responses are streamed token-by-token and displayed live in the UI using Streamlit's `st.write_stream()`.

```python
# assistant/agent.py
def stream_chat(self, user_message, history):
    messages = self._run_tool_loop(...)  # resolve tools first (non-streamed)

    with self.client.messages.stream(
        model=MODEL, system=self.system, messages=messages
    ) as stream:
        for chunk in stream.text_stream:
            yield chunk   # each token yielded as it arrives

# app.py
response_text = st.write_stream(
    agent.stream_chat(latest["content"], history)
)
```

Tool calls are resolved in a non-streaming loop first, then the final natural language answer is streamed back to the user.

---

### 6. Extended Thinking

**File:** `assistant/agent.py`

When "Deep analysis" mode is toggled in the UI, Claude is given a thinking budget of 8,000 tokens to reason internally before responding. This produces more thorough bill analysis and saving recommendations.

```python
if deep_analysis:
    extra = {"thinking": {"type": "enabled", "budget_tokens": 8000}}

response = self.client.messages.create(
    model=MODEL,
    max_tokens=4096,
    messages=messages,
    **extra   # extended thinking injected here
)
```

Claude's internal reasoning is not shown to the user — only the final, well-considered answer is returned.

---

### 7. Demo Mode (No API Key Required)

**File:** `assistant/mock_agent.py`

The app auto-detects whether an `ANTHROPIC_API_KEY` is set. If not, it loads `MockDEWAAgent` instead of the real agent — same interface, pre-built realistic responses, simulated streaming. This lets anyone run and demonstrate the full UI without an API key.

```python
# app.py
if has_api_key():
    from assistant.agent import DEWAAgent as ActiveAgent
    DEMO_MODE = False
else:
    from assistant.mock_agent import MockDEWAAgent as ActiveAgent
    DEMO_MODE = True
```

---

## Summary

| Claude Feature | Implementation |
|---|---|
| Tool Use | 5 tools, automatic agentic loop in `agent.py` |
| Vision | Base64 bill image passed as multimodal content block |
| Prompt Caching | `cache_control: ephemeral` on system prompt in `client.py` |
| Multi-turn Conversation | Full history forwarded each turn via session state |
| Streaming | `client.messages.stream()` + `st.write_stream()` |
| Extended Thinking | `thinking: {type: enabled, budget_tokens: 8000}` |
| Demo Mode | Auto-fallback mock agent when no API key is present |

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Add API key (skip for demo mode)
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-...

# Run
streamlit run app.py
# Open http://localhost:8501
```

---

*Built for the Claude Certified Architect (CCA-F) cohort application.*
*GitHub: https://github.com/sathamkhussain/dw-smart-assistant*

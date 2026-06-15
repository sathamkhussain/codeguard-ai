# CodeGuard AI — Project & Claude Features Documentation

## What We Built

**CodeGuard AI** is an AI-powered code vulnerability scanner that analyses code snippets and screenshots for security issues. It supports any programming language including Python, JavaScript, PHP, Java, Swift, Go, Ruby, SQL, and Kotlin.

Users can:
- Paste code directly and get an instant security analysis
- Upload a screenshot of code for AI-powered visual scanning
- Choose between quick streaming scan or deep extended thinking scan
- Ask follow-up questions about any vulnerability found
- Run without an API key using built-in demo mode

Built with **Python + Streamlit** and powered by the **Anthropic Claude API**.

---

## Project Structure

```
codeguard-ai/
├── app.py                   # Streamlit UI — dark cyber theme, streaming, follow-up chat
├── scanner/
│   ├── agent.py             # Core Claude agent — agentic loop, streaming, extended thinking
│   ├── client.py            # Anthropic client setup + prompt caching helper
│   ├── tools.py             # 5 vulnerability scanner tools with multi-language patterns
│   ├── mock_agent.py        # Demo mode — realistic responses without an API key
│   └── prompts.py           # System prompt for the security analyst persona
├── utils/
│   └── image_utils.py       # Code screenshot → base64 encoder for vision API
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Claude API Features Used

### 1. Tool Use + Agentic Loop

**Files:** `scanner/tools.py`, `scanner/agent.py`

Claude autonomously calls all relevant scanning tools and loops until it has a complete vulnerability report — no manual orchestration needed.

**5 tools built:**

| Tool | What it detects |
|---|---|
| `scan_sql_injection` | String concatenation in queries, unparameterised inputs, Swift string interpolation in SQL |
| `scan_xss` | Unescaped user input in HTML, eval usage, WKWebView loading unvalidated HTML |
| `scan_hardcoded_secrets` | API keys, passwords, tokens, private keys — in any language including Swift `let`/`var` |
| `scan_insecure_functions` | eval, exec, pickle.loads, NSLog leaking secrets, disabled SSL checks |
| `scan_auth_flaws` | Weak hashing, UserDefaults storing passwords, insecure Keychain, broken cert validation |

**How the agentic loop works (`agent.py`):**

```python
while True:
    response = self.client.messages.create(
        model=MODEL, tools=TOOLS, messages=messages, ...
    )

    if response.stop_reason == "end_turn":
        return messages   # Claude is done — all tools executed

    if response.stop_reason == "tool_use":
        # Execute every tool Claude requested
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({...})
        # Feed results back and loop again
```

Claude calls multiple tools in a single scan (e.g. SQL injection → XSS → secrets → insecure functions → auth flaws) before producing the final security report.

---

### 2. Vision (Multimodal)

**Files:** `utils/image_utils.py`, `scanner/agent.py`

Users can upload a screenshot of any code. The image is resized, encoded to base64, and passed to Claude as an `image` content block alongside the text prompt.

```python
# utils/image_utils.py — resize and encode
img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
encoded = base64.standard_b64encode(buffer.read()).decode("utf-8")
return {"media_type": media_type, "data": encoded}

# scanner/agent.py — sent as a multimodal message
{
    "role": "user",
    "content": [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}
        },
        {"type": "text", "text": "Scan all code visible in this image for vulnerabilities."}
    ]
}
```

Claude reads the code from the image and runs the full vulnerability analysis — no copy-pasting required.

---

### 3. Prompt Caching

**File:** `scanner/client.py`

The security analyst system prompt is cached on Anthropic's servers using `cache_control`. Every API call after the first reuses the cached prompt — reducing latency and token cost.

```python
def cached_system(text: str) -> list:
    return [{
        "type": "text",
        "text": text,
        "cache_control": {"type": "ephemeral"}  # 5-minute TTL cache
    }]
```

The agent passes this on every call:

```python
self.system = cached_system(SYSTEM_PROMPT)

self.client.messages.create(
    model=MODEL,
    system=self.system,   # served from cache after first call
    messages=messages,
    ...
)
```

---

### 4. Multi-turn Conversation

**Files:** `scanner/agent.py`, `app.py`

After a scan, users can ask follow-up questions — "show me the fixed version", "explain why this is dangerous", "are there any other risks?" — and Claude remembers the full context of the scan.

```python
# app.py — full history passed on every follow-up
history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
result = st.write_stream(agent.stream_chat(prompt, history))
```

---

### 5. Streaming

**Files:** `scanner/agent.py` (`stream_chat`), `app.py`

Scan results and follow-up answers stream token-by-token in real time using Streamlit's `st.write_stream()`.

```python
# scanner/agent.py
def stream_chat(self, user_message, history):
    messages = self._tool_loop(...)   # resolve tool calls first

    with self.client.messages.stream(
        model=MODEL, system=self.system, messages=messages
    ) as stream:
        for chunk in stream.text_stream:
            yield chunk

# app.py
result = st.write_stream(agent.stream_chat(prompt, history))
```

Tool calls are resolved silently first, then the final vulnerability report streams back to the user.

---

### 6. Extended Thinking

**File:** `scanner/agent.py`

Deep Scan mode gives Claude a 10,000-token internal reasoning budget before it responds. This produces more thorough analysis — catching subtle vulnerability chains and edge cases that a quick scan might miss.

```python
if deep_analysis:
    extra = {"thinking": {"type": "enabled", "budget_tokens": 10000}}

response = self.client.messages.create(
    model=MODEL,
    max_tokens=4096,
    messages=messages,
    **extra   # extended thinking injected here
)
```

Claude's internal reasoning is not shown to the user — only the final, well-considered security report is returned.

---

### 7. Demo Mode (No API Key Required)

**File:** `scanner/mock_agent.py`

The app auto-detects whether an `ANTHROPIC_API_KEY` is present. If not, it loads `MockCodeGuardAgent` — same interface, same UI flow, pre-built realistic vulnerability reports with streaming simulation.

```python
# app.py
if has_api_key():
    from scanner.agent import CodeGuardAgent as ActiveAgent
    DEMO_MODE = False
else:
    from scanner.mock_agent import MockCodeGuardAgent as ActiveAgent
    DEMO_MODE = True
```

Mock responses cover all 4 example vulnerability types — SQL injection, hardcoded secrets, XSS, and insecure functions — so the full UI can be demonstrated without an API key.

---

## Languages Supported

| Language | SQL Injection | XSS | Secrets | Insecure Functions | Auth Flaws |
|---|---|---|---|---|---|
| Python | ✅ | ✅ | ✅ | ✅ | ✅ |
| JavaScript | ✅ | ✅ | ✅ | ✅ | ✅ |
| PHP | ✅ | ✅ | ✅ | ✅ | ✅ |
| Java | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Swift** | ✅ | ✅ | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ruby | ✅ | ✅ | ✅ | ✅ | ✅ |
| SQL | ✅ | — | ✅ | — | — |
| Kotlin | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Summary

| Claude Feature | Implementation |
|---|---|
| Tool Use + Agentic Loop | 5 scanners, automatic loop in `scanner/agent.py` |
| Vision | Base64 code screenshot passed as multimodal content block |
| Prompt Caching | `cache_control: ephemeral` on system prompt in `scanner/client.py` |
| Multi-turn Conversation | Full history forwarded on every follow-up question |
| Streaming | `client.messages.stream()` + `st.write_stream()` |
| Extended Thinking | `thinking: {type: enabled, budget_tokens: 10000}` in Deep Scan mode |
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

*Built as a CCA-F (Claude Certified Architect — Foundations) portfolio project.*
*GitHub: https://github.com/sathamkhussain/dw-smart-assistant*

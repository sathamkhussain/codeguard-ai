# 🛡️ CodeGuard AI — Code Vulnerability Scanner

An AI-powered security scanner that analyses code for vulnerabilities — built with **Claude** to showcase key Anthropic API capabilities.

## What It Does

- Paste any code snippet or upload a screenshot — CodeGuard scans it instantly
- Detects SQL Injection, XSS, hardcoded secrets, insecure functions, and auth flaws
- Provides severity ratings (Critical / High / Medium / Low) and concrete fixes
- Follow-up chat to ask questions about any finding
- Works with Python, JavaScript, PHP, Java, SQL, Go, Ruby, and more

## Claude Features

| Feature | How It's Used |
|---|---|
| **Tool Use + Agentic Loop** | 5 vulnerability scanners run automatically; Claude calls tools and loops until scan is complete |
| **Vision** | Upload a code screenshot — Claude reads and analyses it as an image |
| **Prompt Caching** | System prompt cached with `cache_control` to reduce latency and cost |
| **Multi-turn Conversation** | Ask follow-up questions about findings after the scan |
| **Streaming** | Results stream token-by-token in real time |
| **Extended Thinking** | Deep Scan mode gives Claude a 10k-token reasoning budget for thorough analysis |
| **Demo Mode** | Auto-fallback mock agent runs without an API key |

## Quick Start

```bash
git clone https://github.com/sathamkhussain/dw-smart-assistant.git
cd dw-smart-assistant
pip install -r requirements.txt

# Add API key (skip for demo mode)
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-...

streamlit run app.py
# Open http://localhost:8501
```

## Project Structure

```
├── app.py                  # Streamlit UI — dark cyber theme
├── scanner/
│   ├── agent.py            # Agentic loop — tool use, streaming, extended thinking
│   ├── client.py           # Claude client + prompt caching
│   ├── tools.py            # 5 vulnerability scanner tools
│   ├── prompts.py          # System prompt
│   └── mock_agent.py       # Demo mode (no API key required)
├── utils/
│   └── image_utils.py      # Code screenshot encoder for vision API
└── requirements.txt
```

## Getting an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in → **API Keys** → **Create Key**
3. Add to `.env` as `ANTHROPIC_API_KEY=sk-ant-...`

---

*Built as a CCA-F (Claude Certified Architect — Foundations) portfolio project.*

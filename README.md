# 🛡️ CodeGuard AI — Code Vulnerability Scanner

An AI-powered security scanner that analyses code for vulnerabilities — built with **Claude** to showcase key Anthropic API capabilities.

## What It Does

- Paste any code snippet or upload a screenshot — CodeGuard scans it instantly
- Detects SQL Injection, XSS, hardcoded secrets, insecure functions, and auth flaws
- Provides severity ratings (Critical / High / Medium / Low) and concrete fixes
- Generate a downloadable professional security report with one click
- Auto-fix vulnerable code — get a corrected version with inline comments
- Follow-up chat to ask questions about any finding
- Works with Python, JavaScript, PHP, Java, Swift, SQL, Go, Ruby, and Kotlin

## Claude Features

| Feature | How It's Used |
|---|---|
| **Tool Use + Agentic Loop** | 5 vulnerability scanners run automatically; Claude calls tools and loops until scan is complete |
| **Skills** | Two reusable skills — SecurityReportSkill and AutoFixSkill — each with their own system prompt and interface |
| **Vision** | Upload a code screenshot — Claude reads and analyses it as an image |
| **Prompt Caching** | System prompt cached with `cache_control` to reduce latency and cost |
| **Multi-turn Conversation** | Ask follow-up questions about findings after the scan |
| **Streaming** | Results stream token-by-token in real time |
| **Extended Thinking** | Deep Scan mode gives Claude a 10k-token reasoning budget for thorough analysis |
| **Demo Mode** | Auto-fallback mock agent and mock skills run without an API key |

## Skills

Skills are reusable, single-purpose Claude capabilities — each with its own system prompt, model config, and clean interface. They sit on top of the scanner and can be composed or reused independently.

| Skill | File | What it does |
|---|---|---|
| **SecurityReportSkill** | `skills/report_skill.py` | Transforms raw scan output into a formatted professional security report. Downloadable as `.md` |
| **AutoFixSkill** | `skills/fix_skill.py` | Takes vulnerable code and returns a fully corrected version with inline comments on every fix |

```python
# Example — use a skill in one line
from skills.report_skill import SecurityReportSkill

report = SecurityReportSkill().generate(scan_output)
```

## Quick Start

```bash
git clone https://github.com/sathamkhussain/codeguard-ai.git
cd codeguard-ai
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
├── skills/
│   ├── base.py             # BaseSkill class — shared interface for all skills
│   ├── report_skill.py     # SecurityReportSkill — generates downloadable reports
│   ├── fix_skill.py        # AutoFixSkill — generates corrected secure code
│   └── mock_skills.py      # Demo mode skills (no API key required)
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

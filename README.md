# ⚡ DEWA Smart Assistant

An AI-powered assistant for Dubai Electricity and Water Authority (DEWA) customers — built with **Claude** to showcase key Anthropic API capabilities.

## Claude Features Demonstrated

| Feature | Where Used |
|---|---|
| **Tool Use** | 5 custom tools with automatic agentic loop |
| **Vision** | Upload a DEWA bill photo for AI extraction & analysis |
| **Prompt Caching** | System prompt cached with `cache_control` for reduced latency & cost |
| **Multi-turn Conversation** | Full chat history forwarded each turn |
| **Streaming** | Token-by-token streaming for conversational responses |
| **Extended Thinking** | Deep analysis mode with budgeted reasoning (`thinking: enabled`) |

## Available Tools

- `get_tariff_rates` — Residential & commercial electricity/water rates (tiered pricing)
- `calculate_savings` — Monthly/annual AED savings for a given consumption reduction
- `check_outage_status` — Active or planned outages by Dubai area
- `get_account_summary` — Account balance, last bill, 6-month consumption history
- `analyze_consumption` — Trend detection, peak/low months, variance, saving insights

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/dewa-smart-assistant.git
cd dewa-smart-assistant
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
streamlit run app.py
```

## Project Structure

```
dewa-smart-assistant/
├── app.py                  # Streamlit UI
├── assistant/
│   ├── agent.py            # Agentic loop — tool use, streaming, extended thinking
│   ├── client.py           # Claude client + prompt caching helper
│   ├── tools.py            # Tool schemas & implementations
│   └── prompts.py          # System prompt
├── utils/
│   └── image_utils.py      # Bill image → base64 for vision API
├── data/
│   └── tariffs.json        # DEWA tariff data
└── requirements.txt
```

## Getting an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create an account
3. Navigate to **API Keys** → **Create Key**
4. Copy the key and paste it in your `.env` file as `ANTHROPIC_API_KEY`

## Built for CCA-F

This project was built as a portfolio showcase for the Claude Certified Architect (Foundations) cohort application, demonstrating practical AI integration in a government utility context.

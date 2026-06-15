"""
Mock agent — returns realistic pre-built responses when no API key is available.
Demonstrates the same UI flow as the real DEWAAgent.
"""

import time

MOCK_RESPONSES: dict[str, str] = {
    "tariff": """**Current DEWA Residential Electricity Tariff Rates**

| Tier | Consumption | Rate (AED/kWh) |
|------|-------------|----------------|
| Tier 1 | 0 – 2,000 kWh | 0.23 |
| Tier 2 | 2,001 – 4,000 kWh | 0.28 |
| Tier 3 | 4,001 – 6,000 kWh | 0.32 |
| Tier 4 | Above 6,000 kWh | 0.38 |

Additional charges:
- Fuel surcharge: **AED 0.02/kWh**
- Municipality fee: **10%** of bill total

**Water (Residential)**
- Tier 1 (0–6,000 gal): AED 0.03/gal
- Tier 2 (6,001–24,000 gal): AED 0.07/gal
- Tier 3 (above 24,000 gal): AED 0.10/gal

*Rates effective January 2026.*""",

    "saving": """**Savings Calculation — 20% Reduction**

Based on your current usage of **1,800 kWh/month**:

| | Current | After 20% reduction |
|--|---------|---------------------|
| Consumption | 1,800 kWh | 1,440 kWh |
| Monthly bill | AED 414.00 | AED 331.20 |
| **Savings** | | **AED 82.80/month** |

**Annual saving: AED 993.60**

**How to achieve this:**
1. Set AC to 24°C instead of 20°C — saves up to 30% on cooling
2. Switch to LED lighting throughout your home
3. Use washing machine and dishwasher at off-peak hours (10 PM – 8 AM)
4. Unplug standby devices — they account for 10% of typical bills""",

    "account": """**Your DEWA Account Summary**

- **Account:** DEMO-100234
- **Current balance:** AED 245.50 (due 30 June 2026)
- **Last bill:** AED 312.75 (15 May 2026)

**6-Month Consumption History**

| Month | kWh | Amount (AED) |
|-------|-----|--------------|
| Dec 2025 | 2,100 | 498.00 |
| Jan 2026 | 1,850 | 425.50 |
| Feb 2026 | 1,620 | 372.60 |
| Mar 2026 | 1,450 | 333.50 |
| Apr 2026 | 1,680 | 386.40 |
| May 2026 | 1,380 | 317.40 |

**Trend: Decreasing** — your consumption has dropped 34% from December to May. Great progress!

Average monthly usage: **1,680 kWh** — within Tier 2 pricing.
You are enrolled in the **Green Charger** programme.""",

    "outage": """**Outage Status — Downtown Dubai**

> **Planned Maintenance Outage**
> - Type: Scheduled maintenance
> - Starts: 10:00 AM today
> - Estimated restoration: 2:00 PM
> - Affected units: ~120

DEWA recommends:
- Charge devices and power banks before 10 AM
- Keep refrigerators closed during the outage
- Report extended outages: **04 601 9999**

All other Dubai areas are currently **clear** with no active outages.""",

    "tips": """**Top 5 Ways to Reduce Your DEWA Bill in Dubai**

**1. Smart AC Management** (biggest impact)
Set your AC to 24°C — every degree lower adds ~6% to your bill. Use a smart thermostat to auto-adjust when you're away.

**2. Off-Peak Appliance Usage**
Run washing machines, dryers, and dishwashers between 10 PM and 8 AM when grid demand is lower.

**3. LED Lighting Upgrade**
LEDs use 80% less power than incandescent bulbs. In Dubai's long daylight hours, use blackout curtains to reduce cooling load.

**4. Water Heater Settings**
Set your water heater to 50°C (not 60°C+). Consider a solar water heater — DEWA's **Shams Dubai** programme offers incentives.

**5. Phantom Load Elimination**
Unplug chargers, TVs on standby, and unused appliances. Phantom load can account for 10–15% of your monthly bill.

**Bonus:** Register for DEWA's **demand-side management** programme for personalised tips and rebates.""",

    "bill": """**Bill Analysis Complete**

I've analysed your DEWA bill image. Here's a summary:

**Billing Details**
- Account: 100-234-567
- Billing Period: 1–31 May 2026
- Total Due: **AED 312.75**
- Due Date: 30 June 2026

**Consumption Breakdown**
| Utility | Usage | Charge |
|---------|-------|--------|
| Electricity | 1,380 kWh | AED 282.50 |
| Water | 4,200 gal | AED 18.90 |
| Fuel surcharge | — | AED 11.35 |

**Personalised Recommendations**

1. **Your usage is 18% below the Dubai average** for a similar home size — well done.
2. The slight spike vs April (+300 kWh) may be due to rising temperatures. Pre-cool rooms before peak heat hours (12–4 PM).
3. Your water consumption is in Tier 1 — most efficient tier. Continue conserving.

Overall: this is a healthy bill. A 10% further reduction is achievable with smart AC scheduling.""",

    "default": """I'm the DEWA Smart Assistant running in **Demo Mode** (no API key configured).

I can demonstrate:
- Tariff rate lookups
- Savings calculations
- Account summaries
- Outage status checks
- Bill image analysis
- Energy saving tips

Try one of the quick questions on the left, or ask me about tariffs, savings, or outages.

> **To enable real Claude AI responses**, add your `ANTHROPIC_API_KEY` to the `.env` file.""",
}


def _pick_response(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["tariff", "rate", "price", "cost per kwh"]):
        return MOCK_RESPONSES["tariff"]
    if any(w in msg for w in ["sav", "reduc", "lower", "cut", "20%", "15%"]):
        return MOCK_RESPONSES["saving"]
    if any(w in msg for w in ["account", "summary", "history", "balance", "bill amount"]):
        return MOCK_RESPONSES["account"]
    if any(w in msg for w in ["outage", "power cut", "blackout", "downtown"]):
        return MOCK_RESPONSES["outage"]
    if any(w in msg for w in ["tip", "advice", "green", "energy", "water saving"]):
        return MOCK_RESPONSES["tips"]
    if any(w in msg for w in ["analys", "image", "photo", "upload", "bill"]):
        return MOCK_RESPONSES["bill"]
    return MOCK_RESPONSES["default"]


class MockDEWAAgent:
    """Simulates DEWAAgent responses without hitting the Claude API."""

    TOOLS_SIMULATED = ["get_tariff_rates", "get_account_summary", "analyze_consumption"]

    def chat(
        self,
        user_message: str,
        history: list,
        image_data: dict = None,
        deep_analysis: bool = False,
    ) -> str:
        time.sleep(0.6)  # simulate network latency
        if image_data:
            return MOCK_RESPONSES["bill"]
        return _pick_response(user_message)

    def stream_chat(self, user_message: str, history: list, image_data=None):
        response = _pick_response(user_message)
        for word in response.split(" "):
            yield word + " "
            time.sleep(0.02)

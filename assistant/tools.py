import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Tool schemas for Claude API ───────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_tariff_rates",
        "description": (
            "Get current DEWA electricity and/or water tariff rates. "
            "Returns tiered pricing, fuel surcharges, and municipality fees."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_type": {
                    "type": "string",
                    "enum": ["residential", "commercial"],
                    "description": "Customer account type"
                },
                "utility": {
                    "type": "string",
                    "enum": ["electricity", "water", "both"],
                    "description": "Which utility rates to retrieve"
                }
            },
            "required": ["customer_type", "utility"]
        }
    },
    {
        "name": "calculate_savings",
        "description": (
            "Calculate the monthly and annual AED savings if the customer reduces "
            "electricity consumption by a given percentage. Returns current vs target bill."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "current_kwh": {
                    "type": "number",
                    "description": "Current monthly electricity consumption in kWh"
                },
                "reduction_pct": {
                    "type": "number",
                    "description": "Target reduction percentage (e.g. 15 means 15% less)"
                },
                "customer_type": {
                    "type": "string",
                    "enum": ["residential", "commercial"]
                }
            },
            "required": ["current_kwh", "reduction_pct", "customer_type"]
        }
    },
    {
        "name": "check_outage_status",
        "description": "Check for active or planned DEWA power outages in a specific Dubai area.",
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {
                    "type": "string",
                    "description": "Dubai area or district (e.g. Downtown Dubai, Jumeirah, Deira, Marina)"
                }
            },
            "required": ["area"]
        }
    },
    {
        "name": "get_account_summary",
        "description": (
            "Retrieve the customer's DEWA account summary: current balance, last bill amount, "
            "due date, and 6-month consumption history."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "DEWA account number (optional — uses demo account if omitted)"
                }
            },
            "required": []
        }
    },
    {
        "name": "analyze_consumption",
        "description": (
            "Analyze a list of monthly consumption data points. Returns trend direction, "
            "peak/low months, variance, and actionable saving insights."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "months_data": {
                    "type": "array",
                    "description": "Array of monthly records",
                    "items": {
                        "type": "object",
                        "properties": {
                            "month":      {"type": "string"},
                            "kwh":        {"type": "number"},
                            "amount_aed": {"type": "number"}
                        },
                        "required": ["month", "kwh"]
                    }
                }
            },
            "required": ["months_data"]
        }
    }
]


# ── Tool implementations ──────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> dict:
    dispatch = {
        "get_tariff_rates":  _get_tariff_rates,
        "calculate_savings": _calculate_savings,
        "check_outage_status": _check_outage_status,
        "get_account_summary": _get_account_summary,
        "analyze_consumption":  _analyze_consumption,
    }
    fn = dispatch.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    return fn(**inputs)


def _get_tariff_rates(customer_type: str, utility: str) -> dict:
    with open(DATA_DIR / "tariffs.json") as f:
        data = json.load(f)

    result: dict = {"customer_type": customer_type, "currency": "AED", "rates": {}}
    if utility in ("electricity", "both"):
        result["rates"]["electricity"] = data["electricity"][customer_type]
    if utility in ("water", "both"):
        result["rates"]["water"] = data["water"].get(customer_type, data["water"]["residential"])
    result["last_updated"] = data["last_updated"]
    return result


def _calculate_bill(kwh: float, customer_type: str) -> float:
    if customer_type == "commercial":
        return round(kwh * 0.40, 2)
    tiers = [(2000, 0.23), (4000, 0.28), (6000, 0.32), (float("inf"), 0.38)]
    total, prev = 0.0, 0
    for cap, rate in tiers:
        if kwh <= prev:
            break
        usage = min(kwh, cap) - prev
        total += usage * rate
        prev = cap
    return round(total, 2)


def _calculate_savings(current_kwh: float, reduction_pct: float, customer_type: str) -> dict:
    target_kwh = current_kwh * (1 - reduction_pct / 100)
    current_bill = _calculate_bill(current_kwh, customer_type)
    target_bill  = _calculate_bill(target_kwh, customer_type)
    saved = round(current_bill - target_bill, 2)
    return {
        "current_kwh": current_kwh,
        "current_bill_aed": current_bill,
        "target_kwh": round(target_kwh, 1),
        "target_bill_aed": target_bill,
        "monthly_savings_aed": saved,
        "annual_savings_aed": round(saved * 12, 2),
        "reduction_pct": reduction_pct,
    }


def _check_outage_status(area: str) -> dict:
    mock: dict[str, dict] = {
        "downtown dubai": {
            "status": "planned",
            "type": "maintenance",
            "start": "10:00",
            "estimated_restore": "14:00",
            "affected_units": 120,
        },
        "festival city": {
            "status": "active",
            "type": "unplanned",
            "since": "09:15",
            "estimated_restore": "TBD",
            "affected_units": 45,
        },
    }
    key = area.lower()
    for area_key, info in mock.items():
        if area_key in key or key in area_key:
            return {"area": area, **info}
    return {"area": area, "status": "clear", "message": "No active or planned outages."}


def _get_account_summary(account_number: str = "") -> dict:
    return {
        "account_number": account_number or "DEMO-100234",
        "customer_name": "Demo Customer",
        "account_type": "residential",
        "current_balance_aed": 245.50,
        "due_date": "2026-06-30",
        "last_bill_aed": 312.75,
        "last_bill_date": "2026-05-15",
        "consumption_history": [
            {"month": "Dec 2025", "kwh": 2100, "amount_aed": 498.00},
            {"month": "Jan 2026", "kwh": 1850, "amount_aed": 425.50},
            {"month": "Feb 2026", "kwh": 1620, "amount_aed": 372.60},
            {"month": "Mar 2026", "kwh": 1450, "amount_aed": 333.50},
            {"month": "Apr 2026", "kwh": 1680, "amount_aed": 386.40},
            {"month": "May 2026", "kwh": 1380, "amount_aed": 317.40},
        ],
        "average_monthly_kwh": 1680,
        "green_charger_registered": True,
        "shams_dubai_enrolled": False,
    }


def _analyze_consumption(months_data: list) -> dict:
    kwh_list = [m["kwh"] for m in months_data]
    avg = sum(kwh_list) / len(kwh_list)
    peak = max(months_data, key=lambda x: x["kwh"])
    low  = min(months_data, key=lambda x: x["kwh"])
    trend = "decreasing" if kwh_list[-1] < kwh_list[0] else "increasing"
    variance_pct = round((max(kwh_list) - min(kwh_list)) / avg * 100, 1)

    insights = [
        f"Your consumption trend is {trend} over the period.",
        f"Peak month: {peak['month']} at {peak['kwh']} kWh — likely due to summer AC usage.",
        f"Lowest month: {low['month']} at {low['kwh']} kWh.",
        "Setting AC to 24°C instead of 20°C can cut cooling costs by up to 30%.",
        "Running washing machines and dishwashers overnight (off-peak) reduces load on the grid.",
    ]
    if variance_pct > 40:
        insights.append(
            f"High variance ({variance_pct}%) — check for appliance faults or lifestyle changes."
        )

    return {
        "average_monthly_kwh": round(avg, 1),
        "peak_month": peak,
        "lowest_month": low,
        "trend": trend,
        "variance_pct": variance_pct,
        "insights": insights,
    }

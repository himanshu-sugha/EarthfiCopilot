"""
Agent 5: The Narrator — Conversational AI Interface
Uses Z.AI GLM-4 to answer follow-up questions about the analysis.
Provides chat-based interaction with all agent outputs as context.
"""

import os
import json
from datetime import datetime

try:
    from zhipuai import ZhipuAI
    HAS_ZHIPU = True
except ImportError:
    HAS_ZHIPU = False

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ZHIPU_API_KEY, ZHIPU_MODEL_PRIORITY, ZHIPU_BASE_URL


NARRATOR_SYSTEM = """You are EarthfiCopilot's Narrator Agent — a conversational AI interface for commodity intelligence.

You have access to the full analysis context from:
- Agent 1 (The Sentinel): Satellite NDVI vegetation data
- Agent 2 (The Oracle): News and market intelligence
- Agent 3 (The Strategist): Trading report and recommendation
- Agent 4 (The Dispatcher): Anomaly alerts

Answer user questions about:
- The satellite data and what NDVI means
- Current market conditions and news
- The trading recommendation and why
- Risk factors and alternative scenarios
- Technical details about the analysis methodology

Be concise, professional, and data-driven. Reference specific numbers from the analysis.
If asked about something not in the data, say so clearly."""


def build_context(sat_data, news_data, report_data, alert_data):
    """Build context string from all agent outputs."""
    # Strip non-serializable data
    sat_safe = {}
    for k, v in (sat_data or {}).items():
        if k not in ("recent_ndvi_array", "baseline_ndvi_array", "recent_rgb", "baseline_rgb"):
            sat_safe[k] = v

    context = f"""## Analysis Context

### Satellite Data
{json.dumps(sat_safe, indent=2, default=str)}

### Market Intelligence
Sentiment: {(news_data or {}).get('overall_sentiment', 'N/A')}
Themes: {(news_data or {}).get('key_themes', [])}
Price: {json.dumps((news_data or {}).get('commodity_price', {}), default=str)}

### Trading Report
{(report_data or {}).get('report', 'No report generated yet.')}

### Alerts
{json.dumps((alert_data or {}).get('alerts', []), indent=2, default=str)}
"""
    return context


def chat(user_message, sat_data=None, news_data=None, report_data=None, alert_data=None, history=None):
    """
    Process a chat message using Z.AI GLM-4.
    Returns the assistant's response.
    """
    key = ZHIPU_API_KEY
    if not key or key == "your_zhipu_api_key_here" or not HAS_ZHIPU:
        return _offline_response(user_message, sat_data, news_data)

    try:
        client = ZhipuAI(api_key=key, base_url=ZHIPU_BASE_URL)
        context = build_context(sat_data, news_data, report_data, alert_data)

        messages = [
            {"role": "system", "content": NARRATOR_SYSTEM + "\n\n" + context},
        ]
        # Add conversation history
        if history:
            for h in history[-6:]:  # Keep last 6 messages for context
                messages.append(h)
        messages.append({"role": "user", "content": user_message})

        for model_id in ZHIPU_MODEL_PRIORITY:
            try:
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    temperature=0.6,
                    max_tokens=800,
                )
                return resp.choices[0].message.content
            except Exception:
                continue

        return _offline_response(user_message, sat_data, news_data)

    except Exception as e:
        return f"⚠️ Z.AI connection error: {str(e)}\n\nPlease check your API key in the `.env` file."


def _offline_response(user_message, sat_data=None, news_data=None):
    """Generate a basic response without Z.AI."""
    msg = user_message.lower()

    if any(w in msg for w in ["ndvi", "satellite", "vegetation"]):
        ndvi = (sat_data or {}).get("recent_ndvi_mean", "N/A")
        change = (sat_data or {}).get("ndvi_change_percent", "N/A")
        return (f"📊 **NDVI Analysis**\n\n"
                f"Current mean NDVI: **{ndvi}**\n"
                f"Change over 90 days: **{change}%**\n\n"
                f"NDVI (Normalized Difference Vegetation Index) ranges from -1 to 1. "
                f"Healthy vegetation typically shows values >0.6. Values <0.4 indicate stress.\n\n"
                f"*Connect Z.AI API key for deeper analysis.*")

    if any(w in msg for w in ["price", "market", "futures"]):
        price = (news_data or {}).get("commodity_price", {})
        return (f"💰 **Market Data**\n\n"
                f"Commodity: {price.get('commodity', 'N/A')}\n"
                f"Price: {price.get('currency', '')} {price.get('price', 'N/A')}\n"
                f"1M Change: {price.get('change_1m', 'N/A')}%\n\n"
                f"*Connect Z.AI API key for deeper analysis.*")

    if any(w in msg for w in ["recommend", "trade", "buy", "sell", "long", "short"]):
        return ("📈 **Trading Recommendation**\n\n"
                "Based on the current analysis, the system has generated a trading recommendation "
                "in the Trading Report tab. Please review it there.\n\n"
                "*Connect Z.AI API key for interactive Q&A about the recommendation.*")

    return ("👋 I'm the **Narrator Agent** — your conversational interface for EarthfiCopilot.\n\n"
            "I can answer questions about:\n"
            "- 🛰️ Satellite data & NDVI\n"
            "- 📰 Market news & sentiment\n"
            "- 📈 Trading recommendations\n"
            "- 🚨 Anomaly alerts\n\n"
            "*Connect your Z.AI API key (free at open.bigmodel.cn) for full conversational AI.*")


if __name__ == "__main__":
    print(chat("What does the NDVI data show?"))

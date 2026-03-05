"""
Agent 3: The Strategist — Z.AI GLM-4 Powered Trading Analyst
Synthesizes satellite data (Agent 1) and market intelligence (Agent 2)
into professional institutional-grade trading reports using Z.AI's GLM models.
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
from config import ZHIPU_API_KEY, ZHIPU_MODELS, ZHIPU_DEFAULT_MODEL


SYSTEM_PROMPT = """You are EarthfiCopilot's Strategist Agent — an elite institutional-grade commodity trading analyst 
powered by satellite Earth Observation data and real-time market intelligence.

Synthesize:
1. Satellite vegetation health data (NDVI indices from Sentinel-2)
2. Current news and market intelligence
3. Commodity price movements

Into a professional, actionable trading report that a hedge fund portfolio manager would use.

Your report MUST include these sections in Markdown:
- **Executive Summary** (2-3 sentences with recommendation)
- **Satellite Data Analysis** (interpret NDVI changes, table format)
- **Market Intelligence Summary** (news themes, sentiment, price data)
- **Supply-Demand Impact Assessment** (table with factors)
- **Trading Recommendation** (LONG/SHORT/HOLD + confidence %)
- **Price Target** (1-3 month range)
- **Risk Factors** (numbered list)

Use precise financial language. Cite specific numbers. Format in clean Markdown with tables."""


def _get_client():
    """Initialize Z.AI client."""
    if not HAS_ZHIPU:
        return None
    key = ZHIPU_API_KEY
    if not key or key == "your_zhipu_api_key_here":
        return None
    return ZhipuAI(api_key=key)


def _build_prompt(sat_data, news_data):
    """Build analysis prompt from Agent 1 + Agent 2 outputs."""
    sat = {
        "region": sat_data.get("region", "Unknown"),
        "commodity": sat_data.get("commodity", "Unknown"),
        "baseline_ndvi": sat_data.get("baseline_ndvi_mean", "N/A"),
        "recent_ndvi": sat_data.get("recent_ndvi_mean", "N/A"),
        "ndvi_change_pct": sat_data.get("ndvi_change_percent", "N/A"),
        "vegetation_status": sat_data.get("vegetation_status", "UNKNOWN"),
        "data_mode": sat_data.get("data_mode", "UNKNOWN"),
    }
    news = {
        "sentiment": news_data.get("overall_sentiment", "NEUTRAL"),
        "themes": news_data.get("key_themes", []),
        "price": news_data.get("commodity_price", {}),
        "headlines": [
            {"title": a.get("title"), "source": a.get("source"), "summary": a.get("summary")}
            for a in news_data.get("news_articles", [])[:5]
        ],
    }
    return f"""Analyze this data and produce a professional commodity trading report.

## SATELLITE DATA (Sentinel-2 NDVI)
```json
{json.dumps(sat, indent=2, default=str)}
```

## MARKET INTELLIGENCE
```json
{json.dumps(news, indent=2, default=str)}
```

Generate a complete institutional-grade trading report with specific numbers and clear recommendation."""


def generate_report(sat_data, news_data, model_tier=None):
    """Call Z.AI GLM-4 to generate the trading report."""
    print(f"\n{'━'*60}")
    print(f"  🧠  AGENT 3: THE STRATEGIST — Financial Analysis")
    print(f"{'━'*60}")

    model_tier = model_tier or ZHIPU_DEFAULT_MODEL
    client = _get_client()

    if client is None or not HAS_ZHIPU:
        print("  ⚠️ Z.AI not configured — generating demo report")
        return _demo_report(sat_data, news_data)

    model_id = ZHIPU_MODELS.get(model_tier, ZHIPU_MODELS["free"])
    prompt = _build_prompt(sat_data, news_data)
    print(f"  [Strategist] Calling Z.AI model: {model_id}...")

    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2500,
            top_p=0.9,
        )
        text = resp.choices[0].message.content
        usage = resp.usage
        print(f"  ✅ Report generated! Tokens: {usage.total_tokens}")

        return {
            "agent": "The Strategist (Z.AI GLM-4)",
            "model": model_id,
            "generated_at": datetime.now().isoformat(),
            "tokens": {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens, "total": usage.total_tokens},
            "report": text,
            "data_mode": "LIVE_AI",
        }
    except Exception as e:
        print(f"  ⚠️ Z.AI call failed: {e}")
        return _demo_report(sat_data, news_data)


def _demo_report(sat_data, news_data):
    """Generate realistic demo report when Z.AI is unavailable."""
    ndvi_change = sat_data.get("ndvi_change_percent", -47.2)
    status = sat_data.get("vegetation_status", "SEVERE_DECLINE")
    baseline = sat_data.get("baseline_ndvi_mean", 0.72)
    recent = sat_data.get("recent_ndvi_mean", 0.38)
    commodity = sat_data.get("commodity", "Arabica Coffee")
    region = sat_data.get("region", "Unknown")
    price = news_data.get("commodity_price", {}).get("price", 2.85)
    currency = news_data.get("commodity_price", {}).get("currency", "USD/lb")
    sentiment = news_data.get("overall_sentiment", "BEARISH_SUPPLY")

    text = f"""# EarthfiCopilot — {commodity} Trading Report

## 📊 Executive Summary

Satellite-derived vegetation indices for **{region}** reveal a **{abs(ndvi_change):.1f}% decline** in NDVI over 90 days, indicating severe agricultural stress. Combined with **{sentiment.replace('_', ' ').lower()}** supply-side news, we issue a **STRONG LONG** on {commodity} Futures with **85% confidence**.

---

## 🛰️ Satellite Data Analysis

| Metric | Baseline (90d) | Current | Change |
|--------|----------------|---------|--------|
| Mean NDVI | {baseline:.4f} | {recent:.4f} | **{ndvi_change:+.1f}%** |
| Status | Healthy | **{status.replace('_', ' ').title()}** | ⚠️ Critical |
| Source | Sentinel-2 L2A | Planetary Computer | Free |

NDVI below 0.4 in agricultural zones indicates significant vegetation stress. The decline from {baseline:.2f} to {recent:.2f} is consistent with severe drought, historically correlating with 10-15% yield reduction.

---

## 📰 Market Intelligence

- **Sentiment:** {sentiment.replace('_', ' ').title()}
- **Themes:** Drought, production downgrades, futures rally, La Niña
- **Current Price:** {currency} {price:.2f}

---

## 📈 Supply-Demand Assessment

| Factor | Impact | Confidence |
|--------|--------|-----------|
| Production shortfall | -12% YoY | High |
| La Niña prolongation | -3 to -5% risk | Medium |
| Global demand growth | +2.5% YoY | High |
| Projected supply gap | 8-15M units | Medium-High |

---

## 🎯 Trading Recommendation

| | |
|---|---|
| **Direction** | **LONG** (Buy) |
| **Instrument** | {commodity} Futures |
| **Confidence** | **85%** |
| **Entry** | {currency} {price:.2f} |
| **Target (3M)** | {currency} {price * 1.25:.2f} - {price * 1.35:.2f} |
| **Stop Loss** | {currency} {price * 0.92:.2f} |
| **Risk-Reward** | 3.2:1 |

---

## ⚠️ Risk Factors

1. Unexpected late-season rainfall could mitigate drought
2. Sharp price increases may slow demand
3. Currency risk in producer nations
4. Alternative supply sources may fill gap

---

*Generated by EarthfiCopilot | Powered by Z.AI GLM-4 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Disclaimer: AI-generated analysis for educational purposes. Not financial advice.*"""

    return {
        "agent": "The Strategist (Demo Report)",
        "model": "demo_template",
        "generated_at": datetime.now().isoformat(),
        "tokens": {"prompt": 0, "completion": 0, "total": 0},
        "report": text,
        "data_mode": "DEMO_REPORT",
    }


if __name__ == "__main__":
    dummy_sat = {"baseline_ndvi_mean": 0.72, "recent_ndvi_mean": 0.38,
                 "ndvi_change_percent": -47.2, "vegetation_status": "SEVERE_DECLINE",
                 "region": "Minas Gerais, Brazil", "commodity": "Arabica Coffee"}
    dummy_news = {"overall_sentiment": "BEARISH_SUPPLY", "key_themes": ["Drought"],
                  "commodity_price": {"price": 2.85, "currency": "USD/lb"}, "news_articles": []}
    result = generate_report(dummy_sat, dummy_news)
    print("\n" + result["report"])

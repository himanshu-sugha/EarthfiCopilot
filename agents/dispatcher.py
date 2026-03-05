"""
Agent 4: The Dispatcher — Anomaly Detection & Alert System
Uses Z.AI GLM-4 to classify satellite + news data into priority alerts.
Identifies drought, flood, fire, price spike, or supply shock events.
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


ALERT_PROMPT = """You are EarthfiCopilot's Dispatcher Agent — an anomaly detection system.

Given satellite NDVI data and market intelligence, identify and classify anomalies into alerts.

Return a JSON array of alerts. Each alert must have:
- "type": one of ["DROUGHT", "FLOOD", "PRICE_SPIKE", "SUPPLY_SHOCK", "WEATHER_EXTREME", "PRODUCTION_DROP"]
- "severity": one of ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
- "title": short alert title (max 80 chars)
- "description": 1-2 sentence explanation
- "confidence": 0-100 integer
- "action": recommended action (1 sentence)

Return ONLY the JSON array, no other text. Generate 2-5 alerts based on the data."""


def generate_alerts(sat_data, news_data):
    """Generate priority alerts from satellite + news data using Z.AI."""
    print(f"\n{'━'*60}")
    print(f"  🚨  AGENT 4: THE DISPATCHER — Anomaly Detection")
    print(f"{'━'*60}")

    key = ZHIPU_API_KEY
    if key and key != "your_zhipu_api_key_here" and HAS_ZHIPU:
        client = ZhipuAI(api_key=key, base_url=ZHIPU_BASE_URL)
        sat_summary = {
            "region": sat_data.get("region"),
            "commodity": sat_data.get("commodity"),
            "ndvi_change_pct": sat_data.get("ndvi_change_percent"),
            "vegetation_status": sat_data.get("vegetation_status"),
        }
        news_summary = {
            "sentiment": news_data.get("overall_sentiment"),
            "themes": news_data.get("key_themes"),
            "price": news_data.get("commodity_price", {}).get("price"),
            "price_change_1m": news_data.get("commodity_price", {}).get("change_1m"),
        }

        prompt = f"""Satellite data: {json.dumps(sat_summary)}
News data: {json.dumps(news_summary)}

Generate alerts based on this data."""

        for model_id in ZHIPU_MODEL_PRIORITY:
            try:
                print(f"  [Dispatcher] Trying Z.AI model: {model_id}...")
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": ALERT_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )

                text = resp.choices[0].message.content.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                alerts = json.loads(text)
                print(f"  ✅ Generated {len(alerts)} alerts via Z.AI {model_id}")
                return {
                    "agent": f"The Dispatcher (Z.AI {model_id})",
                    "generated_at": datetime.now().isoformat(),
                    "data_mode": "LIVE_AI",
                    "alerts": alerts,
                    "tokens": resp.usage.total_tokens,
                }
            except Exception as e:
                print(f"  ⚠️ {model_id} failed: {str(e)[:80]}")
                continue

    # Fallback: rule-based alerts
    return _rule_based_alerts(sat_data, news_data)


def _rule_based_alerts(sat_data, news_data):
    """Generate alerts using rules when Z.AI is unavailable."""
    print("  [Dispatcher] Using rule-based alert generation")
    alerts = []
    ndvi_change = sat_data.get("ndvi_change_percent", 0)
    status = sat_data.get("vegetation_status", "STABLE")
    commodity = sat_data.get("commodity", "Unknown")
    region = sat_data.get("region", "Unknown")
    sentiment = news_data.get("overall_sentiment", "NEUTRAL")
    price_change = news_data.get("commodity_price", {}).get("change_1m", 0)

    # Drought alert
    if ndvi_change < -15:
        severity = "CRITICAL" if ndvi_change < -30 else "HIGH"
        alerts.append({
            "type": "DROUGHT",
            "severity": severity,
            "title": f"🔴 Severe Vegetation Decline in {region}",
            "description": f"NDVI dropped {abs(ndvi_change):.1f}% over 90 days. Status: {status.replace('_', ' ')}. This indicates severe drought stress on {commodity} crops.",
            "confidence": min(95, int(50 + abs(ndvi_change))),
            "action": f"Consider LONG position on {commodity} futures due to expected supply reduction.",
        })
    elif ndvi_change < -5:
        alerts.append({
            "type": "DROUGHT",
            "severity": "MEDIUM",
            "title": f"🟡 Moderate Vegetation Stress in {region}",
            "description": f"NDVI declined {abs(ndvi_change):.1f}%. Monitor for further deterioration.",
            "confidence": int(40 + abs(ndvi_change)),
            "action": "Increase monitoring frequency. Prepare contingency positions.",
        })

    # Price spike alert
    if price_change and abs(price_change) > 5:
        direction = "surge" if price_change > 0 else "drop"
        alerts.append({
            "type": "PRICE_SPIKE",
            "severity": "HIGH" if abs(price_change) > 10 else "MEDIUM",
            "title": f"📈 {commodity} Price {direction.title()} ({price_change:+.1f}% / 1M)",
            "description": f"{commodity} prices {direction}d {abs(price_change):.1f}% in the past month, indicating significant market movement.",
            "confidence": 80,
            "action": f"Review {commodity} positions. Market is pricing in supply concerns.",
        })

    # Supply shock
    if "BEARISH" in sentiment:
        alerts.append({
            "type": "SUPPLY_SHOCK",
            "severity": "HIGH",
            "title": f"⚠️ Supply-Side Bearish Sentiment for {commodity}",
            "description": f"News sentiment is {sentiment.replace('_', ' ').lower()}. Multiple sources report production downgrades.",
            "confidence": 75,
            "action": "Cross-reference satellite data with production forecasts. Adjust positions accordingly.",
        })

    # Weather alert
    themes = news_data.get("key_themes", [])
    if any("La Niña" in t or "Weather" in t for t in themes):
        alerts.append({
            "type": "WEATHER_EXTREME",
            "severity": "MEDIUM",
            "title": "🌊 La Niña / Extreme Weather Pattern Detected",
            "description": "Weather patterns indicate ongoing La Niña conditions, which historically impact crop yields in key growing regions.",
            "confidence": 70,
            "action": "Monitor long-range weather forecasts. Consider hedging strategies.",
        })

    if not alerts:
        alerts.append({
            "type": "PRODUCTION_DROP",
            "severity": "LOW",
            "title": "✅ No Critical Anomalies Detected",
            "description": "Current conditions appear within normal ranges. Continue routine monitoring.",
            "confidence": 60,
            "action": "Maintain current positions. Re-assess in 7 days.",
        })

    print(f"  ✅ Generated {len(alerts)} rule-based alerts")
    return {
        "agent": "The Dispatcher (Rule-Based)",
        "generated_at": datetime.now().isoformat(),
        "data_mode": "RULE_BASED",
        "alerts": alerts,
        "tokens": 0,
    }


if __name__ == "__main__":
    dummy_sat = {"ndvi_change_percent": -47.2, "vegetation_status": "SEVERE_DECLINE",
                 "commodity": "Coffee", "region": "Minas Gerais, Brazil"}
    dummy_news = {"overall_sentiment": "BEARISH_SUPPLY", "key_themes": ["Drought", "La Niña Pattern"],
                  "commodity_price": {"price": 2.85, "change_1m": 8.2}}
    result = generate_alerts(dummy_sat, dummy_news)
    print("\n" + json.dumps(result, indent=2))

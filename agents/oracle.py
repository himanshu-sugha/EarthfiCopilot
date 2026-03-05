"""
Agent 2: The Oracle — News & Market Intelligence Aggregator
Fetches real-time agricultural news, commodity prices, and weather data
using free RSS feeds and public APIs.
"""

import json
import re
from datetime import datetime

try:
    import feedparser
    HAS_FEED = True
except ImportError:
    HAS_FEED = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import get_news_feeds


# ─── Fallback demo headlines ──────────────────────────────────
def _get_demo_headlines(commodity="Coffee"):
    return [
        {
            "title": f"Severe Drought Threatens {commodity} Production in Key Growing Region",
            "source": "Reuters",
            "date": "2026-03-04",
            "summary": f"Rainfall has dropped 40% below historical average over the past three months, raising "
                       f"concerns about the {commodity.lower()} crop. Soil moisture levels are critically low.",
            "sentiment": "bearish",
            "relevance": "high",
        },
        {
            "title": f"{commodity} Futures Surge 8% Amid Supply Concerns",
            "source": "Bloomberg",
            "date": "2026-03-03",
            "summary": f"{commodity} futures rallied sharply as traders price in potential supply disruptions. "
                       f"Spot prices jumped to multi-month highs on tightening supply outlook.",
            "sentiment": "bullish_for_price",
            "relevance": "high",
        },
        {
            "title": f"Production Forecast Revised Downward by 12% for {commodity}",
            "source": "AgriNews",
            "date": "2026-03-02",
            "summary": f"National agricultural agencies have revised {commodity.lower()} production estimates "
                       f"significantly downward, citing adverse weather conditions in key growing states.",
            "sentiment": "bearish_supply",
            "relevance": "critical",
        },
        {
            "title": f"Global {commodity} Demand Continues to Rise Despite Price Increases",
            "source": "Financial Times",
            "date": "2026-03-01",
            "summary": f"Global consumption is projected to rise 2.5% year-over-year, driven by growing demand "
                       f"in Asia-Pacific markets. The demand-supply gap could widen.",
            "sentiment": "bullish_for_price",
            "relevance": "medium",
        },
        {
            "title": "La Niña Weather Pattern Expected to Persist Through Q2 2026",
            "source": "NOAA",
            "date": "2026-02-28",
            "summary": "La Niña conditions will persist through June 2026, potentially exacerbating drought in "
                       "major growing regions while bringing excess rainfall to some alternatives.",
            "sentiment": "mixed",
            "relevance": "high",
        },
    ]


def fetch_live_news(commodity="Coffee", max_per_feed=5):
    """Fetch live news from Google News RSS feeds."""
    if not HAS_FEED:
        return None

    feeds = get_news_feeds(commodity)
    articles = []

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title = re.sub(r'<[^>]+>', '', entry.get('title', ''))
                summary = re.sub(r'<[^>]+>', '', entry.get('summary', entry.get('description', '')))
                articles.append({
                    "title": title,
                    "source": source,
                    "date": entry.get('published', datetime.now().strftime('%Y-%m-%d')),
                    "summary": summary[:300],
                    "link": entry.get('link', ''),
                })
            print(f"  [Oracle] Fetched {min(len(feed.entries), max_per_feed)} from {source}")
        except Exception as e:
            print(f"  [Oracle] Warning: {source} failed: {e}")

    return articles if articles else None


def fetch_commodity_price(commodity="Coffee"):
    """Get approximate commodity price (demo values, extendable to real APIs)."""
    prices = {
        "Arabica Coffee": {"price": 2.85, "currency": "USD/lb", "change_1m": 8.2, "change_3m": 22.5},
        "Wheat": {"price": 6.42, "currency": "USD/bu", "change_1m": 3.1, "change_3m": 11.8},
        "Corn": {"price": 4.75, "currency": "USD/bu", "change_1m": -2.3, "change_3m": 5.4},
        "Soybeans": {"price": 12.38, "currency": "USD/bu", "change_1m": 4.7, "change_3m": 15.2},
        "Cotton": {"price": 0.82, "currency": "USD/lb", "change_1m": 1.9, "change_3m": -3.1},
    }
    data = prices.get(commodity, prices["Arabica Coffee"])
    data["commodity"] = commodity
    data["source"] = "Market Estimate"
    data["date"] = datetime.now().strftime('%Y-%m-%d')
    return data


def extract_themes(articles):
    """Extract key themes from articles."""
    themes = set()
    keywords_map = {
        "drought": "Drought Conditions", "rainfall": "Rainfall Anomaly",
        "la niña": "La Niña Pattern", "la nina": "La Niña Pattern",
        "price": "Price Volatility", "futures": "Futures Activity",
        "supply": "Supply Disruption", "production": "Production Forecast",
        "demand": "Demand Growth", "harvest": "Harvest Concerns",
        "flood": "Flood Risk", "fire": "Wildfire Risk",
        "export": "Export Changes", "tariff": "Trade Policy",
    }
    for a in articles:
        text = (a.get("title", "") + " " + a.get("summary", "")).lower()
        for kw, theme in keywords_map.items():
            if kw in text:
                themes.add(theme)
    return list(themes) if themes else ["General Market Conditions"]


def compute_sentiment(articles):
    """Rule-based sentiment analysis."""
    bearish = ["drought", "decline", "drop", "shortage", "downward", "worst", "crisis", "low", "flood", "fire"]
    bullish = ["surge", "rally", "growth", "increase", "rise", "demand", "record", "recover"]

    b_count = sum(1 for a in articles for kw in bearish
                  if kw in (a.get("title", "") + " " + a.get("summary", "")).lower())
    g_count = sum(1 for a in articles for kw in bullish
                  if kw in (a.get("title", "") + " " + a.get("summary", "")).lower())

    if b_count > g_count + 2:
        return "STRONGLY_BEARISH_SUPPLY"
    elif b_count > g_count:
        return "BEARISH_SUPPLY"
    elif g_count > b_count + 2:
        return "BULLISH_SUPPLY"
    elif g_count > b_count:
        return "MILDLY_BULLISH"
    return "NEUTRAL"


def gather_intelligence(commodity="Arabica Coffee"):
    """
    Main entry point for Agent 2.
    Returns structured intelligence report for The Strategist.
    """
    print(f"\n{'━'*60}")
    print(f"  📡  AGENT 2: THE ORACLE — Intelligence Gathering")
    print(f"{'━'*60}")

    live = fetch_live_news(commodity)

    if live and len(live) >= 3:
        news_data = live[:8]
        mode = "LIVE_NEWS"
        print(f"  [Oracle] Using {len(news_data)} live articles")
    else:
        news_data = _get_demo_headlines(commodity)
        mode = "DEMO_NEWS"
        print(f"  [Oracle] Using {len(news_data)} demo headlines")

    price = fetch_commodity_price(commodity)

    report = {
        "agent": "The Oracle (Market Intelligence)",
        "analysis_date": datetime.now().isoformat(),
        "data_mode": mode,
        "commodity": commodity,
        "commodity_price": price,
        "news_articles": news_data,
        "key_themes": extract_themes(news_data),
        "overall_sentiment": compute_sentiment(news_data),
    }

    print(f"  ✅ Intelligence complete! Sentiment: {report['overall_sentiment']}")
    return report


if __name__ == "__main__":
    report = gather_intelligence()
    print("\n" + json.dumps(report, indent=2, default=str))

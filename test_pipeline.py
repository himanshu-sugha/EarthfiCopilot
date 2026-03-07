"""Quick pipeline test — verifies all agents work"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__) or '.')

from config import REGIONS, ZAI_API_KEY
from agents.sentinel import analyze_region
from agents.oracle import gather_intelligence
from agents.strategist import generate_report
from agents.dispatcher import generate_alerts
from agents.narrator import chat

region = list(REGIONS.keys())[0]
ri = REGIONS[region]
print(f"=== Testing: {region} ===")
print(f"Z.AI key configured: {bool(ZAI_API_KEY)}")

# Agent 1: Sentinel
sat = analyze_region(ri['bbox'], ri['commodity'])
print(f"\n[Sentinel] NDVI={sat.get('recent_ndvi_mean')}, status={sat.get('vegetation_status')}, change={sat.get('ndvi_change_percent')}%")
print(f"[Sentinel] NDWI flood={sat.get('ndwi',{}).get('flood_risk')}, SCL quality={sat.get('scl_quality',{}).get('quality_score')}")

# Agent 2: Oracle
news = gather_intelligence(region, ri['commodity'])
print(f"\n[Oracle] sentiment={news.get('overall_sentiment')}, price={news.get('commodity_price',{}).get('price')}")

# Agent 3: Strategist
report = generate_report(sat, news)
print(f"\n[Strategist] mode={report.get('data_mode')}, model={report.get('model')}, tokens={report.get('tokens',{}).get('total',0)}")
print(f"[Strategist] report length: {len(report.get('report',''))} chars")

# Agent 4: Dispatcher
alerts = generate_alerts(sat, news)
print(f"\n[Dispatcher] mode={alerts.get('data_mode')}, alerts={len(alerts.get('alerts',[]))}")

# Commercial Insights test
ndvi_mean = sat.get('recent_ndvi_mean', 0.5)
ndvi_dev = ndvi_mean - 0.6
yield_pct = round(ndvi_dev * 100, 1) if ndvi_dev < 0 else round(min(ndvi_dev * 50, 15), 1) if ndvi_dev > 0.1 else 0
print(f"\n[Commercial] NDVI={ndvi_mean}, deviation={ndvi_dev:.2f}, yield_impact={yield_pct:+.1f}%")

print("\n=== ALL AGENTS OK ===")

"""
EarthfiCopilot — CLI Orchestrator
Runs all 5 agents in sequence and outputs summary.
Usage: python main.py [--demo] [--region "Region Name"]
"""

import argparse
import json
import sys
from datetime import datetime

from agents.sentinel import analyze_region, get_serializable
from agents.oracle import gather_intelligence
from agents.strategist import generate_report
from agents.dispatcher import generate_alerts
from config import REGIONS, DEFAULT_REGION


def run_pipeline(region_name=None, use_ai=True):
    """Run the full 5-agent pipeline."""
    region_name = region_name or DEFAULT_REGION
    region_info = REGIONS.get(region_name, REGIONS[DEFAULT_REGION])
    commodity = region_info["commodity"]

    print(f"\n{'█'*60}")
    print(f"  🌍 EarthfiCopilot — Multi-Agent Commodity Intelligence")
    print(f"  Region: {region_name}")
    print(f"  Commodity: {commodity}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'█'*60}")

    # Agent 1: The Sentinel
    sat_data = analyze_region(region_name=region_name)

    # Agent 2: The Oracle
    news_data = gather_intelligence(commodity=commodity)

    # Agent 3: The Strategist
    report_data = generate_report(sat_data, news_data)

    # Agent 4: The Dispatcher
    alert_data = generate_alerts(sat_data, news_data)

    # Summary
    print(f"\n{'█'*60}")
    print(f"  ✅ PIPELINE COMPLETE")
    print(f"{'█'*60}")
    print(f"  Satellite: {sat_data.get('data_mode', 'N/A')}")
    print(f"  News: {news_data.get('data_mode', 'N/A')}")
    print(f"  Report: {report_data.get('data_mode', 'N/A')}")
    print(f"  Alerts: {alert_data.get('data_mode', 'N/A')} ({len(alert_data.get('alerts', []))} alerts)")

    return sat_data, news_data, report_data, alert_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EarthfiCopilot CLI")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (no API calls)")
    parser.add_argument("--region", type=str, default=DEFAULT_REGION, help="Region to analyze")
    parser.add_argument("--list-regions", action="store_true", help="List available regions")
    args = parser.parse_args()

    if args.list_regions:
        print("\nAvailable regions:")
        for name, info in REGIONS.items():
            print(f"  - {name} ({info['commodity']})")
        sys.exit(0)

    sat, news, report, alerts = run_pipeline(region_name=args.region, use_ai=not args.demo)

    # Print the trading report
    print("\n" + "="*60)
    print(report.get("report", "No report generated"))
    print("="*60)

    # Print alerts
    print("\n🚨 ALERTS:")
    for a in alerts.get("alerts", []):
        print(f"  [{a.get('severity', '?')}] {a.get('title', 'Unknown')}")

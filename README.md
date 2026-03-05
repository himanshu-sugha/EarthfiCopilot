# EarthfiCopilot — Multi-Agent Commodity Intelligence from Space

**5-agent AI system that turns free satellite data + real-time news into institutional-grade commodity trading intelligence, powered by Z.AI GLM-4.**

![Z.AI](https://img.shields.io/badge/Powered%20by-Z.AI%20GLM--4-6366f1?style=for-the-badge)
![Sentinel-2](https://img.shields.io/badge/Data-Sentinel--2%20Satellite-10b981?style=for-the-badge)
![Cost](https://img.shields.io/badge/API%20Cost-$0-22c55e?style=for-the-badge)

## What is EarthfiCopilot?

EarthfiCopilot is a **production-ready multi-agent AI system** that:

1. **Fetches satellite imagery** (Sentinel-2 via Microsoft Planetary Computer — free)
2. **Computes vegetation health indices** (NDVI, change detection)
3. **Aggregates real-time news** (commodity prices, weather, market sentiment)
4. **Generates trading reports** using Z.AI's GLM-4 model (institutional-grade)
5. **Detects anomalies** (drought, floods, supply shocks) with Z.AI classification
6. **Answers follow-up questions** via a conversational Z.AI chat interface

All **100% free** — Z.AI GLM-4-Flash has no rate limits, Sentinel-2 data is open access.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                        │
│  🗺️ Map  📊 Charts  📰 News  📈 Report  💬 Chat  🚨 Alerts │
└──────────────┬───────────────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────────────┐
│              main.py — Agent Orchestrator                     │
└──┬──────┬──────────┬──────────┬──────────┬───────────────────┘
   │      │          │          │          │
┌──┴──┐ ┌─┴────┐ ┌──┴────┐ ┌──┴─────┐ ┌──┴──────┐
│🛰️   │ │📡    │ │🧠     │ │🚨     │ │💬      │
│Sent-│ │Oracle│ │Strat- │ │Dispat-│ │Narrat- │
│inel │ │      │ │egist  │ │cher   │ │or      │
│     │ │      │ │       │ │       │ │        │
│NDVI │ │RSS   │ │Z.AI   │ │Z.AI   │ │Z.AI    │
│STAC │ │Prices│ │GLM-4  │ │GLM-4  │ │GLM-4   │
└─────┘ └──────┘ └───────┘ └───────┘ └────────┘
```

| Agent | Name | Role | Z.AI? |
|-------|------|------|-------|
| 1 | **The Sentinel** | Satellite NDVI vegetation analysis | — |
| 2 | **The Oracle** | News aggregation, prices, sentiment | — |
| 3 | **The Strategist** | Trading report generation | ✅ GLM-4 |
| 4 | **The Dispatcher** | Anomaly detection & alerts | ✅ GLM-4 |
| 5 | **The Narrator** | Conversational chat interface | ✅ GLM-4 |

**3 out of 5 agents use Z.AI GLM-4** — for reasoning, classification, and conversation.

## Supported Commodities & Regions

| Region | Commodity | Exchange |
|--------|-----------|----------|
| Minas Gerais, Brazil | Arabica Coffee | ICE KC |
| Punjab, India | Wheat | CBOT ZW |
| Iowa, USA | Corn | CBOT ZC |
| Mato Grosso, Brazil | Soybeans | CBOT ZS |
| Nile Delta, Egypt | Cotton | ICE CT |

## Quick Start

### 1. Install

```bash
git clone https://github.com/YOUR_REPO/earthfi-copilot.git
cd earthfi-copilot
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your free Z.AI API key:
# Get it at https://open.bigmodel.cn/
```

### 3. Run Dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501 → Select a region → Click **Run Analysis**!

### 4. CLI Mode

```bash
python main.py                                    # Default region
python main.py --region "Punjab, India (Wheat)"   # Custom region
python main.py --list-regions                     # List all regions
```

## Z.AI Integration (3 Deep Usages)

EarthfiCopilot demonstrates **meaningful usage** of Z.AI's GLM series models across three distinct agent capabilities:

### 1. Financial Reasoning (The Strategist)
GLM-4 synthesizes satellite NDVI data + news intelligence into professional trading reports with LONG/SHORT/HOLD recommendations, price targets, and risk assessments.

### 2. Anomaly Classification (The Dispatcher)
GLM-4 classifies multi-source data into priority alerts (DROUGHT, FLOOD, PRICE_SPIKE, SUPPLY_SHOCK), assigning severity levels and confidence scores.

### 3. Conversational Interface (The Narrator)
GLM-4 powers a chat interface where users ask follow-up questions about the analysis. Full context from all agents is injected into the conversation.

## TCC Satellite Challenge Alignment

This project directly addresses the TCC challenge:

- **Detects real-world events**: Drought, floods, crop stress via NDVI change detection
- **Retrieves relevant satellite data**: Sentinel-2 L2A via Microsoft Planetary Computer
- **Analyzes it**: NDVI computation, temporal comparison, anomaly detection
- **Delivers insights customers would pay for**: Institutional-grade commodity trading reports

## Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| LLM Engine | Z.AI GLM-4-Flash | **$0** (unlimited free tier) |
| Satellite Data | Sentinel-2 via Planetary Computer | **$0** (open access) |
| News & Prices | Google News RSS + public APIs | **$0** |
| UI Framework | Streamlit + Plotly + Folium | **$0** |
| Language | Python 3.10+ | **$0** |

## Project Structure

```
earthfi-copilot/
├── app.py              # Streamlit dashboard (5 tabs)
├── main.py             # CLI orchestrator
├── config.py           # API keys, regions, model config
├── agents/
│   ├── sentinel.py     # Agent 1: Satellite NDVI analysis
│   ├── oracle.py       # Agent 2: News + commodity prices
│   ├── strategist.py   # Agent 3: Z.AI trading reports
│   ├── dispatcher.py   # Agent 4: Z.AI anomaly alerts
│   └── narrator.py     # Agent 5: Z.AI chat interface
├── ui/
│   └── styles.py       # Premium dark-mode CSS
├── requirements.txt
├── .env.example
└── README.md
```

## Hackathon

Built for **UK AI Agent Hackathon EP4 x OpenClaw** (March 1-7, 2026).

### Bounties Applied

| Bounty | How We Qualify |
|--------|----------------|
| **Z.AI** | GLM-4 powers 3/5 agents (reasoning + classification + conversation) |
| **TCC Satellite** | Sentinel-2 → event detection → AI analysis → paid insights |
| **Animoca Minds** | Multi-agent financial co-pilot with cognition and decision-making |
| **Claw for Human** | Showcase what LLMs can build — commodity intelligence from space |

## License

MIT

---

*Built by Himanshu | Powered by Z.AI GLM-4 | Sentinel-2 via Microsoft Planetary Computer*

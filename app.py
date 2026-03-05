"""
EarthfiCopilot — Streamlit Dashboard
Premium dark-mode multi-agent commodity intelligence interface.
Run: streamlit run app.py
"""

import streamlit as st
import numpy as np
import json
from datetime import datetime

# Page config — MUST be first Streamlit call
st.set_page_config(
    page_title="EarthfiCopilot — Commodity Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import get_custom_css
from agents.sentinel import analyze_region, get_serializable
from agents.oracle import gather_intelligence
from agents.strategist import generate_report
from agents.dispatcher import generate_alerts
from agents.narrator import chat as narrator_chat
from config import REGIONS, DEFAULT_REGION, APP_NAME, APP_TAGLINE, ZHIPU_API_KEY

# ─── Inject CSS ──────────────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛰️ EarthfiCopilot")
    st.markdown("*Multi-Agent Commodity Intelligence*")
    st.markdown("---")

    # Region selector
    region = st.selectbox("🌍 Select Region", list(REGIONS.keys()), index=0)
    region_info = REGIONS[region]

    st.markdown(f"**Commodity:** {region_info['commodity']}")
    st.markdown(f"**Exchange:** {region_info['exchange']}")
    st.markdown(f"**BBox:** `{region_info['bbox']}`")

    st.markdown("---")

    # Run button
    run_clicked = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🤖 Agent Stack")

    agents_info = {
        "🛰️ The Sentinel": "Satellite NDVI",
        "📡 The Oracle": "News + Prices",
        "🧠 The Strategist": "Z.AI Trading Report",
        "🚨 The Dispatcher": "Anomaly Alerts",
        "💬 The Narrator": "Chat Interface",
    }
    for name, desc in agents_info.items():
        st.markdown(f"**{name}**  \n{desc}")

    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    api_status = "✅ Connected" if ZHIPU_API_KEY and ZHIPU_API_KEY != "your_zhipu_api_key_here" else "⚠️ Not set"
    st.markdown(f"**Z.AI API:** {api_status}")
    st.markdown(f"**Model:** GLM-4-Flash (Free)")

    st.markdown("---")
    st.markdown(
        '<div class="powered-by">Powered by Z.AI GLM-4<br>Sentinel-2 via Planetary Computer<br>'
        'UK AI Agent Hackathon EP4</div>',
        unsafe_allow_html=True,
    )


# ─── Header ──────────────────────────────────────────────────
st.markdown(
    f'<div class="hero-header">'
    f'<h1>🛰️ {APP_NAME}</h1>'
    f'<p>{APP_TAGLINE} — Powered by Z.AI GLM-4 & Sentinel-2</p>'
    f'</div>',
    unsafe_allow_html=True,
)


# ─── Session State ───────────────────────────────────────────
if "sat_data" not in st.session_state:
    st.session_state.sat_data = None
if "news_data" not in st.session_state:
    st.session_state.news_data = None
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "alert_data" not in st.session_state:
    st.session_state.alert_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_run" not in st.session_state:
    st.session_state.analysis_run = False


# ─── Run Pipeline ────────────────────────────────────────────
if run_clicked:
    st.session_state.chat_history = []

    with st.status("🚀 Running EarthfiCopilot Pipeline...", expanded=True) as status:
        # Agent 1
        st.write("🛰️ **Agent 1: The Sentinel** — Analyzing satellite imagery...")
        st.session_state.sat_data = analyze_region(region_name=region)

        # Agent 2
        st.write("📡 **Agent 2: The Oracle** — Gathering market intelligence...")
        commodity = region_info["commodity"]
        st.session_state.news_data = gather_intelligence(commodity=commodity)

        # Agent 3
        st.write("🧠 **Agent 3: The Strategist** — Generating trading report via Z.AI...")
        st.session_state.report_data = generate_report(
            st.session_state.sat_data, st.session_state.news_data
        )

        # Agent 4
        st.write("🚨 **Agent 4: The Dispatcher** — Detecting anomalies...")
        st.session_state.alert_data = generate_alerts(
            st.session_state.sat_data, st.session_state.news_data
        )

        st.session_state.analysis_run = True
        status.update(label="✅ Pipeline complete!", state="complete", expanded=False)


# ─── Main Content (Tabs) ─────────────────────────────────────
if not st.session_state.analysis_run:
    st.markdown("### 👈 Select a region and click **Run Analysis** to start")
    st.markdown("")

    # Show architecture diagram
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">5</div>'
            '<div class="metric-label">AI Agents</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">5</div>'
            '<div class="metric-label">Commodities</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">$0</div>'
            '<div class="metric-label">API Cost</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🏗️ Architecture")
    st.code("""
    ┌──────────────────────────────────────────────┐
    │           Streamlit Dashboard                 │
    │  Map · Charts · News · Report · Chat · Alerts│
    └─────────────────┬────────────────────────────┘
                      │
    ┌─────────────────┴────────────────────────────┐
    │          Agent Orchestrator (main.py)          │
    └──┬────┬─────┬──────┬──────┬──────────────────┘
       │    │     │      │      │
    🛰️    📡    🧠     🚨    💬
    Sent.  Orac. Strat. Disp. Narr.
    NDVI   RSS   GLM-4  GLM-4  GLM-4
    """, language=None)

else:
    sat = st.session_state.sat_data
    news = st.session_state.news_data
    report = st.session_state.report_data
    alerts = st.session_state.alert_data

    # ─── Top Metrics Row ─────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)

    ndvi_change = sat.get("ndvi_change_percent", 0)
    with m1:
        delta_class = "metric-delta-down" if ndvi_change < 0 else "metric-delta-up"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{sat.get("recent_ndvi_mean", "N/A")}</div>'
            f'<div class="metric-label">Current NDVI</div>'
            f'<div class="{delta_class}">{ndvi_change:+.1f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{sat.get("vegetation_status", "N/A").replace("_", " ").title()[:12]}</div>'
            f'<div class="metric-label">Veg. Status</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    price = news.get("commodity_price", {})
    with m3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{price.get("currency", "$")}{price.get("price", "N/A")}</div>'
            f'<div class="metric-label">{news.get("commodity", "Price")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with m4:
        sentiment = news.get("overall_sentiment", "NEUTRAL").replace("_", " ").title()
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{sentiment[:12]}</div>'
            f'<div class="metric-label">Sentiment</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with m5:
        n_alerts = len(alerts.get("alerts", []))
        critical = sum(1 for a in alerts.get("alerts", []) if a.get("severity") in ("CRITICAL", "HIGH"))
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{n_alerts}</div>'
            f'<div class="metric-label">Alerts ({critical} critical)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ─── Tabs ─────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛰️ Satellite", "📰 Intelligence", "📈 Trading Report", "🚨 Alerts", "💬 Chat"
    ])

    # ─── Tab 1: Satellite ─────────────────────────
    with tab1:
        st.markdown("### 🛰️ Satellite Vegetation Analysis")

        data_badge = "badge-live" if sat.get("data_mode") == "LIVE_SATELLITE" else "badge-demo"
        data_label = "LIVE" if sat.get("data_mode") == "LIVE_SATELLITE" else "DEMO"
        st.markdown(
            f'<span class="agent-badge {data_badge}">{data_label} DATA</span>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### NDVI Comparison")
            baseline_ndvi = sat.get("baseline_ndvi_array")
            recent_ndvi = sat.get("recent_ndvi_array")

            if baseline_ndvi is not None and isinstance(baseline_ndvi, np.ndarray):
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots

                fig = make_subplots(rows=1, cols=2, subplot_titles=("Baseline (90d ago)", "Current"))
                fig.add_trace(go.Heatmap(z=baseline_ndvi, colorscale="RdYlGn", zmin=-0.2, zmax=1, showscale=False), 1, 1)
                fig.add_trace(go.Heatmap(z=recent_ndvi, colorscale="RdYlGn", zmin=-0.2, zmax=1, colorbar=dict(title="NDVI")), 1, 2)
                fig.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#94a3b8",
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("#### NDVI Distribution")
            if recent_ndvi is not None and isinstance(recent_ndvi, np.ndarray):
                import plotly.graph_objects as go

                fig2 = go.Figure()
                fig2.add_trace(go.Histogram(
                    x=baseline_ndvi.flatten(), name="Baseline",
                    opacity=0.6, marker_color="#34d399",
                    nbinsx=50,
                ))
                fig2.add_trace(go.Histogram(
                    x=recent_ndvi.flatten(), name="Current",
                    opacity=0.6, marker_color="#f87171",
                    nbinsx=50,
                ))
                fig2.update_layout(
                    barmode="overlay",
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#94a3b8",
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    xaxis_title="NDVI Value",
                    yaxis_title="Pixel Count",
                )
                st.plotly_chart(fig2, use_container_width=True)

        # RGB thumbnails
        col_c, col_d = st.columns(2)
        with col_c:
            rgb = sat.get("baseline_rgb")
            if rgb:
                st.image(rgb, caption="Baseline RGB", use_container_width=True)
        with col_d:
            rgb = sat.get("recent_rgb")
            if rgb:
                st.image(rgb, caption="Current RGB", use_container_width=True)

        # Data table
        st.markdown("#### Scene Metadata")
        safe = get_serializable(sat)
        exclude = {"agent", "data_source", "bbox", "analysis_date", "region", "commodity"}
        display_data = {k: v for k, v in safe.items() if k not in exclude}
        st.json(display_data)

    # ─── Tab 2: Intelligence ──────────────────────
    with tab2:
        st.markdown("### 📰 Market Intelligence")

        data_badge = "badge-live" if news.get("data_mode") == "LIVE_NEWS" else "badge-demo"
        data_label = "LIVE" if news.get("data_mode") == "LIVE_NEWS" else "DEMO"
        st.markdown(
            f'<span class="agent-badge {data_badge}">{data_label} NEWS</span> '
            f'<span class="agent-badge badge-ai">Sentiment: {news.get("overall_sentiment", "N/A")}</span>',
            unsafe_allow_html=True,
        )

        # Price info
        st.markdown("#### Commodity Price")
        price = news.get("commodity_price", {})
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Commodity", price.get("commodity", "N/A"))
        pc2.metric("Price", f"{price.get('currency', '$')}{price.get('price', 'N/A')}")
        pc3.metric("1M Change", f"{price.get('change_1m', 'N/A')}%")
        pc4.metric("3M Change", f"{price.get('change_3m', 'N/A')}%")

        # Key themes
        st.markdown("#### Key Themes")
        themes = news.get("key_themes", [])
        theme_md = " | ".join([f"**{t}**" for t in themes])
        st.markdown(theme_md)

        # News articles
        st.markdown("#### News Feed")
        for article in news.get("news_articles", []):
            st.markdown(
                f'<div class="news-card">'
                f'<span class="news-source">{article.get("source", "Unknown")} · {article.get("date", "")}</span>'
                f'<h4>{article.get("title", "Untitled")}</h4>'
                f'<p>{article.get("summary", "")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ─── Tab 3: Trading Report ────────────────────
    with tab3:
        st.markdown("### 📈 AI-Generated Trading Report")

        model_badge = "badge-ai" if report.get("data_mode") == "LIVE_AI" else "badge-demo"
        model_label = f"Z.AI {report.get('model', 'demo')}" if report.get("data_mode") == "LIVE_AI" else "Demo Template"
        tokens = report.get("tokens", {}).get("total", 0)

        st.markdown(
            f'<span class="agent-badge {model_badge}">{model_label}</span> '
            f'<span class="agent-badge badge-live">Tokens: {tokens}</span>',
            unsafe_allow_html=True,
        )

        st.markdown(report.get("report", "*No report generated.*"))

    # ─── Tab 4: Alerts ────────────────────────────
    with tab4:
        st.markdown("### 🚨 Anomaly Alerts")

        mode_badge = "badge-ai" if alerts.get("data_mode") == "LIVE_AI" else "badge-demo"
        mode_label = "Z.AI" if alerts.get("data_mode") == "LIVE_AI" else "Rule-Based"
        st.markdown(
            f'<span class="agent-badge {mode_badge}">{mode_label} Detection</span>',
            unsafe_allow_html=True,
        )

        for alert in alerts.get("alerts", []):
            sev = alert.get("severity", "LOW").lower()
            css_class = f"alert-{sev}"
            st.markdown(
                f'<div class="{css_class}">'
                f'<strong>[{alert.get("severity", "?")}] {alert.get("title", "Alert")}</strong><br>'
                f'{alert.get("description", "")}<br>'
                f'<em>🎯 {alert.get("action", "")}</em><br>'
                f'<small>Confidence: {alert.get("confidence", "?")}% | Type: {alert.get("type", "?")}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ─── Tab 5: Chat ──────────────────────────────
    with tab5:
        st.markdown("### 💬 Ask The Narrator")
        st.markdown("*Chat with Z.AI about the analysis*")

        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Chat input
        user_input = st.chat_input("Ask about the satellite data, market trends, or trading recommendation...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.spinner("🧠 Thinking..."):
                response = narrator_chat(
                    user_input,
                    sat_data=sat,
                    news_data=news,
                    report_data=report,
                    alert_data=alerts,
                    history=st.session_state.chat_history,
                )

            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

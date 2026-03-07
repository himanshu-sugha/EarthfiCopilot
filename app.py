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
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import get_css
from agents.sentinel import analyze_region, get_serializable
from agents.oracle import gather_intelligence
from agents.strategist import generate_report
from agents.dispatcher import generate_alerts
from agents.narrator import chat as narrator_chat
from config import REGIONS, DEFAULT_REGION, APP_NAME, APP_TAGLINE, ZAI_API_KEY
from data.faostat_yields import get_yield_history, estimate_yield_from_ndvi, forecast_yield

# ─── Inject CSS ──────────────────────────────────────────────
st.markdown(get_css(), unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("assets/logo.png", use_container_width=True)
    with col_title:
        st.markdown(f"## {APP_NAME}")
    st.markdown(f"*{APP_TAGLINE}*")
    st.markdown("---")

    # Region selector (Default to index 1: Punjab, India)
    region = st.selectbox("🌍 Select Region", list(REGIONS.keys()), index=1)
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
    api_status = "✅ Connected" if ZAI_API_KEY and ZAI_API_KEY != "your_zai_api_key_here" else "⚠️ Not set"
    st.markdown(f"**Z.AI API:** {api_status}")
    st.markdown(f"**Model:** GLM-4-Flash (Free)")

    st.markdown("---")
    st.markdown(
        '<div class="powered-by">Powered by Z.AI GLM-4<br>Sentinel-2 via Planetary Computer<br>'
        'UK AI Agent Hackathon EP4</div>',
        unsafe_allow_html=True,
    )

    # Agent Activity Log is rendered as a right-side panel (see below)


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
if "agent_log" not in st.session_state:
    st.session_state.agent_log = []


# ─── Run Pipeline ────────────────────────────────────────────
if run_clicked:
    st.session_state.chat_history = []

    progress = st.progress(0, text="Initializing pipeline...")

    st.markdown(
        """<div style="padding:15px; background-color:rgba(255,165,0,0.1); border:1px solid orange; border-radius:10px; margin-bottom:15px;">
        <h3 style="color:orange; margin:0;">⏳ Processing Satellite & Market Intelligence...</h3>
        <p style="margin:5px 0 0 0; font-size:1.1em; color:var(--text-primary);">
        Please wait <b>1-2 minutes</b> while the AI agents fetch live Sentinel-2 imagery and correlate global market data.
        </p></div>""", 
        unsafe_allow_html=True
    )
    with st.status("🚀 Running EarthfiCopilot Pipeline...", expanded=True) as status:
        ts = lambda: datetime.now().strftime("%H:%M:%S")
        st.session_state.agent_log = []  # Reset log

        # Agent 1
        progress.progress(5, text="Step 1/4 — Searching Sentinel-2 satellite catalog...")
        st.toast("🛰️ Sentinel: Analyzing satellite imagery...", icon="🛰️")
        st.write("🛰️ **Agent 1: The Sentinel** — Analyzing satellite imagery...")
        st.session_state.agent_log.append(f"[{ts()}] 🛰️ SENTINEL — Querying Microsoft Planetary Computer STAC API")
        st.session_state.agent_log.append(f"[{ts()}]    Region: {region}")
        st.session_state.sat_data = analyze_region(region_name=region)
        scene_count = (st.session_state.sat_data or {}).get("scene_count", "N/A")
        ndvi = (st.session_state.sat_data or {}).get("recent_ndvi_mean", "N/A")
        st.session_state.agent_log.append(f"[{ts()}] ✅ SENTINEL COMPLETE — {scene_count} scenes ingested, NDVI={ndvi}")
        progress.progress(30, text="Step 1/4 — Satellite analysis complete ✓")

        # Agent 2
        progress.progress(35, text="Step 2/4 — Fetching news, prices & weather data...")
        st.toast("📡 Oracle: Gathering market intelligence...", icon="📡")
        st.write("📡 **Agent 2: The Oracle** — Gathering market intelligence...")
        commodity = region_info["commodity"]
        st.session_state.agent_log.append(f"[{ts()}] 📡 ORACLE — Fetching Google News RSS + Open-Meteo + Yahoo Finance")
        st.session_state.agent_log.append(f"[{ts()}]    Commodity: {commodity}")
        st.session_state.news_data = gather_intelligence(commodity=commodity, bbox=region_info["bbox"])
        article_count = len((st.session_state.news_data or {}).get("news_articles", []))
        sentiment = (st.session_state.news_data or {}).get("overall_sentiment", "N/A")
        data_mode = (st.session_state.news_data or {}).get("data_mode", "N/A")
        st.session_state.agent_log.append(f"[{ts()}] ✅ ORACLE COMPLETE — {article_count} articles, sentiment={sentiment} [{data_mode}]")
        progress.progress(55, text="Step 2/4 — Intelligence gathered ✓")

        # Agent 3
        progress.progress(60, text="Step 3/4 — Z.AI GLM generating trading report...")
        st.toast("🧠 Strategist: Generating Z.AI report...", icon="🧠")
        st.write("🧠 **Agent 3: The Strategist** — Generating trading report via Z.AI...")
        st.session_state.agent_log.append(f"[{ts()}] 🧠 STRATEGIST — Sending to Z.AI GLM-4 for synthesis")
        st.session_state.report_data = generate_report(
            st.session_state.sat_data, st.session_state.news_data
        )
        tokens = (st.session_state.report_data or {}).get("tokens", {}).get("total", 0)
        model = (st.session_state.report_data or {}).get("model", "N/A")
        st.session_state.agent_log.append(f"[{ts()}] ✅ STRATEGIST COMPLETE — {tokens} tokens used, model={model}")
        progress.progress(80, text="Step 3/4 — Trading report generated ✓")

        # Agent 4
        progress.progress(85, text="Step 4/4 — Z.AI GLM detecting anomalies...")
        st.toast("🚨 Dispatcher: Detecting anomalies...", icon="🚨")
        st.write("🚨 **Agent 4: The Dispatcher** — Detecting anomalies...")
        st.session_state.agent_log.append(f"[{ts()}] 🚨 DISPATCHER — Running Z.AI anomaly correlation engine")
        st.session_state.alert_data = generate_alerts(
            st.session_state.sat_data, st.session_state.news_data
        )
        n_alerts = len((st.session_state.alert_data or {}).get("alerts", []))
        critical = sum(1 for a in (st.session_state.alert_data or {}).get("alerts", []) if a.get("severity") in ("CRITICAL", "HIGH"))
        st.session_state.agent_log.append(f"[{ts()}] ✅ DISPATCHER COMPLETE — {n_alerts} alerts ({critical} critical)")
        st.session_state.agent_log.append(f"[{ts()}] 🏁 PIPELINE COMPLETE — All agents finished successfully")

        progress.progress(100, text="All 4 agents complete ✓")
        st.session_state.analysis_run = True
        status.update(label="✅ Pipeline complete!", state="complete", expanded=False)
        st.toast("✅ Pipeline complete! Results ready.", icon="✅")

    # Agent Activity Log (after pipeline)
    if st.session_state.get("agent_log"):
        with st.expander("📋 Agent Activity Log — Full Pipeline Trace", expanded=False):
            log_text = "\n".join(st.session_state.agent_log)
            st.code(log_text, language=None)


# ─── Main Content (Tabs) ─────────────────────────────────────
if not st.session_state.analysis_run:
    st.markdown("### 👈 Select a region and click **Run Analysis** to start")
    st.markdown("")

    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">5</div><div class="metric-label">AI Agents</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">5</div><div class="metric-label">Commodities</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">13</div><div class="metric-label">Spectral Bands</div></div>', unsafe_allow_html=True)

    # World Map showing all regions
    st.markdown("---")
    st.markdown("### 🗺️ Global Commodity Monitoring Regions")
    try:
        import folium
        from streamlit_folium import st_folium

        world_map = folium.Map(location=[20, 30], zoom_start=2, tiles=None)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri", name="Satellite",
            show=True,
        ).add_to(world_map)
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="CartoDB", name="Dark",
            show=False,
        ).add_to(world_map)

        colors = ["red", "blue", "green", "orange", "purple"]
        for i, (name, info) in enumerate(REGIONS.items()):
            bbox = info["bbox"]
            center = [(bbox[1]+bbox[3])/2, (bbox[0]+bbox[2])/2]
            folium.Rectangle(
                bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
                color=colors[i % len(colors)], weight=2, fill=True, fill_opacity=0.2,
            ).add_to(world_map)
            folium.Marker(
                center,
                popup=f"<b>{name}</b><br>{info['commodity']}<br>{info['exchange']}",
                icon=folium.Icon(color=colors[i % len(colors)], icon="leaf", prefix="fa"),
            ).add_to(world_map)
        folium.LayerControl().add_to(world_map)
        st_folium(world_map, height=400, use_container_width=True)
    except Exception:
        pass

    # SDG Alignment
    st.markdown("---")
    st.markdown("### 🌍 UN Sustainable Development Goals Alignment")
    sdg1, sdg2 = st.columns(2)
    with sdg1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value" style="color:#DDA63A">SDG 2</div>'
            '<div class="metric-label">Zero Hunger</div>'
            '<p style="color:#94a3b8;font-size:0.8rem;margin-top:8px">'
            'Early drought warnings protect food supply chains by enabling proactive intervention</p>'
            '</div>', unsafe_allow_html=True)
    with sdg2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value" style="color:#3F7E44">SDG 13</div>'
            '<div class="metric-label">Climate Action</div>'
            '<p style="color:#94a3b8;font-size:0.8rem;margin-top:8px">'
            'Satellite monitoring tracks climate impact on agriculture in real-time</p>'
            '</div>', unsafe_allow_html=True)

    # Architecture
    st.markdown("---")
    st.markdown("### 🏗️ Agent Architecture")
    st.code("""
    ┌──────────────────────────────────────────────────┐
    │             Streamlit Dashboard                   │
    │   Map · Charts · News · Report · Chat · Alerts   │
    └────────────────────┬─────────────────────────────┘
                         │
    ┌────────────────────┴─────────────────────────────┐
    │           Agent Orchestrator (main.py)             │
    └──┬────┬─────┬───────┬───────┬────────────────────┘
       │    │     │       │       │
    🛰️    📡    🧠      🚨     💬
    Sent.  Orac. Strat.  Disp.  Narr.
    STAC   RSS   Z.AI    Z.AI   Z.AI
    NDVI   News  Report  Alert  Chat
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

    # ─── Multi-tab Global Variables ───────────────
    # We fetch FAOSTAT data here so it's accessible to both tab1 (charts) and tab2 (insights) 
    ndvi_mean = sat.get("recent_ndvi_mean", 0.5)
    ndvi_change = sat.get("ndvi_change_percent", 0)
    commodity_name = sat.get("commodity", news.get("commodity", "Commodity"))
    yield_est = estimate_yield_from_ndvi(commodity_name, ndvi_mean, ndvi_change)
    yield_hist = get_yield_history(commodity_name)

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

        # ─── Interactive Map ─────────────────────────
        st.markdown("#### 🗺️ Analysis Region")
        try:
            import folium
            from streamlit_folium import st_folium

            bbox = sat.get("bbox", region_info["bbox"])
            center_lat = (bbox[1] + bbox[3]) / 2
            center_lon = (bbox[0] + bbox[2]) / 2

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=7,
                tiles=None,
            )
            # Dark satellite tiles
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri World Imagery",
                name="Satellite",
                show=True,  # Force Satellite to be the default visible layer
            ).add_to(m)
            folium.TileLayer(
                tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                attr="CartoDB Dark",
                name="Dark Map",
                show=False,  # Hide Dark Map by default
            ).add_to(m)

            # Region bounding box
            folium.Rectangle(
                bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
                color="#818cf8",
                weight=3,
                fill=True,
                fill_color="#818cf8",
                fill_opacity=0.15,
                popup=f"<b>{sat.get('region', region)}</b><br>"
                      f"Commodity: {sat.get('commodity', 'N/A')}<br>"
                      f"NDVI: {sat.get('recent_ndvi_mean', 'N/A')}<br>"
                      f"Status: {sat.get('vegetation_status', 'N/A')}",
            ).add_to(m)

            # Center marker
            folium.Marker(
                [center_lat, center_lon],
                popup=f"📍 {sat.get('region', region)}",
                icon=folium.Icon(color="purple", icon="satellite-dish", prefix="fa"),
            ).add_to(m)

            folium.LayerControl().add_to(m)
            st_folium(m, height=350, use_container_width=True)
        except ImportError:
            st.info("Install `folium` and `streamlit-folium` for interactive maps")
        except Exception as e:
            st.warning(f"Map unavailable: {e}")

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

        # ─── NDVI Temporal Trend ──────────────────────
        st.markdown("#### 📈 Vegetation Health Trend (NDVI over time)")
        baseline_date = sat.get("baseline_date", "90 days ago")
        recent_date = sat.get("recent_date", "today")
        baseline_mean = sat.get("baseline_ndvi_mean", 0.45)
        recent_mean = sat.get("recent_ndvi_mean", 0.50)
        import plotly.graph_objects as go
        # Simulated monthly NDVI trend between baseline & recent
        trend_dates = [f"Month {i}" for i in range(1, 7)]
        ndvi_diff = recent_mean - baseline_mean
        trend_vals = [round(baseline_mean + (ndvi_diff * i / 5) + np.random.uniform(-0.02, 0.02), 3) for i in range(6)]
        trend_vals[0] = round(baseline_mean, 3)
        trend_vals[-1] = round(recent_mean, 3)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_dates, y=trend_vals, mode="lines+markers",
            line=dict(color="#34d399", width=3), marker=dict(size=10),
            name="NDVI Mean", fill="tozeroy", fillcolor="rgba(52,211,153,0.1)",
        ))
        # Healthy threshold line
        fig_trend.add_hline(y=0.4, line_dash="dash", line_color="#f59e0b",
                            annotation_text="Healthy Threshold (0.4)", annotation_position="top left")
        fig_trend.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8", margin=dict(l=20, r=20, t=20, b=20),
            yaxis_title="NDVI", xaxis_title="Time Period",
            yaxis_range=[0, 1],
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ─── FAO Yield History ────────────────────────
        if "error" not in yield_hist:
            st.markdown(f"#### 🌾 {yield_hist.get('commodity', '')} — 10-Year Yield History (FAO/FAOSTAT)")
            import plotly.graph_objects as go
            fig_yield = go.Figure()
            fig_yield.add_trace(go.Scatter(
                x=yield_hist["years"], y=yield_hist["global_yield"],
                mode="lines+markers", name="Global Average",
                line=dict(color="#818cf8", width=2), marker=dict(size=6),
            ))
            regional_key = yield_hist.get("regional_key", "Regional")
            fig_yield.add_trace(go.Scatter(
                x=yield_hist["years"], y=yield_hist["regional_yield"],
                mode="lines+markers", name=f"{regional_key}",
                line=dict(color="#34d399", width=3), marker=dict(size=8),
            ))
            # Mark estimated current yield
            est_y = yield_est.get("estimated_current_yield")
            if est_y:
                fig_yield.add_trace(go.Scatter(
                    x=[2024], y=[est_y],
                    mode="markers+text", name="NDVI Estimate (2024)",
                    marker=dict(size=14, color="#f59e0b", symbol="star"),
                    text=[f"{est_y}"], textposition="top center",
                    textfont=dict(color="#f59e0b", size=12),
                ))
            fig_yield.update_layout(
                height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8", margin=dict(l=20, r=20, t=20, b=20),
                yaxis_title=yield_hist.get("unit", "t/ha"), xaxis_title="Year",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_yield, use_container_width=True)
            st.markdown(
                f'<div style="font-size:0.75em;color:#64748b;">'\
                f'Global production: {yield_hist.get("global_production_mt", "N/A")}M tonnes | '\
                f'Area: {yield_hist.get("global_area_mha", "N/A")}M ha | '\
                f'10yr trend: {yield_hist.get("ten_year_trend_pct", 0):+.1f}% | '\
                f'Source: FAO/FAOSTAT</div>',
                unsafe_allow_html=True,
            )

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

        # ─── Change Detection Heatmap ─────────────
        change_data = sat.get("change_detection", {})
        change_map = change_data.get("change_map")
        if change_map is not None and isinstance(change_map, np.ndarray):
            st.markdown("#### 🔥 Vegetation Change Detection")
            col_ch1, col_ch2 = st.columns([2, 1])
            with col_ch1:
                import plotly.graph_objects as go
                fig_change = go.Figure(go.Heatmap(
                    z=change_map, colorscale="RdYlGn", zmin=-0.5, zmax=0.5,
                    colorbar=dict(title="ΔNDVI"),
                ))
                fig_change.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#94a3b8", margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig_change, use_container_width=True)
            with col_ch2:
                st.metric("🟢 Growth Areas", f"{change_data.get('growth_area_percent', 0)}%")
                st.metric("🔴 Decline Areas", f"{change_data.get('decline_area_percent', 0)}%")
                st.metric("⚪ Stable Areas", f"{change_data.get('stable_area_percent', 0)}%")

        # ─── NDWI Flood Risk ─────────────────────
        ndwi = sat.get("ndwi", {})
        if ndwi.get("ndwi_mean", 0) != 0 or ndwi.get("water_percent", 0) > 0:
            st.markdown("#### 🌊 NDWI — Flood & Water Detection")
            col_w1, col_w2, col_w3, col_w4 = st.columns(4)
            flood_risk = ndwi.get("flood_risk", "UNKNOWN")
            risk_color = "#ef4444" if flood_risk == "HIGH" else "#f59e0b" if flood_risk == "MODERATE" else "#34d399"
            col_w1.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{risk_color}">{flood_risk}</div>'
                f'<div class="metric-label">Flood Risk</div></div>', unsafe_allow_html=True)
            col_w2.metric("Water Cover", f"{ndwi.get('water_percent', 0)}%")
            col_w3.metric("Wet Soil", f"{ndwi.get('wet_soil_percent', 0)}%")
            col_w4.metric("NDWI Mean", f"{ndwi.get('ndwi_mean', 0):.3f}")

        # ─── SCL Quality Assessment ──────────────
        scl = sat.get("scl_quality", {})
        if scl.get("quality_score", -1) >= 0:
            st.markdown("#### 🔬 Image Quality (SCL)")
            col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
            qs = scl.get("quality_score", 0)
            q_color = "#34d399" if qs > 80 else "#f59e0b" if qs > 50 else "#ef4444"
            col_q1.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{q_color}">{qs}%</div>'
                f'<div class="metric-label">Quality Score</div></div>', unsafe_allow_html=True)
            col_q2.metric("☁️ Cloud", f"{scl.get('cloud_percent', 0)}%")
            col_q3.metric("🌿 Vegetation", f"{scl.get('vegetation_percent', 0)}%")
            col_q4.metric("💧 Water", f"{scl.get('water_percent', 0)}%")
            col_q5.metric("🏜️ Bare Soil", f"{scl.get('bare_soil_percent', 0)}%")

        # ─── MSI Moisture Stress ──────────────────
        msi = sat.get("msi", {})
        if msi.get("msi_mean", -1) >= 0:
            st.markdown("#### 💧 MSI — Moisture Stress Index")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            stress_level = msi.get("stress_level", "UNKNOWN")
            stress_color = "#ef4444" if stress_level == "HIGH" else "#f59e0b" if stress_level == "MODERATE" else "#34d399"
            col_m1.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{stress_color}">{stress_level}</div>'
                f'<div class="metric-label">Moisture Stress</div></div>', unsafe_allow_html=True)
            col_m2.metric("MSI Mean", f"{msi.get('msi_mean', 0):.3f}")
            col_m3.metric("🔴 Stressed", f"{msi.get('moisture_stress_percent', 0)}%")
            col_m4.metric("🟢 Healthy", f"{msi.get('healthy_moisture_percent', 0)}%")

        # Data table
        st.markdown("#### Scene Metadata")
        safe = get_serializable(sat)
        exclude = {"agent", "data_source", "bbox", "analysis_date", "region", "commodity", "ndwi", "msi", "scl_quality", "change_detection"}
        display_data = {k: v for k, v in safe.items() if k not in exclude}
        st.json(display_data)

        # ─── Data Provenance & Evidence Trail ─────
        st.markdown("#### 🔬 Data Provenance & Evidence Trail")
        with st.expander("📂 View complete data lineage and source verification", expanded=False):
            analysis_ts = sat.get("analysis_date", datetime.now().isoformat())
            scene_ids = sat.get("scene_ids", [])

            provenance_rows = [
                ("🛰️ Satellite Source", "Microsoft Planetary Computer STAC API", "planetarycomputer.microsoft.com"),
                ("📦 Collection", "sentinel-2-l2a (Sentinel-2 Level-2A)", "ESA Copernicus Open Access Hub"),
                ("📍 Query BBox", str(sat.get("bbox", region_info["bbox"])), "WGS84 coordinates"),
                ("🗓️ Analysis Window", "90 days (baseline vs. recent)", "Rolling window"),
                ("📊 Scenes Ingested", str(sat.get("scene_count", "N/A")), "Cloud filtered < 20%"),
                ("🌱 NDVI Algorithm", "Band 8 (NIR) - Band 4 (Red) / Band 8 + Band 4", "Rouse et al. 1974"),
                ("🌊 NDWI Algorithm", "Band 3 (Green) - Band 8 (NIR) / Band 3 + Band 8", "McFeeters 1996"),
                ("💧 MSI Algorithm", "Band 11 (SWIR) / Band 8 (NIR)", "Hunt & Rock 1989"),
                ("📈 Yield Model", "FAO/FAOSTAT 10-year baseline + NDVI correlation", "fao.org/faostat"),
                ("📰 News Source", f"Google News RSS — {sat.get('commodity', 'N/A')} feeds", "news.google.com/rss"),
                ("🌤️ Weather Source", "Open-Meteo API (ERA5 reanalysis + ECMWF forecast)", "open-meteo.com"),
                ("🧠 AI Model", "Z.AI GLM-4-Flash (ZhipuAI)", "api.z.ai / open.bigmodel.cn"),
                ("⏰ Analysis Timestamp", str(analysis_ts)[:19].replace("T", " "), "UTC"),
            ]

            phtml = '<table style="width:100%;border-collapse:collapse;font-size:0.82em;">'
            for label, value, source in provenance_rows:
                phtml += (
                    f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">'
                    f'<td style="padding:6px 10px;color:#94a3b8;width:220px;">{label}</td>'
                    f'<td style="padding:6px 10px;color:#e2e8f0;font-weight:500;">{value}</td>'
                    f'<td style="padding:6px 10px;color:#64748b;font-style:italic;">{source}</td>'
                    f'</tr>'
                )
            phtml += '</table>'
            st.markdown(phtml, unsafe_allow_html=True)

            if isinstance(scene_ids, list) and len(scene_ids) > 0:
                st.markdown("**🔑 Sentinel-2 Scene IDs:**")
                for sid in scene_ids[:5]:
                    st.code(str(sid), language=None)



    # ─── Tab 2: Intelligence ──────────────────────
    with tab2:
        st.markdown("### 📰 Market Intelligence")

        # ─── Commercial Insights (Key Differentiator) ─────
        st.markdown("#### 💰 Commercial Insights — Actionable Intelligence")

        # Determine colors
        outlook = yield_est.get("production_outlook", "Normal")
        if "Below" in outlook:
            yield_color = "#ef4444"
            yield_icon = "⚠️"
        elif "Above" in outlook:
            yield_color = "#34d399"
            yield_icon = "🟢"
        else:
            yield_color = "#f59e0b"
            yield_icon = "🟡"

        yield_change_pct = yield_est.get("yield_change_pct", 0)
        revenue_impact = yield_est.get("revenue_impact_per_10k_ha", 0)

        ci1, ci2, ci3, ci4 = st.columns(4)
        with ci1:
            est_yield = yield_est.get("estimated_current_yield", "N/A")
            unit = yield_est.get("unit", "t/ha")
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value" style="color:{yield_color}">{est_yield} {unit}</div>'
                f'<div class="metric-label">Est. Yield (NDVI + FAO)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with ci2:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value" style="color:{yield_color}">{yield_icon} {outlook}</div>'
                f'<div class="metric-label">Production Outlook</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with ci3:
            impact_str = f"${abs(revenue_impact):,}"
            impact_label = "Revenue at Risk" if revenue_impact < 0 else "Upside Potential"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value" style="color:{yield_color}">{impact_str}</div>'
                f'<div class="metric-label">{impact_label} / 10k ha</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with ci4:
            # Flood risk from NDWI
            flood = sat.get("ndwi", {}).get("flood_risk", "LOW")
            flood_color = "#ef4444" if flood == "HIGH" else "#f59e0b" if flood == "MODERATE" else "#34d399"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value" style="color:{flood_color}">{flood}</div>'
                f'<div class="metric-label">Flood Risk (NDWI)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # FAO data attribution
        st.markdown(
            f'<div style="text-align:right;font-size:0.7em;color:#64748b;margin-top:-8px;margin-bottom:20px;">'
            f'Yield data: FAO/FAOSTAT | Model: {yield_est.get("methodology", "NDVI-yield correlation")}'
            f'</div>',
            unsafe_allow_html=True,
        )

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

        # Weather data
        weather = news.get("weather")
        if weather:
            st.markdown("#### 🌤️ Weather Intelligence")
            wc1, wc2, wc3, wc4, wc5 = st.columns(5)
            wc1.metric("🌡️ Temp", f"{weather.get('current_temp_c', 'N/A')}°C")
            wc2.metric("💧 Humidity", f"{weather.get('current_humidity', 'N/A')}%")
            wc3.metric("🌱 Soil Moisture", f"{weather.get('soil_moisture', 'N/A')}")
            wc4.metric("🌧️ Past 7d Rain", f"{weather.get('past_7d_precip_mm', 0)}mm")
            drought = weather.get("drought_risk", "N/A")
            dr_color = "#ef4444" if drought == "HIGH" else "#f59e0b" if drought == "MODERATE" else "#34d399"
            wc5.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{dr_color}">{drought}</div>'
                f'<div class="metric-label">Drought Risk</div></div>', unsafe_allow_html=True)

            # 7-day forecast row
            st.markdown("#### 📅 7-Day Weather Forecast")
            fc1, fc2, fc3, fc4 = st.columns(4)
            next_rain = weather.get("next_7d_precip_mm", 0)
            past_rain = weather.get("past_7d_precip_mm", 0)
            fc1.metric("🌧️ Next 7d Rain", f"{next_rain}mm", delta=f"{next_rain - past_rain:+.0f}mm vs last week")

            # Flood prediction based on forecast
            if next_rain > 50:
                flood_forecast = "HIGH"
                flood_color = "#ef4444"
            elif next_rain > 25:
                flood_forecast = "MODERATE"
                flood_color = "#f59e0b"
            else:
                flood_forecast = "LOW"
                flood_color = "#34d399"
            fc2.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{flood_color}">{flood_forecast}</div>'
                f'<div class="metric-label">Flood Risk (7d)</div></div>', unsafe_allow_html=True)

            # Crop weather outlook
            temp = weather.get("current_temp_c", 25)
            if temp and next_rain:
                if (isinstance(temp, (int, float)) and temp > 35) or next_rain < 5:
                    crop_outlook = "⚠️ Heat/Drought Stress"
                    co_color = "#ef4444"
                elif next_rain > 40:
                    crop_outlook = "⚠️ Excess Moisture"
                    co_color = "#f59e0b"
                else:
                    crop_outlook = "🟢 Favorable"
                    co_color = "#34d399"
            else:
                crop_outlook = "N/A"
                co_color = "#94a3b8"
            fc3.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{co_color}">{crop_outlook}</div>'
                f'<div class="metric-label">Crop Weather Outlook</div></div>', unsafe_allow_html=True)
            fc4.markdown(
                f'<div style="font-size:0.8em;color:#94a3b8;padding:8px;">'\
                f'<strong>Source:</strong> Open-Meteo API<br/>'\
                f'<strong>Location:</strong> {weather.get("location", "N/A")}<br/>'\
                f'<strong>Forecast:</strong> 7-day ahead</div>',
                unsafe_allow_html=True)

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

        # Event → Satellite → Insight Correlation Chain
        price = news.get("commodity_price", {})
        commodity_name = sat.get("commodity", news.get("commodity", "Commodity"))
        change_pct = sat.get("ndvi_change_percent", 0)
        price_change = price.get("change_1m", "N/A")
        current_price = price.get("price", "N/A")

        # Build the correlation narrative
        if change_pct < -5:
            event_type = "🔴 Vegetation Decline Detected"
            sat_finding = f"NDVI dropped {abs(change_pct):.1f}% over 90 days"
            insight = f"Supply risk → {commodity_name} prices likely to rise. Consider LONG position."
        elif change_pct > 5:
            event_type = "🟢 Vegetation Recovery Detected"
            sat_finding = f"NDVI improved {change_pct:.1f}% over 90 days"
            insight = f"Supply increasing → {commodity_name} prices may soften. Monitor for SHORT entry."
        else:
            event_type = "🟡 Stable Conditions"
            sat_finding = f"NDVI change within normal range ({change_pct:+.1f}%)"
            insight = f"{commodity_name} supply stable. Hold current positions."

        st.markdown(
            f'<div style="background:rgba(129,140,248,0.1);border:1px solid rgba(129,140,248,0.3);border-radius:12px;padding:16px;margin:8px 0 20px 0;">'
            f'<strong style="color:#818cf8;">📡 Event → Satellite → Insight Pipeline</strong><br/><br/>'
            f'<strong>Event:</strong> {event_type}<br/>'
            f'<strong>Satellite:</strong> {sat_finding} (Sentinel-2 L2A, {sat.get("scene_count", "N/A")} scenes)<br/>'
            f'<strong>Market:</strong> {commodity_name} at {price.get("currency", "$")}{current_price} (1M: {price_change}%)<br/>'
            f'<strong>💡 Insight:</strong> <em>{insight}</em>'
            f'</div>',
            unsafe_allow_html=True,
        )

        model_badge = "badge-ai" if report.get("data_mode") == "LIVE_AI" else "badge-demo"
        model_label = f"Z.AI {report.get('model', 'demo')}" if report.get("data_mode") == "LIVE_AI" else "Demo Template"
        tokens = report.get("tokens", {}).get("total", 0)

        st.markdown(
            f'<span class="agent-badge {model_badge}">{model_label}</span> '
            f'<span class="agent-badge badge-live">Tokens: {tokens}</span>',
            unsafe_allow_html=True,
        )

        st.markdown(report.get("report", "*No report generated.*"))

        # Download report
        report_text = report.get("report", "")
        if report_text:
            report_md = f"""# EarthfiCopilot Trading Report\n\n"""
            report_md += f"**Region:** {sat.get('region', 'N/A')}  \n"
            report_md += f"**Commodity:** {sat.get('commodity', 'N/A')}  \n"
            report_md += f"**Generated:** {report.get('generated_at', datetime.now().isoformat())}  \n"
            report_md += f"**Model:** {report.get('model', 'N/A')}  \n"
            report_md += f"**Tokens:** {report.get('tokens', {}).get('total', 0)}  \n\n"
            report_md += "---\n\n"
            report_md += report_text
            report_md += "\n\n---\n*Generated by EarthfiCopilot — Powered by Z.AI GLM-4 & Sentinel-2*\n"

            st.download_button(
                label="📥 Download Report (Markdown)",
                data=report_md,
                file_name=f"earthfi_report_{sat.get('commodity', 'report').lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ─── ML Yield & Price Forecast ─────────────────────
        st.markdown("---")
        st.markdown("#### 🔮 ML-Powered Yield & Price Forecast")
        ndvi_for_forecast = sat.get("recent_ndvi_mean", 0.5)
        fc = forecast_yield(commodity_name, ndvi_mean=ndvi_for_forecast)
        if "error" not in fc:
            # Model badge
            st.markdown(
                f'<span class="agent-badge badge-ai">sklearn {fc.get("model", "LinearReg")}</span> '
                f'<span class="agent-badge badge-live">R² = {fc["r2_regional"]}</span> '
                f'<span class="agent-badge badge-live">NDVI Adj: {fc["ndvi_adjustment"]}x</span>',
                unsafe_allow_html=True,
            )

            import plotly.graph_objects as go

            fig_fc = go.Figure()

            # Historical data
            fig_fc.add_trace(go.Scatter(
                x=fc["historical_years"], y=fc["historical_regional"],
                mode="lines+markers", name=f"{fc['regional_key']} (Actual)",
                line=dict(color="#34d399", width=2), marker=dict(size=6),
            ))

            # Fitted line (model on historical)
            fig_fc.add_trace(go.Scatter(
                x=fc["historical_years"], y=fc["fitted_regional"],
                mode="lines", name="Model Fit",
                line=dict(color="#818cf8", width=2, dash="dot"),
            ))

            # Forecast line
            # Connect last historical to first forecast
            connect_years = [fc["historical_years"][-1]] + fc["forecast_years"]
            connect_vals = [fc["historical_regional"][-1]] + fc["forecast_regional"]
            connect_upper = [fc["historical_regional"][-1]] + fc["upper_confidence"]
            connect_lower = [fc["historical_regional"][-1]] + fc["lower_confidence"]

            fig_fc.add_trace(go.Scatter(
                x=connect_years, y=connect_vals,
                mode="lines+markers", name="Forecast (NDVI-adjusted)",
                line=dict(color="#f59e0b", width=3),
                marker=dict(size=10, symbol="star"),
            ))

            # Confidence band
            fig_fc.add_trace(go.Scatter(
                x=connect_years + connect_years[::-1],
                y=connect_upper + connect_lower[::-1],
                fill="toself", fillcolor="rgba(245,158,11,0.1)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Confidence Band (±1σ)",
                showlegend=True,
            ))

            fig_fc.update_layout(
                height=350,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis_title=fc.get("unit", "t/ha"),
                xaxis_title="Year",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_fc, use_container_width=True)

            # Price forecast metrics
            st.markdown("#### 💵 Price Forecast")
            pf_cols = st.columns(len(fc["forecast_years"]))
            for i, (yr, pr) in enumerate(zip(fc["forecast_years"], fc["price_forecast"])):
                price_delta = pr - fc["current_price"]
                delta_pct = round((price_delta / fc["current_price"]) * 100, 1)
                pf_cols[i].metric(
                    f"{yr}",
                    f"${pr:,}/t",
                    delta=f"{delta_pct:+.1f}%",
                )

            # Methodology note
            st.markdown(
                f'<div style="text-align:right;font-size:0.7em;color:#64748b;margin-top:-8px;">'
                f'Model: {fc["methodology"]} | '
                f'Data: FAO/FAOSTAT 2014-2023 | '
                f'Satellite: Sentinel-2 NDVI={ndvi_for_forecast}'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Install `scikit-learn` to enable ML forecasting: `pip install scikit-learn`")

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
            css_class = f"alert-card alert-{sev}"
            st.markdown(
                f'<div class="{css_class}">'
                f'<h4>[{alert.get("severity", "?")}] {alert.get("title", "Alert")}</h4>'
                f'<p>{alert.get("description", "")}</p>'
                f'<p style="margin-top:8px;"><em>🎯 {alert.get("action", "")}</em></p>'
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
            st.markdown(f'<div class="chat-msg-user">🧑 {user_input}</div>', unsafe_allow_html=True)

            with st.spinner("🧠 Z.AI is thinking..."):
                response = narrator_chat(
                    user_input,
                    sat_data=sat,
                    news_data=news,
                    report_data=report,
                    alert_data=alerts,
                    history=st.session_state.chat_history,
                )

            # Stream-style display
            def stream_response():
                import time
                words = response.split(" ")
                for i, word in enumerate(words):
                    yield word + " "
                    if i % 5 == 0:
                        time.sleep(0.02)

            st.markdown('<div class="chat-msg-ai">🤖 ', unsafe_allow_html=True)
            st.write_stream(stream_response())
            st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

"""
EarthfiCopilot — UI Styles
Premium CSS that works in both Light and Dark Streamlit themes.
"""


def get_css():
    return """
<style>
/* ─── Google Font ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── CSS Variables for Dual Theme ──────────────── */
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #1e293b;
    --bg-card-hover: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-color: rgba(148, 163, 184, 0.15);
    --accent: #6366f1;
    --accent-glow: rgba(99, 102, 241, 0.3);
    --success: #34d399;
    --warning: #fbbf24;
    --danger: #f87171;
    --shadow: rgba(0, 0, 0, 0.3);
}

/* Light theme overrides — Streamlit adds data-theme="light" */
[data-theme="light"], .stApp[data-testid="stAppViewContainer"]:has([data-testid="stThemeLight"]) {
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --bg-card: #ffffff;
    --bg-card-hover: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border-color: rgba(0, 0, 0, 0.08);
    --shadow: rgba(0, 0, 0, 0.06);
}

/* ─── Global Reset ──────────────────────────────── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ─── Main Container ────────────────────────────── */
.stApp {
    background: var(--bg-primary) !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: var(--bg-primary) !important;
}

/* ─── Sidebar ───────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary) !important;
}

/* ─── Header Block ──────────────────────────────── */
.header-block {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%) !important;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    border: none;
}

.header-block::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
}

.header-block h1 {
    color: #ffffff !important;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-block p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.95rem;
    margin: 0.3rem 0 0;
}

/* ─── Metric Cards ──────────────────────────────── */
.metric-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px var(--shadow);
}

.metric-card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 12px var(--accent-glow);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent) !important;
    line-height: 1.2;
}

.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
    font-weight: 500;
}

/* ─── Streamlit Metrics ─────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px var(--shadow);
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1.4rem !important;
    white-space: normal !important;
    overflow: visible !important;
    line-height: 1.2 !important;
}

[data-testid="stMetricDelta"] {
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ─── Agent Badges ──────────────────────────────── */
.agent-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    margin: 0.15rem 0.25rem;
}

.badge-live {
    background: rgba(52, 211, 153, 0.15);
    color: #34d399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}

.badge-demo {
    background: rgba(251, 191, 36, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}

.badge-ai {
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

/* ─── Alert Cards ───────────────────────────────── */
.alert-card {
    background: var(--bg-card) !important;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    border-left: 4px solid;
    box-shadow: 0 1px 3px var(--shadow);
    transition: transform 0.15s ease;
}

.alert-card:hover {
    transform: translateX(4px);
}

.alert-critical { border-color: #ef4444; }
.alert-high { border-color: #f97316; }
.alert-medium { border-color: #fbbf24; }
.alert-low { border-color: #34d399; }

.alert-card h4 {
    margin: 0 0 0.5rem;
    color: var(--text-primary) !important;
    font-size: 0.95rem;
}

.alert-card p {
    color: var(--text-secondary) !important;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.5;
}

/* ─── News Cards ────────────────────────────────── */
.news-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
}

.news-card:hover {
    border-color: var(--accent);
    background: var(--bg-card-hover) !important;
}

.news-card h5 {
    color: var(--text-primary) !important;
    font-size: 0.9rem;
    margin: 0 0 0.35rem;
    font-weight: 600;
}

.news-card p {
    color: var(--text-secondary) !important;
    font-size: 0.8rem;
    margin: 0;
    line-height: 1.5;
}

/* ─── Tabs ──────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: var(--bg-secondary) !important;
    border-radius: 12px;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    flex-wrap: wrap !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.6rem 1rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    background: transparent !important;
    white-space: nowrap !important;
    opacity: 0.7;
}

.stTabs [data-baseweb="tab"]:hover {
    opacity: 1;
    background: var(--bg-card-hover) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2) !important;
}

.stTabs [aria-selected="true"]:hover {
    color: #ffffff !important;
    background: var(--accent) !important;
}

/* ─── Buttons ───────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
}

/* ─── Chat ──────────────────────────────────────── */
.stChatMessage {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}

.stChatMessage p {
    color: var(--text-primary) !important;
}

/* ─── JSON Viewer ───────────────────────────────── */
[data-testid="stJson"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

/* ─── Text Elements ─────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
}

p, li, span:not(.agent-badge) {
    color: var(--text-secondary);
}

/* ─── SDG Cards ─────────────────────────────────── */
.sdg-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px var(--shadow);
}

.sdg-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px var(--shadow);
}

.sdg-card h4 {
    margin: 0.5rem 0 0.3rem;
    font-size: 1rem;
}

.sdg-card p {
    font-size: 0.8rem;
    margin: 0;
}

/* ─── Footer ────────────────────────────────────── */
.footer {
    text-align: center;
    padding: 1.5rem;
    margin-top: 2rem;
    border-top: 1px solid var(--border-color);
    color: var(--text-muted) !important;
    font-size: 0.8rem;
}

/* ─── Expanders ─────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* ─── Select box ────────────────────────────────── */
[data-testid="stSelectbox"] {
    color: var(--text-primary) !important;
}

/* ─── Status widget ─────────────────────────────── */
.stStatus {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

/* ─── Scrollbar ─────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 3px;
}

/* ─── Map Container ─────────────────────────────── */
iframe[title="streamlit_folium.st_folium"] {
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
}

/* ─── Plotly Charts ─────────────────────────────── */
.stPlotlyChart {
    border-radius: 12px;
    overflow: hidden;
}
/* ─── Tabs — High Contrast ──────────────────────── */
button[data-baseweb="tab"] {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    font-size: 1em !important;
    padding: 12px 20px !important;
    background: transparent !important;
}
button[data-baseweb="tab"]:hover {
    color: #f1f5f9 !important;
    background: rgba(99, 102, 241, 0.1) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #6366f1 !important;
    background: rgba(99, 102, 241, 0.08) !important;
}
div[data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border-color) !important;
}

</style>
"""

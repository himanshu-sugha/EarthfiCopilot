"""
EarthfiCopilot UI — Custom CSS Styles
Premium dark-mode design system for the Streamlit dashboard.
"""


def get_custom_css():
    """Return custom CSS for the Streamlit app."""
    return """
<style>
    /* ─── Global Theme ────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
    }

    /* ─── Header ──────────────────────────────────────── */
    .hero-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    .hero-header h1 {
        background: linear-gradient(90deg, #818cf8, #34d399, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }
    .hero-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 4px 0 0 0;
    }

    /* ─── Metric Cards ────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #818cf8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-delta-up { color: #34d399; }
    .metric-delta-down { color: #f87171; }

    /* ─── Alert Cards ─────────────────────────────────── */
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.05));
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    .alert-high {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.05));
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    .alert-medium {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.05));
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    .alert-low {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.05));
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }

    /* ─── Agent Status Badges ─────────────────────────── */
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px 4px;
    }
    .badge-live { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-demo { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-ai { background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.4); }

    /* ─── News Cards ──────────────────────────────────── */
    .news-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 10px;
        padding: 14px;
        margin: 8px 0;
        transition: border-color 0.2s;
    }
    .news-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
    }
    .news-card h4 {
        color: #e2e8f0;
        margin: 0 0 6px 0;
        font-size: 0.95rem;
    }
    .news-card p {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0;
    }
    .news-source {
        color: #818cf8;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ─── Sidebar ─────────────────────────────────────── */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    }

    /* ─── Tabs ────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }

    /* ─── Chat ────────────────────────────────────────── */
    .chat-msg-user {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    .chat-msg-ai {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
    }

    /* ─── Footer ──────────────────────────────────────── */
    .powered-by {
        text-align: center;
        color: #475569;
        font-size: 0.8rem;
        padding: 20px 0;
        border-top: 1px solid rgba(71, 85, 105, 0.2);
        margin-top: 40px;
    }
</style>
"""

"""
EarthfiCopilot — Configuration
Central configuration for all agents, API keys, and default settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Z.AI (Zhipu) Configuration ──────────────────────────────
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
# Z.AI English platform uses api.z.ai; Chinese platform uses open.bigmodel.cn
# Auto-detect: z.ai keys work on both, but api.z.ai is the official endpoint
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://api.z.ai/api/paas/v4")
ZHIPU_MODELS = {
    "flash": "glm-4-flash",          # Free on some accounts
    "4.7": "glm-4.7",                # Latest generation
    "4.5": "glm-4.5",                # Flagship model
    "plus": "glm-4-plus",            # Premium
}
# Try models in order — first available one wins
ZHIPU_MODEL_PRIORITY = ["glm-4-flash", "glm-4.7", "glm-4.5", "glm-4-plus", "glm-4"]
ZHIPU_DEFAULT_MODEL = "flash"

# ─── Satellite Configuration ─────────────────────────────────
PLANETARY_COMPUTER_API = "https://planetarycomputer.microsoft.com/api/stac/v1"
SENTINEL_COLLECTION = "sentinel-2-l2a"

# ─── Prebuilt Regions ────────────────────────────────────────
REGIONS = {
    "Minas Gerais, Brazil (Coffee)": {
        "bbox": [-46.5, -22.5, -44.5, -20.5],
        "commodity": "Arabica Coffee",
        "exchange": "ICE KC",
    },
    "Punjab, India (Wheat)": {
        "bbox": [73.8, 29.5, 76.8, 31.5],
        "commodity": "Wheat",
        "exchange": "CBOT ZW",
    },
    "Iowa, USA (Corn)": {
        "bbox": [-96.0, 40.5, -90.0, 43.5],
        "commodity": "Corn",
        "exchange": "CBOT ZC",
    },
    "Mato Grosso, Brazil (Soy)": {
        "bbox": [-57.0, -15.0, -53.0, -11.0],
        "commodity": "Soybeans",
        "exchange": "CBOT ZS",
    },
    "Nile Delta, Egypt (Cotton)": {
        "bbox": [30.0, 30.5, 32.0, 31.5],
        "commodity": "Cotton",
        "exchange": "ICE CT",
    },
}

DEFAULT_REGION = "Minas Gerais, Brazil (Coffee)"

# ─── News Sources ────────────────────────────────────────────
def get_news_feeds(commodity: str) -> dict:
    """Generate Google News RSS feeds tailored to the commodity."""
    base = "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q="
    commodity_lower = commodity.lower()
    return {
        f"{commodity} Agriculture": f"{base}{commodity_lower}+agriculture+drought+crop",
        f"{commodity} Markets": f"{base}{commodity_lower}+futures+commodity+price+market",
        f"{commodity} Weather": f"{base}{commodity_lower}+weather+rainfall+drought+harvest",
    }

# ─── APP Settings ────────────────────────────────────────────
APP_NAME = "EarthfiCopilot"
APP_VERSION = "2.0.0"
APP_TAGLINE = "Multi-Agent Commodity Intelligence from Space"

"""Configuration, asset definitions, and style palettes."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Default Assets Configuration
DEFAULT_ASSETS = {
    "Gold": {
        "symbol": "GC=F",
        "alpaca_symbol": None,  # Alpaca does not offer spot gold
        "fallback_symbol": "GLD",
        "color": "#eda100",  # Amber
        "asset_class": "Commodity",
        "periods_per_year": 252,
    },
    "Bitcoin": {
        "symbol": "BTC-USD",
        "alpaca_symbol": "BTC/USD",
        "fallback_symbol": "BTC-USD",
        "color": "#eb6834",  # Orange
        "asset_class": "Crypto",
        "periods_per_year": 365,
    },
    "NVIDIA": {
        "symbol": "NVDA",
        "alpaca_symbol": "NVDA",
        "fallback_symbol": "NVDA",
        "color": "#2a78d6",  # Blue
        "asset_class": "Equity",
        "periods_per_year": 252,
    },
}

# General Default Settings
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_INITIAL_CAPITAL = 100000.0
DEFAULT_TRANSACTION_COST_BPS = 0.0010  # 10 bps (0.10%)
DEFAULT_SLIPPAGE_BPS = 0.0005          # 5 bps (0.05%)
DEFAULT_RISK_FREE_RATE = 0.04          # 4.0% annual

# Cache directory
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID", "")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "")
APCA_PAPER = os.getenv("APCA_PAPER", "True").lower() in ("true", "1", "t")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_MODEL = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-72B-Instruct")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Theme Colors
UI_THEME = {
    "bg_dark": "#0e1117",
    "surface": "#1a1c24",
    "surface_card": "#222530",
    "border": "#2d313e",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a5b5",
    "text_muted": "#6b7280",
    "accent": "#2a78d6",
    "success": "#10b981",
    "danger": "#ef4444",
}

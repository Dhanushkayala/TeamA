"""
Per-user profile persistence for BetaScope.

Stores a JSON file per user at: data/users/{username}.json

Schema:
{
  "username": "demo",
  "display_name": "Demo User",
  "email": "demo@betascope.io",
  "joined": "2024-01-01",
  "total_sessions": 3,
  "assets_analyzed": ["Gold", "Bitcoin", "NVIDIA"],
  "strategies_run": {"SMA Crossover": 2, "Momentum": 1},
  "achievements": ["first_session", "sharpe_hunter"],
  "session_history": [
    {
      "date": "2024-01-01T12:00:00",
      "asset": "Bitcoin",
      "strategy": "SMA Crossover",
      "sharpe": 1.42,
      "total_return_pct": 38.4,
      "max_drawdown_pct": -22.1
    }
  ]
}
"""

import json
import datetime
from pathlib import Path
from typing import Any

# Directory for per-user profiles
_USERS_DIR = Path(__file__).parents[2] / "data" / "users"


def _profile_path(username: str) -> Path:
    return _USERS_DIR / f"{username}.json"


def _ensure_dir() -> None:
    _USERS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Achievement Definitions ──────────────────────────────────────────────────
ACHIEVEMENTS = {
    "first_session": {
        "id": "first_session",
        "title": "First Launch",
        "description": "Completed your first BetaScope session",
        "icon": "🚀",
        "rarity": "common",
    },
    "sharpe_hunter": {
        "id": "sharpe_hunter",
        "title": "Sharpe Hunter",
        "description": "Achieved a Sharpe Ratio above 2.0 in a backtest",
        "icon": "🎯",
        "rarity": "rare",
    },
    "multi_asset": {
        "id": "multi_asset",
        "title": "Diversifier",
        "description": "Analyzed 3 or more assets in a single session",
        "icon": "🌐",
        "rarity": "uncommon",
    },
    "bear_survivor": {
        "id": "bear_survivor",
        "title": "Bear Market Survivor",
        "description": "Ran a strategy with Max Drawdown below −30%",
        "icon": "🐻",
        "rarity": "uncommon",
    },
    "strategy_explorer": {
        "id": "strategy_explorer",
        "title": "Strategy Explorer",
        "description": "Tried all 4 built-in strategy models",
        "icon": "🧭",
        "rarity": "rare",
    },
    "veteran": {
        "id": "veteran",
        "title": "BetaScope Veteran",
        "description": "Completed 10 or more sessions",
        "icon": "🏆",
        "rarity": "epic",
    },
    "momentum_master": {
        "id": "momentum_master",
        "title": "Momentum Master",
        "description": "Achieved 100%+ total return with Momentum strategy",
        "icon": "⚡",
        "rarity": "epic",
    },
}


def load_profile(username: str, display_name: str = "", email: str = "") -> dict:
    """Load a user's profile, creating it if it doesn't exist."""
    _ensure_dir()
    path = _profile_path(username)

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Create fresh profile
    profile = {
        "username": username,
        "display_name": display_name or username.capitalize(),
        "email": email,
        "joined": datetime.datetime.now().isoformat()[:10],
        "total_sessions": 0,
        "assets_analyzed": [],
        "strategies_run": {},
        "achievements": [],
        "session_history": [],
    }
    _save_profile(profile)
    return profile


def _save_profile(profile: dict) -> None:
    """Persist profile to disk."""
    _ensure_dir()
    path = _profile_path(profile["username"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def save_session(
    username: str,
    display_name: str,
    asset: str,
    strategy: str,
    sharpe: float,
    total_return_pct: float,
    max_drawdown_pct: float,
    assets_in_universe: list[str],
) -> dict:
    """
    Record a completed backtest session to the user profile.
    Auto-unlocks achievements. Returns the updated profile.
    """
    profile = load_profile(username, display_name)

    # Update counters
    profile["total_sessions"] += 1

    for a in assets_in_universe:
        if a not in profile["assets_analyzed"]:
            profile["assets_analyzed"].append(a)

    profile["strategies_run"][strategy] = profile["strategies_run"].get(strategy, 0) + 1

    # Append session record (keep last 50)
    session_record = {
        "date": datetime.datetime.now().isoformat(),
        "asset": asset,
        "strategy": strategy,
        "sharpe": round(sharpe, 3),
        "total_return_pct": round(total_return_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
    }
    profile["session_history"].append(session_record)
    if len(profile["session_history"]) > 50:
        profile["session_history"] = profile["session_history"][-50:]

    # ── Achievement checks ───────────────────────────────────────────────────
    def unlock(ach_id: str):
        if ach_id not in profile["achievements"]:
            profile["achievements"].append(ach_id)

    if profile["total_sessions"] >= 1:
        unlock("first_session")
    if sharpe >= 2.0:
        unlock("sharpe_hunter")
    if len(assets_in_universe) >= 3:
        unlock("multi_asset")
    if max_drawdown_pct <= -30.0:
        unlock("bear_survivor")
    if len(profile["strategies_run"]) >= 4:
        unlock("strategy_explorer")
    if profile["total_sessions"] >= 10:
        unlock("veteran")
    if strategy == "Momentum" and total_return_pct >= 100.0:
        unlock("momentum_master")

    _save_profile(profile)
    return profile


def get_recent_sessions(username: str, n: int = 10) -> list[dict]:
    """Return the last n sessions for this user (most recent first)."""
    path = _profile_path(username)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    history = profile.get("session_history", [])
    return list(reversed(history[-n:]))

"""Volume-weighted average price helpers using Kalshi public trade history."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional

import requests

BASE = "https://api.elections.kalshi.com/trade-api/v2"


def recent_vwap(ticker: str, limit: int = 50,
                max_age_hours: float = 6.0) -> Optional[float]:
    """Return volume-weighted average YES price of recent trades, or None.
    Only considers trades within max_age_hours."""
    try:
        r = requests.get(
            f"{BASE}/markets/trades",
            params={"ticker": ticker, "limit": limit},
            headers={"User-Agent": "kalshi-weather-bot/2"},
            timeout=8,
        ).json()
    except requests.RequestException:
        return None
    trades = r.get("trades", [])
    if not trades:
        return None
    cutoff = time.time() - max_age_hours * 3600
    num = 0.0
    den = 0.0
    for t in trades:
        cts = t.get("created_time", "")
        try:
            dt = datetime.fromisoformat(cts.rstrip("Z").split(".")[0] + "+00:00")
        except Exception:
            continue
        if dt.timestamp() < cutoff:
            continue
        try:
            p = float(t.get("yes_price_dollars") or 0)
            c = float(t.get("count_fp") or 0)
        except (TypeError, ValueError):
            continue
        if c <= 0 or p <= 0:
            continue
        num += p * c
        den += c
    if den == 0:
        return None
    return num / den

"""Read recent settled trade results, return adjusted risk parameters.

If recent win rate < target, raise min_edge + shrink kelly_fraction.
If recent win rate > target, mildly relax.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = DATA / "settlement_results.csv"

DEFAULT_MIN_EDGE = 0.04
DEFAULT_KELLY = 0.50
LOOKBACK_TRADES = 30
TARGET_WIN_RATE = 0.40   # below this, tighten


def adaptive_params(base_min_edge: float = DEFAULT_MIN_EDGE,
                    base_kelly: float = DEFAULT_KELLY) -> tuple[float, float, str]:
    """Returns (min_edge, kelly_fraction, reason)."""
    if not RESULTS.exists():
        return base_min_edge, base_kelly, "no settled trades yet"
    rows = list(csv.DictReader(RESULTS.open()))
    if len(rows) < 10:
        return base_min_edge, base_kelly, f"only {len(rows)} settled, no adjust"
    recent = rows[-LOOKBACK_TRADES:]
    wins = sum(1 for r in recent if float(r["pnl_dollars"]) > 0)
    wr = wins / len(recent)
    if wr < TARGET_WIN_RATE - 0.10:
        return base_min_edge * 1.5, base_kelly * 0.5, \
               f"wr {wr:.2f} below target; tightened"
    if wr < TARGET_WIN_RATE:
        return base_min_edge * 1.2, base_kelly * 0.75, \
               f"wr {wr:.2f} slightly below target"
    if wr > TARGET_WIN_RATE + 0.20:
        return base_min_edge * 0.9, base_kelly * 1.1, \
               f"wr {wr:.2f} strong"
    return base_min_edge, base_kelly, f"wr {wr:.2f} in target range"


def drawdown_brake() -> float:
    """If we are in drawdown >20% from peak, return a kelly multiplier < 1."""
    if not RESULTS.exists():
        return 1.0
    rows = list(csv.DictReader(RESULTS.open()))
    if len(rows) < 5:
        return 1.0
    cum = 0.0; peak = 0.0
    for r in rows:
        cum += float(r["pnl_dollars"])
        peak = max(peak, cum)
    drawdown = peak - cum
    if peak <= 0 or drawdown <= 0:
        return 1.0
    pct = drawdown / max(peak, 10)
    if pct > 0.40:
        return 0.25  # severe brake
    if pct > 0.25:
        return 0.50
    if pct > 0.15:
        return 0.75
    return 1.0


def per_city_kelly_mult(city: str) -> float:
    """Look at this city's settled history and return a kelly multiplier.
    Strong wr -> >1.0, weak wr -> <1.0. Defaults to 1.0 with insufficient data."""
    if not RESULTS.exists():
        return 1.0
    rows = list(csv.DictReader(RESULTS.open()))
    rows = [r for r in rows
            if r.get("ticker", "").startswith(f"KXHIGH{city}-")]
    if len(rows) < 8:
        return 1.0
    recent = rows[-20:]
    wins = sum(1 for r in recent if float(r["pnl_dollars"]) > 0)
    wr = wins / len(recent)
    if wr > 0.55:
        return 1.25
    if wr > 0.45:
        return 1.0
    if wr > 0.30:
        return 0.75
    return 0.5

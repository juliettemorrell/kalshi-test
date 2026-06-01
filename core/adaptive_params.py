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
        # tighten aggressively
        return base_min_edge * 1.5, base_kelly * 0.5, \
               f"wr {wr:.2f} below target; tightened"
    if wr < TARGET_WIN_RATE:
        return base_min_edge * 1.2, base_kelly * 0.75, \
               f"wr {wr:.2f} slightly below target"
    if wr > TARGET_WIN_RATE + 0.20:
        # very good; allow slight loosening
        return base_min_edge * 0.9, base_kelly * 1.1, \
               f"wr {wr:.2f} strong"
    return base_min_edge, base_kelly, f"wr {wr:.2f} in target range"

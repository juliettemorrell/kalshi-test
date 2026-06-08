"""Auto-create KILLSWITCH file if balance drops too fast.

Reads data/balance_history.csv. If most recent total_worth is >30% below
yesterday's, write KILLSWITCH locally so subsequent runs exit immediately.
This is the "I cannot watch this anymore" fail-safe.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HIST = DATA / "balance_history.csv"
KILL = ROOT / "KILLSWITCH"

FIELDS = ["snapshot_utc", "cash", "portfolio", "total"]


def record(cash: float, portfolio: float):
    """Append a snapshot row + return whether the circuit breaker fired."""
    DATA.mkdir(exist_ok=True)
    total = cash + portfolio
    new = not HIST.exists()
    with HIST.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({
            "snapshot_utc": datetime.now(timezone.utc).isoformat(),
            "cash": round(cash, 2),
            "portfolio": round(portfolio, 2),
            "total": round(total, 2),
        })

    # Check 24h-back row vs now
    if KILL.exists():
        return True
    rows = list(csv.DictReader(HIST.open()))
    if len(rows) < 2:
        return False
    # Look back ~24h: find first row whose snapshot is >20h before latest
    latest_ts = datetime.fromisoformat(rows[-1]["snapshot_utc"])
    benchmark = None
    for r in rows[:-1]:
        try:
            dt = datetime.fromisoformat(r["snapshot_utc"])
        except Exception:
            continue
        gap_h = (latest_ts - dt).total_seconds() / 3600
        if gap_h >= 20 and gap_h <= 30:
            benchmark = float(r["total"])
            break
    if benchmark is None or benchmark <= 0:
        return False
    drop_pct = (benchmark - total) / benchmark
    if drop_pct > 0.30:
        KILL.write_text(
            f"Auto-tripped by circuit breaker on {datetime.now(timezone.utc).isoformat()}\n"
            f"Total dropped from ${benchmark:.2f} to ${total:.2f} "
            f"({drop_pct*100:.1f}%) in ~24h.\n"
            f"Remove this file to resume trading.\n"
        )
        print(f"CIRCUIT BREAKER TRIPPED: -{drop_pct*100:.1f}% in 24h")
        return True
    return False

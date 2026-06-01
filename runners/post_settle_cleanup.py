"""After settlement, cancel any resting orders for past settle dates.

Settlement happens around 12-14 UTC. By 15 UTC any remaining unfilled
orders for that settle date are dead weight - they'll either expire or
tie up capital that should be free for tomorrow's bets."""
from __future__ import annotations

import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.client import KalshiClient
from core import risk

MONTHS = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
          "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}


def settle_date_of(ticker: str):
    m = re.match(r"^[A-Z]+-(\d{2})([A-Z]{3})(\d{2})-", ticker)
    if not m: return None
    try:
        return datetime(2000 + int(m.group(1)), MONTHS[m.group(2)],
                        int(m.group(3))).date()
    except Exception:
        return None


def main():
    if os.getenv("KALSHI_ENV") != "prod":
        print("not prod"); sys.exit(2)
    if risk.kill_switch_active():
        print("kill switch"); sys.exit(0)
    client = KalshiClient()
    orders = client.get_orders(status="resting")
    today = datetime.now(timezone.utc).date()
    canceled = 0
    for o in orders:
        tic = o.get("ticker", "")
        sd = settle_date_of(tic)
        if not sd:
            continue
        if sd < today:
            try:
                client.cancel_order(o["order_id"])
                canceled += 1
                print(f"  canceled past-settle {tic}")
            except Exception as e:
                print(f"  cancel fail {tic}: {e}")
    print(f"post-settle cleanup: canceled {canceled}")


if __name__ == "__main__":
    main()

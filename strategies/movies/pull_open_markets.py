"""Pull near-term open Kalshi markets across categories for the daily
Claude research task. Writes data/open_markets_today.csv."""
from __future__ import annotations

import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
OUT = DATA / "open_markets_today.csv"

BASE = "https://api.elections.kalshi.com/trade-api/v2"
UA = "research/1.0"

FIELDS = ["category", "series_ticker", "event_ticker", "event_title",
          "market_ticker", "sub_title", "yes_bid", "yes_ask",
          "last_price", "volume", "open_interest", "close_time",
          "days_until_close"]

CATEGORIES = ["Entertainment", "Sports", "Financials", "Economics",
              "Politics", "Elections", "Science and Technology",
              "Companies", "Social", "World", "Health"]

MAX_DAYS = 14


def get(url, params=None):
    for _ in range(3):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return {}


def days_until(close_iso):
    if not close_iso:
        return None
    try:
        ct = datetime.fromisoformat(close_iso.replace("Z", "+00:00"))
        return round((ct - datetime.now(timezone.utc)).total_seconds() / 86400, 1)
    except Exception:
        return None


def main():
    # phase 1: collect near-term event_tickers across categories
    keep_events = {}  # event_ticker -> ev dict
    for cat in CATEGORIES:
        cursor = None
        for _ in range(3):
            params = {"status": "open", "limit": 100, "category": cat}
            if cursor:
                params["cursor"] = cursor
            d = get(f"{BASE}/events", params)
            evs = d.get("events", [])
            if not evs:
                break
            for ev in evs:
                ev_t = ev.get("event_ticker")
                if not ev_t or ev_t in keep_events:
                    continue
                close = ev.get("close_time") or ev.get("strike_date")
                dc = days_until(close)
                if dc is None or dc > MAX_DAYS or dc < -0.5:
                    continue
                ev["_close"] = close
                ev["_d"] = dc
                keep_events[ev_t] = ev
            cursor = d.get("cursor")
            if not cursor:
                break

    print(f"near-term events kept: {len(keep_events)}")

    # phase 2: pull markets for each kept event
    rows = []
    for ev_t, ev in keep_events.items():
        md = get(f"{BASE}/markets", {"event_ticker": ev_t, "limit": 50})
        for m in md.get("markets", []):
            rows.append({
                "category": ev.get("category", ""),
                "series_ticker": ev.get("series_ticker", ""),
                "event_ticker": ev_t,
                "event_title": ev.get("title", ""),
                "market_ticker": m.get("ticker", ""),
                "sub_title": m.get("yes_sub_title", ""),
                "yes_bid": m.get("yes_bid_dollars"),
                "yes_ask": m.get("yes_ask_dollars"),
                "last_price": m.get("last_price_dollars"),
                "volume": m.get("volume_fp"),
                "open_interest": m.get("open_interest_fp"),
                "close_time": ev["_close"],
                "days_until_close": ev["_d"],
            })
        time.sleep(0.05)

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} markets -> {OUT}")

    from collections import Counter
    cats = Counter(r["category"] for r in rows)
    print("by category:")
    for c, n in cats.most_common():
        print(f"  {n}: {c}")


if __name__ == "__main__":
    main()

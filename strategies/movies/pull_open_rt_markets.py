"""Pull all currently OPEN Rotten Tomatoes-style Kalshi markets.

Scans the Entertainment category, filters to series whose ticker starts
with KXRT, RT, or KXMC (Metacritic), and returns one row per market
with current bid/ask, current implied probability, and the implied
score bucket (e.g. "80%+ RT", "60-69%", etc).

Output: writes data/open_movie_markets.csv that the scheduled Claude
research task reads and pairs with social signals.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
OUT = DATA / "open_movie_markets.csv"

BASE = "https://api.elections.kalshi.com/trade-api/v2"
UA = "research/1.0"

FIELDS = ["series_ticker", "event_ticker", "movie_title", "market_ticker",
          "sub_title", "yes_bid", "yes_ask", "last_price", "volume",
          "open_interest", "close_time"]


def get(url, params=None):
    for _ in range(3):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=10)
            if r.status_code == 200:
                return r.json()
            time.sleep(0.5)
        except requests.RequestException:
            time.sleep(0.5)
    return {}


def title_from_series(series_ticker: str) -> str:
    """KXRTAVATARFIREANDASH -> 'Avatar Fire And Ash'."""
    stem = re.sub(r"^(KX)?(RT|MC)", "", series_ticker)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    s = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", s)
    return s.strip().title() or series_ticker


def is_movie_series(ticker: str) -> bool:
    t = ticker.upper()
    return (t.startswith("KXRT") or t.startswith("RT") or t.startswith("KXMC"))


def main():
    rows = []
    cursor = None
    pages = 0
    while True:
        params = {"status": "open", "limit": 200,
                  "category": "Entertainment"}
        if cursor:
            params["cursor"] = cursor
        d = get(f"{BASE}/events", params)
        evs = d.get("events", [])
        if not evs:
            break
        for ev in evs:
            st = ev.get("series_ticker", "")
            if not is_movie_series(st):
                continue
            ev_ticker = ev.get("event_ticker")
            if not ev_ticker:
                continue
            md = get(f"{BASE}/markets",
                     {"event_ticker": ev_ticker, "limit": 50})
            for m in md.get("markets", []):
                rows.append({
                    "series_ticker": st,
                    "event_ticker": ev_ticker,
                    "movie_title": title_from_series(st),
                    "market_ticker": m.get("ticker", ""),
                    "sub_title": m.get("yes_sub_title", ""),
                    "yes_bid": m.get("yes_bid_dollars"),
                    "yes_ask": m.get("yes_ask_dollars"),
                    "last_price": m.get("last_price_dollars"),
                    "volume": m.get("volume_fp"),
                    "open_interest": m.get("open_interest_fp"),
                    "close_time": m.get("close_time"),
                })
            time.sleep(0.1)
        cursor = d.get("cursor")
        pages += 1
        if not cursor or pages > 10:
            break

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} open movie/RT markets -> {OUT}")
    if rows:
        movies = sorted({r["movie_title"] for r in rows})
        print(f"unique movies covered: {len(movies)}")
        for m in movies[:20]:
            print(f"  {m}")


if __name__ == "__main__":
    main()

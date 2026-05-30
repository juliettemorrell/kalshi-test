"""Pull a sample of historical Kalshi KXHIGH events with checkpointed writes.

Writes incrementally to data/kalshi_markets.csv so we never lose progress.
Runs only N events per city per invocation (configurable). Re-invocation
resumes by skipping events already in the CSV.
"""
from __future__ import annotations

import csv
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "kalshi_markets.csv"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

BASE = "https://api.elections.kalshi.com/trade-api/v2"
DAYS_BACK = 35      # Kalshi purges market detail for older settled events
SAMPLE_EVERY = 1    # take every day
MAX_TRADE_PAGES = 2

S = requests.Session()

FIELDS = ["city", "settle_date", "event_ticker", "market_ticker",
          "lower", "upper", "side", "open_yes", "open_ts",
          "close_yes", "close_ts", "result"]


def get_json(url, params=None):
    for attempt in range(3):
        try:
            r = S.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 503, 502):
                time.sleep(0.5 + attempt)
                continue
            return {}
        except requests.RequestException:
            time.sleep(0.3)
    return {}


def load_done_events() -> set[str]:
    if not OUT.exists():
        return set()
    seen = set()
    with OUT.open() as f:
        for row in csv.DictReader(f):
            seen.add(row["event_ticker"])
    return seen


_MONTHS = {m: i for i, m in enumerate(
    ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"], 1)}


def settle_date_of(ev: dict):
    """Derive settle date from strike_date if present, else from ticker (YYMMMDD)."""
    sd = ev.get("strike_date")
    if sd:
        try:
            return datetime.fromisoformat(sd.replace("Z", "+00:00")) \
                .astimezone(timezone.utc).date()
        except Exception:
            pass
    m = re.match(r".*-(\d{2})([A-Z]{3})(\d{2})$", ev.get("event_ticker", ""))
    if not m:
        return None
    yy, mon, dd = m.group(1), m.group(2), m.group(3)
    if mon not in _MONTHS:
        return None
    try:
        return datetime(2000 + int(yy), _MONTHS[mon], int(dd)).date()
    except Exception:
        return None


def list_events(series: str) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK + 2)).date()
    cursor, out = None, []
    while True:
        params = {"series_ticker": series, "limit": 200, "status": "settled"}
        if cursor:
            params["cursor"] = cursor
        d = get_json(f"{BASE}/events", params)
        evs = d.get("events", [])
        if not evs:
            break
        for ev in evs:
            sd = settle_date_of(ev)
            if not sd:
                continue
            if sd < cutoff:
                return out
            ev["_settle_date"] = sd
            out.append(ev)
        cursor = d.get("cursor")
        if not cursor:
            break
    return out


def parse_market(m):
    t = m["ticker"]
    if "-B" in t:
        try:
            b = float(t.rsplit("-B", 1)[1])
            return (b, b + 1.0, "bracket")
        except ValueError:
            return None
    if "-T" in t:
        sub = (m.get("yes_sub_title") or "").lower()
        try:
            b = float(t.rsplit("-T", 1)[1])
        except ValueError:
            return None
        if "or above" in sub:
            return (b, 200.0, "tail_hi")
        if "or below" in sub:
            return (-100.0, b, "tail_lo")
    return None


def fetch_trades(ticker):
    cursor, latest, earliest = None, None, None
    for i in range(MAX_TRADE_PAGES):
        params = {"ticker": ticker, "limit": 500}
        if cursor:
            params["cursor"] = cursor
        d = get_json(f"{BASE}/markets/trades", params)
        ts = d.get("trades", [])
        if not ts:
            break
        if i == 0:
            latest = ts[0]
        earliest = ts[-1]
        cursor = d.get("cursor")
        if not cursor:
            break
    return earliest, latest


def main():
    events_per_city = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    done = load_done_events()
    print(f"resuming, {len(done)} events already collected", flush=True)

    new_file = not OUT.exists()
    f = OUT.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        w.writeheader()

    deadline = time.time() + 38  # leave 7s buffer under 45s shell limit
    for code, city in CFG["cities"].items():
        if time.time() > deadline:
            break
        series = city["kalshi_series"]
        print(f"== {code} ({series}) ==", flush=True)
        events = sorted(list_events(series), key=lambda e: e["_settle_date"])
        events = [e for e in events[::SAMPLE_EVERY] if e["event_ticker"] not in done]
        events = events[:events_per_city]
        print(f"  {len(events)} new events", flush=True)
        for ev in events:
            if time.time() > deadline:
                print("  deadline hit", flush=True); break
            ev_ticker = ev["event_ticker"]
            settle_date = ev["_settle_date"]
            md = get_json(f"{BASE}/markets", {"event_ticker": ev_ticker, "limit": 50})
            ev_rows = []
            for m in md.get("markets", []):
                parsed = parse_market(m)
                if not parsed:
                    continue
                lo, hi, side = parsed
                earliest, latest = fetch_trades(m["ticker"])
                if not earliest or not latest:
                    continue
                ev_rows.append(dict(
                    city=code, settle_date=settle_date.isoformat(),
                    event_ticker=ev_ticker, market_ticker=m["ticker"],
                    lower=lo, upper=hi, side=side,
                    open_yes=float(earliest["yes_price_dollars"]),
                    open_ts=earliest["created_time"],
                    close_yes=float(latest["yes_price_dollars"]),
                    close_ts=latest["created_time"],
                    result=m.get("result"),
                ))
            for row in ev_rows:
                w.writerow(row)
            f.flush()
            print(f"  + {ev_ticker}: {len(ev_rows)} markets", flush=True)
    f.close()
    print("done", flush=True)


if __name__ == "__main__":
    main()

"""Phase 0 logger - run daily at a consistent time to capture:
  - Day-ahead Kalshi prices for tomorrow's KXHIGH markets
  - Current GFS forecast for tomorrow
  - (Next day) the realized high

Writes append-only to data/phase0_log.csv. Re-running on the same day is
idempotent (one row per market per snapshot date).
"""
from __future__ import annotations

import csv
import time
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LOG = DATA / "phase0_log.csv"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

BASE = "https://api.elections.kalshi.com/trade-api/v2"
S = requests.Session()

FIELDS = ["snapshot_utc", "snapshot_date_local", "city",
          "settle_date", "market_ticker", "lower", "upper", "side",
          "yes_bid", "yes_ask", "no_bid", "no_ask", "last_price",
          "volume", "open_interest", "forecast_high",
          "ensemble_spread", "n_sources"]


def get_json(url, params=None):
    for _ in range(3):
        try:
            r = S.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
            time.sleep(0.5)
        except requests.RequestException:
            time.sleep(0.5)
    return {}


def get_forecast(lat: float, lon: float, target_date: str) -> float | None:
    """Get current GFS forecast for the given local date."""
    d = get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat, "longitude": lon,
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
            "models": "gfs_seamless",
            "start_date": target_date, "end_date": target_date,
        },
    )
    try:
        return d["daily"]["temperature_2m_max"][0]
    except (KeyError, IndexError, TypeError):
        return None


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


def existing_rows_today(today: str) -> set[tuple[str, str]]:
    if not LOG.exists():
        return set()
    out = set()
    with LOG.open() as f:
        for row in csv.DictReader(f):
            if row.get("snapshot_date_local") == today:
                out.add((row["city"], row["market_ticker"]))
    return out


def main() -> None:
    now = datetime.now(timezone.utc)
    today_local = (now - timedelta(hours=4)).date()  # ET-ish
    tomorrow_local = today_local + timedelta(days=1)
    seen = existing_rows_today(today_local.isoformat())

    new_file = not LOG.exists()
    f = LOG.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        w.writeheader()

    n_total = 0
    for code, city in CFG["cities"].items():
        series = city["kalshi_series"]
        # tomorrow's event ticker format: SERIES-YYMMMDD
        mon = tomorrow_local.strftime("%b").upper()
        ev_ticker = f"{series}-{tomorrow_local:%y}{mon}{tomorrow_local:%d}"
        print(f"{code}: pulling {ev_ticker}", flush=True)
        md = get_json(f"{BASE}/markets", {"event_ticker": ev_ticker, "limit": 50})
        markets = md.get("markets", [])
        if not markets:
            print(f"  no markets returned (event may not be open yet)")
            continue
        # full ensemble snapshot at logger time
        try:
            from core.forecast_sources import ensemble_forecast
            fcst, e_spread, sources = ensemble_forecast(
                city["lat"], city["lon"], tomorrow_local.isoformat())
            n_sources = len(sources)
        except Exception:
            fcst = get_forecast(city["lat"], city["lon"],
                                tomorrow_local.isoformat())
            e_spread = 0.0
            n_sources = 1
        for m in markets:
            parsed = parse_market(m)
            if not parsed:
                continue
            lo, hi, side = parsed
            if (code, m["ticker"]) in seen:
                continue
            row = dict(
                snapshot_utc=now.isoformat(),
                snapshot_date_local=today_local.isoformat(),
                city=code,
                settle_date=tomorrow_local.isoformat(),
                market_ticker=m["ticker"],
                lower=lo, upper=hi, side=side,
                yes_bid=m.get("yes_bid_dollars"),
                yes_ask=m.get("yes_ask_dollars"),
                no_bid=m.get("no_bid_dollars"),
                no_ask=m.get("no_ask_dollars"),
                last_price=m.get("last_price_dollars"),
                volume=m.get("volume_fp"),
                open_interest=m.get("open_interest_fp"),
                forecast_high=fcst,
                ensemble_spread=round(e_spread, 2) if e_spread else 0,
                n_sources=n_sources,
            )
            w.writerow(row)
            n_total += 1
        f.flush()
        time.sleep(0.2)
    f.close()
    print(f"\nlogged {n_total} new market snapshots -> {LOG}", flush=True)


if __name__ == "__main__":
    main()

"""Paper trading loop on Kalshi DEMO.

Runs daily. For each city:
  1. Pull tomorrow's KXHIGH event's markets
  2. Pull current GFS forecast
  3. Generate trade signals via strategies.weather.edge
  4. Pass each signal through risk.gate(); if allowed, place a maker order
     on demo via client.place_order with a deterministic client_order_id
     so reruns the same day don't double-place
  5. Log every signal + decision + order result

Environment (set as GitHub Secrets when running in Actions):
  KALSHI_ENV=demo
  KALSHI_API_KEY_ID=<your demo key id>
  KALSHI_PRIVATE_KEY_PATH=<path to demo .pem>
"""
from __future__ import annotations

import csv
import hashlib
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.client import KalshiClient
from core import risk
from strategies.weather import edge as edge_mod

DATA = ROOT / "data"
LOG = DATA / "paper_orders.csv"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

FIELDS = ["run_utc", "city", "settle_date", "market_ticker", "side",
          "limit_price_cents", "count", "p_model", "p_market", "edge",
          "decision", "order_id", "client_order_id", "error"]


def forecast_for(lat: float, lon: float, when: str) -> float | None:
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": "temperature_2m_max",
                "temperature_unit": "fahrenheit",
                "timezone": "America/New_York",
                "models": "gfs_seamless",
                "start_date": when, "end_date": when,
            }, timeout=10,
        ).json()
        return r["daily"]["temperature_2m_max"][0]
    except Exception:
        return None


def main() -> None:
    if os.getenv("KALSHI_ENV", "demo") != "demo":
        print("paper.py refuses to run with KALSHI_ENV != demo", file=sys.stderr)
        sys.exit(2)
    if risk.kill_switch_active():
        print("kill switch active; exiting"); sys.exit(0)

    client = KalshiClient()
    state = risk.refresh_from_portfolio(client)
    print(f"demo balance: ${state.bankroll_dollars:.2f}, "
          f"open exposure: ${state.open_exposure_dollars:.2f}")

    buckets = edge_mod.load_buckets()
    now = datetime.now(timezone.utc)
    tomorrow_local = (now - timedelta(hours=4)).date() + timedelta(days=1)
    target = tomorrow_local.isoformat()

    new_file = not LOG.exists()
    f = LOG.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        w.writeheader()

    for code, city in CFG["cities"].items():
        series = city["kalshi_series"]
        mon = tomorrow_local.strftime("%b").upper()
        ev_ticker = f"{series}-{tomorrow_local:%y}{mon}{tomorrow_local:%d}"
        try:
            markets = client.list_markets(ev_ticker)
        except Exception as e:
            print(f"{code}: list_markets error: {e}"); continue
        if not markets:
            print(f"{code}: no markets for {ev_ticker}"); continue

        fcst = forecast_for(city["lat"], city["lon"], target)
        if fcst is None:
            print(f"{code}: no forecast"); continue

        signals = edge_mod.signals_for_event(
            markets, fcst, code, target, buckets)
        print(f"{code}: forecast={fcst:.1f}F, {len(signals)} signals")

        for sig in signals:
            entry_price = sig.limit_price_cents / 100
            decision = risk.gate(state, entry_price, sig.edge)
            row = {
                "run_utc": now.isoformat(), "city": code,
                "settle_date": target, "market_ticker": sig.market_ticker,
                "side": sig.side, "limit_price_cents": sig.limit_price_cents,
                "count": decision.max_contracts,
                "p_model": sig.p_model, "p_market": sig.p_market,
                "edge": sig.edge, "decision": decision.reason,
                "order_id": "", "client_order_id": "", "error": "",
            }
            if not decision.allowed:
                w.writerow(row); continue

            # deterministic client_order_id: same signal same day -> same id
            seed = f"{sig.market_ticker}|{sig.side}|{sig.limit_price_cents}|{target}"
            coid = hashlib.sha1(seed.encode()).hexdigest()[:24]
            row["client_order_id"] = coid

            try:
                kw = dict(
                    ticker=sig.market_ticker, side=sig.side, action="buy",
                    count=decision.max_contracts,
                    client_order_id=coid,
                )
                if sig.side == "yes":
                    kw["yes_price_cents"] = sig.limit_price_cents
                else:
                    kw["no_price_cents"] = sig.limit_price_cents
                resp = client.place_order(**kw)
                row["order_id"] = resp.get("order", {}).get("order_id", "")
                # bookkeeping
                state.open_exposure_dollars += entry_price * decision.max_contracts
            except Exception as e:
                row["error"] = str(e)[:200]
            w.writerow(row); f.flush()

    f.close()
    print(f"paper run complete -> {LOG}")


if __name__ == "__main__":
    main()

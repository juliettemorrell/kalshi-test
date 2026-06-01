"""Midday refresh: cut losers, take profits, place new signals.

Runs at 14:00 UTC (10am ET) - HRRR has fired, morning observations are
in, weather pattern for the day is much clearer.

For each currently OPEN position on a today-settling KXHIGH market:
  1. Pull current orderbook + fresh GFS+ECMWF ensemble forecast
  2. Recompute model probability with updated forecast
  3. STOP-LOSS: if model_prob < 10% AND current mid < entry - 25c, sell
  4. TAKE-PROFIT: if model_prob > 85% AND current mid > 80c, sell to lock
  5. After exits, search for NEW signals on today's markets and place them

This is where post-overnight P&L gets reshaped: bad bets get cut so
their capital can fund newly-correct bets identified after sunrise.
"""
from __future__ import annotations

import csv
import hashlib
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.client import KalshiClient
from core import risk
from strategies.weather import edge as edge_mod

DATA = ROOT / "data"
LOG = DATA / "midday_actions.csv"
PROMOTED = ROOT / "PROMOTED"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

from core.forecast_sources import ensemble_forecast
from core.observations import current_obs, today_max_so_far

FIELDS = ["run_utc", "city", "settle_date", "market_ticker",
          "action", "side", "limit_price_cents", "count",
          "p_model_now", "p_market_mid", "reason",
          "order_id", "client_order_id", "error"]


def forecast_now(lat, lon, when):
    mean, spread, _ = ensemble_forecast(lat, lon, when)
    return mean, spread


def parse_ticker_bracket(ticker):
    """Get (lo, hi, side) from a KXHIGH market ticker."""
    return edge_mod.parse_market_range(ticker, None)


def settle_date_of_ticker(ticker):
    """Extract settle date YYYY-MM-DD from a KXHIGH-26JUN02-... ticker."""
    import re
    m = re.match(r"^[A-Z]+-(\d{2})([A-Z]{3})(\d{2})-", ticker)
    if not m:
        return None
    months = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
              "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}
    yy, mon, dd = m.group(1), m.group(2), m.group(3)
    if mon not in months:
        return None
    try:
        return datetime(2000+int(yy), months[mon], int(dd)).date()
    except Exception:
        return None


def city_from_ticker(ticker):
    """KXHIGHNY-... -> 'NY' if it matches one of our configured cities."""
    for code in CFG["cities"]:
        if ticker.startswith(f"KXHIGH{code}-"):
            return code
    return None


def main():
    if not PROMOTED.exists():
        print("PROMOTED missing; refusing midday", file=sys.stderr); sys.exit(2)
    if os.getenv("KALSHI_ENV") != "prod":
        print("KALSHI_ENV != prod", file=sys.stderr); sys.exit(2)
    if risk.kill_switch_active():
        print("kill switch active"); sys.exit(0)

    client = KalshiClient()
    state = risk.refresh_from_portfolio(client)
    state.bankroll_dollars = min(state.bankroll_dollars,
                                 CFG["backtest"]["bankroll"])
    print(f"midday balance: ${state.bankroll_dollars:.2f}, "
          f"open exposure: ${state.open_exposure_dollars:.2f}", flush=True)

    buckets = edge_mod.load_buckets()
    now = datetime.now(timezone.utc)
    today_local = (now - timedelta(hours=4)).date()
    today = today_local.isoformat()

    new_file = not LOG.exists()
    f = LOG.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        w.writeheader()

    # ==== PHASE 1: review open positions for stop-loss / take-profit ====
    positions = client.get_positions()
    sells = 0
    # cache current station observations by city (one call per city)
    obs_cache: dict[str, float | None] = {}
    for code, city in CFG["cities"].items():
        obs_cache[code] = today_max_so_far(city["station"])
        print(f"  {code} max-so-far: {obs_cache[code]}F", flush=True)
    for p in positions:
        contracts = int(p.get("position", 0) or 0)
        if contracts == 0:
            continue
        tic = p.get("ticker", "") or p.get("market_ticker", "")
        if not tic.startswith("KXHIGH"):
            continue
        sd = settle_date_of_ticker(tic)
        if not sd or sd.isoformat() != today:
            continue  # only act on positions settling today
        code = city_from_ticker(tic)
        if not code:
            continue
        city = CFG["cities"][code]
        parsed = parse_ticker_bracket(tic)
        if not parsed:
            continue
        lo, hi, _ = parsed

        fcst, spread = forecast_now(city["lat"], city["lon"], today)
        if fcst is None:
            continue

        # widen bucket by ensemble spread
        lo_eff = lo - spread / 2
        hi_eff = hi + spread / 2
        month = sd.month
        season = edge_mod.SEASONS[month]
        bucket = buckets.get(f"{code}_{season}")
        if not bucket:
            continue
        p_model = edge_mod.model_prob_in_range(fcst, lo_eff, hi_eff, bucket)

        # get orderbook to find current mid
        try:
            md = client.list_markets(p.get("event_ticker") or "")
            m_now = next((m for m in md if m["ticker"] == tic), None)
        except Exception:
            m_now = None
        if not m_now:
            try:
                m_now = client.get_market(tic)
            except Exception:
                continue

        yb = float(m_now.get("yes_bid_dollars") or 0)
        ya = float(m_now.get("yes_ask_dollars") or 0)
        if yb <= 0 and ya <= 0:
            continue
        mid_yes = (yb + ya) / 2 if (yb > 0 and ya < 1) else (yb or ya)

        # We hold contracts; sign tells which side. Kalshi position sign:
        # positive = YES holding, negative = NO holding.
        holding_yes = contracts > 0
        p_we_win = p_model if holding_yes else (1 - p_model)
        mid_we = mid_yes if holding_yes else (1 - mid_yes)

        # entry approx (avg cost / contract in cents)
        avg_cost = float(p.get("market_exposure", 0) or 0) / 100 / max(1, abs(contracts))

        # Observation-driven kill: if YES bet on [lo,hi] and the station
        # has already exceeded hi+1F today, the high WILL be above hi.
        # Conversely if max-so-far < lo-1F AND p_model agrees, dead.
        obs_max = obs_cache.get(code)
        obs_dead = False
        if obs_max is not None:
            if holding_yes and obs_max > hi + 1:
                obs_dead = True   # YES on bracket already exceeded
            elif (not holding_yes) and obs_max <= lo - 5:
                # NO bet thrives, no rush to sell
                pass

        decision = None
        if obs_dead and mid_we < (avg_cost - 0.10):
            decision = "OBS_DEAD"
        elif p_we_win < 0.10 and mid_we < (avg_cost - 0.25):
            decision = "STOP_LOSS"
        elif p_we_win > 0.85 and mid_we > 0.80:
            decision = "TAKE_PROFIT"
        if not decision:
            continue

        # place a closing order: opposite side at slightly worse-than-mid
        sell_side = "yes" if holding_yes else "no"
        # sell at 1c below mid_we to cross the spread
        sell_price_cents = max(1, int(round(mid_we * 100)) - 1)
        n = abs(contracts)
        seed = f"MIDDAY|{tic}|{sell_side}|{sell_price_cents}|{today}"
        coid = hashlib.sha1(seed.encode()).hexdigest()[:24]
        row = {
            "run_utc": now.isoformat(), "city": code,
            "settle_date": today, "market_ticker": tic,
            "action": decision, "side": sell_side,
            "limit_price_cents": sell_price_cents, "count": n,
            "p_model_now": round(p_we_win, 3),
            "p_market_mid": round(mid_we, 3),
            "reason": f"avg_cost={avg_cost:.2f}",
            "order_id": "", "client_order_id": coid, "error": "",
        }
        try:
            kw = dict(
                ticker=tic, side=sell_side, action="sell",
                count=n, client_order_id=coid,
            )
            if sell_side == "yes":
                kw["yes_price_cents"] = sell_price_cents
            else:
                kw["no_price_cents"] = sell_price_cents
            resp = client.place_order(**kw)
            row["order_id"] = resp.get("order", {}).get("order_id", "")
            sells += 1
        except Exception as e:
            row["error"] = str(e)[:200]
        w.writerow(row); f.flush()

    print(f"midday phase 1: {sells} exit orders placed", flush=True)

    # ==== PHASE 2: look for new signals on today's markets ====
    # Refresh state in case sells freed capital
    state = risk.refresh_from_portfolio(client)
    state.bankroll_dollars = min(state.bankroll_dollars,
                                 CFG["backtest"]["bankroll"])
    new_orders = 0
    for code, city in CFG["cities"].items():
        series = city["kalshi_series"]
        mon = today_local.strftime("%b").upper()
        ev_ticker = f"{series}-{today_local:%y}{mon}{today_local:%d}"
        try:
            markets = client.list_markets(ev_ticker)
        except Exception:
            continue
        if not markets:
            continue
        fcst, spread = forecast_now(city["lat"], city["lon"], today)
        if fcst is None:
            continue
        signals = edge_mod.signals_for_event(
            markets, fcst, code, today, buckets, verbose=False,
            ensemble_spread_f=spread, enable_tails=True,
            min_market_volume=50, max_spread_cents=12)
        for sig in signals:
            entry = sig.limit_price_cents / 100
            decision_obj = risk.gate(state, entry, sig.edge)
            if not decision_obj.allowed:
                continue
            seed = f"MIDDAY-NEW|{sig.market_ticker}|{sig.side}|{sig.limit_price_cents}|{today}"
            coid = hashlib.sha1(seed.encode()).hexdigest()[:24]
            try:
                kw = dict(
                    ticker=sig.market_ticker, side=sig.side, action="buy",
                    count=decision_obj.max_contracts,
                    client_order_id=coid,
                )
                if sig.side == "yes":
                    kw["yes_price_cents"] = sig.limit_price_cents
                else:
                    kw["no_price_cents"] = sig.limit_price_cents
                resp = client.place_order(**kw)
                row = {
                    "run_utc": now.isoformat(), "city": code,
                    "settle_date": today,
                    "market_ticker": sig.market_ticker,
                    "action": "NEW_SIGNAL", "side": sig.side,
                    "limit_price_cents": sig.limit_price_cents,
                    "count": decision_obj.max_contracts,
                    "p_model_now": sig.p_model,
                    "p_market_mid": sig.p_market,
                    "reason": f"edge={sig.edge}",
                    "order_id": resp.get("order", {}).get("order_id", ""),
                    "client_order_id": coid, "error": "",
                }
                w.writerow(row); f.flush()
                state.open_exposure_dollars += entry * decision_obj.max_contracts
                new_orders += 1
            except Exception:
                pass
    print(f"midday phase 2: {new_orders} new orders placed", flush=True)
    f.close()
    print(f"midday run complete -> {LOG}", flush=True)


if __name__ == "__main__":
    main()

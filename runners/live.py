"""Live trading loop on Kalshi PROD.

REFUSES TO RUN unless a sentinel file exists at <repo>/PROMOTED proving
that paper validation has passed. This is enforced in code, on purpose.

To promote (after paper run gate is met):
  cd kalshi-weather-bot
  python core/calibration.py --check-paper      # must report PASS
  echo "promoted on $(date)" > PROMOTED
  git add PROMOTED && git commit -m "promote to live"

Environment:
  KALSHI_ENV=prod
  KALSHI_API_KEY_ID=<your prod key id>
  KALSHI_PRIVATE_KEY_PATH=<path to prod .pem>
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
from core.adaptive_params import adaptive_params, per_city_kelly_mult
from strategies.weather import edge as edge_mod

DATA = ROOT / "data"
LOG = DATA / "live_orders.csv"
PROMOTED = ROOT / "PROMOTED"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

FIELDS = ["run_utc", "city", "settle_date", "market_ticker", "side",
          "limit_price_cents", "count", "p_model", "p_market", "edge",
          "decision", "order_id", "client_order_id", "error"]


from core.forecast_sources import ensemble_forecast
from core import xgb_predict


def forecast_for(lat: float, lon: float, when: str,
                 city_code: str | None = None) -> tuple[float | None, float]:
    """5-source ensemble + XGBoost bias correction."""
    mean, spread, sources = ensemble_forecast(lat, lon, when)
    if mean is None:
        return None, 0.0
    if city_code:
        corrected, std = xgb_predict.correct(mean, spread, city_code,
                                              when, n_models=len(sources))
        # widen effective spread to include model-predicted std
        eff_spread = max(spread, std)
        return corrected, eff_spread
    return mean, spread


def cancel_stale_orders(client, stale_hours: float) -> int:
    """Cancel any resting orders older than stale_hours. Returns count."""
    import re as _re
    from datetime import datetime as _dt
    try:
        orders = client.get_orders(status="resting")
    except Exception as e:
        print(f"  could not list orders: {e}"); return 0
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=stale_hours))
    n = 0
    for o in orders:
        cts = o.get("created_time") or o.get("created_ts") or ""
        try:
            m = _re.match(r"^(.*?)\.(\d+)Z$", cts)
            if m:
                clean = f"{m.group(1)}.{m.group(2).ljust(6,'0')[:6]}+00:00"
            else:
                clean = cts.replace("Z", "+00:00")
            ct = _dt.fromisoformat(clean)
        except Exception:
            continue
        if ct < cutoff:
            oid = o.get("order_id")
            if not oid:
                continue
            try:
                client.cancel_order(oid)
                n += 1
            except Exception as e:
                print(f"  cancel {oid} failed: {e}")
    return n


def main() -> None:
    if not PROMOTED.exists():
        print("PROMOTED sentinel not found; refusing to run live.",
              file=sys.stderr)
        print("Run paper first and only promote after the gate passes.",
              file=sys.stderr)
        sys.exit(2)
    if os.getenv("KALSHI_ENV") != "prod":
        print("live.py refuses to run with KALSHI_ENV != prod",
              file=sys.stderr)
        sys.exit(2)
    if risk.kill_switch_active():
        print("kill switch active; exiting"); sys.exit(0)

    client = KalshiClient()
    # adapt risk params based on recent performance
    adj_edge, adj_kelly, reason = adaptive_params(
        CFG["backtest"]["min_edge"],
        CFG["backtest"]["kelly_fraction"],
    )
    CFG["backtest"]["min_edge"] = adj_edge
    CFG["backtest"]["kelly_fraction"] = adj_kelly
    print(f"adaptive: min_edge={adj_edge:.3f} kelly={adj_kelly:.3f} ({reason})",
          flush=True)
    # cancel resting orders older than threshold to free reserved capital
    stale_h = CFG["backtest"].get("cancel_stale_hours", 16)
    n_cancel = cancel_stale_orders(client, stale_h)
    if n_cancel:
        print(f"canceled {n_cancel} stale resting order(s) (>{stale_h}h)")
    state = risk.refresh_from_portfolio(client)
    # Hard cap bankroll at the configured deposit. Do not top up to chase.
    state.bankroll_dollars = min(state.bankroll_dollars,
                                 CFG["backtest"]["bankroll"])
    print(f"live balance (capped): ${state.bankroll_dollars:.2f}, "
          f"open exposure: ${state.open_exposure_dollars:.2f}")

    buckets = edge_mod.load_buckets()
    now = datetime.now(timezone.utc)
    # Trade BOTH tomorrow's markets (primary) and day+2 markets (secondary).
    # Day+2 markets have wider spread and less liquidity but doubling the
    # decision-points expands exposure to our edge.
    targets = [
        ((now - timedelta(hours=4)).date() + timedelta(days=1), 1.0),
        ((now - timedelta(hours=4)).date() + timedelta(days=2), 0.5),  # half conf
    ]

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
            continue
        fcst, spread = forecast_for(city["lat"], city["lon"], target,
                                     city_code=code)
        if fcst is None:
            continue
        signals = edge_mod.signals_for_event(
            markets, fcst, code, target, buckets, verbose=True,
            ensemble_spread_f=spread, enable_tails=True,
            min_market_volume=50, max_spread_cents=12)
        print(f"{code} {target}: forecast={fcst:.1f}F (spread={spread:.1f}F, "
              f"conf={conf:.2f}), {len(signals)} signals")

        # confidence multiplier: tight ensemble + small XGB std => bigger size
        conf = max(0.4, min(1.5, 2.0 / max(1.0, spread + 1.0)))
        state.confidence_multiplier = conf
        # Inter-bracket hedge cap: limit total exposure on this single event
        per_event_cap = state.bankroll_dollars * 0.25
        per_event_used = 0.0
        for sig in signals:
            entry = sig.limit_price_cents / 100
            if per_event_used >= per_event_cap:
                break
            decision = risk.gate(state, entry, sig.edge)
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
            seed = f"LIVE|{sig.market_ticker}|{sig.side}|{sig.limit_price_cents}|{target}"
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
                state.open_exposure_dollars += entry * decision.max_contracts
                per_event_used += entry * decision.max_contracts
            except Exception as e:
                row["error"] = str(e)[:200]
            w.writerow(row); f.flush()

    f.close()
    print(f"live run complete -> {LOG}")

    # write a per-run summary line to daily_runs.csv
    summary_path = DATA / "daily_runs.csv"
    new = not summary_path.exists()
    import csv as _csv
    with summary_path.open("a", newline="") as sf:
        sw = _csv.DictWriter(sf, fieldnames=[
            "run_utc", "workflow", "balance_total", "open_exposure",
            "min_edge", "kelly_fraction"
        ])
        if new:
            sw.writeheader()
        sw.writerow({
            "run_utc": now.isoformat(),
            "workflow": "live",
            "balance_total": round(state.bankroll_dollars, 2),
            "open_exposure": round(state.open_exposure_dollars, 2),
            "min_edge": adj_edge,
            "kelly_fraction": adj_kelly,
        })


if __name__ == "__main__":
    main()

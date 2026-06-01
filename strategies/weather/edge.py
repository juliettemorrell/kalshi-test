"""Convert (current forecast, market snapshot) -> trade decisions.

Uses the empirical per-city/season error distribution to compute model
probability for each market's bracket. Compares to current market price.
Emits a list of TradeSignal objects.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

SEASONS = {12: "DJF", 1: "DJF", 2: "DJF",
           3: "MAM", 4: "MAM", 5: "MAM",
           6: "JJA", 7: "JJA", 8: "JJA",
           9: "SON", 10: "SON", 11: "SON"}

_MONTHS = {m: i for i, m in enumerate(
    ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"], 1)}


def parse_market_range(ticker: str, sub_title: str | None) -> tuple[float, float, str] | None:
    if "-B" in ticker:
        try:
            b = float(ticker.rsplit("-B", 1)[1])
            return (b, b + 1.0, "bracket")
        except ValueError:
            return None
    if "-T" in ticker:
        sub = (sub_title or "").lower()
        try:
            b = float(ticker.rsplit("-T", 1)[1])
        except ValueError:
            return None
        if "or above" in sub:
            return (b, 200.0, "tail_hi")
        if "or below" in sub:
            return (-100.0, b, "tail_lo")
    return None


@dataclass
class TradeSignal:
    market_ticker: str
    side: str            # 'yes' or 'no'
    limit_price_cents: int
    edge: float
    p_model: float
    p_market: float
    lo: float
    hi: float
    forecast: float


def _empirical_cdf(err: float, qv: np.ndarray, ql: np.ndarray) -> float:
    if err <= qv[0]:
        return 0.005
    if err >= qv[-1]:
        return 0.995
    return float(np.interp(err, qv, ql))


def model_prob_in_range(forecast: float, lo: float, hi: float,
                        bucket: dict) -> float:
    qv = np.asarray(bucket["quantile_values"])
    ql = np.asarray(bucket["quantile_levels"])
    return max(0.0, min(1.0,
        _empirical_cdf(forecast - lo, qv, ql) - _empirical_cdf(forecast - hi, qv, ql)))


def signals_for_event(markets: list[dict],
                      forecast_high: float,
                      city_code: str,
                      settle_date: str,
                      buckets: dict,
                      verbose: bool = False,
                      ensemble_spread_f: float = 0.0,
                      enable_tails: bool = True,
                      min_market_volume: float = 50.0,
                      max_spread_cents: int = 12) -> list[TradeSignal]:
    """forecast_high = ensemble mean. ensemble_spread_f widens uncertainty
    when models disagree (range of multi-model means in F)."""
    month = datetime.fromisoformat(settle_date).month
    season = SEASONS[month]
    bucket = buckets.get(f"{city_code}_{season}")
    if not bucket:
        if verbose:
            print(f"  [edge] {city_code}: no bucket for season {season}")
        return []

    min_edge = CFG["backtest"]["min_edge"]
    longshot = CFG["backtest"]["longshot_floor_cents"] / 100
    out: list[TradeSignal] = []
    stats = {"considered": 0, "no_bid_ask": 0, "extreme_price": 0,
             "tail_skipped": 0, "edge_too_small": 0, "below_floor": 0,
             "thin_book": 0, "wide_spread": 0,
             "fired": 0, "best_edge": 0.0}

    for m in markets:
        stats["considered"] += 1
        parsed = parse_market_range(m["ticker"], m.get("yes_sub_title"))
        if not parsed:
            continue
        lo, hi, side = parsed
        if side != "bracket" and not enable_tails:
            stats["tail_skipped"] += 1
            continue
        # liquidity gates: prefer 24h volume over all-time when available
        try:
            v24 = float(m.get("volume_24h_fp") or 0)
            vall = float(m.get("volume_fp") or 0)
            # use higher of the two; v24 may be 0 for new markets
            vol = max(v24, vall)
        except (TypeError, ValueError):
            vol = 0.0
        if vol < min_market_volume:
            stats["thin_book"] += 1
            continue

        # ATM price comes from the resting book. We post a maker order one
        # cent better than the current best price on the side we want.
        yes_bid = _to_float(m.get("yes_bid_dollars"))
        yes_ask = _to_float(m.get("yes_ask_dollars"))
        if yes_bid is None or yes_ask is None:
            stats["no_bid_ask"] += 1
            continue
        # spread gate (in cents)
        spread_c = int(round((yes_ask - yes_bid) * 100))
        if spread_c > max_spread_cents:
            stats["wide_spread"] += 1
            continue
        # use mid as p_market when both sides quoted, else last
        if yes_bid > 0 and yes_ask < 1:
            p_market = (yes_bid + yes_ask) / 2
        else:
            last = _to_float(m.get("last_price_dollars"))
            if last is None or last <= 0:
                stats["no_bid_ask"] += 1
                continue
            p_market = last
        if p_market <= 0 or p_market >= 1:
            stats["extreme_price"] += 1
            continue

        # inflate uncertainty by ensemble spread AND extreme-weather multiplier
        try:
            from core.extreme_weather import variance_multiplier
            month_int = datetime.fromisoformat(settle_date).month
            v_mult = variance_multiplier(forecast_high, ensemble_spread_f,
                                          month_int, city_code)
        except Exception:
            v_mult = 1.0
        eff_spread = ensemble_spread_f * v_mult
        lo_eff = lo - eff_spread / 2
        hi_eff = hi + eff_spread / 2
        p_model = model_prob_in_range(forecast_high, lo_eff, hi_eff, bucket)
        edge = p_model - p_market
        if abs(edge) > abs(stats["best_edge"]):
            stats["best_edge"] = edge

        if edge >= min_edge and longshot <= yes_ask < (1 - longshot):
            # VWAP-aware: only chase up to model_prob - 2c (leave margin)
            fair_cap_c = max(1, int(round(p_model * 100)) - 2)
            # Real VWAP from recent trades when available
            try:
                from core.vwap import recent_vwap
                rv = recent_vwap(m["ticker"], limit=30, max_age_hours=4)
            except Exception:
                rv = None
            vwap_cap_c = (max(1, int(round(rv * 100)) - 1)
                          if rv is not None else fair_cap_c)
            limit_cents = max(int(round(yes_bid * 100)) + 1,
                              int(round(p_market * 100)))
            limit_cents = min(limit_cents,
                              max(int(round(yes_ask * 100)) - 1, 1),
                              fair_cap_c, vwap_cap_c)
            if limit_cents < int(longshot * 100):
                stats["below_floor"] += 1; continue
            out.append(TradeSignal(
                market_ticker=m["ticker"], side="yes",
                limit_price_cents=limit_cents,
                edge=round(edge, 3),
                p_model=round(p_model, 3),
                p_market=round(p_market, 3),
                lo=lo, hi=hi, forecast=forecast_high,
            ))
            stats["fired"] += 1
        elif edge <= -min_edge:
            no_bid = 1 - yes_ask
            no_ask = 1 - yes_bid
            if no_ask <= longshot or no_ask >= (1 - longshot):
                stats["below_floor"] += 1; continue
            # VWAP-aware: cap at fair (1-p_model) - 2c on NO side too
            no_fair_cap = max(1, int(round((1 - p_model) * 100)) - 2)
            no_limit_cents = max(int(round(no_bid * 100)) + 1,
                                 int(round((1 - p_market) * 100)))
            no_limit_cents = min(no_limit_cents,
                                 max(int(round(no_ask * 100)) - 1, 1),
                                 no_fair_cap)
            if no_limit_cents < int(longshot * 100):
                stats["below_floor"] += 1; continue
            out.append(TradeSignal(
                market_ticker=m["ticker"], side="no",
                limit_price_cents=no_limit_cents,
                edge=round(edge, 3),
                p_model=round(p_model, 3),
                p_market=round(p_market, 3),
                lo=lo, hi=hi, forecast=forecast_high,
            ))
            stats["fired"] += 1
        else:
            stats["edge_too_small"] += 1

    if verbose:
        print(f"  [edge {city_code}] {stats}")
    return out


def _to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_buckets() -> dict:
    with (DATA / "error_buckets.json").open() as f:
        return json.load(f)

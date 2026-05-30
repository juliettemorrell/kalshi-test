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
                      buckets: dict) -> list[TradeSignal]:
    month = datetime.fromisoformat(settle_date).month
    season = SEASONS[month]
    bucket = buckets.get(f"{city_code}_{season}")
    if not bucket:
        return []

    min_edge = CFG["backtest"]["min_edge"]
    longshot = CFG["backtest"]["longshot_floor_cents"] / 100
    out: list[TradeSignal] = []

    for m in markets:
        parsed = parse_market_range(m["ticker"], m.get("yes_sub_title"))
        if not parsed:
            continue
        # only trade bracket markets per overlay 1 (tails are usually longshots)
        lo, hi, side = parsed
        if side != "bracket":
            continue

        # ATM price comes from the resting book. We post a maker order one
        # cent better than the current best price on the side we want.
        yes_bid = _to_float(m.get("yes_bid_dollars"))
        yes_ask = _to_float(m.get("yes_ask_dollars"))
        if yes_bid is None or yes_ask is None:
            continue
        # use mid as p_market when both sides quoted, else whichever exists
        if yes_bid > 0 and yes_ask < 1:
            p_market = (yes_bid + yes_ask) / 2
        else:
            last = _to_float(m.get("last_price_dollars"))
            if last is None:
                continue
            p_market = last
        if p_market <= 0 or p_market >= 1:
            continue

        p_model = model_prob_in_range(forecast_high, lo, hi, bucket)
        edge = p_model - p_market

        if edge >= min_edge and longshot <= yes_ask < (1 - longshot):
            # buy YES as a maker: bid at current ask - 1c, or higher if needed
            limit_cents = max(int(round(yes_bid * 100)) + 1,
                              int(round(p_market * 100)))
            limit_cents = min(limit_cents, int(round(yes_ask * 100)) - 1)
            if limit_cents < int(longshot * 100):
                continue
            out.append(TradeSignal(
                market_ticker=m["ticker"], side="yes",
                limit_price_cents=limit_cents,
                edge=round(edge, 3),
                p_model=round(p_model, 3),
                p_market=round(p_market, 3),
                lo=lo, hi=hi, forecast=forecast_high,
            ))
        elif edge <= -min_edge:
            # buy NO: NO bid/ask is implied as 100 - YES ask/bid
            no_bid = 1 - yes_ask
            no_ask = 1 - yes_bid
            if no_ask <= longshot or no_ask >= (1 - longshot):
                continue
            no_limit_cents = max(int(round(no_bid * 100)) + 1,
                                 int(round((1 - p_market) * 100)))
            no_limit_cents = min(no_limit_cents, int(round(no_ask * 100)) - 1)
            if no_limit_cents < int(longshot * 100):
                continue
            out.append(TradeSignal(
                market_ticker=m["ticker"], side="no",
                limit_price_cents=no_limit_cents,
                edge=round(edge, 3),
                p_model=round(p_model, 3),
                p_market=round(p_market, 3),
                lo=lo, hi=hi, forecast=forecast_high,
            ))
    return out


def _to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_buckets() -> dict:
    with (DATA / "error_buckets.json").open() as f:
        return json.load(f)

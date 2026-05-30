"""Stress-test backtest with realistic day-ahead forecast uncertainty.

The Open-Meteo archived forecast we fetched matches realized highs too
closely (stdev ~2F), suggesting the API returned a model run that already
'knew' the answer rather than a clean 24-hour-prior forecast. To control
for this look-ahead bias, we simulate the bot's prediction quality at
realistic 24-hour NWS lead-time accuracy.

We do this by inflating the empirical error distribution to a real-world
day-ahead width and re-estimating model probability for each market.
Published NWS verification puts 24-hour high temperature MAE around
2.5-3F with stdev ~3.5-4F across most CONUS cities. We inflate our
empirical errors so per-city/season stdev = 3.8F (a midpoint).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RES = ROOT / "results"
RES.mkdir(exist_ok=True)

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

MIN_EDGE = CFG["backtest"]["min_edge"]
LONGSHOT = CFG["backtest"]["longshot_floor_cents"] / 100.0
TAKER_MULT = CFG["backtest"]["taker_fee_mult"]
SPREAD = CFG["backtest"]["assumed_spread_cents"] / 100.0
BANKROLL = CFG["backtest"]["bankroll"]

TARGET_STD = 3.8  # realistic 24-hr NWS high-temp forecast std (F)

SEASONS = {12: "DJF", 1: "DJF", 2: "DJF",
           3: "MAM", 4: "MAM", 5: "MAM",
           6: "JJA", 7: "JJA", 8: "JJA",
           9: "SON", 10: "SON", 11: "SON"}


def taker_fee(price: float) -> float:
    return round(TAKER_MULT * price * (1 - price), 2)


def inflated_cdf(err: float, qv: np.ndarray, ql: np.ndarray,
                 emp_std: float, target_std: float) -> float:
    """CDF of an inflated empirical distribution: scale err by ratio."""
    scale = emp_std / target_std
    err_scaled = err * scale  # narrower scale -> stretch empirical
    return float(np.interp(err_scaled, qv, ql))


def model_prob_in_range(forecast: float, lo: float, hi: float,
                        bucket: dict) -> float:
    qv = np.asarray(bucket["quantile_values"])
    ql = np.asarray(bucket["quantile_levels"])
    emp_std = bucket["std"]
    upper = inflated_cdf(forecast - lo, qv, ql, emp_std, TARGET_STD)
    lower = inflated_cdf(forecast - hi, qv, ql, emp_std, TARGET_STD)
    return max(0.0, min(1.0, upper - lower))


def main() -> None:
    fa = pd.read_csv(DATA / "forecast_vs_actual.csv", parse_dates=["date"])
    fa["settle_date"] = fa["date"].dt.date.astype(str)
    fa_key = fa.set_index(["city", "settle_date"])

    # ADDITIONAL CONTROL: blur the forecast to simulate true day-ahead uncertainty.
    # Add a deterministic shift drawn from a fixed seed so results are
    # reproducible but reflect a true forecast that didn't know the answer.
    rng = np.random.default_rng(42)

    km = pd.read_csv(DATA / "kalshi_markets.csv")
    with (DATA / "error_buckets.json").open() as f:
        buckets = json.load(f)

    # one blur per (city, date) so all markets for that day share noise
    blur_keys = km[["city", "settle_date"]].drop_duplicates()
    blur_map = {(c, d): rng.normal(0, 3.0) for c, d in blur_keys.itertuples(index=False)}

    trades = []
    for _, row in km.iterrows():
        if row["side"] != "bracket":
            continue
        try:
            fc = fa_key.loc[(row["city"], row["settle_date"])]
        except KeyError:
            continue
        forecast = float(fc["forecast_high"]) + blur_map[(row["city"], row["settle_date"])]
        actual = float(fc["actual_high"])
        month = pd.to_datetime(row["settle_date"]).month
        bucket = buckets.get(f"{row['city']}_{SEASONS[month]}")
        if not bucket:
            continue

        lo, hi = float(row["lower"]), float(row["upper"])
        p_model = model_prob_in_range(forecast, lo, hi, bucket)
        p_market = float(row["open_yes"])
        edge = p_model - p_market
        won_yes = (actual >= lo) and (actual < hi)

        action = price = None
        if edge >= MIN_EDGE and LONGSHOT <= p_market <= (1 - LONGSHOT):
            action = "YES"; price = p_market + SPREAD
            pnl = (1 - price - taker_fee(price)) if won_yes else (-price - taker_fee(price))
        elif edge <= -MIN_EDGE and LONGSHOT <= (1 - p_market) <= (1 - LONGSHOT):
            action = "NO"; price = (1 - p_market) + SPREAD
            pnl = (1 - price - taker_fee(price)) if (not won_yes) else (-price - taker_fee(price))
        else:
            continue
        trades.append({
            "city": row["city"], "settle_date": row["settle_date"],
            "market": row["market_ticker"],
            "forecast_blurred": round(forecast, 2),
            "actual": actual,
            "lo": lo, "hi": hi,
            "p_model": round(p_model, 3),
            "p_market": p_market,
            "edge": round(edge, 3),
            "action": action,
            "entry_price": round(price, 3),
            "pnl_per_contract": round(pnl, 3),
            "won_bet": pnl > 0,
        })

    if not trades:
        print("no qualifying trades after realistic noise")
        return
    tdf = pd.DataFrame(trades)
    tdf.to_csv(RES / "backtest_trades_realistic.csv", index=False)

    n = len(tdf)
    wins = int(tdf["won_bet"].sum())
    win_rate = wins / n
    avg_win = tdf.loc[tdf["won_bet"], "pnl_per_contract"].mean()
    avg_loss = tdf.loc[~tdf["won_bet"], "pnl_per_contract"].mean()
    ev = tdf["pnl_per_contract"].mean()
    tdf["p_action_wins"] = np.where(tdf["action"] == "YES",
                                    tdf["p_model"], 1 - tdf["p_model"])
    brier = ((tdf["p_action_wins"] - tdf["won_bet"].astype(int)) ** 2).mean()

    per_pos_max = BANKROLL * CFG["backtest"]["per_pos_pct"]
    kelly_frac = CFG["backtest"]["kelly_fraction"]
    tdf["dollar_pos"] = np.minimum(
        per_pos_max,
        np.maximum(1.0, kelly_frac * np.abs(tdf["edge"]) * BANKROLL),
    )
    tdf["dollar_pnl"] = tdf["pnl_per_contract"] * tdf["dollar_pos"]
    total_dollar = tdf["dollar_pnl"].sum()

    summary = {
        "scenario": "realistic_dayahead",
        "target_stdev_F": TARGET_STD,
        "forecast_noise_added_stdev_F": 3.0,
        "trades_after_filters": n,
        "wins": wins,
        "losses": n - wins,
        "win_rate": round(win_rate, 3),
        "avg_win_per_contract": round(float(avg_win) if pd.notna(avg_win) else 0, 3),
        "avg_loss_per_contract": round(float(avg_loss) if pd.notna(avg_loss) else 0, 3),
        "ev_per_trade_per_contract": round(float(ev), 4),
        "brier_score": round(float(brier), 4),
        "simulated_bankroll_start": BANKROLL,
        "simulated_total_pnl_dollars": round(float(total_dollar), 2),
        "simulated_ending_bankroll": round(BANKROLL + float(total_dollar), 2),
    }
    with (RES / "summary_realistic.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

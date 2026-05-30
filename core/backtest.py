"""Settlement-price backtest.

For each (event, bracket market) we have:
  - open_yes: earliest available trade price (best proxy for day-ahead price)
  - close_yes: settlement-window price (sanity check, near 0 or 1)
  - result: yes/no settlement

We pair each market with our archived forecast for that city/date and the
realized high. Model probability that the realized high falls in the
market's [lower, upper) range is computed from the empirical error
distribution for that city/season:
  P(actual in [lo, hi)) = ECDF_err(forecast - lo) - ECDF_err(forecast - hi)

Trading rule:
  edge = model_prob - open_yes
  Trade YES if edge >= MIN_EDGE and open_yes >= LONGSHOT_FLOOR
  Trade NO  if edge <= -MIN_EDGE and (1-open_yes) >= LONGSHOT_FLOOR
P&L per contract:
  Win  -> +(1 - price) - fee
  Loss -> -price - fee
where price is the assumed entry price (open_yes for YES, 1-open_yes for NO),
and fee is taker fee = round(0.07 * price * (1-price), 2).
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

SEASONS = {12: "DJF", 1: "DJF", 2: "DJF",
           3: "MAM", 4: "MAM", 5: "MAM",
           6: "JJA", 7: "JJA", 8: "JJA",
           9: "SON", 10: "SON", 11: "SON"}


def taker_fee(price: float) -> float:
    """Kalshi taker fee per contract."""
    return round(TAKER_MULT * price * (1 - price), 2)


def model_prob_in_range(forecast: float, lo: float, hi: float,
                        bucket: dict) -> float:
    """P(actual high in [lo, hi)) using empirical forecast-error distribution.
    error = forecast - actual. So actual in [lo, hi) iff
    error in (forecast - hi, forecast - lo].
    """
    qv = np.asarray(bucket["quantile_values"])
    ql = np.asarray(bucket["quantile_levels"])

    def cdf(err_val: float) -> float:
        if err_val <= qv[0]:
            return float(ql[0]) * (err_val - qv[0] + 0.01) / 0.01 if False else 0.005
        if err_val >= qv[-1]:
            return 0.995
        # linear interp on empirical CDF
        return float(np.interp(err_val, qv, ql))

    # Upper bound: errors strictly less than forecast - lo
    # Lower bound: errors at most forecast - hi
    upper = cdf(forecast - lo)
    lower = cdf(forecast - hi)
    return max(0.0, min(1.0, upper - lower))


def main() -> None:
    fa = pd.read_csv(DATA / "forecast_vs_actual.csv", parse_dates=["date"])
    fa["settle_date"] = fa["date"].dt.date.astype(str)
    fa_key = fa.set_index(["city", "settle_date"])

    km = pd.read_csv(DATA / "kalshi_markets.csv")
    print(f"loaded {len(km)} market snapshots")

    with (DATA / "error_buckets.json").open() as f:
        buckets = json.load(f)

    trades = []
    paired = 0
    skipped_no_forecast = 0
    skipped_tail_only = 0

    for _, row in km.iterrows():
        # join with forecast/actual
        try:
            fc = fa_key.loc[(row["city"], row["settle_date"])]
        except KeyError:
            skipped_no_forecast += 1
            continue
        forecast = float(fc["forecast_high"])
        actual = float(fc["actual_high"])
        month = pd.to_datetime(row["settle_date"]).month
        season = SEASONS[month]
        bucket = buckets.get(f"{row['city']}_{season}")
        if not bucket:
            continue

        lo, hi = float(row["lower"]), float(row["upper"])
        # Focus on bracket markets (tails are typically very longshot)
        if row["side"] != "bracket":
            skipped_tail_only += 1
            continue

        p_model = model_prob_in_range(forecast, lo, hi, bucket)
        p_market = float(row["open_yes"])
        edge = p_model - p_market

        # Determine settlement: actual in [lo, hi)?
        won_yes = (actual >= lo) and (actual < hi)

        # Apply rules
        action = None
        price = None
        if edge >= MIN_EDGE and p_market >= LONGSHOT and p_market <= (1 - LONGSHOT):
            action = "YES"
            price = p_market + SPREAD  # pay spread to cross
            pnl = (1 - price - taker_fee(price)) if won_yes else (-price - taker_fee(price))
        elif edge <= -MIN_EDGE and (1 - p_market) >= LONGSHOT and (1 - p_market) <= (1 - LONGSHOT):
            action = "NO"
            price = (1 - p_market) + SPREAD
            pnl = (1 - price - taker_fee(price)) if (not won_yes) else (-price - taker_fee(price))
        else:
            continue

        paired += 1
        trades.append({
            "city": row["city"],
            "settle_date": row["settle_date"],
            "market": row["market_ticker"],
            "forecast": forecast,
            "actual": actual,
            "lo": lo, "hi": hi,
            "p_model": round(p_model, 3),
            "p_market": p_market,
            "edge": round(edge, 3),
            "action": action,
            "entry_price": round(price, 3),
            "won_yes": won_yes,
            "pnl_per_contract": round(pnl, 3),
        })

    if not trades:
        print("no qualifying trades")
        return

    tdf = pd.DataFrame(trades)
    tdf.to_csv(RES / "backtest_trades.csv", index=False)

    # Aggregate stats
    n = len(tdf)
    wins = ((tdf["pnl_per_contract"] > 0)).sum()
    losses = ((tdf["pnl_per_contract"] <= 0)).sum()
    win_rate = wins / n
    avg_win = tdf.loc[tdf["pnl_per_contract"] > 0, "pnl_per_contract"].mean()
    avg_loss = tdf.loc[tdf["pnl_per_contract"] <= 0, "pnl_per_contract"].mean()
    total_pnl_per_contract = tdf["pnl_per_contract"].sum()
    expected_value = tdf["pnl_per_contract"].mean()

    # Calibration: bin predicted prob, check realized
    calib_bins = np.linspace(0.05, 0.95, 10)
    calib_rows = []
    # compute realized = was the action's bet right?
    tdf["bet_won"] = (tdf["pnl_per_contract"] > 0).astype(int)
    # For action=YES, model prob = p_model and we won iff won_yes
    # For action=NO, our prob of winning = 1 - p_model and we won iff not won_yes
    tdf["p_action_wins"] = np.where(tdf["action"] == "YES",
                                    tdf["p_model"], 1 - tdf["p_model"])
    for i in range(len(calib_bins) - 1):
        lo_b, hi_b = calib_bins[i], calib_bins[i + 1]
        mask = (tdf["p_action_wins"] >= lo_b) & (tdf["p_action_wins"] < hi_b)
        if mask.sum() == 0:
            continue
        calib_rows.append({
            "bin_lo": round(lo_b, 2),
            "bin_hi": round(hi_b, 2),
            "n": int(mask.sum()),
            "mean_pred": round(tdf.loc[mask, "p_action_wins"].mean(), 3),
            "mean_realized": round(tdf.loc[mask, "bet_won"].mean(), 3),
        })
    pd.DataFrame(calib_rows).to_csv(RES / "calibration.csv", index=False)

    # Brier score on the chosen-action probability
    brier = ((tdf["p_action_wins"] - tdf["bet_won"]) ** 2).mean()

    # Position sizing simulation on $100 bankroll, quarter-Kelly
    # Position dollars = max(1, kelly_frac * edge / odds * bankroll), cap at 2.5%
    per_pos_max = BANKROLL * CFG["backtest"]["per_pos_pct"]
    kelly_frac = CFG["backtest"]["kelly_fraction"]
    tdf["dollar_pos"] = np.minimum(
        per_pos_max,
        np.maximum(1.0, kelly_frac * np.abs(tdf["edge"]) * BANKROLL),
    )
    # contracts at $1 = 100 cents (Kalshi contracts are dollar-denominated)
    tdf["contracts"] = tdf["dollar_pos"]  # 1 contract = $1 max payoff
    tdf["dollar_pnl"] = tdf["pnl_per_contract"] * tdf["contracts"]
    total_pnl_dollars = tdf["dollar_pnl"].sum()

    summary = {
        "trades_total_examined": int(len(km)),
        "trades_paired_with_forecast": int(len(km) - skipped_no_forecast),
        "trades_after_filters": int(n),
        "wins": int(wins),
        "losses": int(losses),
        "win_rate": round(float(win_rate), 3),
        "avg_win_per_contract": round(float(avg_win), 3),
        "avg_loss_per_contract": round(float(avg_loss), 3),
        "total_pnl_per_contract_unit": round(float(total_pnl_per_contract), 2),
        "ev_per_trade_per_contract": round(float(expected_value), 4),
        "brier_score": round(float(brier), 4),
        "simulated_bankroll_start": BANKROLL,
        "simulated_total_pnl_dollars": round(float(total_pnl_dollars), 2),
        "simulated_ending_bankroll": round(BANKROLL + float(total_pnl_dollars), 2),
        "params": {
            "min_edge": MIN_EDGE,
            "longshot_floor": LONGSHOT,
            "taker_fee_mult": TAKER_MULT,
            "spread_assumption": SPREAD,
            "kelly_fraction": kelly_frac,
            "per_pos_pct": CFG["backtest"]["per_pos_pct"],
        }
    }
    with (RES / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

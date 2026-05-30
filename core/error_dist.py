"""Empirical forecast-error distributions per city/season.

We treat the GFS deterministic high as the point forecast, and the realized
ERA5 high as truth. Errors = forecast - actual. We bin by city x meteorological
season and dump:
  - per-bucket quantile tables (used as the empirical CDF for prob estimates)
  - a summary table that compares empirical tail rates vs Gaussian.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SEASONS = {12: "DJF", 1: "DJF", 2: "DJF",
           3: "MAM", 4: "MAM", 5: "MAM",
           6: "JJA", 7: "JJA", 8: "JJA",
           9: "SON", 10: "SON", 11: "SON"}


def main() -> None:
    df = pd.read_csv(DATA / "forecast_vs_actual.csv", parse_dates=["date"])
    df["season"] = df["date"].dt.month.map(SEASONS)

    summary_rows = []
    buckets: dict[str, dict] = {}

    for (city, season), g in df.groupby(["city", "season"]):
        errs = g["error"].to_numpy()
        if len(errs) < 20:
            continue
        mu, sigma = errs.mean(), errs.std(ddof=1)
        empirical_2sig = float(((errs - mu).__abs__() > 2 * sigma).mean())
        empirical_3sig = float(((errs - mu).__abs__() > 3 * sigma).mean())
        gauss_2sig = 2 * (1 - stats.norm.cdf(2))   # ~0.0455
        gauss_3sig = 2 * (1 - stats.norm.cdf(3))   # ~0.0027

        q = np.quantile(errs, np.linspace(0.01, 0.99, 99))
        buckets[f"{city}_{season}"] = {
            "n": int(len(errs)),
            "mean": float(mu),
            "std": float(sigma),
            "quantile_levels": np.linspace(0.01, 0.99, 99).tolist(),
            "quantile_values": q.tolist(),
        }
        summary_rows.append(
            dict(city=city, season=season, n=len(errs),
                 mean=round(mu, 2), std=round(sigma, 2),
                 emp_2sig_pct=round(100 * empirical_2sig, 1),
                 gauss_2sig_pct=round(100 * gauss_2sig, 1),
                 emp_3sig_pct=round(100 * empirical_3sig, 1),
                 gauss_3sig_pct=round(100 * gauss_3sig, 2),
                 max_abs_err=round(float(np.abs(errs - mu).max()), 1))
        )

    pd.DataFrame(summary_rows).to_csv(DATA / "error_summary.csv", index=False)
    with (DATA / "error_buckets.json").open("w") as f:
        json.dump(buckets, f, indent=2)

    # global rollup
    all_err = df["error"].to_numpy()
    mu, sigma = all_err.mean(), all_err.std(ddof=1)
    emp2 = ((all_err - mu).__abs__() > 2 * sigma).mean()
    emp3 = ((all_err - mu).__abs__() > 3 * sigma).mean()
    print(f"GLOBAL: n={len(all_err)} mean={mu:.2f} std={sigma:.2f}")
    print(f"  empirical 2-sigma: {100*emp2:.2f}% (gauss expects 4.55%)")
    print(f"  empirical 3-sigma: {100*emp3:.2f}% (gauss expects 0.27%)")
    print(f"  written: error_summary.csv, error_buckets.json")


if __name__ == "__main__":
    main()

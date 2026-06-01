"""Pull historical forecast (as-issued) and realized highs from Open-Meteo.

Open-Meteo provides two free endpoints we need:
- Historical Forecast API: the archived forecasts the model issued on a given day
- Archive API: ERA5 reanalysis used as ground-truth realized highs

We pull both for each city, align by date, and write CSVs to data/.
"""
from __future__ import annotations

import csv
import json
import time
from datetime import date, timedelta
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

LOOKBACK = max(CFG["backtest"].get("lookback_days", 365), 1095)  # min 3 years
END = date.today() - timedelta(days=2)            # ERA5 lags ~2 days
START = END - timedelta(days=LOOKBACK)
# multi-model ensemble: GFS + ECMWF (both archived by Open-Meteo)
MODELS = ["gfs_seamless", "ecmwf_ifs025"]


def _get(url: str, params: dict) -> dict:
    for attempt in range(4):
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 503):
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
    raise RuntimeError(f"failed {url} {params}")


def fetch_forecast_archive(lat: float, lon: float, start: date, end: date,
                           model: str = "gfs_seamless") -> dict:
    """Archived forecast highs for a specific model."""
    return _get(
        "https://historical-forecast-api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
            "models": model,
        },
    )


def fetch_realized(lat: float, lon: float, start: date, end: date) -> dict:
    """ERA5 reanalysis: closest free proxy to realized NWS highs."""
    return _get(
        "https://archive-api.open-meteo.com/v1/archive",
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
        },
    )


def fetch_ensemble_spread(lat: float, lon: float, start: date, end: date) -> dict:
    """GFS ensemble spread proxy: hourly temps -> daily max distribution.
    We use the deterministic GFS for the mean and approximate spread from
    intraday hourly variation as a stand-in (Open-Meteo's free tier doesn't
    expose individual members beyond a small window). The real bot would use
    proper ensemble member access; for the backtest this is a usable proxy."""
    return _get(
        "https://historical-forecast-api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
            "models": "gfs_seamless",
        },
    )


def main() -> None:
    rows = []
    for code, city in CFG["cities"].items():
        print(f"fetching {code} ({city['name']}) {START} -> {END}", flush=True)
        real = fetch_realized(city["lat"], city["lon"], START, END)
        real_map = dict(zip(real["daily"]["time"],
                            real["daily"]["temperature_2m_max"]))

        # collect per-model archived highs, then build ensemble mean
        per_model = {}
        for mdl in MODELS:
            try:
                d = fetch_forecast_archive(city["lat"], city["lon"],
                                           START, END, mdl)
                per_model[mdl] = dict(zip(d["daily"]["time"],
                                          d["daily"]["temperature_2m_max"]))
                print(f"  {mdl}: {len(per_model[mdl])} days", flush=True)
            except Exception as e:
                print(f"  {mdl}: failed ({e})", flush=True)
            time.sleep(0.3)

        all_dates = sorted(set().union(*per_model.values()))
        for d in all_dates:
            rh = real_map.get(d)
            if rh is None:
                continue
            forecasts = []
            for mdl in MODELS:
                v = per_model.get(mdl, {}).get(d)
                if v is not None:
                    forecasts.append(v)
            if not forecasts:
                continue
            ens_mean = sum(forecasts) / len(forecasts)
            ens_spread = (max(forecasts) - min(forecasts)) if len(forecasts) > 1 else 0
            rows.append({
                "city": code, "date": d,
                "forecast_high": round(ens_mean, 2),
                "ensemble_spread": round(ens_spread, 2),
                "n_models": len(forecasts),
                "actual_high": round(rh, 2),
                "error": round(ens_mean - rh, 2),
            })
        time.sleep(0.3)

    out = DATA / "forecast_vs_actual.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows (multi-model ensemble) -> {out}", flush=True)


if __name__ == "__main__":
    main()

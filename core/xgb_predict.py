"""Per-city XGBoost inference. Falls back to identity if missing."""
from __future__ import annotations

import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

_loaded = False
_bias_per_city: dict[str, object] = {}
_std_per_city: dict[str, object] = {}
_meta: dict | None = None
_history_cache: dict[str, dict[str, dict]] = {}


def _load():
    global _loaded, _meta
    if _loaded:
        return True
    try:
        import xgboost as xgb
    except ImportError:
        return False
    meta_p = DATA / "xgb_meta.json"
    if not meta_p.exists():
        return False
    _meta = json.loads(meta_p.read_text())
    for city in _meta.get("cities", []):
        b = DATA / f"xgb_{city}_bias.json"
        s = DATA / f"xgb_{city}_std.json"
        if b.exists() and s.exists():
            bm = xgb.XGBRegressor(); bm.load_model(str(b))
            sm = xgb.XGBRegressor(); sm.load_model(str(s))
            _bias_per_city[city] = bm
            _std_per_city[city] = sm
    _loaded = True
    return bool(_bias_per_city)


def _history_for(city: str) -> dict[str, dict]:
    """Return {YYYY-MM-DD: {actual_high, error}} for the given city,
    so we can compute persistence features at inference time."""
    if city in _history_cache:
        return _history_cache[city]
    p = DATA / "forecast_vs_actual.csv"
    out: dict[str, dict] = {}
    if p.exists():
        with p.open() as f:
            for row in csv.DictReader(f):
                if row.get("city") != city:
                    continue
                d = row.get("date", "")[:10]
                try:
                    out[d] = {
                        "actual_high": float(row["actual_high"]),
                        "error": float(row["error"]),
                    }
                except Exception:
                    continue
    _history_cache[city] = out
    return out


def correct(ensemble_mean: float, ensemble_spread: float,
            city_code: str, when_iso: str,
            n_models: int = 5) -> tuple[float, float]:
    """Return (corrected_forecast, predicted_std)."""
    if not _load():
        return ensemble_mean, max(2.0, ensemble_spread)
    bias_model = _bias_per_city.get(city_code)
    std_model = _std_per_city.get(city_code)
    if not bias_model or not std_model:
        return ensemble_mean, max(2.0, ensemble_spread)

    try:
        d = date.fromisoformat(when_iso)
    except Exception:
        return ensemble_mean, max(2.0, ensemble_spread)
    doy = d.timetuple().tm_yday

    hist = _history_for(city_code)
    prev_actual = hist.get((d - timedelta(days=1)).isoformat(), {}).get("actual_high")
    prev_error = hist.get((d - timedelta(days=1)).isoformat(), {}).get("error")
    prev_2_actual = hist.get((d - timedelta(days=2)).isoformat(), {}).get("actual_high")
    if prev_actual is None or prev_error is None or prev_2_actual is None:
        # fallback: use ensemble_mean as prev_actual proxy
        prev_actual = ensemble_mean
        prev_error = 0.0
        prev_2_actual = ensemble_mean

    row = {
        "forecast_high": ensemble_mean,
        "ensemble_spread": ensemble_spread,
        "n_models": n_models,
        "doy_sin": math.sin(2 * math.pi * doy / 365.25),
        "doy_cos": math.cos(2 * math.pi * doy / 365.25),
        "prev_actual": prev_actual,
        "prev_error": prev_error,
        "actual_delta_yesterday": prev_actual - prev_2_actual,
    }
    feat_cols = _meta["feature_cols"]
    X = np.array([[row[k] for k in feat_cols]])
    bias = float(bias_model.predict(X)[0])
    std = float(std_model.predict(X)[0])
    corrected = ensemble_mean - bias
    return corrected, max(1.0, std)

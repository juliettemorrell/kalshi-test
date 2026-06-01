"""XGBoost inference: given ensemble + features, return bias-corrected
forecast and predicted std. Used at trade time to refine the model
input before the empirical CDF lookup."""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

_bias = None
_std = None
_meta = None


def _load():
    global _bias, _std, _meta
    if _bias is not None:
        return True
    try:
        import xgboost as xgb
    except ImportError:
        return False
    meta_p = DATA / "xgb_meta.json"
    if not meta_p.exists():
        return False
    _meta = json.loads(meta_p.read_text())
    _bias = xgb.XGBRegressor()
    _bias.load_model(str(DATA / "xgb_bias.json"))
    _std = xgb.XGBRegressor()
    _std.load_model(str(DATA / "xgb_std.json"))
    return True


def correct(ensemble_mean: float, ensemble_spread: float,
            city_code: str, when_iso: str,
            n_models: int = 2) -> tuple[float, float]:
    """Return (corrected_mean, predicted_std). Falls back to identity if
    no model is available."""
    if not _load():
        return ensemble_mean, max(2.0, ensemble_spread)
    cities = _meta["cities"]
    feat_cols = _meta["feature_cols"]
    try:
        d = date.fromisoformat(when_iso)
        doy = d.timetuple().tm_yday
    except Exception:
        doy = 180
    row = {
        "forecast_high": ensemble_mean,
        "ensemble_spread": ensemble_spread,
        "n_models": n_models,
        "doy_sin": math.sin(2 * math.pi * doy / 365.25),
        "doy_cos": math.cos(2 * math.pi * doy / 365.25),
    }
    for c in cities:
        row[f"city_{c}"] = 1 if c == city_code else 0
    X = np.array([[row[k] for k in feat_cols]])
    bias = float(_bias.predict(X)[0])
    std = float(_std.predict(X)[0])
    # ensemble_mean is the FORECAST; error = forecast - actual.
    # corrected_actual_mean = ensemble_mean - predicted_bias
    corrected = ensemble_mean - bias
    return corrected, max(1.5, std)

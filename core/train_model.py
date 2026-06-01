"""Train an XGBoost model to predict the day's high temperature error
from features available at trade time.

Features (X):
  - ensemble_mean (F)
  - ensemble_spread (F): disagreement between GFS and ECMWF
  - day_of_year sin/cos: seasonality
  - city one-hot
  - n_models in ensemble

Target (y):
  - actual_high - ensemble_mean   (i.e. the signed error in F)

We then convert XGB output to a calibrated distribution by training a
second pass that learns the error standard deviation conditional on the
features. At inference: actual_high ~ N(ensemble + predicted_bias,
predicted_std).

Output: data/xgb_model.json + data/xgb_meta.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CITIES = ["NY", "CHI", "LAX", "MIA", "AUS"]


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["doy"] = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * df["doy"] / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * df["doy"] / 365.25)
    for c in CITIES:
        df[f"city_{c}"] = (df["city"] == c).astype(int)
    df["ensemble_spread"] = df.get("ensemble_spread", 0).fillna(0)
    df["n_models"] = df.get("n_models", 2).fillna(2)
    return df


def main():
    try:
        import xgboost as xgb
    except ImportError:
        print("xgboost not installed; skipping training")
        return

    csv_path = DATA / "forecast_vs_actual.csv"
    if not csv_path.exists():
        print(f"no training data at {csv_path}"); return

    df = pd.read_csv(csv_path)
    df = make_features(df)

    feat_cols = (["forecast_high", "ensemble_spread", "n_models",
                  "doy_sin", "doy_cos"]
                 + [f"city_{c}" for c in CITIES])
    X = df[feat_cols].to_numpy()
    y = df["error"].to_numpy().astype(float)   # signed error in F

    # train / val split: last 90 days = val
    n = len(df)
    val_n = min(450, max(60, n // 10))
    X_tr, X_val = X[:-val_n], X[-val_n:]
    y_tr, y_val = y[:-val_n], y[-val_n:]

    print(f"training on {len(X_tr)} rows, validating on {len(X_val)}", flush=True)

    # Stage 1: predict the bias (mean error)
    bias_model = xgb.XGBRegressor(
        n_estimators=400, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, min_child_weight=3,
        random_state=42, n_jobs=2, objective="reg:squarederror",
        early_stopping_rounds=30,
    )
    bias_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)

    # Compute residuals after bias prediction; train abs-residual model
    # as a proxy for conditional standard deviation
    res_tr = y_tr - bias_model.predict(X_tr)
    abs_res_tr = np.abs(res_tr)
    res_val = y_val - bias_model.predict(X_val)
    abs_res_val = np.abs(res_val)

    std_model = xgb.XGBRegressor(
        n_estimators=400, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, min_child_weight=3,
        random_state=42, n_jobs=2, objective="reg:squarederror",
        early_stopping_rounds=30,
    )
    std_model.fit(X_tr, abs_res_tr, eval_set=[(X_val, abs_res_val)], verbose=False)

    # Eval
    bias_pred = bias_model.predict(X_val)
    std_pred = std_model.predict(X_val)
    mae_val = float(np.mean(np.abs(y_val - bias_pred)))
    naive_mae = float(np.mean(np.abs(y_val)))
    print(f"validation MAE: {mae_val:.3f}F (naive 'no correction': {naive_mae:.3f}F)",
          flush=True)

    bias_model.save_model(str(DATA / "xgb_bias.json"))
    std_model.save_model(str(DATA / "xgb_std.json"))
    meta = {
        "feature_cols": feat_cols,
        "cities": CITIES,
        "n_train": len(X_tr),
        "n_val": len(X_val),
        "val_mae": mae_val,
        "naive_mae": naive_mae,
    }
    (DATA / "xgb_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"saved xgb_bias.json + xgb_std.json + xgb_meta.json", flush=True)


if __name__ == "__main__":
    main()

"""Train per-city XGBoost models for bias + std prediction.

Adds persistence features (yesterday's actual, yesterday's error) which
are very predictive of today's outcome.

Saves data/xgb_<CITY>_bias.json, xgb_<CITY>_std.json, xgb_meta.json
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
    df.sort_values(["city", "date"], inplace=True)
    df["doy"] = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * df["doy"] / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * df["doy"] / 365.25)
    # persistence features per city
    df["prev_actual"] = df.groupby("city")["actual_high"].shift(1)
    df["prev_error"] = df.groupby("city")["error"].shift(1)
    df["prev_2_actual"] = df.groupby("city")["actual_high"].shift(2)
    df["actual_delta_yesterday"] = df["prev_actual"] - df["prev_2_actual"]
    df["ensemble_spread"] = df.get("ensemble_spread", 0).fillna(0)
    df["n_models"] = df.get("n_models", 2).fillna(2)
    return df.dropna(subset=["prev_actual", "prev_error", "prev_2_actual"])


FEATURE_COLS = ["forecast_high", "ensemble_spread", "n_models",
                "doy_sin", "doy_cos",
                "prev_actual", "prev_error", "actual_delta_yesterday"]


def train_one_city(df_city: pd.DataFrame, xgb) -> tuple[object, object, dict]:
    X = df_city[FEATURE_COLS].to_numpy()
    y = df_city["error"].to_numpy().astype(float)
    n = len(X)
    val_n = min(80, max(30, n // 8))
    X_tr, X_val = X[:-val_n], X[-val_n:]
    y_tr, y_val = y[:-val_n], y[-val_n:]

    bias_model = xgb.XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, min_child_weight=3,
        random_state=42, n_jobs=2, objective="reg:squarederror",
        early_stopping_rounds=25,
    )
    bias_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
    res_tr = np.abs(y_tr - bias_model.predict(X_tr))
    res_val = np.abs(y_val - bias_model.predict(X_val))
    std_model = xgb.XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, min_child_weight=3,
        random_state=42, n_jobs=2, objective="reg:squarederror",
        early_stopping_rounds=25,
    )
    std_model.fit(X_tr, res_tr, eval_set=[(X_val, res_val)], verbose=False)

    mae_val = float(np.mean(np.abs(y_val - bias_model.predict(X_val))))
    naive_mae = float(np.mean(np.abs(y_val)))
    return bias_model, std_model, {
        "n_train": len(X_tr), "n_val": len(X_val),
        "val_mae": round(mae_val, 3), "naive_mae": round(naive_mae, 3),
        "improvement_pct": round((naive_mae - mae_val) / naive_mae * 100, 1),
    }


def main():
    try:
        import xgboost as xgb
    except ImportError:
        print("xgboost not installed; skipping training"); return

    csv_path = DATA / "forecast_vs_actual.csv"
    if not csv_path.exists():
        print(f"no training data at {csv_path}"); return

    df = pd.read_csv(csv_path)
    df = make_features(df)
    print(f"rows after feature engineering: {len(df)}", flush=True)

    meta = {"feature_cols": FEATURE_COLS, "cities": CITIES, "per_city": {}}
    for city in CITIES:
        sub = df[df["city"] == city]
        if len(sub) < 100:
            print(f"  {city}: only {len(sub)} rows, skipping")
            continue
        bias, std, stats = train_one_city(sub, xgb)
        bias.save_model(str(DATA / f"xgb_{city}_bias.json"))
        std.save_model(str(DATA / f"xgb_{city}_std.json"))
        meta["per_city"][city] = stats
        print(f"  {city}: MAE {stats['val_mae']:.2f}F "
              f"(naive {stats['naive_mae']:.2f}F, "
              f"-{stats['improvement_pct']}%)", flush=True)

    (DATA / "xgb_meta.json").write_text(json.dumps(meta, indent=2))
    print("saved per-city models + meta", flush=True)


if __name__ == "__main__":
    main()

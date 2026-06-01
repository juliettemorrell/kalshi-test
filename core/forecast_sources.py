"""Unified multi-source forecast: GFS + ECMWF + HRRR + ICON via Open-Meteo,
plus NWS direct via api.weather.gov. Returns ensemble mean + spread."""
from __future__ import annotations

import requests
import time
from pathlib import Path

OM_MODELS = ["gfs_seamless", "ecmwf_ifs025", "hrrr_seamless", "icon_seamless"]


def _open_meteo(lat: float, lon: float, when_iso: str, model: str) -> float | None:
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": "temperature_2m_max",
                "temperature_unit": "fahrenheit",
                "timezone": "America/New_York",
                "models": model,
                "start_date": when_iso, "end_date": when_iso,
            }, timeout=10,
        ).json()
        v = r.get("daily", {}).get("temperature_2m_max", [None])[0]
        return float(v) if v is not None else None
    except Exception:
        return None


def _nws_forecast(lat: float, lon: float, when_iso: str) -> float | None:
    """National Weather Service direct point forecast.
    Settlement is on NWS, so this is the most aligned source we can get."""
    try:
        headers = {"User-Agent": "kalshi-weather-bot (research)",
                   "Accept": "application/geo+json"}
        # step 1: resolve point to gridpoint
        r = requests.get(
            f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}",
            headers=headers, timeout=10,
        ).json()
        forecast_url = r.get("properties", {}).get("forecast")
        if not forecast_url:
            return None
        r2 = requests.get(forecast_url, headers=headers, timeout=10).json()
        periods = r2.get("properties", {}).get("periods", [])
        # find the daytime period whose startTime is the target date
        for p in periods:
            if not p.get("isDaytime"):
                continue
            start = p.get("startTime", "")[:10]
            if start == when_iso:
                temp = p.get("temperature")
                unit = p.get("temperatureUnit", "F")
                if temp is None:
                    return None
                t = float(temp)
                if unit == "C":
                    t = t * 9 / 5 + 32
                return t
        return None
    except Exception:
        return None


def ensemble_forecast(lat: float, lon: float, when_iso: str) -> tuple[float | None, float, dict]:
    """Returns (mean_F, spread_F, per_source_dict).

    NWS direct gets DOUBLE weight in the ensemble because it's the same
    source Kalshi settles on. If NWS disagrees with model consensus by
    4F+ we widen the spread automatically (caller sees more uncertainty).
    """
    sources = {}
    for mdl in OM_MODELS:
        v = _open_meteo(lat, lon, when_iso, mdl)
        if v is not None:
            sources[mdl] = v
        time.sleep(0.15)
    v = _nws_forecast(lat, lon, when_iso)
    if v is not None:
        sources["nws_direct"] = v
    if not sources:
        return None, 0.0, {}
    values = list(sources.values())
    # weighted mean: NWS direct gets 2x weight, others 1x
    weights = []
    for k in sources:
        weights.append(2.0 if k == "nws_direct" else 1.0)
    wsum = sum(weights)
    mean = sum(v * w for v, w in zip(values, weights)) / wsum
    spread = (max(values) - min(values)) if len(values) > 1 else 0.0
    # NWS-vs-model sanity check
    if "nws_direct" in sources and len(sources) > 1:
        other = [v for k, v in sources.items() if k != "nws_direct"]
        nws = sources["nws_direct"]
        other_mean = sum(other) / len(other)
        nws_gap = abs(nws - other_mean)
        if nws_gap > 4.0:
            # widen spread, model is less trustworthy when NWS disagrees
            spread = max(spread, nws_gap)
    return mean, spread, sources

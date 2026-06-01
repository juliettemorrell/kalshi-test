"""Detect extreme-weather patterns and widen our model uncertainty
accordingly. During heat domes / cold snaps / strong fronts, the
variance of forecast errors is much higher than baseline."""
from __future__ import annotations


def variance_multiplier(forecast_high_f: float, ensemble_spread_f: float,
                         month: int, city_code: str) -> float:
    """Return a multiplier for the predicted std. 1.0 = baseline.
    > 1.0 means we should widen our uncertainty. Conservative default 1.0
    when nothing notable is detected."""
    mult = 1.0
    # Ensemble disagreement: large spread => more uncertainty
    if ensemble_spread_f > 4:
        mult *= 1.4
    elif ensemble_spread_f > 2.5:
        mult *= 1.2
    # Extreme temperatures: outside seasonal norm => more variance
    # rough thresholds by city/month (could be tuned with history)
    extreme_hot = {
        "NY": [(6, 92), (7, 95), (8, 95), (9, 92)],
        "CHI": [(6, 92), (7, 95), (8, 95)],
        "LAX": [(7, 92), (8, 92), (9, 95)],
        "MIA": [(6, 95), (7, 95), (8, 95), (9, 94)],
        "AUS": [(6, 100), (7, 102), (8, 102), (9, 100)],
    }.get(city_code, [])
    for m, thresh in extreme_hot:
        if m == month and forecast_high_f >= thresh:
            mult *= 1.3
            break
    extreme_cold = {
        "NY": [(12, 20), (1, 15), (2, 18)],
        "CHI": [(12, 10), (1, 5), (2, 10)],
    }.get(city_code, [])
    for m, thresh in extreme_cold:
        if m == month and forecast_high_f <= thresh:
            mult *= 1.4
            break
    return mult

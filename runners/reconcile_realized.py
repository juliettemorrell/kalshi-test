"""Run alongside the logger to backfill realized highs once they're available.

For each snapshot row missing 'realized_high', look up the actual high from
Open-Meteo's archive API (which has a ~2-day lag) and update in place.
"""
from __future__ import annotations

import csv
import time
from datetime import date, timedelta
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOG = DATA / "phase0_log.csv"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)


def realized(lat, lon, day):
    try:
        r = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat, "longitude": lon,
                "start_date": day, "end_date": day,
                "daily": "temperature_2m_max",
                "temperature_unit": "fahrenheit",
                "timezone": "America/New_York",
            },
            timeout=10,
        ).json()
        return r["daily"]["temperature_2m_max"][0]
    except Exception:
        return None


def main():
    if not LOG.exists():
        print("no log yet"); return
    rows = list(csv.DictReader(LOG.open()))
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    if "realized_high" not in fieldnames:
        fieldnames.append("realized_high")
    cutoff = date.today() - timedelta(days=2)
    seen_lookup: dict[tuple, float] = {}
    n_filled = 0
    for r in rows:
        if r.get("realized_high"):
            continue
        try:
            sd = date.fromisoformat(r["settle_date"])
        except Exception:
            continue
        if sd > cutoff:
            continue  # too recent, ERA5 not yet available
        key = (r["city"], r["settle_date"])
        if key in seen_lookup:
            val = seen_lookup[key]
        else:
            city = CFG["cities"][r["city"]]
            val = realized(city["lat"], city["lon"], r["settle_date"])
            seen_lookup[key] = val
            time.sleep(0.1)
        if val is not None:
            r["realized_high"] = round(val, 2)
            n_filled += 1
    with LOG.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"filled realized_high on {n_filled} rows")


if __name__ == "__main__":
    main()

"""Real-time NWS station observations. Used by midday refresh to check
whether the current day is already pacing way above/below the forecast."""
from __future__ import annotations

from datetime import datetime, timezone

import requests


def current_obs(station_id: str) -> dict | None:
    """Latest observation from a NWS station (e.g. 'KNYC', 'KORD').
    Returns {'temp_f', 'observed_at', 'dewpoint_f'} or None."""
    try:
        r = requests.get(
            f"https://api.weather.gov/stations/{station_id}/observations/latest",
            headers={"User-Agent": "kalshi-weather-bot (research)",
                     "Accept": "application/geo+json"},
            timeout=10,
        ).json()
        props = r.get("properties", {})
        t_c = (props.get("temperature") or {}).get("value")
        d_c = (props.get("dewpoint") or {}).get("value")
        when = props.get("timestamp")
        if t_c is None:
            return None
        t_f = t_c * 9 / 5 + 32
        d_f = d_c * 9 / 5 + 32 if d_c is not None else None
        return {"temp_f": round(t_f, 1),
                "dewpoint_f": round(d_f, 1) if d_f else None,
                "observed_at": when}
    except Exception:
        return None


def today_max_so_far(station_id: str) -> float | None:
    """Highest temp observed so far today at this station. Useful for
    saying 'we're already at 80F at 10am, anything below that is dead.'"""
    try:
        # last 24h of observations
        r = requests.get(
            f"https://api.weather.gov/stations/{station_id}/observations",
            params={"limit": 50},
            headers={"User-Agent": "kalshi-weather-bot (research)",
                     "Accept": "application/geo+json"},
            timeout=10,
        ).json()
        features = r.get("features", [])
        if not features:
            return None
        # find observations from today (local-ish, use UTC since fine grain)
        today_utc = datetime.now(timezone.utc).date()
        # NWS observations include local-ish noon by default; we filter
        # observations whose timestamp's local date matches roughly today
        highest = None
        for f in features:
            props = f.get("properties", {})
            ts = props.get("timestamp", "")
            t_c = (props.get("temperature") or {}).get("value")
            if t_c is None or not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                continue
            # use UTC date for the comparison; OK approximation for our use
            if dt.date() < today_utc:
                continue
            t_f = t_c * 9 / 5 + 32
            if highest is None or t_f > highest:
                highest = t_f
        return round(highest, 1) if highest is not None else None
    except Exception:
        return None

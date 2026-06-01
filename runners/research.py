"""Daily Kalshi socials research using Claude API. Robust universe scan.

Strategy:
1. Pull /events for EVERY category (deep pagination to surface near-term ones)
2. For each event, hydrate its markets with prices and volume
3. Filter: <=60d settle, vol > $50 (excludes weather + multi-venture parlay)
4. Sort by volume; pass top ~80 markets WITH full context to Claude
5. Claude scores each, picks 0-3, writes log

Env: ANTHROPIC_API_KEY (GitHub secret)
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOG = DATA / "socials_research_log.md"

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
UA = "research/2.0"
MODEL = "claude-sonnet-4-6"
ANTHROPIC = "https://api.anthropic.com/v1/messages"

CATS = ["Entertainment","Sports","Financials","Economics","Politics",
        "Elections","Companies","Social","World","Health",
        "Science and Technology","Transportation"]
MAX_SETTLE_DAYS = 60
MIN_VOLUME = 50           # $50 of contracts traded minimum
PAGES_PER_CAT = 5         # paginate to find non-default-ordered events


def kget(url, params=None, tries=3):
    for i in range(tries):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=12)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(0.5 + i)
    return {}


def days_until(iso):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (dt - datetime.now(timezone.utc)).total_seconds() / 86400
    except Exception:
        return None


def collect_universe():
    """Pull events from each category, deeply page, dedupe."""
    seen_events = {}
    for cat in CATS:
        cursor = None
        for _ in range(PAGES_PER_CAT):
            params = {"status": "open", "limit": 200, "category": cat}
            if cursor:
                params["cursor"] = cursor
            d = kget(f"{KALSHI}/events", params)
            evs = d.get("events", [])
            if not evs:
                break
            for ev in evs:
                et = ev.get("event_ticker")
                if not et or et in seen_events:
                    continue
                seen_events[et] = ev
            cursor = d.get("cursor")
            if not cursor:
                break
    return seen_events


def hydrate_markets(events):
    """For each event, pull markets, keep only liquid + near-term + sane."""
    keep = []
    n = len(events)
    for i, (et, ev) in enumerate(events.items()):
        d = kget(f"{KALSHI}/markets", {"event_ticker": et, "limit": 30})
        for m in d.get("markets", []):
            tic = m.get("ticker", "")
            # skip weather (already trading) and exchange parlay garbage
            if "KXHIGH" in tic or "KXLOW" in tic or "KXMVE" in tic:
                continue
            try:
                vol = float(m.get("volume_fp") or 0)
            except (TypeError, ValueError):
                vol = 0
            if vol < MIN_VOLUME:
                continue
            dc = days_until(m.get("close_time"))
            if dc is None or dc <= 0 or dc > MAX_SETTLE_DAYS:
                continue
            ask = m.get("yes_ask_dollars")
            bid = m.get("yes_bid_dollars")
            try:
                askf = float(ask) if ask is not None else None
            except (TypeError, ValueError):
                askf = None
            if askf is None or askf <= 0.005 or askf >= 0.995:
                continue
            keep.append({
                "category": ev.get("category"),
                "event_title": (ev.get("title") or "")[:90],
                "event_ticker": et,
                "market_ticker": tic,
                "sub": (m.get("subtitle") or m.get("yes_sub_title") or "")[:60],
                "ask": ask, "bid": bid,
                "last": m.get("last_price_dollars"),
                "vol": round(vol, 0),
                "oi": float(m.get("open_interest_fp") or 0),
                "days_to_close": round(dc, 1),
            })
        if (i + 1) % 25 == 0:
            print(f"  hydrated {i+1}/{n} events, {len(keep)} markets so far",
                  flush=True)
    return keep


def call_claude(prompt: str) -> str:
    key = os.environ["ANTHROPIC_API_KEY"]
    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(
        ANTHROPIC,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body, timeout=180,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def main():
    today = datetime.now(timezone.utc).date().isoformat()
    print(f"=== research run {today} ===", flush=True)

    print("collecting universe...", flush=True)
    events = collect_universe()
    print(f"  events: {len(events)}", flush=True)

    print("hydrating markets...", flush=True)
    markets = hydrate_markets(events)
    print(f"  liquid near-term markets: {len(markets)}", flush=True)

    # sort by volume * recency (recent + liquid = best signal)
    markets.sort(key=lambda m: -m["vol"])
    top = markets[:80]

    if not top:
        text = (f"## {today}\n\n**No actionable markets today.**\n\n"
                f"Deep scan of {len(events)} open events across {len(CATS)} "
                f"categories yielded zero non-weather markets meeting our "
                f"thresholds (vol >= {MIN_VOLUME}, settle within "
                f"{MAX_SETTLE_DAYS}d, ask between 1c-99c). The Kalshi "
                f"universe outside weather is genuinely thin right now.\n\n---\n")
    else:
        # build compact table for Claude
        lines = []
        for m in top:
            lines.append(
                f"{m['days_to_close']:>4.1f}d | "
                f"vol=${int(m['vol']):>6d} | "
                f"bid={m['bid']} ask={m['ask']} | "
                f"{m['category'][:13]:13} | "
                f"{m['market_ticker'][:42]:42} | "
                f"{m['event_title'][:70]}"
            )
        table = "\n".join(lines)

        prompt = f"""You are doing real Kalshi research for a small ($50-100)
retail bot. Date: {today}. The weather bot trades automatically. Your
job: pick 0-3 specific non-weather markets that are catalyst-driven and
mispriced.

Below are the TOP {len(top)} LIQUID, NEAR-TERM (<={MAX_SETTLE_DAYS}d
settle), NON-WEATHER markets currently open on Kalshi. They've already
been filtered for volume and excluded multi-venture parlays. This is
the real actionable universe.

```
days | vol      | bid/ask    | category    | ticker                              | event title
{table}
```

For your picks:
1. Identify a SPECIFIC public news catalyst that explains why you think
   the market is mispriced (cite the news).
2. Estimate fair probability and edge in cents.
3. Confidence: high/medium/low.

Skip sports games (sportsbook arb dominates retail edge).
Skip markets you can't tell a real story about.
Honest "no actionable picks" is OK; specify why.

Output a markdown section starting with `## {today}` and ending with
`---`. Keep under 500 words.
"""
        print("calling Claude...", flush=True)
        text = call_claude(prompt)

    LOG.parent.mkdir(exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Kalshi Socials Research Log\n\n"
                       "Auto-generated daily by GitHub Actions.\n\n---\n\n")
    with LOG.open("a") as f:
        f.write("\n" + text.strip() + "\n\n")
    print(f"appended to {LOG}", flush=True)
    print(text[:800], flush=True)


if __name__ == "__main__":
    main()

"""Daily socials research using the Claude API.

Runs in GitHub Actions. No laptop dependency. Pulls open Kalshi markets,
asks Claude to find catalyst-driven opportunities and append findings
to data/socials_research_log.md.

Env vars:
  ANTHROPIC_API_KEY - secret added in GitHub repo settings
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

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
UA = "research/1.0"

# Anthropic API
MODEL = "claude-sonnet-4-6"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def kget(url, params=None):
    for _ in range(3):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return {}


def gather_market_universe(max_events=80):
    """Return a compact list of currently-open near-term non-weather events."""
    universe = []
    seen = set()
    cats = ["Entertainment", "Sports", "Financials", "Economics",
            "Politics", "Companies", "Social", "World", "Health"]
    for cat in cats:
        d = kget(f"{KALSHI_BASE}/events",
                 {"status": "open", "limit": 50, "category": cat})
        for ev in d.get("events", []):
            et = ev.get("event_ticker")
            if not et or et in seen:
                continue
            seen.add(et)
            universe.append({
                "category": ev.get("category"),
                "event_ticker": et,
                "title": (ev.get("title") or "")[:120],
            })
            if len(universe) >= max_events:
                return universe
    return universe


def fetch_market_prices(event_ticker):
    """Return list of markets with current prices for shortlisting."""
    d = kget(f"{KALSHI_BASE}/markets",
             {"event_ticker": event_ticker, "limit": 20})
    out = []
    for m in d.get("markets", []):
        out.append({
            "ticker": m.get("ticker"),
            "sub": (m.get("yes_sub_title") or m.get("subtitle") or "")[:60],
            "yes_bid": m.get("yes_bid_dollars"),
            "yes_ask": m.get("yes_ask_dollars"),
            "last": m.get("last_price_dollars"),
            "vol": m.get("volume_fp"),
            "close": m.get("close_time"),
        })
    return out


def call_claude(prompt: str) -> str:
    key = os.environ["ANTHROPIC_API_KEY"]
    body = {
        "model": MODEL,
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(
        ANTHROPIC_URL,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body, timeout=120,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def main():
    universe = gather_market_universe()
    print(f"gathered {len(universe)} near-term events", flush=True)

    today = datetime.now(timezone.utc).date().isoformat()
    universe_str = "\n".join(
        f"- {u['category']:13} | {u['event_ticker']:55} | {u['title']}"
        for u in universe[:60]
    )

    prompt = f"""You are doing daily Kalshi research for a $50 retail bot.
The weather strategy is already running automatically. Your job is to
find 0-3 non-weather markets where a public news catalyst + tradeable
near-term price line up.

Today's date: {today}

Open events (category, ticker, title):
{universe_str}

Rules:
1. Skip anything settling more than 60 days out.
2. Prefer markets with public news catalysts you can name specifically.
3. Skip sports games (sportsbook arb dominates retail edge).
4. Skip ultra-long-tail political speculation.
5. If nothing looks tradeable, say so honestly.

Output a concise markdown section starting with `## {today}` and ending
with `---`. For each pick include: market_ticker, current_price_estimate,
your_estimated_prob, edge, confidence (low/med/high), specific catalyst.
Keep it under 400 words. If no picks, state why in 1 paragraph.
"""

    print("calling Claude...", flush=True)
    text = call_claude(prompt)
    print(text[:500], flush=True)
    print("...", flush=True)

    # append to log
    LOG.parent.mkdir(exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Kalshi Socials Research Log\n\n"
                       "Auto-generated daily by GitHub Actions.\n\n---\n\n")
    with LOG.open("a") as f:
        f.write("\n" + text.strip() + "\n\n---\n")
    print(f"appended to {LOG}", flush=True)


if __name__ == "__main__":
    main()

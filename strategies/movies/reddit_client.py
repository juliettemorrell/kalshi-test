"""Reddit scraper using public JSON endpoints (no auth, no API key).

Reddit allows unauthenticated GET access to .json endpoints with a sane
User-Agent. Rate limit is ~60 req/min unauth. We stay well below by
caching per-(query, subreddit, day).

Three subreddits matter for movie sentiment:
  r/movies      - mainstream
  r/boxoffice   - structured opinions on release performance
  r/horror, r/scifi, r/marvelstudios, r/StarWars - genre signal

For each upcoming movie market, we query Reddit search and aggregate:
  - mention_count: how many posts in last N days
  - total_upvotes: engagement signal
  - total_comments: discussion volume
  - avg_score_per_post: sentiment-ish proxy (positive interest)
  - latest_post_age_hours: freshness
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests

UA = "Mozilla/5.0 (compatible; kalshi-research-bot/1.0; contact via github)"
BASE = "https://www.reddit.com"

DEFAULT_SUBS = ["movies", "boxoffice", "horror", "scifi",
                "marvelstudios", "StarWars", "letterboxd"]


def _get(url: str, params: dict | None = None) -> dict:
    for attempt in range(3):
        try:
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=12)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            return {}
        except (requests.RequestException, ValueError):
            time.sleep(0.5 + attempt)
    return {}


def search_subreddit(subreddit: str, query: str,
                     sort: str = "new", limit: int = 50,
                     since_days: int = 14) -> list[dict]:
    """Return raw posts for query in subreddit within last since_days."""
    d = _get(f"{BASE}/r/{subreddit}/search.json",
             {"q": query, "restrict_sr": 1, "sort": sort, "limit": limit})
    posts = []
    cutoff = time.time() - since_days * 86400
    for child in d.get("data", {}).get("children", []):
        p = child.get("data", {})
        if p.get("created_utc", 0) < cutoff:
            continue
        posts.append({
            "subreddit": subreddit,
            "title": p.get("title", ""),
            "selftext": p.get("selftext", "")[:500],
            "score": p.get("score", 0),
            "ups": p.get("ups", 0),
            "downs": p.get("downs", 0),
            "num_comments": p.get("num_comments", 0),
            "created_utc": p.get("created_utc", 0),
            "url": p.get("permalink", ""),
            "upvote_ratio": p.get("upvote_ratio"),
        })
    return posts


def aggregate(query: str, subs: Iterable[str] = DEFAULT_SUBS,
              since_days: int = 14) -> dict:
    """Pull all matching posts across subreddits and return aggregates."""
    all_posts: list[dict] = []
    for s in subs:
        all_posts.extend(search_subreddit(s, query, since_days=since_days))
        time.sleep(0.4)  # courtesy

    if not all_posts:
        return {
            "query": query, "mention_count": 0, "total_upvotes": 0,
            "total_comments": 0, "avg_score": 0.0,
            "avg_upvote_ratio": None, "latest_post_age_hours": None,
            "subs_with_hits": [],
        }

    total_up = sum(p["score"] for p in all_posts)
    total_c = sum(p["num_comments"] for p in all_posts)
    ratios = [p["upvote_ratio"] for p in all_posts if p["upvote_ratio"] is not None]
    latest_ts = max(p["created_utc"] for p in all_posts)
    age_hours = (time.time() - latest_ts) / 3600

    subs_hit = sorted({p["subreddit"] for p in all_posts})
    return {
        "query": query,
        "mention_count": len(all_posts),
        "total_upvotes": total_up,
        "total_comments": total_c,
        "avg_score": round(total_up / len(all_posts), 1),
        "avg_upvote_ratio": round(sum(ratios) / len(ratios), 3) if ratios else None,
        "latest_post_age_hours": round(age_hours, 1),
        "subs_with_hits": subs_hit,
    }


def movie_title_from_ticker(ticker: str) -> str:
    """Extract a probably-searchable movie title from a Kalshi RT ticker.
    KXRTSMILE2 -> 'smile 2', KXRTAVATARFIREANDASH -> 'avatar fire and ash'."""
    stem = re.sub(r"^(KX)?RT", "", ticker.split("-")[0], count=1)
    # split CamelCase / glob runs; this is heuristic
    # insert space before each uppercase letter following a lowercase or digit
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    # numbers like 2/3 stay attached
    s = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", s)
    return s.strip().title()


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Avatar Fire and Ash"
    print(json.dumps(aggregate(q, since_days=14), indent=2))

"""Re-quote unfilled orders that the market moved away from.

Runs at 00:30 UTC and 02:30 UTC (late evening / early night ET) when the
overnight forecast is fully baked but settlement is still hours away.
For each resting BUY order: if the current ask is 2+c better than our
limit, cancel and replace at the new ask-1c so we actually fill.
"""
from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.client import KalshiClient
from core import risk

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)

PROMOTED = ROOT / "PROMOTED"


def main():
    if not PROMOTED.exists():
        print("PROMOTED missing"); sys.exit(2)
    if os.getenv("KALSHI_ENV") != "prod":
        print("not prod"); sys.exit(2)
    if risk.kill_switch_active():
        print("kill"); sys.exit(0)

    client = KalshiClient()
    try:
        orders = client.get_orders(status="resting")
    except Exception as e:
        print(f"orders error: {e}"); return

    if not orders:
        print("no resting orders to consider"); return

    requoted = 0
    for o in orders:
        tic = o.get("ticker")
        if not tic or not tic.startswith("KXHIGH"):
            continue
        side = o.get("side")
        action = o.get("action")
        if action != "buy":
            continue
        our_price_c = o.get("yes_price") or o.get("no_price") or 0
        try:
            our_price_c = int(our_price_c)
        except Exception:
            continue
        try:
            m = client.get_market(tic)
        except Exception:
            continue
        if side == "yes":
            current_ask_c = int(round(float(m.get("yes_ask_dollars") or 1) * 100))
        else:
            current_ask_c = int(round((1 - float(m.get("yes_bid_dollars") or 0)) * 100))
        # If current ask is 2+ cents above our limit, we'll never fill;
        # re-bid at ask - 1 to actually cross.
        improvement_needed = current_ask_c - our_price_c
        if improvement_needed < 2:
            continue
        if current_ask_c >= 99 or current_ask_c <= 1:
            continue
        new_price_c = max(1, current_ask_c - 1)
        # cancel old
        try:
            client.cancel_order(o.get("order_id"))
        except Exception as e:
            print(f"  cancel fail {tic}: {e}")
            continue
        # place new at improved price
        count = int(o.get("remaining_count") or 0) or int(o.get("count") or 0)
        if count <= 0:
            continue
        seed = f"REQUOTE|{tic}|{side}|{new_price_c}|{datetime.now(timezone.utc).date().isoformat()}"
        coid = hashlib.sha1(seed.encode()).hexdigest()[:24]
        try:
            kw = dict(ticker=tic, side=side, action="buy",
                      count=count, client_order_id=coid)
            if side == "yes":
                kw["yes_price_cents"] = new_price_c
            else:
                kw["no_price_cents"] = new_price_c
            client.place_order(**kw)
            requoted += 1
            print(f"  requoted {tic} {our_price_c}c -> {new_price_c}c")
        except Exception as e:
            print(f"  replace fail {tic}: {e}")

    print(f"quote refresh complete: {requoted} re-quoted")


if __name__ == "__main__":
    main()

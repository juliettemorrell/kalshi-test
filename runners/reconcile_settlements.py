"""Track actual settlement results and accumulate a wins/losses log.

Runs once a day in the morning. Pulls fills history from Kalshi for
yesterday's settled markets, joins to our orders log, and appends to
data/settlement_results.csv.

Also writes data/daily_pnl.md as a running performance dashboard.
"""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.client import KalshiClient

DATA = ROOT / "data"
RESULTS = DATA / "settlement_results.csv"
DASH = DATA / "daily_pnl.md"

FIELDS = ["settle_date", "ticker", "side", "entry_price", "contracts",
          "result", "settle_price", "pnl_dollars", "source_workflow"]


def main():
    if os.getenv("KALSHI_ENV") != "prod":
        print("not prod"); sys.exit(2)

    client = KalshiClient()
    bal = client.get_balance()
    cash = (bal.get("balance", 0) or 0) / 100
    portfolio = (bal.get("portfolio_value", 0) or 0) / 100
    total = cash + portfolio
    print(f"balance: cash=${cash:.2f} positions=${portfolio:.2f} total=${total:.2f}",
          flush=True)
    # Auto-balance health check: warn if total drifts hugely from expected
    expected_baseline = 50.0
    if total < expected_baseline * 0.10:
        print(f"WARN: balance ${total:.2f} below 10% of starting bankroll",
              flush=True)
    if total > expected_baseline * 5:
        print(f"WARN: balance ${total:.2f} above 5x starting bankroll (suspicious?)",
              flush=True)

    # pull settled fills via portfolio/fills
    try:
        d = client.request("GET", "/portfolio/fills",
                           params={"limit": 200})
        fills = d.get("fills", [])
    except Exception as e:
        print(f"fills error: {e}")
        fills = []

    # join fills against existing orders logs by client_order_id (preferred)
    # falling back to ticker for old rows that lacked the COID
    order_source: dict[str, str] = {}
    coid_source: dict[str, str] = {}
    for log in ["live_orders.csv", "midday_actions.csv"]:
        p = DATA / log
        if not p.exists():
            continue
        wf = "live" if log == "live_orders.csv" else "midday"
        with p.open() as f:
            for row in csv.DictReader(f):
                t = row.get("market_ticker") or row.get("ticker")
                if t:
                    order_source[t] = wf
                coid = row.get("client_order_id")
                if coid:
                    coid_source[coid] = wf

    # for each fill, determine if it's settled (yes_price 0 or 1 final)
    new_rows = []
    for fl in fills:
        tic = fl.get("ticker", "")
        if not tic.startswith("KXHIGH"):
            continue
        side = fl.get("side") or fl.get("yes_no", "")
        action = fl.get("action", "")
        if action != "buy":
            continue
        cents = fl.get("yes_price") or fl.get("no_price") or 0
        ct = fl.get("count", 0) or 0
        # check if the market the fill is in is settled
        try:
            mkt = client.get_market(tic)
        except Exception:
            continue
        if mkt.get("status") not in ("settled", "finalized", "expired"):
            continue
        result = mkt.get("result", "")
        # compute PNL: buy YES at p, get $1 if result==yes, else $0
        # buy NO at p, get $1 if result==no, else $0
        entry = float(cents) / 100
        won = ((side == "yes" and result == "yes") or
               (side == "no" and result == "no"))
        pnl_per = (1 - entry) if won else (-entry)
        pnl = round(pnl_per * float(ct), 2)
        fl_coid = fl.get("client_order_id")
        src = coid_source.get(fl_coid) or order_source.get(tic, "unknown")
        new_rows.append({
            "settle_date": (fl.get("created_time", "") or "")[:10],
            "ticker": tic, "side": side,
            "entry_price": round(entry, 3),
            "contracts": int(ct),
            "result": result,
            "settle_price": 1.0 if won else 0.0,
            "pnl_dollars": pnl,
            "source_workflow": src,
        })

    # append non-duplicate (by ticker + side + contracts) rows
    seen = set()
    if RESULTS.exists():
        with RESULTS.open() as f:
            for r in csv.DictReader(f):
                key = (r["ticker"], r["side"], r["contracts"])
                seen.add(key)
    new_file = not RESULTS.exists()
    with RESULTS.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        added = 0
        for r in new_rows:
            key = (r["ticker"], r["side"], str(r["contracts"]))
            if key in seen:
                continue
            w.writerow(r)
            added += 1
    print(f"appended {added} settlement rows", flush=True)

    # rebuild dashboard markdown from full log
    if not RESULTS.exists():
        return
    rows = list(csv.DictReader(RESULTS.open()))
    total_pnl = sum(float(r["pnl_dollars"]) for r in rows)
    wins = sum(1 for r in rows if float(r["pnl_dollars"]) > 0)
    losses = sum(1 for r in rows if float(r["pnl_dollars"]) <= 0)
    by_wf = {}
    by_city = {}
    by_side = {}
    for r in rows:
        wf = r.get("source_workflow", "?")
        by_wf.setdefault(wf, []).append(float(r["pnl_dollars"]))
        # city from ticker prefix
        tic = r.get("ticker", "")
        for c in ["NY","CHI","LAX","MIA","AUS"]:
            if tic.startswith(f"KXHIGH{c}-"):
                by_city.setdefault(c, []).append(float(r["pnl_dollars"]))
                break
        by_side.setdefault(r.get("side", "?"), []).append(float(r["pnl_dollars"]))

    # Brier score (uses entry_price as model probability)
    brier = sum((float(r["entry_price"]) - float(r["settle_price"])) ** 2
                for r in rows) / max(1, len(rows))
    # Drawdown: cumulative pnl curve, max peak-to-trough
    cum = 0.0; peak = 0.0; max_dd = 0.0
    pnl_series = [float(r["pnl_dollars"]) for r in rows]
    for p in pnl_series:
        cum += p
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
    # Sharpe-like (no risk-free): mean / std of per-trade pnl
    if len(pnl_series) > 1:
        import statistics as _st
        mean_p = _st.fmean(pnl_series)
        std_p = _st.pstdev(pnl_series) or 1e-9
        sharpe = mean_p / std_p
    else:
        sharpe = 0.0
    # Reliability bins: entry_price (treated as predicted prob) vs win
    rel_bins = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    rel_rows = []
    for i in range(len(rel_bins)-1):
        lo, hi = rel_bins[i], rel_bins[i+1]
        subset = [r for r in rows
                  if lo <= float(r["entry_price"]) < hi]
        if not subset:
            continue
        actual = sum(float(r["settle_price"]) for r in subset) / len(subset)
        rel_rows.append((round(lo,1), round(hi,1), len(subset),
                         round(actual, 3)))

    today = datetime.now(timezone.utc).date().isoformat()
    lines = [
        "# Kalshi Bot Performance Dashboard",
        "",
        f"_updated {today}_",
        "",
        f"- **Current total worth (cash + positions): ${total:.2f}**",
        f"  - cash: ${cash:.2f}",
        f"  - open positions: ${portfolio:.2f}",
        "",
        "## Settled trades to date",
        "",
        f"- total settled: **{len(rows)}**",
        f"- wins / losses: **{wins} / {losses}**",
        f"- win rate: **{(wins/max(1,len(rows))*100):.1f}%**",
        f"- realized P&L: **${total_pnl:+.2f}**",
        f"- Brier score: **{brier:.4f}** (lower=better)",
        f"- per-trade Sharpe: **{sharpe:.2f}**",
        f"- max drawdown: **${max_dd:.2f}**",
        "",
        "## Reliability (entry_price as predicted prob)",
        "",
        "| pred range | n | mean realized |",
        "|---|---|---|",
    ]
    for lo, hi, n, actual in rel_rows:
        lines.append(f"| {lo}-{hi} | {n} | {actual} |")
    lines.append("")
    lines.append("## By workflow source")
    lines.append("")
    for wf, pnls in sorted(by_wf.items()):
        w = sum(1 for x in pnls if x > 0)
        lines.append(f"- **{wf}**: {len(pnls)} settled, "
                     f"{w}W/{len(pnls)-w}L, ${sum(pnls):+.2f}")
    lines.append("")
    lines.append("## By city")
    lines.append("")
    for c, pnls in sorted(by_city.items()):
        w = sum(1 for x in pnls if x > 0)
        lines.append(f"- **{c}**: {len(pnls)} settled, "
                     f"{w}W/{len(pnls)-w}L, ${sum(pnls):+.2f}")
    lines.append("")
    lines.append("## By side")
    lines.append("")
    for s, pnls in sorted(by_side.items()):
        w = sum(1 for x in pnls if x > 0)
        lines.append(f"- **{s}**: {len(pnls)} settled, "
                     f"{w}W/{len(pnls)-w}L, ${sum(pnls):+.2f}")
    lines.append("")
    # By bracket-distance-from-forecast (extract bracket lo from ticker, but
    # we don't have entry forecast snapshot - so we use entry_price as proxy:
    # entry near 0.5 = ATM bet, near 0.05/0.95 = far OTM)
    by_pricetier = {"deep_otm (<10c)": [], "otm (10-30c)": [],
                    "atm (30-70c)": [], "itm (70-90c)": [],
                    "deep_itm (>90c)": []}
    for r in rows:
        p = float(r["entry_price"])
        if p < 0.10: bucket = "deep_otm (<10c)"
        elif p < 0.30: bucket = "otm (10-30c)"
        elif p < 0.70: bucket = "atm (30-70c)"
        elif p < 0.90: bucket = "itm (70-90c)"
        else: bucket = "deep_itm (>90c)"
        by_pricetier[bucket].append(float(r["pnl_dollars"]))
    lines.append("## By entry-price tier (proxy for bracket distance)")
    lines.append("")
    for tier, pnls in by_pricetier.items():
        if not pnls:
            continue
        w = sum(1 for x in pnls if x > 0)
        lines.append(f"- **{tier}**: {len(pnls)} settled, "
                     f"{w}W/{len(pnls)-w}L, ${sum(pnls):+.2f}")
    lines.append("")
    lines.append("## Recent settlements (last 20)")
    lines.append("")
    for r in rows[-20:]:
        em = "+" if float(r["pnl_dollars"]) > 0 else ""
        lines.append(f"- {r['settle_date']} | {r['ticker'][:40]:40} | "
                     f"{r['side']:3} @ {r['entry_price']} | "
                     f"x{r['contracts']:>3} | result={r['result']} | "
                     f"{em}${r['pnl_dollars']}")
    DASH.write_text("\n".join(lines) + "\n")
    print(f"dashboard -> {DASH}", flush=True)


if __name__ == "__main__":
    main()

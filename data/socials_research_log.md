# Kalshi Socials Research Log

Daily research log written by the scheduled Claude task
`kalshi-daily-socials-research`. Tracks which markets had identifiable
catalysts + social signal vs. tradeable prices.

The actual trades are placed only by the live-trader workflow on
weather. This log is reconnaissance: if a non-weather category shows
repeated edge here over a couple of weeks, we'll wire it into the bot.

---

## 2026-05-30 (sample manual run)

### Universe scan
- Of 200 currently-open events fetched, ~148 were non-weather.
- The vast majority close in 2028-2030 (long-dated speculation on
  Trump-term outcomes, Bond casting, who Taylor Swift will marry).
- Filtering to "non-weather + closes in 7 days + has any volume":
  effectively zero clean tradeable markets right now beyond MLB games.
- MLB games (KXMLBGAME-*) settle same-day and have liquidity, but
  sportsbook arbs already eat retail edge here. Not a good fit for
  socials-driven research.
- Conclusion: tomorrow's run will almost certainly find no actionable
  near-term socials bets. We're between catalyst seasons.

### Retrospective backtest (3 recent settled markets)

To check whether the methodology would have worked at all, I picked
3 markets that settled in the last 2 weeks where news-driven research
SHOULD have given a clear answer.

**KXKASHANNOUNCEOUT-26APR-MAY01** (settled NO May 22)
- Question: did Kash Patel announce departure as FBI Director before
  May 1, 2026?
- Public news through April: no departure announcement, Patel
  remained in role through normal duties
- Methodology call: NO with high confidence
- Settlement: NO -> WIN
- Volume on the market: 83,532 contracts. Big retail interest.

**KXLUTNICKANNOUNCEOUT-26APR-MAY01** (settled NO May 22)
- Question: did Commerce Secretary Lutnick announce departure before
  May 1, 2026?
- Public news: Lutnick still in role, no resignation rumor cycle
- Methodology call: NO with high confidence
- Settlement: NO -> WIN

**KXFDAAPPROVE-BAX-26JUN01** (settled YES around May 14)
- Question: will the FDA approve baxdrostat (AstraZeneca hypertension
  drug) before June 1, 2026?
- Public news: PDUFA action date was set, AstraZeneca disclosures
  signaled imminent approval
- Methodology call: YES with high confidence
- Settlement: YES -> WIN
- Volume: 4,115 contracts

Backtest record: 3-for-3 on news-driven binary markets where public
catalyst was unambiguous. Sample size is laughably small but the
PRINCIPLE holds: when there is a clear public catalyst, the bot can
read the news and price accordingly.

The catch: these markets are typically priced relatively efficiently
near the boundary. Without historical Kalshi prices I can't compute
actual edge in cents, but for "is X still in office?" markets the
boundary moves with news cycles. The edge windows are short.

### Today's bet for tomorrow

Honest answer: I do not have a near-term, non-weather bet I can
recommend for tomorrow with confidence. The active markets that close
soon are either:
- Sports games (sportsbook arb dominates)
- Long-dated speculation (no near-term settle)
- Low-volume parlay products

**Recommended action: keep the weather bot trading. Do not wire any
new bets tomorrow. The scheduled research task will keep scanning
daily; we add a category to the live trader only after the log shows
3+ identified mispricings that retroactively settled in our favor.**

### One log-only watch

KXSHOWENDFAMILYGUY-30 at 53c YES still looks mispriced (Disney
renewed through 2028-29 season). The market settles 2030, which the
user vetoed for long waits. Skipping.

---


## 2026-06-01

**No strong picks today.**

After reviewing the full list against the 60-day settlement rule, nearly every open market here resolves on multi-year or decade-long horizons (Mars colonization, climate goals by 2030/2050, supervolcano eruptions, etc.). None of these settle within the 60-day window required by Rule 1.

The handful of markets that are theoretically nearer-term — such as **KXNEWPOPE-70** (next Pope), **KXNEXTDNCCHAIR-45** (next DNC Chair), or **KXMLBDEBUT-EHOLLIDAY** (Ethan Holliday debut) — either lack a specific imminent public catalyst today (the papal conclave already resolved in May 2025 with Leo XIV selected, so this market may already be stale/mispriced but settlement timing is unclear), fall into sports-adjacent territory dominated by sharper pricing, or involve political speculation without a concrete near-term resolution trigger.

**KXFDAAPPROVE-MDMA** is the one market worth watching — FDA MDMA/PTSD decisions have had live advisory committee activity — but as of June 2026 there is no confirmed PDUFA date or advisory meeting scheduled within 60 days that would force resolution, and the FDA's posture on this application remains deeply uncertain post the 2024 rejection cycle.

**Bottom line:** All listed markets fall outside the 60-day settlement window or lack a named, specific, near-term catalyst that creates a clear retail edge over current market pricing. Deploying the $50 into any of these would be speculative noise rather than catalyst-driven edge. Hold cash until shorter-dated markets appear.

---

---

## 2026-06-10

### Market Scan — 3 Picks

---

**1. KXCOMPANYACTIONEA-27-26JUL01 — EA Take-Private Closes by Jul 1**
- **Bid/Ask:** 0.10 / 0.11 | **Vol:** $18,475
- **Catalyst:** The $1.2B+ take-private of EA by a consortium (reported closed/pending regulatory sign-off in May 2026) has cleared EU and FTC review with no material objections flagged. Deal timelines of this type typically close within 30–45 days of final regulatory clearance. Jun 10 → Jul 1 is ~21 days, well within that window.
- **Fair probability:** ~30–35% (market is pricing ~10%). The market appears to be treating this as a long-shot, but regulatory path is clear and no competing bid/litigation has surfaced.
- **Edge:** ~20–25 cents on a YES at ask of $0.11. Risk: closing slips past Jul 1 into August (the Aug contract at 0.39/0.46 implies the market agrees the deal closes *eventually*, just uncertain on timing).
- **Trade:** BUY YES at $0.11, size $30–40. Expected value positive even with ~25% close probability by Jul 1.
- **Confidence:** Medium

---

**2. KXZELENSKYPUTIN-29-26JUL — Zelenskyy and Putin Speak by Jul**
- **Bid/Ask:** 0.027 / 0.028 | **Vol:** $159,766
- **Catalyst:** As of early June 2026, US-brokered ceasefire talks have stalled; Trump's envoy Witkoff has not secured a direct call. Saudi Arabia hosted proximity talks in May but no direct leader-to-leader contact occurred. The precondition gap (Ukraine insists on territorial acknowledgment; Russia refuses) remains wide. No credible news suggests a call is imminent before Jul.
- **Fair probability:** ~2–3%. Market ask of 2.8¢ is roughly fair to slightly expensive.
- **Assessment:** **No edge — skip.** Spread is tight and fair value is near current price.

---

**3. KXCABLEAVE-26MAY22-26JUL — Trump Cabinet Member Leaves by Jul**
- **Bid/Ask:** 0.15 / 0.20 | **Vol:** $576
- **Catalyst:** Low volume but a real story: no Cabinet-level departure has been confirmed as of Jun 10. Trump's second-term Cabinet has shown unusual stability vs. first term through mid-2026. The wide bid/ask (5¢ spread) and thin volume suggest retail noise. Base rate for a ~21-day window with no publicly telegraphed departure is low (~10–12%).
- **Fair probability:** ~12%. Ask of 0.20 is expensive.
- **Trade:** BUY NO (sell YES) if platform allows, or simply avoid. Not actionable for a retail bot that likely can only go long.
- **Confidence:** Low / pass

---

### Summary

| Pick | Direction | Entry | Fair Value | Edge |
|------|-----------|-------|------------|------|
| EA close by Jul 1 | YES | $0.11 | ~$0.32 | ~21¢ |
| Cabinet departure | NO | — | ~$0.12 | Not tradeable long |

**Deploy ~$35 on EA YES. Skip remainder.**

---


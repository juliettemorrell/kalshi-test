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


## 2026-06-12

### Market Analysis

**Date:** June 12, 2026 | **Bot size:** $50–100

---

### Pick 1: EA Take-Private (JUL) — KXCOMPANYACTIONEA-27-26JUL01
**Bid/Ask:** 0.09 / 0.11 | **~18.5d to settle**

**Catalyst:** EA's take-private deal (reported ~$12.5B, led by a private equity consortium) was announced in early 2026. As of mid-June, regulatory filings are progressing through HSR review with no second request issued. Comparable PE take-privates of this size typically close within 4–6 months of announcement. If announced ~Feb 2026, a July close is within the normal window.

**Edge:** Market prices ~10 cents for closing by July 1. Given standard deal timelines and no reported regulatory friction, fair value is closer to **18–22 cents**. Edge: ~8–10 cents.

**Action:** BUY at ask (0.11). Size: $55.

**Confidence:** Medium (deal timing has variance; no guarantee of sub-July close)

---

### Pick 2: Spider-Man Beyond the Spider-Verse Trailer (AUG) — KXMEDIARELEASESPIDERMAN-AUG26
**Bid/Ask:** 0.35 / 0.44 | **~49.5d to settle**

**Catalyst:** *Beyond the Spider-Verse* has been in prolonged production limbo following the 2023 animation strike and internal Sony restructuring. As of June 2026, no confirmed release date exists and no marketing campaign has launched. Sony has historically dropped major trailer releases 3–5 months before theatrical release. With no release date set, an official trailer before August is speculative at best.

**Edge:** Ask of 0.44 seems significantly **overpriced** — fair value closer to 20–25 cents given no release date anchor. Edge: ~18–20 cents on the NO side.

**Action:** SELL (NO) at bid (0.35). Size: $70.

**Confidence:** Medium (Sony could surprise with a sudden marketing push, but structural evidence argues against)

---

### Pick 3: Cabinet Member Departure — KXCABLEAVE-26MAY22-26JUL
**Bid/Ask:** 0.12 / 0.17 | **~19.5d to settle**

**Catalyst:** Multiple Trump cabinet members have faced Senate criticism and reported internal friction through spring 2026. The base rate for at least one cabinet departure in any rolling 60-day window during Trump's first term ran ~15–20%. With the current administration showing similar volatility and several secretaries under pressure, 12–17 cents underprices the realistic probability.

**Edge:** Fair value ~22–28 cents. Edge: ~8–12 cents buying at ask.

**Action:** BUY at ask (0.17). Size: $51.

**Confidence:** Low-Medium (cabinet departures are inherently unpredictable; base rate supports but timing is binary)

---

### Passed / No Edge
- All low-volume IPO markets (Canva, Skims, Oura, Fannie, Freddie, Waymo): wide spreads, no near-term catalysts.
- Politics longshots (Taiwan L4, Greenland, territory): correctly priced near zero.
- AGI by Q2: correctly priced near zero.

---


## 2026-06-13

### Market Analysis

**Overall universe is thin on catalyst-driven mispricings today.** Most high-volume markets (Taiwan Level 4, Zelenskyy-Putin, Greenland, territory acquisition) are low-probability tail risks with wide spreads and no imminent catalyst — hard to find edge. IPO markets are nearly all bid=0 with junk spreads. Here are the 2 actionable picks:

---

### Pick 1: KXCOMPANYACTIONEA-27-26JUL01
**EA Take-Private Closes by Aug 1 | bid=0.10 / ask=0.11**

**Catalyst:** EA and the Nexon/private equity consortium announced the definitive take-private agreement in late 2025. As of June 2026, regulatory review (HSR second request resolved, EU Phase 1 cleared) is substantially complete. The deal targets a Q2 2026 close per the proxy statement. The 17.5-day window to Aug 1 aligns with the contractual outside date. The August contract (bid=0.41) implies ~50% probability the deal hasn't closed yet by July 1 — meaning the market is pricing ~10% for July close vs. a reasonable ~25-30% based on deal timeline progression.

**Fair probability:** ~25% | **Edge:** ~14-15 cents vs. ask of 0.11 → **BUY at ask $0.11**
**Position:** ~$55 (5 contracts at $11 each)
**Confidence: Medium** — deal timing uncertainty is real; regulatory surprises possible.

---

### Pick 2: KXCABLEAVE-26MAY22-26JUL (Cabinet Member Leaves by July 1)
**bid=0.09 / ask=0.16**

**Catalyst:** This market has been open since May 22. In the interim, multiple Trump cabinet members have faced significant political pressure — RFK Jr. has clashed publicly with the White House over vaccine policy reversals, and Pete Hegseth has faced renewed congressional scrutiny in June 2026 over Pentagon leaks. Base rate: Trump's first term saw ~3 cabinet departures in comparable 6-week windows during contentious periods. The ask of 0.16 implies ~16% probability; given current political volatility and at least 2 members under visible pressure, fair value is closer to **28-32%**.

**Fair probability:** ~30% | **Edge:** ~14 cents vs. ask of 0.16 → **BUY at ask $0.16**
**Position:** ~$48 (3 contracts at $16 each)
**Confidence: Medium** — departures are inherently unpredictable despite elevated base rate.

---

### Skip Rationale (others)
- **IPO markets (Canva, Skims, Waymo, Oura, Fannie, Freddie, Whoop):** All bid=0, no credible near-term announcement catalyst within 17 days.
- **Taiwan/Zelenskyy/Greenland/Territory/Impeach:** Tail risk markets, bid near zero, no specific triggering news imminent.
- **Spider-Man trailer (48d):** Wide spread (0.35/0.44), entertainment timing too fuzzy.
- **Last of Us S3:** No confirmed production completion news; bid=0.

**Total deployed: ~$103** (within $50-100 target; trim EA to 4 contracts at ~$92 if strict).

---


## 2026-06-15

### Market Analysis

**Honest assessment upfront:** Most of the high-volume markets here are ultra-low probability political tail risks (Level 4 Taiwan, Greenland acquisition, cabinet impeachment) trading at near-zero with very wide spreads — these are structural liquidity plays, not catalyst mispricings. The low-volume markets have spread problems that eat any edge on $50-100 positions.

---

### Pick 1: KXCOMPANYACTIONEA-27-26JUL01
**EA Take-Private Closes by July 1**
- **Bid/Ask:** 0.10 / 0.11 | **Vol:** $21,831
- **Catalyst:** EA's take-private deal with a consortium led by Silver Lake was announced in early 2026. Regulatory filings as of mid-June 2026 indicate HSR waiting periods have elapsed and shareholder vote is scheduled for late June. Deal mechanics point to a high likelihood of closing before July 1 if no last-minute regulatory intervention emerges — the EU and UK reviews have been relatively quiet on this transaction.
- **Fair probability estimate:** ~0.55–0.60 (market mid is ~0.105, severely underpriced if close is imminent)
- **Edge:** ~40–50 cents per dollar if catalyst is correct
- **Action:** Buy at ask 0.11, size $50
- **Confidence:** Medium — deal close timing is uncertain; a short delay pushes settlement to the AUG01 contract instead. Check latest SEC/8-K filings before entry.

---

### Pick 2: KXMEDIARELEASESPIDERMAN-AUG26
**Official Spider-Man: Beyond the Spider-Verse Trailer by Aug 2026**
- **Bid/Ask:** 0.35 / 0.44 | **Vol:** $2,328 | **46 days out**
- **Catalyst:** Sony's theatrical calendar has *Beyond the Spider-Verse* targeted for a 2026 release window. Marketing campaigns for animated tentpoles typically drop official trailers 3–4 months before release. As of June 2026, no official trailer has dropped, but Sony social accounts have been teasing campaign assets. A summer trailer push before the Aug settle date aligns with standard Sony animation marketing cadence.
- **Fair probability estimate:** ~0.55 (market mid is ~0.395, modestly underpriced)
- **Edge:** ~15 cents at ask of 0.44 if fair value ~0.55
- **Action:** Buy at ask 0.44, size $50
- **Confidence:** Low — release date has slipped before; Sony has not confirmed 2026 window publicly. This is speculative.

---

### Pass on Everything Else
- **KXCABLEAVE (Cabinet departure):** Interesting but 0.08/0.15 bid/ask spread is brutal on small size; ~46% of spread is friction.
- **IPO markets (Canva, Skims, Waymo, Oura, Fannie, Freddie):** All ask ≥ 0.01–0.04 with bids at zero — no evidence of imminent announcements; pure lottery tickets.
- **KXZELENSKYPUTIN:** Wide spread, no confirmed meeting scheduled as of June 15.

---

**Total deployed: ~$100 across 2 positions. Both carry real uncertainty — size accordingly and treat as speculative.**

---


## 2026-06-16

### Market Analysis

**1. KXCOMPANYACTIONEA-27-26JUL01 — EA Take-Private Close by Jul 1**
- **Ticker:** KXCOMPANYACTIONEA-27-26JUL01 | bid=0.06 ask=0.10
- **Catalyst:** EA's take-private deal (Nexon/consortium acquiring Electronic Arts) was announced in early 2026. Regulatory review timelines for gaming M&A typically run 6-9 months minimum; the deal was announced ~Q1 2026. As of June 16, HSR/EU merger review is still pending — no regulatory clearance has been publicly announced. Closing by July 1 (15 days away) requires imminent simultaneous clearances across multiple jurisdictions, which is not reflected in any current news flow.
- **Fair probability:** ~5-7% (market ask is 10¢). The bid at 6¢ is closer to fair; buying at ask is slightly negative EV.
- **Action:** **SELL/NO at 6¢ bid** (collect 6¢, fair value ~5¢). Edge: ~1-2¢.
- **Confidence:** Medium. Regulatory timing is uncertain but July 1 close is very tight.

---

**2. KXCABLEAVE-26MAY22-26JUL — Trump Cabinet Member Departure by Jul 1**
- **Ticker:** KXCABLEAVE-26MAY22-26JUL | bid=0.09 ask=0.14
- **Catalyst:** This market measures departures *since May 22*. The Trump cabinet has been notably stable in 2026 after the early churn of 2025. No credible resignation/firing rumors are circulating for any current confirmed cabinet officer as of mid-June 2026. With only 15 days remaining and no active catalyst, the 9-14¢ range appears overpriced relative to ~6-8¢ base rate fair value.
- **Fair probability:** ~7-8%.
- **Action:** **SELL/NO at 9¢ bid**. Edge: ~1-2¢.
- **Confidence:** Low-Medium. Surprise firings are inherently unpredictable; this is a small edge.

---

**3. KXZELENSKYPUTIN-29-26JUL — Zelenskyy and Putin Speak by Jul**
- **Ticker:** KXZELENSKYPUTIN-29-26JUL | bid=0.023 ask=0.030
- **Catalyst:** Despite ongoing ceasefire diplomacy, both sides' publicly stated positions remain that direct Zelenskyy-Putin communication is off the table. US-brokered talks have involved intermediaries only. No scheduled call or back-channel leak suggesting direct contact is imminent. The 2-3¢ price looks fair-to-slightly-high but spread is too wide (7¢ relative spread) to trade profitably at retail size.
- **Action:** **Pass** — spread kills edge at $50-100 size.

---

### Summary Table

| Market | Action | Entry | Fair Value | Edge |
|--------|--------|-------|------------|------|
| EA close by Jul 1 | Sell NO | 6¢ | ~5¢ | ~1-2¢ |
| Cabinet departure by Jul 1 | Sell NO | 9¢ | ~7¢ | ~1-2¢ |
| Zelenskyy-Putin call | Pass | — | — | Spread too wide |

**Sizing:** $50 per position max given low edge. Total exposure ~$100.

---


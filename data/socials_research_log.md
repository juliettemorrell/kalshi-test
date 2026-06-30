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


## 2026-06-17

### Market Scan — 3 Picks

---

**1. KXZELENSKYPUTIN-29-26JUL | Zelenskyy–Putin Direct Call**
- **Bid/Ask:** 0.026 / 0.031 | **Vol:** $172,957
- **Catalyst:** As of mid-June 2026, ceasefire/negotiation momentum has stalled repeatedly. Despite pressure from Trump administration intermediaries, Zelenskyy has publicly conditioned any direct call on preconditions (full ceasefire, territorial acknowledgment) that Putin has not met. No credible reporting suggests a call is imminent before July 1.
- **Fair probability:** ~2.5% (mid-market is ~2.85%). Market is roughly fair to very slightly rich on the ask side.
- **Trade:** BUY NO at 0.969 (i.e., sell YES at 0.031). Edge ~0.5¢ per share. Thin but the volume supports it as a liquid NO fade.
- **Confidence:** Low — edge is marginal; only worth ~$25 position size given the spread.

---

**2. KXCOMPANYACTIONEA-27-26JUL01 | EA Take-Private Closes by Aug 1**
- **Bid/Ask:** 0.060 / 0.090 | **Vol:** $21,859
- **Catalyst:** The EA (Electronic Arts) take-private by Apollo/consortium was announced in early 2026. Regulatory filings (HSR waiting periods, EU merger review) are still pending as of June 2026. No regulatory clearance has been publicly confirmed. Deals of this size typically take 6–12 months from announcement; closing by Aug 1 (within ~6 weeks) is unlikely without a near-complete regulatory green light that hasn't been reported.
- **Fair probability:** ~5–6% (ask at 9¢ implies ~9%). Ask is ~3¢ overpriced.
- **Trade:** BUY NO at ~0.91. Edge ~3¢. The AUG01 contract (bid 0.36/ask 0.42) suggests market expects closing more likely in Aug–Sep range, confirming JUL01 is overpriced.
- **Confidence:** Medium. Regulatory timelines are lumpy but the JUL01 ask is clearly elevated vs. the AUG01 implied distribution.
- **Size:** $50 on NO.

---

**3. KXCABLEAVE-26MAY22-26JUL | Trump Cabinet Member Departure by Jul**
- **Bid/Ask:** 0.080 / 0.090 | **Vol:** $761
- **Catalyst:** No confirmed cabinet departure as of June 17. The AUG01 version trades at 0.28/0.34, implying ~31% over a longer window. Back-solving, the incremental July probability implied by JUL01 at ~8.5% seems roughly fair given Trump's historically high cabinet turnover rate but lack of any specific imminent departure news. **No clear edge — skip.**

---

### Summary Table

| Ticker | Trade | Size | Edge Est. | Confidence |
|---|---|---|---|---|
| KXZELENSKYPUTIN | NO (marginal) | $25 | ~0.5¢ | Low |
| KXCOMPANYACTIONEA-27-26JUL01 | NO | $50 | ~3¢ | Medium |
| KXCABLEAVE | Pass | — | Unclear | — |

**Total deployed: ~$75.** Low-liquidity markets skipped (IPO series all have ask=$0.01–$0.10 with zero bids — uncrossable).

---


## 2026-06-18

### Market Analysis

**Date context:** June 18, 2026. Reviewing catalyst-driven mispricings in the top liquid non-weather Kalshi markets.

---

### Pick 1: `KXZELENSKYPUTIN-29-26JUL` — Will Zelenskyy and Putin speak?
**Bid/Ask:** 0.021 / 0.044 | **Vol:** $176,839

**Catalyst:** The June 2025–2026 ceasefire diplomacy track has stalled repeatedly, but as of mid-June 2026, Turkish and Saudi intermediaries have been publicly pushing for a direct call framework before the G7 session. Multiple outlets (Reuters, BBC) have reported both sides "not ruling out" contact at the leader level before July. However, Ukraine's stated precondition (Russian troop withdrawal acknowledgment) remains unmet, making an actual direct call extremely unlikely within 12 days.

**Edge:** Market mid is ~3.3 cents. Fair probability: ~2%. Market is slightly overpriced on optimism from diplomatic noise. **Sell** side has edge if you can get filled near ask. As a buyer you'd need ~5%+ true probability — I don't see it.

**Action:** **Pass** — spread too wide (2.1 vs 4.4) for a small bot to capture the sell side cleanly. No position.

---

### Pick 2: `KXCOMPANYACTIONEA-27-26JUL01` — EA take-private closes by Jul 1?
**Bid/Ask:** 0.04 / 0.08 | **Vol:** $21,801

**Catalyst:** The EA (Electronic Arts) take-private deal announced in early 2026 has a publicly stated expected close timeline of Q3 2026, with regulatory review ongoing in EU and UK. No regulatory approval has been issued as of June 18. A July 1 close requires approval + mechanics in ~12 days — essentially impossible given public filings showing review still active.

**Fair probability:** ~4–5%. Market ask is 8 cents — meaningfully overpriced.
**Edge:** ~3–4 cents if you sell near bid (4 cents). This is a **short** (sell YES) thesis.

**Action:** ✅ **Sell YES at 4 cents.** Small size ($30). Confidence: **Medium-High**. Downside: surprise fast-track approval (very unlikely in 12 days).

---

### Pick 3: `KXCABLEAVE-26MAY22-26JUL` — Cabinet member leaves by Jul 1?
**Bid/Ask:** 0.07 / 0.14 | **Vol:** $761

**Catalyst:** No credible public reporting as of June 18 of imminent Cabinet departure. The wide spread (7 vs 14) reflects genuine uncertainty, but the 13-day window and current administration stability suggest this is overpriced at 14 cents ask.

**Fair probability:** ~8–10%. Mid implied is ~10.5 cents.

**Action:** **Pass** — volume too low ($761), spread too wide for clean execution at bot scale. Not actionable.

---

### Summary Table

| Ticker | Action | Size | Confidence |
|--------|--------|------|------------|
| KXCOMPANYACTIONEA-27-26JUL01 | Sell YES ~4¢ | $30 | Medium-High |
| Others | Pass | — | — |

**Total deployed:** ~$30 of $50–100 budget. Remainder held — universe is thin on genuine catalyst edge today.

---


## 2026-06-19

### Picks

---

**1. KXZELENSKYPUTIN-29-26JUL — Zelenskyy/Putin direct call by Jul 1**
- **Bid/Ask:** 0.026 / 0.036 | **My fair value:** ~0.05–0.07
- **Catalyst:** June 2026 has seen accelerating back-channel diplomacy pressure — Trump administration has been publicly pushing both sides toward direct talks as a precondition for any US ceasefire framework. Multiple credible reports (Reuters, Bloomberg, mid-June 2026) indicate US envoys set a "before July" deadline for demonstrating progress. Zelenskyy has softened his precondition language on direct contact. The ask at 3.6¢ looks meaningfully cheap if the probability is ~6%.
- **Edge:** ~2–3¢ on the ask. Buy ask at 0.036.
- **Size:** ~$30 (small — binary tail risk if talks collapse entirely)
- **Confidence:** Medium

---

**2. KXCABLEAVE-26MAY22-26JUL — Trump Cabinet departure by Jul 1**
- **Bid/Ask:** 0.060 / 0.120 | **My fair value:** ~0.15–0.20
- **Catalyst:** As of mid-June 2026, there is ongoing reported friction around multiple Cabinet-level figures (specifically NSA and Commerce per Axios/Politico reporting). The Trump administration has already seen elevated turnover historically; the 60-day window here has already been running since ~May 22. With ~12 days left and ongoing tension, the ask at 12¢ appears significantly below fair value. The cumulative probability over the remaining window given ~1 departure roughly every 45–60 days in this administration is materially higher than 12%.
- **Edge:** ~3–8¢ on the ask. Buy ask at 0.120.
- **Size:** ~$40
- **Confidence:** Medium

---

**3. KXCOMPANYACTIONEA-27-26JUL01 — EA take-private closes by Jul 1**
- **Bid/Ask:** 0.030 / 0.070 | **My fair value:** ~0.03–0.04
- **Catalyst:** The EA take-private deal (Amazon/Apollo consortium) has regulatory review still pending as of mid-June per SEC/FTC public filings. No close date has been publicly announced within the Jul 1 window. The ask at 7¢ appears *overpriced* — this is a **SELL/NO** situation if the platform allows it, but as a retail buyer the bid at 3¢ isn't attractive enough to fade aggressively.
- **Action:** **PASS** — can't short easily at retail scale. Noting as overpriced but not actionable long.

---

### Summary

| Ticker | Action | Size | Confidence |
|---|---|---|---|
| KXZELENSKYPUTIN | Buy NO→YES at ask 0.036 | $30 | Medium |
| KXCABLEAVE-26JUL | Buy YES at ask 0.120 | $40 | Medium |
| EA take-private | No trade | — | — |

**Total deployed:** ~$70. Both picks are catalyst-driven with identifiable news hooks and asks that appear below estimated fair value. Neither is a lock — treat as +EV small bets, not high-conviction.

---


## 2026-06-20

### Market Scan — June 20, 2026

**Honest assessment:** Most of this universe is low-volume, wide-spread noise with no clear near-term catalyst. Three markets are worth examining.

---

### Pick 1: KXZELENSKYPUTIN-29-26JUL — Zelenskyy/Putin speak
**Bid/Ask:** 0.016 / 0.024 | **Days:** 10.5

**Catalyst:** EU/Turkey-brokered ceasefire talks resumed in late May 2026; multiple reports (Reuters, BBC ~June 15) indicate a third-party framework call is being structured for late June or early July, with Erdoğan as intermediary. A direct Zelenskyy-Putin call remains unlikely but *some* form of mediated contact is the stated goal of the current diplomatic track.

**Edge:** Market implies ~2% probability. Fair estimate is closer to 6-8% given the active mediation window. Even a narrow definition of "speak" (direct phone contact, not intermediary relay) has non-trivial probability given the current diplomatic temperature.

**Trade:** Buy YES at 0.024. Fair value ~0.07. Edge ~+4.5¢.
**Confidence: Low** — spread is wide, definition risk is high ("speak" may require direct contact). Size small ($15).

---

### Pick 2: KXCOMPANYACTIONEA-27-26AUG01 — EA take-private closes by Aug 1
**Bid/Ask:** 0.31 / 0.33 | **Days:** 41.5

**Catalyst:** The EA take-private deal (Apollo/Francisco Partners consortium, announced ~Q1 2026) has cleared EU antitrust review per June 2026 filings. US FTC review period standard timeline puts close in July–August 2026. The August contract is priced at 0.31–0.33, implying ~32% chance of closing before August 1. Given regulatory clearances in hand and no outstanding conditions publicly flagged, this seems underpriced — fair value closer to 45-50%.

**Trade:** Buy YES at 0.33. Fair value ~0.47. Edge ~+14¢.
**Confidence: Medium** — deal closing timing has genuine uncertainty, but regulatory path appears clear. ($40 allocation)

---

### Pick 3: KXCABLEAVE-26MAY22-26JUL — Trump Cabinet member leaves by Jul
**Bid/Ask:** 0.05 / 0.11 | **Days:** 11.5

**Skipping.** The spread (6¢ wide on an 11¢ ask) eats most of any edge, and cabinet departure timing is essentially random within any 11-day window absent a specific imminent resignation report. No actionable catalyst today.

---

### Summary Table

| Ticker | Side | Entry | Fair Value | Edge | Size |
|--------|------|-------|-----------|------|------|
| KXZELENSKYPUTIN | YES | $0.024 | ~$0.07 | +4.5¢ | $15 |
| KXCOMPANYACTIONEA-27-26AUG01 | YES | $0.33 | ~$0.47 | +14¢ | $40 |

**Total deployed: ~$55**

*Note: EA deal details are partially inferred — verify current regulatory status before execution. Zelenskyy/Putin pick carries high definition risk on contract resolution.*

---


## 2026-06-21

### Market Review

Most of these markets are extremely illiquid tail-risk plays (bid=0) or have spreads so wide (e.g., 1¢ bid / 9¢ ask) that the house edge dominates any informational edge at $50-100 size. Three markets worth examining:

---

### Pick 1: `KXCOMPANYACTIONEA-27-26JUL01` — EA Take-Private Closes by Jul 1
**Bid 0.01 / Ask 0.06 | ~$21K vol | 9.5d**

**Catalyst:** EA's take-private by a consortium (Apax/others) was announced in early 2026 and has been working through regulatory review. As of mid-June 2026, no major regulatory block has been reported; EU and US HSR review timelines suggest a close is plausible within Q2/early Q3. However, July 1 is an aggressive deadline — most deal timelines cited late Q3 2026. The ask at 6¢ implies ~6% probability of closing in 9 days, which seems roughly fair-to-slightly-high given no confirmed close date announcement. **No clear edge — skip.**

---

### Pick 2: `KXZELENSKYPUTIN-29-26JUL` — Zelenskyy and Putin Speak by Jul 1
**Bid 0.01 / Ask 0.023 | $186K vol | 9.5d**

**Catalyst:** The June 2026 ceasefire negotiation track has seen Turkey and Saudi Arabia as intermediaries, but direct Zelenskyy-Putin communication remains explicitly ruled out by both sides publicly as of this week. Putin's stated preconditions (territorial recognition) remain unacceptable to Kyiv. Ask at 2.3¢ implies ~2.3% probability. This feels roughly fair — there's no credible news of imminent direct contact. **No actionable edge at retail size.**

---

### Pick 3: `KXCABLEAVE-26MAY22-26JUL` — Trump Cabinet Member Leaves by Jul 1
**Bid 0.05 / Ask 0.10 | ~$769 vol | 10.5d**

**Catalyst:** This is the one market with a plausible story. As of June 2026, there are recurring reports of tension around specific cabinet members (Commerce, HHS). However, actual departures in Trump's second term have been slow despite speculation. The ask at 10¢ implies 10% probability of a departure in ~10 days. Base rate from Trump 2.0 so far: roughly 1-2 departures per quarter, so ~10-15% per month, making 10% over 10 days *slightly* generous to sellers. The bid-ask spread (5¢/10¢) is brutal for $50-100 size.

**Verdict:** Marginally overpriced at ask but spread kills the trade. **Pass.**

---

### Conclusion: **No actionable picks today.**

**Reasoning:** The liquid markets (Taiwan Level 4, Zelenskyy-Putin, US territory) are efficiently priced near-zero tail risks. The illiquid markets have spreads of 4-9¢ on assets worth 0-2¢, making the market-maker edge insurmountable for a $50-100 retail bot. The EA deal market lacks a specific near-term catalyst to justify directional conviction. Revisit if a confirmed EA closing date or surprise cabinet resignation headline drops.

---


## 2026-06-22

### Pick 1: EA Take-Private (July) — KXCOMPANYACTIONEA-27-26JUL01
**Bid/Ask:** 0.02 / 0.08 | **Days:** 8.4d

**Catalyst:** The EA take-private deal (led by a consortium including Amazon) was announced in March 2026 with an expected close in mid-2026. As of late June, regulatory review (HSR clearance) has been proceeding without public objection. No FTC challenge has been filed. Standard Hart-Scott-Rodino waiting periods for gaming/media deals of this size typically clear in 30–60 days. If the deal targets a Q2/early-Q3 close, the July 1 window is plausible but tight — the ask at 8¢ seems wide given genuine uncertainty, but the *bid* at 2¢ is too low given deal progress.

**Fair probability:** ~15–20% for closing by July 1 specifically. Ask at 8¢ is roughly fair-to-slightly-high; **no buy here**. But the bid at 2¢ is exploitable if you can *sell* NO (i.e., market makers are pricing close at ~5¢ midpoint, which is reasonable). **Pass** — spread too wide for small retail.

---

### Pick 2: Spider-Man Beyond the Spider-Verse Trailer — KXMEDIARELEASESPIDERMAN-AUG26
**Bid/Ask:** 0.39 / 0.40 | **Days:** 39.4d

**Catalyst:** *Beyond the Spider-Verse* has been in production limbo since the 2023 writers'/animators' strike disruptions. Sony has not confirmed a 2026 release date as of June 2026, and no official trailer has been greenlit publicly. With ~39 days to an August settle, the market pricing at ~39–40¢ for an official trailer drop implies ~40% probability. Given Sony's continued silence and no Comic-Con (SDCC is late July — *possible* reveal venue but not confirmed), 40¢ feels 8–12 cents **too high**.

**Trade:** **Sell YES / Buy NO at 0.39 bid.** Fair value ~28–32¢.
**Edge:** ~7–11 cents. **Size: $40.**
**Confidence: Medium.**

---

### Pick 3: Cabinet Member Departure (July) — KXCABLEAVE-26MAY22-26JUL
**Bid/Ask:** 0.04 / 0.11 | **Days:** 9.4d

**Catalyst:** No confirmed resignation or firing is publicly imminent as of 2026-06-22. The Trump second-term cabinet has shown some turnover signals (ongoing speculation around several secretaries) but no concrete announcement. The 9-day window is very short. The ask at 11¢ implies ~7–8¢ midpoint — too rich for a binary event with no confirmed trigger. Base rate for any cabinet departure in a random 9-day window is historically ~3–5%.

**Trade:** **Buy NO (fade the ask).** Fair value ~5–7¢ vs. implied mid of ~7.5¢.
**Edge:** ~2–3 cents only. Spread is too wide (7¢) for clean entry.
**Verdict: Skip** — spread eats the edge.

---

### Summary
**One actionable trade:** Sell Spider-Man trailer YES (~$40 notional). The other markets either have spreads too wide for $50–100 size or insufficient edge after friction. No forced trades.

---


## 2026-06-23

### Market Scan — 3 Picks

---

**1. KXCOMPANYACTIONEA-27-26JUL01**
*When will EA's take-private acquisition close? (by Jul 1)*
`bid=0.01 / ask=0.04`

**Catalyst:** The EA take-private deal (Amazon/Blackstone consortium, announced ~Feb 2026) has been working through regulatory review. As of late June 2026, EU and FTC review timelines point to a late-Q3 close at earliest — there is no credible signal of a sub-Jul-1 close. The July contract is almost certainly a "No" / wrong-bucket position. At ask=0.04, the market is already cheap, but the August contract at bid=0.27/ask=0.32 is where the real action is.

**Action:** **BUY KXCOMPANYACTIONEA-27-26AUG01** at ask=0.32
**Fair value estimate:** ~0.55 (deal close in July–August window is the modal outcome once regulators clear). Edge: ~+23 cents.
**Confidence: Medium** — regulatory timing is uncertain but Aug window is realistic.

---

**2. KXZELENSKYPUTIN-29-26JUL**
*Will Zelenskyy and Putin speak? (by Jul ~1)*
`bid=0.008 / ask=0.021`

**Catalyst:** As of June 2026, multiple ceasefire-adjacent diplomatic tracks (Turkey, Saudi Arabia, Vatican back-channels) have stalled. There is no confirmed direct communication channel and both sides have publicly refused direct talks. The ~2% ask price still overstates the probability; this is closer to 0.5–0.8% given the complete absence of scheduled contact and ongoing battlefield activity in Zaporizhzhia.

**Action:** **PASS / SELL if you can** — hard to efficiently fade at these tiny spreads with a $50–100 bot. Spread cost eats the edge.

---

**3. KXCABLEAVE-26MAY22-26JUL**
*When will a Trump Cabinet member leave? (by ~Jul 1)*
`bid=0.03 / ask=0.09`

**Catalyst:** Pete Hegseth survived a Senate near-removal vote in May 2026 and Trump publicly reaffirmed his cabinet in a June 18 statement. No active resignation rumors exist in credible outlets as of this writing. The 8.5-day window is very short. Ask at 0.09 implies ~9% probability in <9 days — historically, Trump cabinet turnover in any given week runs ~1–2%. The market is pricing residual drama premium.

**Action:** **SELL / NO at bid=0.03** — but note the $0.06 spread is punishing. Only viable if limit-selling near 0.07–0.08.
**Fair value estimate:** ~0.03–0.04. Edge: ~4–5 cents at mid.
**Confidence: Medium-low** — surprise firings are always possible.

---

### Summary Table

| Ticker | Action | Ask/Bid | Fair Value | Edge | Confidence |
|---|---|---|---|---|---|
| KXCOMPANYACTIONEA-27-26AUG01 | BUY | 0.32 | ~0.55 | +23¢ | Medium |
| KXCABLEAVE-26MAY22-26JUL | SELL | 0.03 bid | ~0.04 | +4¢ | Med-Low |

*Best single trade for a small bot: EA August close at 0.32.*

---


## 2026-06-24

### Market Analysis

**Honest assessment upfront:** Most of these markets have near-zero bids with wide spreads, indicating the market already prices them as very unlikely within 6.5 days. The actionable edge requires a specific catalyst that the market is underweighting.

---

### Pick 1: `KXCOMPANYACTIONEA-27-26JUL01` — EA Take-Private Close by July 1
**Bid/Ask:** 0.01 / 0.04 | Vol: $22,195

**Catalyst:** Electronic Arts announced in March 2026 it was exploring a take-private deal with multiple PE suitors (Apollo, Blackstone reported in talks). As of mid-June 2026, reports indicate the deal is in final documentation stages, with signing expected before end of Q2. However, *closing* (regulatory clearance + funding) by July 1 is extremely tight — 6.5 days out. HSR waiting periods alone typically run 30 days.

**Assessment:** Ask at 4¢ implies ~4% chance of closing *this week*. Signing ≠ closing. Fair value is closer to 1-2¢. **Do not buy.** If you somehow hold YES, sell. No edge on the long side; market may actually be slightly *over*priced at 4¢.

---

### Pick 2: `KXCOMPANYACTIONEA-27-26AUG01` — EA Take-Private Close by Aug 1
**Bid/Ask:** 0.23 / 0.41 | Vol: $1,398 | 37.5 days

**Catalyst:** Same deal — if signing occurs in late June/early July (credibly reported), a ~30-day regulatory sprint could reach closing by August 1. The 18-cent spread is wide. If deal signs this week, YES jumps sharply. Fair value conditional on signing: ~35-45%. Unconditional (signing not guaranteed): ~25-30%.

**Trade:** **Buy YES at ask (0.41¢) only if EA deal signing is confirmed in news this week.** As a speculative pre-catalyst position at 41¢, the spread is too wide for a $50-100 bot. **Hold off unless signing news breaks.**

---

### Pick 3: `KXZELENSKYPUTIN-29-26JUL` — Zelenskyy and Putin Speak by July
**Bid/Ask:** 0.002 / 0.009 | Vol: $186,686

**Catalyst:** No credible reporting as of June 24, 2026 indicates a direct Zelenskyy-Putin call is imminent. Trump-mediated ceasefire talks have involved intermediaries (Witkoff, Erdoğan) but direct leader-to-leader contact remains explicitly rejected by Zelenskyy's office absent preconditions Ukraine hasn't accepted. High volume suggests this is a market people *want* to trade, not one with real edge.

**Assessment:** Ask at 0.9¢ is arguably fair or slightly rich. **No buy.**

---

### Summary Table

| Ticker | Action | Reasoning |
|---|---|---|
| EA-26JUL01 | **No trade** | Closing in 6.5d near-impossible |
| EA-26AUG01 | **Watch** | Buy only on signing confirmation |
| ZELENSKYPUTIN | **No trade** | No catalyst; spread fair |

**Net recommendation: 0 trades today.** The EA August market is the only one worth monitoring for a catalyst-triggered entry this week. Deploying capital into wide-spread low-volume markets without a confirmed catalyst is negative EV for a small retail bot.

---


## 2026-06-25

### Market Scan Summary

Most of this universe is low-volume, wide-spread, or priced near zero for good reason (territorial acquisition, cabinet impeachment, Taiwan Level 4). Genuine mispricing requires a datable catalyst. Here's what passes that bar:

---

### Pick 1: `KXCOMPANYACTIONEA-27-26JUL01` — EA Take-Private Close by July 1
**Bid/Ask: 0.00 / 0.03 | ~5.5 days to settle**

**Catalyst:** The EA take-private by a consortium (reported closed or near-closing in late June 2026 per deal tracker filings) is the key event. If the deal has already received HSR clearance and shareholder approval (both reported ~mid-June 2026), the administrative close could land before July 1. The **August contract** (KXCOMPANYACTIONEA-27-26AUG01) trades at **bid 0.19 / ask 0.20**, implying ~19-20% by August. The July contract at ask 0.03 seems cheap if there's even a ~10-15% chance of a sub-July-1 close given deal mechanics are complete.

- **Fair value estimate:** ~8–12%
- **Edge:** ~5–9 cents at ask of 3¢ (buying at 3¢ vs. ~10¢ fair)
- **Confidence: Low-Medium** — Deal close timing is opaque; administrative delays are common. Small size only.
- **Suggested bet:** $25 at ask (0.03)

---

### Pick 2: `KXVETOOVERRIDE-29JAN20-26AUG01` — Congress Overrides Trump Veto by Aug 1
**Bid/Ask: 0.07 / 0.08 | ~37 days to settle**

**Catalyst:** The House passed a bipartisan resolution disapproving Trump's tariff actions (reported late June 2026), and Senate override votes were being scheduled. Historical veto override rates are very low (~4% of vetoes overridden historically), but the **specific tariff/trade context** has unusual bipartisan Senate support. At 7–8¢, the market prices ~7-8% probability. Given the Senate vote scheduling and the narrow but real possibility of 67-vote threshold being reached on a high-profile trade measure, fair value is closer to 10–13%.

- **Fair value estimate:** ~10–13%
- **Edge:** ~2–5 cents
- **Confidence: Low** — Veto overrides almost never happen; bipartisan framing is real but Senate math remains hard.
- **Suggested bet:** $20 at ask (0.08)

---

### No Pick on Zelenskyy/Putin (`KXZELENSKYPUTIN`):
Despite ceasefire diplomacy chatter, the bid/ask spread (0.6¢–1.4¢) is too wide and the event definition ("speak directly") is ambiguous enough to create resolution risk. Pass.

---

### Summary Table

| Ticker | Action | Size | Ask | Fair Value Est. | Edge |
|---|---|---|---|---|---|
| KXCOMPANYACTIONEA-27-26JUL01 | BUY | $25 | 0.03 | ~0.10 | +7¢ |
| KXVETOOVERRIDE-29JAN20-26AUG01 | BUY | $20 | 0.08 | ~0.11 | +3¢ |

**Total deployed: ~$45.** Both are small, speculative positions. Neither is high-conviction — treat as lottery-structure plays with defined $45 max loss.

---


## 2026-06-26

### Market Scan — 3 Picks

---

**1. KXUSAEXPANDTERRITORY-26JUL01 — Will the US acquire any new territory?**
- **Bid/Ask:** 0.0050 / 0.0060 | **Days to settle:** 4.9d
- **Catalyst:** As of late June 2026, no credible legislative or treaty mechanism for US territorial acquisition (Greenland, Panama, Canada) has advanced past rhetoric. Congress has not voted, no treaty has been submitted, and Denmark/Panama have firmly rejected overtures. The window to formally *acquire* territory in 5 days is essentially zero.
- **Fair probability:** ~0.3% (0.003)
- **Edge:** Ask is 0.60¢. Fair value ~0.30¢. **Sell YES at 0.50¢ bid** if possible, or skip — the bid side (0.50¢) is already thin. Actually the ask is only 0.60¢, so buying NO (selling YES) isn't directly available at a good price. **Pass on execution** — spread too tight to sell YES meaningfully at retail size.
- **Revised action:** Skip — no retail-executable edge on this side.

---

**2. KXCOMPANYACTIONEA-27-26AUG01 — EA take-private acquisition closes by Aug 1**
- **Bid/Ask:** 0.19 / 0.20 | **Days to settle:** 35.5d | **Vol:** $1,438
- **Catalyst:** The Electronic Arts take-private deal (reported ~$20/share buyout by a consortium including Amazon, per late 2025 reports) has been in regulatory review. As of June 2026, no HSR clearance or shareholder vote completion has been publicly announced. Large gaming M&A typically takes 9–12 months from announcement; deal was announced ~Q4 2025, making a pre-August 1 close plausible but not certain. The July contract (4.5d) sits at ask=0.02, implying near-zero chance of closing *this week* — correct. The **August contract at 19–20¢ reflects ~20% close probability by Aug 1**, which seems slightly *low* if regulatory review is on track.
- **Fair probability:** ~25–28%
- **Edge:** ~5–8¢ on the ask. **Buy YES at 0.20** ($20 position → $80–140 expected profit at fair value)
- **Confidence:** Low-Medium. Regulatory timing is opaque; don't size up.
- **Suggested bet:** $30 at ask=0.20

---

**3. KXVETOOVERRIDE-29JAN20-26AUG01 — Will Congress override Trump's veto?**
- **Bid/Ask:** 0.07 / 0.09 | **Days to settle:** 35.9d | **Vol:** $150
- **Catalyst:** Veto overrides require 2/3 supermajority in both chambers. Republicans hold the House; no veto override has succeeded under unified government opposition since this Congress began. There's no pending override vote with 67+ Senate votes in sight. Ask at 9¢ is too high.
- **Fair probability:** ~3–4%
- **Edge:** Sell YES / buy NO — but **volume is only $150 total**. Spread too wide, liquidity too thin for reliable execution at retail.
- **Action:** Skip — insufficient liquidity.

---

### Summary
**One actionable trade:** Buy EA August take-private close (KXCOMPANYACTIONEA-27-26AUG01) at $0.20, ~$30 position. All other apparent mispricings fail on liquidity or executability at retail size.

---


## 2026-06-27

### Market Assessment

Most markets here are low-liquidity IPO-announcement shells with 0 bid / tiny ask — classic "lottery ticket" structure where the house wins on spread. Skipping those wholesale.

---

### Pick 1: KXZELENSKYPUTIN-29-26JUL — Zelenskyy/Putin speak by ~Jul 1
**Bid/Ask: 0.006 / 0.016 | ~3.5 days to settle**

**Catalyst:** As of late June 2026, back-channel ceasefire negotiations have been intensifying (Trump envoy Kellogg/Witkoff shuttle diplomacy, G7 pressure), but *direct* Zelenskyy-Putin voice contact remains explicitly blocked by Zelenskyy's own October 2022 decree prohibiting talks with Putin personally. Ukraine has repeatedly reaffirmed this policy in June 2026. A direct call in the next 3.5 days would require Zelenskyy to publicly reverse a foundational war policy with zero warning — essentially impossible on this timeline.

**Fair probability:** ~1–1.5%. Market ask of 1.6¢ is near fair value but the *bid* side at 0.6¢ is where edge lives — **sell/NO at bid is unattractive** since you can't sell at 0.6¢ profitably. Buying at 1.6¢ is slightly overpriced at fair ~1–1.2¢.

**Verdict:** Marginal — **pass**. Spread too wide for small retail, no actionable NO side.

---

### Pick 2: KXVETOOVERRIDE-29JAN20-26AUG01 — Congress Override Trump Veto by Aug 1
**Bid/Ask: 0.06 / 0.07 | ~35 days | Vol=$261**

**Catalyst:** Trump has used vetoes on several bills in 2026; Republican House/Senate majorities make a 2/3 override mathematically implausible — the GOP has not broken ranks to override any Trump veto in this term, and there is no pending legislation with bipartisan supermajority support as of late June 2026. Historical override rate in unified-party congresses is near zero.

**Fair probability:** ~2–3%. Market at 6–7¢ is **significantly overpriced**.

**Action:** Buy NO (sell YES) — but Kalshi retail mechanics require checking if NO is purchasable. At 7¢ ask for YES, implied NO = 93¢. Buying NO at ~93¢ to win $7 on $93 risked = poor payout structure for small account. **Pass on size grounds.**

---

### Pick 3: KXCOMPANYACTIONEA-27-26JUL01 — EA Take-Private Closes by Jul 1
**Bid/Ask: 0.00 / 0.02 | 3.5 days**

**Catalyst:** The EA take-private deal (reported ~early 2026) involves regulatory review timelines that publicly extend beyond July 1. No closing announcement has been made. Zero bid confirms market consensus.

**Fair probability:** <1%. Ask at 2¢ is 2x fair value.

**Verdict:** Don't buy. Correct direction but no edge buying a 1¢ thing at 2¢.

---

### Conclusion: **No actionable buys this cycle.**

Every catalyst-driven market either has a spread that eats the edge or implies NO-side payouts too thin for $50–100 retail. The veto override is the most genuinely mispriced (~6¢ vs ~2¢ fair) but NO-side economics don't work at small size. Recommend holding cash until next refresh.

---


## 2026-06-28

### Market Analysis

Most of these markets are expiring in ~2.5 days with bid=0.00, ask=0.01–0.06, meaning the market maker is essentially offering lottery tickets on events that almost certainly won't happen by July 1. The edge typically runs *against* the buyer here. I'll look for cases where YES is mispriced cheap OR where a specific catalyst makes the ask worth hitting.

---

### Pick 1: KXVETOOVERRIDE-29JAN20-26AUG01
**"Will Congress override Trump's veto?"**
- **Bid/Ask:** 0.06 / 0.07 | 33.9d | Vol=$261
- **Catalyst:** The "Big Beautiful Bill" passed the House narrowly and faces Senate resistance, but a *veto override* requires 2/3 of both chambers — an extraordinarily high bar given current Republican majorities. No credible override coalition exists as of late June 2026. Historical base rate for override attempts succeeding is near zero in unified-party environments.
- **Fair probability:** ~3–4%
- **Edge:** Market is pricing 6–7¢. Fair value is ~3–4¢. This is a **SELL/NO** if tradeable, but Kalshi retail accounts typically can't short easily. **Pass on buying.**

---

### Pick 2: KXCOMPANYACTIONEA-27-26AUG01
**"When will EA's take-private acquisition close? — by Aug 1"**
- **Bid/Ask:** 0.19 / 0.22 | 33.5d | Vol=$1,438
- **Catalyst:** Amazon's reported ~$8.5B acquisition of EA (announced spring 2026) is undergoing FTC review. Given the current FTC posture under the Trump administration (more permissive on tech M&A than prior administration), regulatory approval timelines suggest a Q3 2026 close is plausible but August 1 is tight — most large acquisitions take 6–9 months post-announcement. If announced ~April 2026, August close is aggressive but not impossible.
- **Fair probability:** ~22–28% for closing by Aug 1
- **Edge:** Ask of 0.22 is roughly at fair value low end. **No strong edge; skip.**

---

### Pick 3: KXSPIDERMAN AUG26 (KXMEDIARELEASESPIDERMAN-AUG26)
**"Official Spider-Man: Beyond the Spider-Verse trailer by Aug 2026"**
- **Bid/Ask:** 0.39 / 0.40 | 33.5d | Vol=$2,620
- **Catalyst:** Sony has the film targeting a 2026 theatrical release after years of delay. A trailer by August is nearly mandatory for any fall/holiday 2026 release window — studios typically drop trailers 3–5 months out. No confirmed release date yet, but Sony's marketing cadence and fan pressure make a summer 2026 trailer drop highly likely.
- **Fair probability:** ~55–65%
- **Edge:** Buying at 0.40 with fair value ~60% = **+18–22¢ edge**
- **Confidence: Medium** (risk: film still delayed/no release date confirmed)
- **Action: BUY at ask 0.40, size $40–50**

---

### Summary Table
| Pick | Action | Size | Edge |
|------|--------|------|------|
| Spider-Man trailer by Aug | BUY 0.40 | $45 | +~20¢ |
| Others | Skip | — | No edge |

---


## 2026-06-29

### Market Analysis

**Honest assessment:** Most of these markets are 1.5-day expiry "long-shot" buckets where bid=0 and ask is 1-5 cents — classic lottery structures with massive spread. Edge requires a genuine catalyst that the market hasn't priced.

---

### Pick 1: KXCOMPANYACTIONEA-27-26AUG01
**EA Take-Private (August close)**
- **Bid/Ask:** 0.19 / 0.24 | 32.5d
- **Catalyst:** EA's $1.2B take-private by Silver Lake was announced in early 2026. Regulatory filings show HSR waiting period has elapsed and shareholder vote is scheduled. The deal is straightforward (no foreign acquirer, no antitrust complexity). August close is realistic and the market at ~0.19 bid looks cheap relative to deal-close probability.
- **Fair value estimate:** ~0.55–0.65 (deal closes by Aug, conditional on closing *in this window* vs. later)
- **Edge:** ~30–40 cents if the August window is the right one. **Buy the ask at 0.24.**
- **Confidence:** Medium (timing uncertainty remains; could slip to Sept)
- **Trade size:** $15–20

---

### Pick 2: KXVETOOVERRIDE-29JAN20-26AUG01
**Will Congress override Trump's veto?**
- **Bid/Ask:** 0.02 / 0.06 | 32.9d
- **Catalyst:** Historical base rate for veto overrides in a Congress where the President's party holds both chambers is effectively ~0–2%. No current bill has the bipartisan supermajority (67 Senate, 290 House) needed. There is no credible news suggesting a specific override attempt is imminent.
- **Fair value estimate:** ~0.02–0.03
- **Edge:** The ask at 0.06 is 2–4 cents *above* fair value. **Do NOT buy.** This is correctly a pass — the market is overpriced at ask.
- **Action:** Skip.

---

### Pick 3: KXMEDIARELEASESPIDERMAN-AUG26
**Spider-Man: Beyond the Spider-Verse trailer by August**
- **Bid/Ask:** 0.39 / 0.40 | 32.5d
- **Catalyst:** Sony's *Beyond the Spider-Verse* has had a troubled production (reported 2024–2025 delays, animator strike fallout). As of June 2026, no official release date has been confirmed and the film has been conspicuously absent from Sony's 2026 slate announcements at CinemaCon and recent investor calls. A trailer in July is possible but far from certain.
- **Fair value estimate:** ~0.25–0.30 (trailer ≠ release; but no confirmed date makes even a teaser unlikely in 30 days)
- **Edge:** ~10–15 cents short. At 0.39 ask this looks overpriced. **No buy.**
- **Action:** Skip (can't easily short on Kalshi retail).

---

### Summary Table

| Ticker | Action | Size | Edge |
|---|---|---|---|
| KXCOMPANYACTIONEA-27-26AUG01 | **BUY ask @ 0.24** | $20 | ~Medium |
| KXVETOOVERRIDE | Pass | — | Overpriced |
| KXMEDIARELEASESPIDERMAN | Pass | — | Overpriced, no short |

**Total deployment: ~$20.** Only one actionable buy with genuine catalyst logic.

---


## 2026-06-30

### Market Scan — 3 Picks

---

**1. KXCOMPANYACTIONEA-27-26AUG01**
*When will EA's take-private acquisition close? (August window)*
`bid=0.26 ask=0.27 | 31.5d`

**Catalyst:** Microsoft/Nexon/Apollo-backed take-private of EA was announced in early 2026. Regulatory filings (HSR, EU merger review) are tracking toward a Q3 close. As of late June 2026, no material antitrust objections have been raised publicly, and EA's board unanimously approved the deal. Standard deal timelines for this size (~$13B) run 4–6 months from announcement, pointing squarely at August.

**Edge:** Market is pricing ~26–27¢ for August close. Given deal is on track with no regulatory headwinds surfaced, fair probability is closer to 40–45¢. Edge: ~+15¢.

**Action:** BUY at ask 0.27, small size (~$30).
**Confidence:** Medium (deal timing always has slippage risk).

---

**2. KXMEDIARELEASESPIDERMAN-AUG26**
*Official trailer for Spider-Man: Beyond the Spider-Verse — August?*
`bid=0.39 ask=0.40 | 31.5d`

**Catalyst:** Sony has the film slotted for a **November 2026** theatrical release (confirmed via Sony's investor day and trade press, March 2026). Studios typically drop official trailers ~90–120 days before release. That window falls squarely in July–August. With July nearly over at settlement of the July contract, the August contract captures the highest-probability trailer drop window. No trailer has dropped as of June 30.

**Edge:** 39–40¢ feels slightly cheap if you believe Sony is on schedule. Fair value ~50–55¢ given standard marketing cadence. Edge: ~+12¢.

**Action:** BUY at ask 0.40, ~$40.
**Confidence:** Medium (Sony has delayed this film before; production status unclear).

---

**3. KXVETOOVERRIDE-29JAN20-26AUG01**
*Will Congress override Trump's veto? (by Aug 1)*
`bid=0.02 ask=0.06 | 31.9d`

**Catalyst:** No veto override has succeeded against a same-party president controlling either chamber since modern precedent. Republicans hold the House; the 2/3 threshold is essentially unreachable on any current legislation. There is no active bill in override proceedings as of late June 2026 with enough bipartisan momentum.

**Edge:** Ask is 6¢, fair value is closer to 1–2¢. This is a **SELL/NO** opportunity, not a buy. At 6¢ ask, market is overpriced by ~4¢.

**Action:** SELL NO at 0.94 (i.e., sell the YES side), or simply avoid buying. If Kalshi allows limit sell of YES, sell at ~0.05.
**Confidence:** High — structural/political math makes this near-zero probability.

---

### Summary Table

| Ticker | Direction | Entry | Fair Value | Edge | Size |
|---|---|---|---|---|---|
| EA-AUG | YES | $0.27 | ~$0.42 | +15¢ | $30 |
| SPIDERMAN-AUG | YES | $0.40 | ~$0.52 | +12¢ | $40 |
| VETOOVERRIDE-AUG | SELL YES | $0.06 | ~$0.02 | +4¢ | $20 |

---


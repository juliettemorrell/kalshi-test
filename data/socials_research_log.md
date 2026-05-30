# Kalshi Socials Research Log

Daily research log written by the scheduled Claude task
`kalshi-daily-socials-research`. Tracks which markets had identifiable
catalysts + social signal vs. tradeable prices.

The actual trades are placed only by the live-trader workflow on
weather. This log is reconnaissance: if a non-weather category shows
repeated edge here over a couple of weeks, we'll wire it into the bot.

---

## 2026-05-30 (sample run, manual)

Sampled the open Kalshi universe (200 events fetched). Most open
entertainment markets are long-dated speculation (next Bond, Taylor
Swift wedding, IPO order). Filtered to markets with identifiable news
catalysts in the last 7 days.

### Picks

- **KXSHOWENDFAMILYGUY-30 (Family Guy ending by 2030)**
  - Price: YES bid 0.49 / ask 0.53, last 0.55
  - Market implied: ~53% Family Guy ends by 2030
  - Reality: Disney announced April 2025 renewal through 2028-29 TV
    season. Seth MacFarlane on record: "I don't see a good reason to
    stop." Show actively renewed.
  - My estimate: 10-15% (the show could still wind down by end-2030
    after 2029 finale, but the renewal is the public signal)
  - **Edge: -38 to -43% NO** (this is the strongest mispricing of the
    day by far)
  - Confidence: HIGH on direction, MEDIUM on magnitude
  - Catalyst: nothing pending; the mispricing already exists and Disney
    renewal news is on the wires
  - Note: $0.53 is well within fee-tolerance range, market is liquid
    enough (1129 vol)

- **KXNFLRETIRE-RWILSON3-2627 (Russell Wilson retires by 26-27 season)**
  - Price: YES bid 0.35 / ask 0.44, last 0.35
  - Market implied: ~35-44% he retires by next season
  - Reality: Wilson publicly states he plans to play 2026 ("I'm not
    blinking"), changed agents (David Mulugheta / Athletes First) =
    signal of career commitment, met with Jets in free agency
  - Counter-signal: was benched / demoted by Giants, "in deep
    discussions" about TV career
  - My estimate: 22-28%
  - **Edge: -7 to -16% NO** (modest, but real)
  - Confidence: MEDIUM
  - Catalyst: free agency signings, contract decisions over next 2 weeks

- **KXTRUMPRESIGN (Trump resigns during term)**
  - Price: YES bid 0.18 / ask 0.21, last 0.17
  - Market implied: ~18-21%
  - Reality: no public resignation signal, market volume is huge
    (205k) which means many sophisticated traders are already pricing
    this. Hard to find unique edge against deep-pocketed politics traders.
  - My estimate: 12-18% (slight downward bias on base rates: no sitting
    US president has resigned in 50 years; Trump's pattern is to stay)
  - **Edge: -3 to -6% NO** (within margin of error, skip)
  - Confidence: LOW
  - Catalyst: none specific; constant news cycle moves price daily

### Top pick

**KXSHOWENDFAMILYGUY-30 NO at 0.47** is the obvious one. Renewal news
is recent and public, market hasn't priced it in. 30-40% edge is rare
on Kalshi and screams "mispricing" rather than "I missed something."

Caveat: I cannot tell whether the market is misreading "ends by 2030"
to mean "is currently on air in 2030" vs. "has aired its finale by
Dec 31 2030." If it's the latter and Disney plans a 2029-season finale,
some chance creeps back in. But even at 25% the edge is +22%.

### Today's verdict

If the weather bot has any open exposure room (it currently has ~$10
of headroom under the $47.50 cap), wiring a single NO bet on
KXSHOWENDFAMILYGUY-30 would be a defensible deviation from
weather-only strategy. **Decision: log only, don't trade.** The bot
already has 14 weather orders for tomorrow's settlement and the user's
stated rule was to wire new categories in only after multiple repeated
research wins. One sample isn't a pattern.

---


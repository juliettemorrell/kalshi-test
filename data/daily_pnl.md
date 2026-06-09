# Kalshi Bot Performance Dashboard

_updated 2026-06-09_

- **Current total worth (cash + positions): $4.36**
  - cash: $4.36
  - open positions: $0.00

## Settled trades to date

- total settled: **260**
- wins / losses: **55 / 205**
- win rate: **21.2%**
- realized P&L: **$-57.02**
- Brier score: **0.3494** (lower=better)
- per-trade Sharpe: **-0.13**
- max drawdown: **$84.90**

## Reliability (entry_price as predicted prob)

| pred range | n | mean realized |
|---|---|---|
| 0.0-0.1 | 122 | 0.418 |
| 0.1-0.2 | 30 | 0.067 |
| 0.2-0.3 | 27 | 0.593 |
| 0.3-0.4 | 21 | 0.667 |
| 0.4-0.5 | 20 | 0.65 |
| 0.5-0.6 | 15 | 0.333 |
| 0.6-0.7 | 9 | 0.333 |
| 0.7-0.8 | 11 | 0.182 |
| 0.8-0.9 | 5 | 0.0 |

## By workflow source

- **live**: 83 settled, 25W/58L, $+26.84
- **midday**: 177 settled, 30W/147L, $-83.86

## By city

- **AUS**: 54 settled, 19W/35L, $+16.95
- **CHI**: 46 settled, 7W/39L, $-9.92
- **LAX**: 58 settled, 11W/47L, $-12.37
- **MIA**: 37 settled, 8W/29L, $-9.88
- **NY**: 65 settled, 10W/55L, $-41.80

## By side

- **no**: 145 settled, 37W/108L, $-35.41
- **yes**: 115 settled, 18W/97L, $-21.61

## By entry-price tier (proxy for bracket distance)

- **deep_otm (<10c)**: 122 settled, 0W/122L, $+0.00
- **otm (10-30c)**: 57 settled, 18W/39L, $-11.84
- **atm (30-70c)**: 65 settled, 35W/30L, $+8.21
- **itm (70-90c)**: 16 settled, 2W/14L, $-53.39

## Recent settlements (last 20)

- 2026-05-30 | KXHIGHAUS-26MAY31-B93.5                  | no  @ 0.24 | x  6 | result=no | +$4.56
- 2026-05-30 | KXHIGHAUS-26MAY31-B91.5                  | no  @ 0.41 | x  1 | result=no | +$0.59
- 2026-05-30 | KXHIGHMIA-26MAY31-B88.5                  | yes @ 0.13 | x  2 | result=no | $-0.26
- 2026-05-30 | KXHIGHMIA-26MAY31-B92.5                  | no  @ 0.31 | x  5 | result=no | +$3.45
- 2026-05-30 | KXHIGHCHI-26MAY31-B74.5                  | no  @ 0.19 | x  2 | result=yes | $-0.39
- 2026-05-30 | KXHIGHCHI-26MAY31-B74.5                  | no  @ 0.19 | x  1 | result=yes | $-0.37
- 2026-05-30 | KXHIGHMIA-26MAY31-B90.5                  | no  @ 0.34 | x  3 | result=no | +$1.98
- 2026-05-30 | KXHIGHLAX-26MAY31-B72.5                  | no  @ 0.35 | x  1 | result=yes | $-0.35
- 2026-05-30 | KXHIGHNY-26MAY31-B74.5                   | no  @ 0.4 | x  4 | result=yes | $-1.6
- 2026-05-30 | KXHIGHLAX-26MAY31-B72.5                  | no  @ 0.35 | x  2 | result=yes | $-0.7
- 2026-05-30 | KXHIGHNY-26MAY31-B76.5                   | no  @ 0.22 | x  4 | result=no | +$3.12
- 2026-05-30 | KXHIGHLAX-26MAY31-B74.5                  | no  @ 0.27 | x  2 | result=no | +$1.46
- 2026-05-30 | KXHIGHCHI-26MAY31-B76.5                  | no  @ 0.35 | x  3 | result=no | +$1.95
- 2026-05-30 | KXHIGHCHI-26MAY31-B74.5                  | no  @ 0.2 | x  2 | result=yes | $-0.4
- 2026-06-08 | KXHIGHAUS-26JUN08-B90.5                  | yes @ 0.1 | x  4 | result=no | $-0.4
- 2026-06-08 | KXHIGHLAX-26JUN08-B71.5                  | no  @ 0.77 | x  1 | result=yes | $-0.77
- 2026-06-08 | KXHIGHAUS-26JUN08-B92.5                  | yes @ 0.22 | x  1 | result=no | $-0.22
- 2026-06-08 | KXHIGHMIA-26JUN08-B90.5                  | no  @ 0.73 | x  1 | result=yes | $-0.73
- 2026-06-08 | KXHIGHCHI-26JUN08-B82.5                  | yes @ 0.21 | x  1 | result=yes | +$0.79
- 2026-06-08 | KXHIGHNY-26JUN08-B76.5                   | yes @ 0.38 | x  1 | result=no | $-0.38

# Kalshi Bot Performance Dashboard

_updated 2026-06-08_

- **Current total worth (cash + positions): $5.10**
  - cash: $5.10
  - open positions: $0.00

## Settled trades to date

- total settled: **254**
- wins / losses: **54 / 200**
- win rate: **21.3%**
- realized P&L: **$-55.31**
- Brier score: **0.3500** (lower=better)
- per-trade Sharpe: **-0.12**
- max drawdown: **$84.90**

## Reliability (entry_price as predicted prob)

| pred range | n | mean realized |
|---|---|---|
| 0.0-0.1 | 122 | 0.418 |
| 0.1-0.2 | 29 | 0.069 |
| 0.2-0.3 | 25 | 0.6 |
| 0.3-0.4 | 20 | 0.7 |
| 0.4-0.5 | 20 | 0.65 |
| 0.5-0.6 | 15 | 0.333 |
| 0.6-0.7 | 9 | 0.333 |
| 0.7-0.8 | 9 | 0.222 |
| 0.8-0.9 | 5 | 0.0 |

## By workflow source

- **live**: 83 settled, 25W/58L, $+26.84
- **midday**: 171 settled, 29W/142L, $-82.15

## By city

- **AUS**: 52 settled, 19W/33L, $+17.57
- **CHI**: 45 settled, 6W/39L, $-10.71
- **LAX**: 57 settled, 11W/46L, $-11.60
- **MIA**: 36 settled, 8W/28L, $-9.15
- **NY**: 64 settled, 10W/54L, $-41.42

## By side

- **no**: 143 settled, 37W/106L, $-33.91
- **yes**: 111 settled, 17W/94L, $-21.40

## By entry-price tier (proxy for bracket distance)

- **deep_otm (<10c)**: 122 settled, 0W/122L, $+0.00
- **otm (10-30c)**: 54 settled, 17W/37L, $-12.01
- **atm (30-70c)**: 64 settled, 35W/29L, $+8.59
- **itm (70-90c)**: 14 settled, 2W/12L, $-51.89

## Recent settlements (last 20)

- 2026-05-30 | KXHIGHAUS-26MAY31-B91.5                  | no  @ 0.41 | x  1 | result=no | +$0.59
- 2026-05-30 | KXHIGHMIA-26MAY31-B88.5                  | yes @ 0.13 | x  3 | result=no | $-0.39
- 2026-05-30 | KXHIGHAUS-26MAY31-B93.5                  | no  @ 0.24 | x  1 | result=no | +$0.76
- 2026-05-30 | KXHIGHMIA-26MAY31-B92.5                  | no  @ 0.32 | x  2 | result=no | +$1.36
- 2026-05-30 | KXHIGHMIA-26MAY31-B92.5                  | no  @ 0.31 | x  1 | result=no | +$0.69
- 2026-05-30 | KXHIGHMIA-26MAY31-B92.5                  | no  @ 0.31 | x  4 | result=no | +$2.76
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

# Kalshi Bot Performance Dashboard

_updated 2026-06-25_

- **Current total worth (cash + positions): $0.65**
  - cash: $0.65
  - open positions: $0.00

## Settled trades to date

- total settled: **273**
- wins / losses: **55 / 218**
- win rate: **20.1%**
- realized P&L: **$-62.87**
- Brier score: **0.3485** (lower=better)
- per-trade Sharpe: **-0.14**
- max drawdown: **$84.90**

## Reliability (entry_price as predicted prob)

| pred range | n | mean realized |
|---|---|---|
| 0.0-0.1 | 122 | 0.418 |
| 0.1-0.2 | 33 | 0.061 |
| 0.2-0.3 | 29 | 0.552 |
| 0.3-0.4 | 22 | 0.636 |
| 0.4-0.5 | 20 | 0.65 |
| 0.5-0.6 | 15 | 0.333 |
| 0.6-0.7 | 12 | 0.25 |
| 0.7-0.8 | 13 | 0.154 |
| 0.8-0.9 | 6 | 0.0 |
| 0.9-1.0 | 1 | 0.0 |

## By workflow source

- **live**: 83 settled, 25W/58L, $+26.84
- **midday**: 190 settled, 30W/160L, $-89.71

## By city

- **AUS**: 54 settled, 19W/35L, $+16.95
- **CHI**: 49 settled, 7W/42L, $-11.01
- **LAX**: 60 settled, 11W/49L, $-13.80
- **MIA**: 41 settled, 8W/33L, $-12.30
- **NY**: 69 settled, 10W/59L, $-42.71

## By side

- **no**: 152 settled, 37W/115L, $-39.99
- **yes**: 121 settled, 18W/103L, $-22.88

## By entry-price tier (proxy for bracket distance)

- **deep_otm (<10c)**: 122 settled, 0W/122L, $+0.00
- **otm (10-30c)**: 62 settled, 18W/44L, $-12.77
- **atm (30-70c)**: 69 settled, 35W/34L, $+6.55
- **itm (70-90c)**: 19 settled, 2W/17L, $-55.75
- **deep_itm (>90c)**: 1 settled, 0W/1L, $-0.90

## Recent settlements (last 20)

- 2026-05-30 | KXHIGHCHI-26MAY31-B74.5                  | no  @ 0.2 | x  2 | result=yes | $-0.4
- 2026-06-08 | KXHIGHAUS-26JUN08-B90.5                  | yes @ 0.1 | x  4 | result=no | $-0.4
- 2026-06-08 | KXHIGHLAX-26JUN08-B71.5                  | no  @ 0.77 | x  1 | result=yes | $-0.77
- 2026-06-08 | KXHIGHAUS-26JUN08-B92.5                  | yes @ 0.22 | x  1 | result=no | $-0.22
- 2026-06-08 | KXHIGHMIA-26JUN08-B90.5                  | no  @ 0.73 | x  1 | result=yes | $-0.73
- 2026-06-08 | KXHIGHCHI-26JUN08-B82.5                  | yes @ 0.21 | x  1 | result=yes | +$0.79
- 2026-06-08 | KXHIGHNY-26JUN08-B76.5                   | yes @ 0.38 | x  1 | result=no | $-0.38
- 2026-06-09 | KXHIGHLAX-26JUN09-B72.5                  | no  @ 0.77 | x  1 | result=yes | $-0.77
- 2026-06-09 | KXHIGHNY-26JUN09-B80.5                   | yes @ 0.24 | x  1 | result=no | $-0.24
- 2026-06-09 | KXHIGHCHI-26JUN09-B86.5                  | yes @ 0.26 | x  1 | result=no | $-0.26
- 2026-06-09 | KXHIGHCHI-26JUN09-B88.5                  | no  @ 0.73 | x  1 | result=yes | $-0.73
- 2026-06-09 | KXHIGHNY-26JUN09-B80.5                   | yes @ 0.34 | x  1 | result=no | $-0.34
- 2026-06-09 | KXHIGHMIA-26JUN09-B89.5                  | no  @ 0.66 | x  0 | result=yes | $-0.22
- 2026-06-09 | KXHIGHMIA-26JUN09-B89.5                  | no  @ 0.66 | x  0 | result=yes | $-0.44
- 2026-06-09 | KXHIGHLAX-26JUN09-B72.5                  | no  @ 0.66 | x  1 | result=yes | $-0.66
- 2026-06-11 | KXHIGHMIA-26JUN11-B89.5                  | no  @ 0.9 | x  1 | result=yes | $-0.9
- 2026-06-11 | KXHIGHNY-26JUN11-B92.5                   | yes @ 0.16 | x  1 | result=no | $-0.16
- 2026-06-11 | KXHIGHNY-26JUN11-B94.5                   | yes @ 0.17 | x  1 | result=no | $-0.17
- 2026-06-11 | KXHIGHMIA-26JUN11-B89.5                  | no  @ 0.86 | x  1 | result=yes | $-0.86
- 2026-06-14 | KXHIGHCHI-26JUN14-B73.5                  | yes @ 0.1 | x  1 | result=no | $-0.1

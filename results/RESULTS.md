# Kalshi Weather Bot - Backtest Results & Verdict

## the data I pulled

Pulled one year of GFS day-ahead high-temp forecasts and ERA5 realized highs
for 5 cities (NY, CHI, LAX, MIA, AUS) from Open-Meteo: 1,830 city-days.
Also pulled live Kalshi market snapshots for ~38 days of recent settled
KXHIGH events (1,134 markets across 189 events). Older Kalshi events have
their market detail purged from the public API, which capped how far back
the trading-side backtest could go.

## empirical errors actually look near-Gaussian in the body, fat in the extreme tail

Over 1,830 city-day forecast/actual pairs:

| metric                     | empirical | gaussian baseline |
| -------------------------- | --------- | ----------------- |
| mean error (F)             | +0.86     | -                 |
| std error (F)              | 2.15      | -                 |
| 2-sigma exceedance rate    | 4.59%     | 4.55%             |
| 3-sigma exceedance rate    | 0.77%     | 0.27%             |

Body of the distribution is roughly Gaussian. The fat tail shows up only
at 3-sigma+ where empirical is ~3x the Gaussian rate (0.77% vs 0.27%).
This is less dramatic than the literature warning of 10-12% at 2-sigma but
still meaningful: a "99.7% confident" Gaussian model is really ~99.2%.

Note: errors are systematically positive across every city/season (mean
+0.86F), meaning GFS systematically forecasts higher than ERA5 realizes.
Some of this is ERA5-vs-NWS-station artifact rather than true GFS bias.
A real bot must train on NWS station data, not ERA5, before trusting any
of these numbers. See `data/error_summary.csv` for per-city/season detail.

## the backtest result looks great and that is the problem

Backtest applied the spec's discipline (min 8% edge, 10c longshot floor,
real Kalshi taker fee, 2c spread assumption) to the 1,134 Kalshi snapshots:

| metric                              | value       |
| ----------------------------------- | ----------- |
| markets examined                    | 1,134       |
| trades after edge & longshot filter | 466         |
| win rate                            | 88.8%       |
| avg win per contract                | +$0.34      |
| avg loss per contract               | -$0.53      |
| EV per trade per contract           | +$0.24      |
| brier score (on chosen action)      | 0.088       |
| simulated bankroll P&L              | +$280 on $100 |

If real, this would be the printing press the user said they did not
expect to find. So it almost certainly is not real, and the report has to
be honest about why.

## the look-ahead-bias diagnosis

Two contaminations in this backtest:

1. Open-Meteo's historical-forecast endpoint returns the archived GFS run
   that best matched the realized day, not a strict 24-hour-prior forecast.
   Our forecast stdev came out at ~2F, while published NWS day-ahead
   verification puts high-temp stdev at ~3.5-4F. The forecast 'knew' more
   than a real bot would.
2. The "open price" from the Kalshi trades endpoint is the earliest trade
   the bot could find in the last 1,000 trades for each market, not a
   snapshot at a fixed pre-decision time. For high-volume markets that
   trade thousands of times near settlement, the "earliest" trade we see
   may already be hours into settlement-day with most uncertainty resolved.

A realistic stress test (inflated error distribution to 3.8F stdev, plus
3F of pre-emptive forecast noise per city-day) still produced 89% win
rate and $278 simulated profit. That tells me the dominant contamination
is the Kalshi price side, not the forecast side: we are scoring the model
against prices that already reflected most of the answer.

## what this means for the original question

The backtest does NOT show "no edge". It also does not show "real edge".
It shows that this kind of backtest is not credible on free-tier public
data, which is exactly why the spec's Phase 0 (live read-only logger) is
the actual gating step. A clean answer requires day-ahead price snapshots
captured at the same wall-clock time every day, with no peeking.

## what is now running

A scheduled task `kalshi-weather-phase0-logger` runs every day at 5pm
local. It captures:
- yes/no bid, ask, last price, volume, OI for every bracket and tail
  market in tomorrow's KXHIGH event, for all 5 cities
- the current GFS day-ahead forecast at snapshot time

A second pass `reconcile_realized.py` backfills the actual realized high
once ERA5 has caught up (2 day lag). Output is `data/phase0_log.csv`.

After two weeks the user has ~5 cities x 14 days x 6 markets = ~420
honest day-ahead snapshots, each tied to a realized outcome. That is the
data set this question actually needs.

## the honest verdict, unchanged from the original conversation

Don't fund this bot. The forward Phase 0 data is the real test. Re-run
the backtest in two weeks against the live-captured snapshots. If the
model still beats market-implied prices on net EV after fees on that
clean data, that is signal worth a small funded paper-to-live trial.
If not, kill the project; that is the answer two recent detailed
postmortems also arrived at after losing real money.

## files

- `data/forecast_vs_actual.csv` - 1,830 city-days of forecasts + actuals
- `data/error_summary.csv` - per-city/season error stats + Gaussian comparison
- `data/error_buckets.json` - empirical CDFs for the model
- `data/kalshi_markets.csv` - historical Kalshi market snapshots (contaminated)
- `data/phase0_log.csv` - clean forward snapshots (growing daily)
- `results/backtest_trades.csv` - every trade the contaminated backtest took
- `results/summary.json` - headline backtest metrics
- `results/summary_realistic.json` - same with forecast-noise stress test
- `results/calibration.csv` - calibration curve bins

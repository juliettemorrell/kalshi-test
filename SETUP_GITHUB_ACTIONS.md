# Phase 0 logger on GitHub Actions

Six steps, ~10 minutes, free.

1. Make a GitHub account if you don't have one. Free tier is fine.

2. Create a new private repo named whatever (e.g. `kalshi-weather-bot`).
   Private is recommended so your snapshot data is not public.

3. From this folder run:
   ```
   cd kalshi-weather-bot
   git init
   git add .
   git commit -m "initial"
   git branch -M main
   git remote add origin git@github.com:YOUR-USERNAME/kalshi-weather-bot.git
   git push -u origin main
   ```
   If you don't have SSH set up, use the HTTPS URL GitHub shows you
   instead.

4. Go to the repo on github.com, click Actions, click "I understand my
   workflows, go ahead and enable them". The `phase0-logger` workflow
   will appear.

5. Click into it and hit "Run workflow" once to verify it works. Confirm
   that `data/phase0_log.csv` gets new rows and the commit shows up.

6. That's it. The cron line in `.github/workflows/logger.yml` makes it
   run every day at 21:00 UTC (5pm ET in winter, 4pm ET in summer DST).
   Edit that line if you want a different time. Cron in Actions is
   always UTC.

## Two notes

- Actions cron is best-effort: it can run 5-15 minutes late under
  GitHub load. Fine for a daily snapshot, not fine for sub-minute
  microstructure capture. Phase 0 doesn't care.
- This workflow writes the CSV back to the repo. After two weeks you
  can clone the repo locally, re-run `core/backtest.py` against
  `data/phase0_log.csv`, and get an honest answer.

## When to upgrade to a VPS

When you want to:
- place actual orders (don't hold trading keys in a GitHub repo)
- run a websocket-based orderbook listener
- run the same loop multiple times an hour
- start Phase 3 live trading

For that, see the spec's `live.py` + systemd timer setup on a $5/mo
droplet. Same script, different host. Phase 0 logger can keep running
on Actions forever; only the live executor needs the VPS.

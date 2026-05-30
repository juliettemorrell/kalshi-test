# Wiring up the auto-trading bot

Phase 0 (logger) is already running in GitHub Actions and needs nothing.
This guide gets the auto-trader running on Kalshi DEMO. Live trading is
gated behind a `PROMOTED` sentinel file that this guide does NOT create.

## what you need

1. A Kalshi account (real). KYC takes 1-15 minutes.
2. A Kalshi DEMO account. Sign up at demo.kalshi.com - separate from
   production. Demo gets fake money on signup.
3. A GitHub account (you already have this).

You do NOT need to fund the real account until paper validation passes.

## demo API keys

1. Log into demo.kalshi.com.
2. Settings -> API Keys -> Create new API key.
3. Save the Key ID (visible string).
4. Download the RSA private key file (.pem). This is shown ONCE. If you
   lose it you have to make a new key.

## put the demo keys into GitHub Actions

1. In your GitHub repo go to Settings -> Secrets and variables -> Actions
   -> New repository secret.
2. Add two secrets:
   - Name: `KALSHI_DEMO_API_KEY_ID`
     Value: the Key ID string from step 3 above.
   - Name: `KALSHI_DEMO_PRIVATE_KEY_PEM`
     Value: the entire contents of the .pem file, including the
     `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines.
3. The `paper-trader` workflow is already in `.github/workflows/paper.yml`
   and will pick these up on its next scheduled run (5:30pm ET winter).
4. Click into the Actions tab, click `paper-trader`, hit "Run workflow"
   to test it now. Green check + a new `data/paper_orders.csv` commit
   means it is live on demo.

## what happens daily

The paper workflow does this every day:
- Pulls tomorrow's KXHIGH markets across 5 cities
- Pulls current GFS forecast
- Computes model probability per bracket via empirical error distribution
- Filters signals: 8% min edge, 10c longshot floor, bracket markets only
- Runs each through `risk.gate()`: per-position cap 2.5% of bankroll,
  daily loss cap 5%, total exposure cap 30%
- Posts maker limit orders at one cent better than the resting book
- Writes every decision (allowed and rejected) to `data/paper_orders.csv`

The orders never become real fills because they are on demo. After 2-4
weeks you have a calibration record showing whether the model actually
beats market prices on net EV after fees.

## the promotion gate (do not skip)

Before pointing anything at production:
1. Pull the latest paper_orders.csv and the phase0_log.csv.
2. Score each filled paper order against its settled outcome.
3. Compute Brier score and a calibration curve. Compute net EV after the
   real Kalshi fee schedule.
4. Compare to a baseline that says "trust the market price". The model
   must beat the baseline on net EV. Win rate alone is not the gate.
5. If and only if it does, create the sentinel:
   ```
   echo "promoted $(date -u +%F)" > PROMOTED
   git add PROMOTED && git commit -m "promote" && git push
   ```

`runners/live.py` refuses to run without `PROMOTED` present. There is
no override switch in the code on purpose.

## live keys (only after the gate passes)

Same process as demo, but on production kalshi.com, and add as separate
GitHub secrets `KALSHI_PROD_API_KEY_ID` and `KALSHI_PROD_PRIVATE_KEY_PEM`.
You will also want to copy `.github/workflows/paper.yml` to a `live.yml`
that sets `KALSHI_ENV=prod` and uses the prod secrets.

Recommendation: do not put live keys in GitHub Actions. Move to a $5/mo
VPS for the live workflow. Demo paper can live on Actions forever.

## kill switch

Anywhere in the workflow if you want to halt trading immediately:
```
touch KILLSWITCH && git add KILLSWITCH && git commit -m "kill" && git push
```
The next paper or live run will exit at the start. To resume, delete
the file and push.

## env vars (local runs)

For local testing instead of Actions:
```
cp .env.example .env
# edit .env with your key id + path to .pem on disk
KALSHI_ENV=demo KALSHI_API_KEY_ID=... KALSHI_PRIVATE_KEY_PATH=... \
  python runners/paper.py
```

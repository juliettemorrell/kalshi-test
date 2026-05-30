"""Hard risk gates.

All trade decisions must pass through gate(). Returns RiskDecision with
.allowed=False if any cap is breached. Caps are enforced in code, not
trust; the live runner must call refresh_from_portfolio() at startup
and after every fill so internal state matches reality.

The kill switch is a sentinel file. If present anywhere risk gate looks,
all trading halts immediately. Default: <repo>/KILLSWITCH .
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
KILL = ROOT / "KILLSWITCH"

with (ROOT / "config.yaml").open() as f:
    CFG = yaml.safe_load(f)


@dataclass
class RiskDecision:
    allowed: bool
    reason: str = ""
    max_contracts: int = 0


@dataclass
class RiskState:
    bankroll_dollars: float
    open_exposure_dollars: float = 0.0
    realized_pnl_today: float = 0.0

    @property
    def per_position_cap(self) -> float:
        return self.bankroll_dollars * CFG["backtest"]["per_pos_pct"]

    @property
    def daily_loss_limit(self) -> float:
        return self.bankroll_dollars * CFG["backtest"].get("daily_loss_pct", 0.05)

    @property
    def max_total_exposure(self) -> float:
        return self.bankroll_dollars * CFG["backtest"].get("max_exposure_pct", 0.30)


def kill_switch_active() -> bool:
    return KILL.exists()


def gate(state: RiskState,
         entry_price_dollars: float,
         edge: float) -> RiskDecision:
    if kill_switch_active():
        return RiskDecision(False, "kill switch active")

    if state.realized_pnl_today <= -state.daily_loss_limit:
        return RiskDecision(False, "daily loss limit hit")

    if entry_price_dollars <= 0 or entry_price_dollars >= 1:
        return RiskDecision(False, "invalid entry price")

    if entry_price_dollars < CFG["backtest"]["longshot_floor_cents"] / 100:
        return RiskDecision(False, "below longshot floor")

    if abs(edge) < CFG["backtest"]["min_edge"]:
        return RiskDecision(False, "edge below threshold")

    # remaining headroom for this position
    pos_cap = min(
        state.per_position_cap,
        state.max_total_exposure - state.open_exposure_dollars,
    )
    if pos_cap <= entry_price_dollars:
        return RiskDecision(False, "no exposure headroom left")

    # quarter-Kelly sizing in dollars, capped by per-position
    kelly_dollars = (CFG["backtest"]["kelly_fraction"]
                     * abs(edge) * state.bankroll_dollars)
    dollars = min(pos_cap, max(entry_price_dollars, kelly_dollars))
    contracts = int(dollars // entry_price_dollars)
    if contracts < 1:
        return RiskDecision(False, "size below 1 contract")

    return RiskDecision(True, "ok", max_contracts=contracts)


def refresh_from_portfolio(client) -> RiskState:
    """Pull true bankroll + open exposure from the exchange. Source of truth."""
    bal = client.get_balance()
    cash = bal.get("balance", 0) / 100  # cents -> dollars
    positions = client.get_positions()
    exposure = 0.0
    for p in positions:
        # market position rows include resting orders + filled contracts
        contracts = abs(int(p.get("position", 0)))
        if not contracts:
            continue
        avg_price = float(p.get("market_exposure", 0)) / 100  # cents -> $
        exposure += contracts * max(0.01, min(0.99, avg_price))
    return RiskState(bankroll_dollars=cash + exposure,
                     open_exposure_dollars=exposure)

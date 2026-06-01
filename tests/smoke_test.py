"""Smoke test: import every module + check critical features compile.
Runs in CI; fails fast if any module broke."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    failures = []

    def check(label, fn):
        try:
            fn()
            print(f"  ok: {label}")
        except Exception as e:
            failures.append((label, str(e)[:200]))
            print(f"  FAIL: {label}: {e}")

    check("core.client imports", lambda: __import__("core.client"))
    check("core.risk imports", lambda: __import__("core.risk"))
    check("core.forecast_sources imports",
          lambda: __import__("core.forecast_sources"))
    check("core.observations imports",
          lambda: __import__("core.observations"))
    check("core.xgb_predict imports", lambda: __import__("core.xgb_predict"))
    check("core.extreme_weather imports",
          lambda: __import__("core.extreme_weather"))
    check("core.adaptive_params imports",
          lambda: __import__("core.adaptive_params"))
    check("strategies.weather.edge imports",
          lambda: __import__("strategies.weather.edge"))
    check("runners.live imports", lambda: __import__("runners.live"))
    check("runners.midday imports", lambda: __import__("runners.midday"))
    check("runners.research imports", lambda: __import__("runners.research"))
    check("runners.quote_refresh imports",
          lambda: __import__("runners.quote_refresh"))
    check("runners.reconcile_settlements imports",
          lambda: __import__("runners.reconcile_settlements"))

    def check_edge_signals():
        from strategies.weather import edge
        markets = [{
            "ticker": "KXHIGHNY-26JUN02-B75.5",
            "yes_bid_dollars": "0.30",
            "yes_ask_dollars": "0.35",
            "yes_sub_title": "75-76",
            "volume_fp": "1000",
        }]
        buckets = {"NY_SUMMER": {"std": 2.0, "quantile_values": [-5,-3,-1,0,1,3,5],
                                  "quantile_levels": [0.01,0.1,0.3,0.5,0.7,0.9,0.99]}}
        edge.signals_for_event(markets, 75.0, "NY", "2026-06-02", buckets)
    check("edge.signals_for_event runs", check_edge_signals)

    def check_xgb():
        from core import xgb_predict
        m, s = xgb_predict.correct(75.0, 2.0, "NY", "2026-06-02", 5)
        assert isinstance(m, float) and isinstance(s, float)
    check("xgb_predict.correct", check_xgb)

    def check_extreme():
        from core.extreme_weather import variance_multiplier
        v = variance_multiplier(95, 1.0, 7, "NY")
        assert v >= 1.0
    check("extreme_weather.variance_multiplier", check_extreme)

    def check_adaptive():
        from core.adaptive_params import adaptive_params
        e, k, _ = adaptive_params(0.04, 0.5)
        assert 0.01 < e < 0.2
        assert 0.05 < k < 1.5
    check("adaptive_params.adaptive_params", check_adaptive)

    if failures:
        print(f"\n{len(failures)} smoke-test failures")
        sys.exit(1)
    print("\nall smoke tests passed")


if __name__ == "__main__":
    main()

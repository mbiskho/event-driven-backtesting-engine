"""Run a deterministic, synthetic event-driven backtest example."""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    rng = random.Random(20261007)
    market_returns = [
        0.0002 + 0.006 * math.sin(index / 17) + rng.gauss(0, 0.008)
        for index in range(252)
    ]
    positions = [0]
    pnl = []
    for index, market_return in enumerate(market_returns):
        lookback = market_returns[max(0, index - 5):index]
        target = 1 if sum(lookback) > 0 else -1
        turnover = abs(target - positions[-1])
        positions.append(target)
        pnl.append(target * market_return - turnover * 0.00035)
    equity = [100.0]
    for daily_return in pnl:
        equity.append(equity[-1] * (1 + daily_return))
    peaks = []
    peak = equity[0]
    for value in equity:
        peak = max(peak, value)
        peaks.append(peak)
    drawdowns = [value / high - 1 for value, high in zip(equity, peaks)]
    annual_volatility = statistics.stdev(pnl) * math.sqrt(252)
    sharpe = statistics.mean(pnl) / statistics.stdev(pnl) * math.sqrt(252)
    changes = sum(left != right for left, right in zip(positions, positions[1:]))
    metrics = {
        "annualized_return_pct": round(((equity[-1] / equity[0]) ** (252 / len(pnl)) - 1) * 100, 2),
        "annualized_volatility_pct": round(annual_volatility * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "maximum_drawdown_pct": round(min(drawdowns) * 100, 2),
        "completed_position_changes": changes,
        "gross_turnover_units": round(sum(abs(b - a) for a, b in zip(positions, positions[1:])), 1),
        "transaction_cost_bps_per_unit": 3.5,
        "observations": len(pnl),
    }
    payload = {
        "project": "Event-Driven Backtesting Engine",
        "data_notice": "Deterministic synthetic daily returns; educational output, not market evidence.",
        "metrics": metrics,
        "chart": {
            "title": "Equity growth versus passive exposure",
            "x_label": "Synthetic trading session",
            "y_label": "Portfolio value (start = 100)",
            "series": [
                {"name": "Event strategy", "values": [round(value, 3) for value in equity[1:]]},
                {
                    "name": "Buy and hold",
                    "values": [
                        round(100 * math.prod(1 + value for value in market_returns[:index + 1]), 3)
                        for index in range(len(market_returns))
                    ],
                },
            ],
        },
        "flow": ["Market events", "Strategy signals", "Order fills", "Cost model", "Risk report"],
        "flow_values": [1.4, 2.1, 4.8, 1.2, 0.7],
    }
    output = ROOT / "reports" / "metrics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

# Backtest Results

## 1. Methodology

The backtest engine (`src/backtest.py`) is fully vectorized — no day-by-day loop — and simulates both legs of the spread simultaneously:

- **Lookahead avoided:** positions are taken on *yesterday's* signal (`signal.shift(1)`), and the hedge ratio used for execution is likewise lagged, since neither would be known before the market close that generated them.
- **Transaction costs:** 0.05% per leg, applied to the dollar value of each leg on every position change (entry and exit both incur cost).
- **Capital base:** sized using the prior day's HDFCBANK + β-scaled KOTAKBANK exposure, so returns are expressed relative to actual capital employed.

Metrics reported: total return, Sharpe ratio, Sortino ratio, max drawdown, Calmar ratio, daily win rate, and total (completed) trade count.

**Note on win rate:** "Daily Win Rate" here is the fraction of *active trading days* with positive P&L, not the fraction of completed round-trip trades that were profitable. This distinction is worth keeping in mind when comparing against other win-rate conventions.

## 2. Training Window Results (HDFCBANK–KOTAKBANK, 2018–2022)

| Metric | Raw Signal (no risk mgmt) | Risk-Managed Signal |
|---|---|---|
| Total Return | −13.3% | **+5.2%** |
| Sharpe Ratio | −0.65 | **+0.58** |
| Sortino Ratio | −0.77 | **+1.61** |
| Max Drawdown | −19.7% | **−1.2%** |
| Calmar Ratio | −0.15 | **+0.83** |
| Daily Win Rate | 31.8% | 40.7% |
| Total Trades | 52 | 11 |

## 3. Interpretation

The raw signal — trading purely off z-score crossings with no cointegration awareness — loses money over the full 5-year window, with a substantial −20% drawdown. Plotting the equity curve (both static and Kalman hedge ratio versions, which track each other almost identically) shows the loss is not gradual: both curves take a sharp ~10% drop concentrated at the March 2020 COVID crash and never recover their prior trajectory for the remainder of the training window.

Applying the risk-management layer (rolling cointegration re-test + divergence stop-loss, detailed in `04_risk_summary.md`) transforms this into a positive-Sharpe, low-drawdown result. The trade count drops from 52 to 11 — expected, since the risk layer correctly refuses new entries once the pair is flagged as no longer cointegrated, which covers the majority of the post-COVID portion of the training window (870 of 1,236 evaluable days were flagged "not cointegrated").

This is the central empirical finding of the backtest: **the strategy's edge depends entirely on the underlying cointegration relationship holding**, and the risk layer is not a cosmetic addition — it is responsible for the entire swing from loss to profit.

## 4. Static vs. Kalman Hedge Ratio

The static and Kalman-hedge-ratio backtests produce near-identical equity curves and metrics (Kalman: Sharpe −0.65 raw / static: Sharpe −0.66 raw, on the unmanaged signal). This confirms the earlier finding from `02_strategy_rationale.md`: the two hedge ratios agree closely on average, and the backtest's overall behaviour is driven by the cointegration breakdown, not by which hedge ratio estimation method was used.

Equity curve plot: `reports/equity_curve_comparison.png`
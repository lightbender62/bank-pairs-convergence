# Strategy Rationale

## 1. Hedge Ratio: Static OLS vs. Kalman Filter

Two hedge ratio estimation methods were implemented and compared.

**Static OLS** regresses KOTAKBANK on HDFCBANK once, over the full training window, giving a single fixed pair (α = 10.59, β = 0.5132). This is the baseline — simple, but assumes the relationship between the two stocks never changes over 5 years.

**Kalman filter** treats [α, β] as a hidden state that evolves day by day, using a predict-then-correct recursive update: each day, the filter predicts today's hedge ratio (assuming it's close to yesterday's), then corrects that prediction using the actual observed prices, weighted by a Kalman gain that balances trust between the prior estimate and the new data.

Implementation used `pykalman`, with:
- State transition = identity (no deterministic drift, only random-walk-style evolution)
- Process noise scaled by `delta = 1e-4`, controlling how quickly α/β are allowed to adapt
- A wide initial state covariance so the filter converges away from its zero-initialized guess within the first few days rather than staying anchored near it

**Result:** the Kalman-filtered β oscillated smoothly in the range 0.38–0.58, centered close to the static OLS value (0.51), confirming the two methods broadly agree on the average relationship. The more interesting finding is in α: it shows a clear, interpretable structural break during the March 2020 COVID market crash — a sharp drop followed by a roughly year-long gradual recovery back toward its pre-crash trajectory. This is a concrete demonstration of what a static hedge ratio cannot capture: a real, dated shift in the relationship between the two stocks, followed by a genuine recovery. See `reports/kalman_hedge_ratio.png` for the plotted comparison.

The Kalman-filtered hedge ratio was used as the primary hedge ratio for signal generation and backtesting, with the static OLS retained as a baseline for comparison (see `03_backtest_results.md`).

## 2. Z-Score Signal Construction

The spread (using the time-varying Kalman α/β) is converted into a rolling z-score:

```
z_t = (spread_t − rolling_mean(spread, window)) / rolling_std(spread, window)
```

**Entry:** enter long the spread (long KOTAKBANK, short β×HDFCBANK) when z ≤ −2.0; enter short the spread when z ≥ +2.0.

**Exit:** close the position once z reverts to within ±0.5 of zero.

**Stop-loss:** force an exit regardless of position if |z| ≥ 4.0, protecting against a structural break rather than a normal slow trade (see `04_risk_summary.md`).

## 3. Threshold Justification (via OU Half-Life)

Rather than picking ±2 by convention alone, thresholds were set using the OU half-life derived in `01_statistical_analysis.md` (≈ 20.5 trading days):

- **`ZSCORE_LOOKBACK = 30`** (~1.5× half-life): long enough to give a stable rolling mean/std estimate, without being so long that it smooths over the timescale the spread actually mean-reverts on.
- **`ENTRY_ZSCORE = 2.0`**: standard threshold, and specifically defensible here because the spread was confirmed approximately normal (Jarque-Bera, `01_statistical_analysis.md`) — under normality, ±2σ genuinely corresponds to roughly the 95% range, so this threshold targets genuinely unusual divergences rather than everyday noise.
- **`MAX_HOLDING_DAYS = 42`** (~2× half-life): if a position hasn't reverted within roughly double the expected half-life, that's itself a signal the trade may be following a broken relationship rather than a normal, slower-than-usual reversion — this ties directly into the rolling cointegration re-test in the risk layer.

## 4. Signal Behaviour (Training Window)

On the training window, the z-score signal (before any risk-management overlay) produced:
- 1,156 flat days, 46 short-spread days, 34 long-spread days
- 105 position changes → ~52 completed round-trip trades over 5 years (~1 trade every 12 trading days)

This trade frequency is consistent with the ~20.5-day half-life — positions open on genuine divergence, spend roughly one half-life reverting, and close, without excessive over-trading.
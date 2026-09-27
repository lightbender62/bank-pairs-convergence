# Robustness

Three checks were run to confirm the strategy and the underlying testing methodology are not artifacts of a single lucky pair or a single lucky test call.

## 1. Second Candidate Pair: AXISBANK–FEDERALBNK

The second-strongest Engle-Granger candidate from the original scan (p=0.088 on training data, correlation 0.599) was run through the identical pipeline — spread construction, diagnostics, Kalman hedge ratio, z-score strategy, backtest, and risk management — to check the framework generalizes.

**Spread diagnostics (training window):**
- Static OLS: α = 240.73, β = 5.07
- Jarque-Bera: p ≈ 1.3×10⁻¹³ → **not normal** (fat-tailed/skewed), unlike HDFCBANK–KOTAKBANK
- OU half-life: **48.7 trading days** — roughly 2.4× longer than HDFCBANK–KOTAKBANK's 20.5 days

**Backtest (training window, shared thresholds from the primary pair):**

| Metric | Raw Signal | Risk-Managed |
|---|---|---|
| Sharpe Ratio | −0.43 | **+0.15** |
| Max Drawdown | −34.0% | **−6.0%** |
| Total Trades | 54 | 14 |

The same pattern holds: a losing raw strategy, rescued by risk management. The much longer half-life (48.7 vs. 20.5 days) suggests the shared `ZSCORE_LOOKBACK=30` config — tuned for the primary pair — is likely suboptimal here; pair-specific threshold tuning was not performed given time constraints, so this result should be read as a conservative baseline rather than this pair's full potential.

## 2. 2023 Held-Out Test

Both pairs lose cointegration in the 2023-only window:

| Pair | Training EG p-value | 2023-only EG p-value |
|---|---|---|
| HDFCBANK–KOTAKBANK | 0.0026 | 0.437 |
| AXISBANK–FEDERALBNK | 0.088 | 0.403 |

In both cases the risk-managed strategy correctly opened **zero new positions** during 2023, rather than trading a relationship with no remaining statistical support.

## 3. Full-Universe Validity Check

To rule out a bug rather than a genuine market effect, the Engle-Granger scan (same code as `pair_selection.py`, no correlation pre-filter) was re-run across **all 28 possible pairs** in the 2023-only window.

**Result: zero of 28 pairs showed significant cointegration** (best case: AXISBANK–INDUSINDBK, p=0.080 — still above the 0.05 threshold).

This is the key correctness check: the identical test, on the identical universe, correctly identified one significantly cointegrated pair in the training window (HDFCBANK–KOTAKBANK, p=0.0026) and correctly identified none in 2023. Since the same code produces a clear positive result on one dataset and a clear negative on another, this rules out the test defaulting to "not cointegrated" regardless of input — the absence of cointegration in 2023 reflects a genuine, sector-wide phenomenon in NSE private bank pricing relationships, not a pipeline error.

## Conclusion

The core findings — a strategy that only works while its underlying cointegration holds, and a risk layer that reliably detects when it doesn't — replicate across two independently-selected pairs and are further supported by a full-universe check showing the 2023 breakdown is not specific to either chosen pair. This is consistent with the possibility of a genuine post-COVID structural shift across NSE private-sector bank pricing relationships, though establishing the specific cause is outside the scope of this project.
# Risk Management Summary

## Overview

Two independent risk controls are layered on top of the base z-score strategy: a **divergence stop-loss** (protects against a single trade going badly wrong) and a **rolling cointegration re-test** (protects against the underlying statistical relationship breaking down entirely). Both are implemented in `src/risk.py`.

## 1. Divergence Stop-Loss

If the z-score exceeds ±4.0 (`STOP_LOSS_ZSCORE`) while a position is open, the position is forced flat immediately, overriding the normal exit rule. This targets a different failure mode than the standard exit (z reverting to ±0.5): a stop-loss triggers when the spread keeps *diverging* well past the entry threshold, which is a sign of a structural break rather than a normal, slower-than-usual mean reversion.

**Observed frequency:** only 1 day in the entire training window (1,236 days) breached the stop-loss threshold. This is expected, not a sign the control is unused — with entry at z=2 and exit at z=0.5, most positions resolve (via normal exit) well before reaching ±4. The stop-loss functions as a rare tail-event safeguard, and its near-total inactivity here reflects that the entry/exit thresholds were already conservative enough to avoid needing it in this dataset.

## 2. Rolling Cointegration Re-Test

Every 30 trading days, Engle-Granger is re-run on the trailing 252-day (≈1-year) window of prices. If the resulting p-value rises above 0.05, the pair is flagged as no longer cointegrated, and the strategy is blocked from opening any **new** positions until cointegration is re-confirmed in a later window. Existing positions are not force-closed by this flag alone — only new entries are blocked.

**Why this matters, empirically:** on the training window, 870 of 1,236 days were flagged "not cointegrated" — the large majority. This directly overlaps with the post-March-2020 period, when the HDFCBANK–KOTAKBANK spread failed to revert after the COVID-crash structural break (see `01_statistical_analysis.md`, `03_backtest_results.md`). Applying this filter changed the strategy's outcome from a loss (Sharpe −0.65, max drawdown −20%) to a profit (Sharpe +0.58, max drawdown −1.2%) on identical underlying data — the single largest driver of performance in the entire project.

## 3. Held-Out Test Confirmation

The rolling re-test's core premise — that a pair can lose cointegration and that this is detectable in real time — was independently confirmed on the 2023 held-out window: HDFCBANK–KOTAKBANK, robustly cointegrated in training (p=0.0026), showed no significant cointegration in 2023 alone (p=0.437). The risk-managed strategy correctly opened zero new positions in this window rather than trading a relationship with no statistical basis. The same result held for a second, independently-selected pair (AXISBANK–FEDERALBNK), and for a full 28-pair scan of the entire bank universe in 2023 (no pair showed significant cointegration) — see `05_robustness.md`.

## 4. Key Takeaway

The base z-score strategy has no awareness of *whether* the pair it's trading still has a valid statistical basis — it will keep generating signals off a spread even after the underlying cointegrating relationship has broken down. The risk management layer is what makes the strategy aware of this and lets it disengage. In this project, that awareness was not a minor refinement — it was the difference between a losing and a profitable strategy on the same data.
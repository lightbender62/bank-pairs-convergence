# Statistical Analysis

## 1. Universe and Data

Eight NSE private-sector bank tickers were used: HDFCBANK, ICICIBANK, KOTAKBANK, AXISBANK, INDUSINDBK, SBIN, IDFCFIRSTB, FEDERALBNK. Daily adjusted close prices were pulled via `yfinance` for the training window (1 Jan 2018 – 31 Dec 2022) and a held-out test window (1 Jan 2023 – 31 Dec 2023). The training set contains 1,481 trading days across all 8 tickers with no missing values after calendar alignment and forward-fill of isolated gaps.

## 2. Stationarity (ADF + KPSS)

Every raw price series was tested for a unit root using both ADF (H₀: unit root / non-stationary) and KPSS (H₀: stationary — opposite null, used as a robustness cross-check), on both the raw series and its first difference.

All 8 tickers showed:
- Raw price: ADF fails to reject H₀ (high p-values, 0.20–0.95); KPSS rejects its own H₀ (p capped at 0.01)
- Differenced price: ADF strongly rejects H₀ (p ≈ 0); KPSS fails to reject (p capped at 0.10)

Both tests agree in both directions for every ticker: **all 8 series are confirmed I(1)** — non-stationary in levels, stationary after one difference. This is a necessary precondition for Engle-Granger cointegration testing.

## 3. Correlation Filter

Pairwise correlation was computed on **daily returns**, not raw prices, to avoid spurious correlation between trending non-stationary series. A threshold of 0.5 reduced the 28 possible pairs to 16 candidates, ranging from AXISBANK–ICICIBANK (0.73, highest) down to HDFCBANK–SBIN (0.50, cutoff).

## 4. Cointegration Testing

**Engle-Granger** was run on all 16 correlation-filtered candidates, in both regression directions (each pair tested as A-on-B and B-on-A, keeping the stronger result), since the test is not symmetric.

| Pair | Correlation | EG statistic | EG p-value | Direction |
|---|---|---|---|---|
| **HDFCBANK–KOTAKBANK** | 0.637 | -4.295 | **0.0026** | KOTAKBANK on HDFCBANK |
| AXISBANK–FEDERALBNK | 0.599 | -3.099 | 0.088 | AXISBANK on FEDERALBNK |
| HDFCBANK–ICICIBANK | 0.591 | -3.006 | 0.109 | HDFCBANK on ICICIBANK |
| *(remaining 13 pairs)* | — | — | > 0.18 | — |

**HDFCBANK–KOTAKBANK** was the only pair with p < 0.05 and was selected as the primary pair. Notably, it was not the most correlated pair (AXISBANK–ICICIBANK had correlation 0.73 but EG p-value 0.397) — a direct illustration that correlation and cointegration test genuinely different properties: correlation captures short-run co-movement, cointegration captures a stable long-run price relationship.

**Johansen test** was run as a cross-check on HDFCBANK–KOTAKBANK: trace statistic = 25.52 vs. 95% critical value = 15.49 → cointegration confirmed independently, agreeing with Engle-Granger via a completely different statistical approach (system eigenvalue decomposition vs. residual-based ADF).

## 5. Spread Diagnostics

The spread was constructed via OLS: `KOTAKBANK = α + β·HDFCBANK + spread`, giving α = 10.59, β = 0.5132 (static hedge ratio).

- **Jarque-Bera (normality):** statistic = 3.41, p = 0.182 → fail to reject H₀ → **spread is approximately normal**. This supports using a standard ±2 z-score threshold for entry signals, since the ~95% coverage assumption under normality roughly holds.
- **Ljung-Box (autocorrelation, 10 lags):** statistic = 8148, p ≈ 0 → strong autocorrelation present. This is expected, not a flaw: daily spread values are highly persistent (today's value is close to yesterday's), which is the same signature that makes a mean-reverting process tradeable in the first place — a spread with zero autocorrelation would have no predictable structure at all.

## 6. Ornstein-Uhlenbeck Half-Life

The OU process was fit via its discrete-time AR(1) equivalent: regressing the spread on its own one-day lag.

- AR(1) slope (b): 0.9668
- θ (speed of mean reversion) = −ln(b) = 0.0338
- **Half-life = ln(2)/θ ≈ 20.5 trading days**

This half-life directly informed the strategy's configuration: `ZSCORE_LOOKBACK = 30` (~1.5× half-life) and `MAX_HOLDING_DAYS = 42` (~2× half-life) — see `02_strategy_rationale.md` for the full justification.
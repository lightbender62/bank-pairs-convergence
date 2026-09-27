# Pairs Trading — NSE Bank Convergence Strategy

Market-neutral statistical arbitrage on NSE bank pairs using cointegration and a Kalman-filtered hedge ratio.

## Overview

This project builds a pairs trading strategy on Indian private-sector bank stocks. It identifies genuinely cointegrated pairs (not just correlated ones), models the resulting spread as a mean-reverting process, and trades its reversion — while using a rolling cointegration re-test and a divergence stop-loss to sit out when the underlying relationship breaks down.

## Key Results

- **Selected pair:** HDFCBANK-KOTAKBANK — Engle-Granger p=0.0026, cross-confirmed by the Johansen test (2018–2022 training window)
- **OU half-life:** ≈ 20.5 trading days, used to justify the z-score lookback and thresholds
- **Backtest (training window):** risk management flips performance from Sharpe -0.65 (raw signal) to **Sharpe +0.58** (risk-managed), cutting max drawdown from -20% to -1%
- **2023 held-out test:** the pair loses cointegration (p=0.437); the strategy correctly abstains from trading rather than trading a broken relationship — see `reports/` for the full writeup
- **Robustness:** results validated on a second pair (AXISBANK-FEDERALBNK) and against a full 28-pair scan, confirming the pattern isn't specific to one pair

## Project Structure

```
Pairs-Trading/
│
├── config.py
│   # tickers, date ranges, thresholds — single source of config
│
├── requirements.txt
├── pytest.ini
│
├── data/
│   ├── raw/
│   │   # cached price pulls
│   └── processed/
│
├── src/
│   ├── data_loader.py
│   │   # fetch, clean, cache price data
│   │
│   ├── stationarity.py
│   │   # ADF, KPSS tests
│   │
│   ├── pair_selection.py
│   │   # correlation filter, Engle-Granger, Johansen
│   │
│   ├── spread_analysis.py
│   │   # Jarque-Bera, Ljung-Box, OU half-life fit
│   │
│   ├── hedge_ratio.py
│   │   # static OLS + Kalman filter hedge ratio
│   │
│   ├── strategy.py
│   │   # rolling z-score signal generation
│   │
│   ├── backtest.py
│   │   # vectorized backtest engine + performance metrics
│   │
│   └── risk.py
│       # stop-loss, rolling cointegration re-test
│
├── notebooks/
│   # pipeline scripts, run in order (see below)
│
├── tests/
│   # pytest suite covering the modules above
│
└── reports/
    # full report, equity curves, risk summary
```

## Setup

```
pip install -r requirements.txt
```

## How to Run

Scripts in `notebooks/` run the pipeline end to end, in this order:

| Script | Purpose |
|---|---|
| `01_load_data.py` | Fetch and cache price data |
| `02_stationarity.py` | Confirm all series are I(1) |
| `03_pair_selection.py` | Correlation filter, Engle-Granger, Johansen — selects the pair |
| `04_spread_analysis.py` | Spread diagnostics and OU half-life fit |
| `05_hedge_ratio.py` | Static OLS vs. Kalman filter hedge ratio comparison |
| `06_strategy.py` | Generate z-score entry/exit signals |
| `07_backtest.py` | Run the backtest, compare raw vs. risk-managed performance |
| `08_risk.py` | Rolling cointegration re-test and stop-loss |
| `09_second_pair_robustness.py` | Repeat the full pipeline on a second pair |
| `10_test_window_evaluation.py` | Evaluate on the 2023 held-out window |
| `11_second_pair_test.py` | 2023 evaluation for the second pair |
| `12_test_window_full_scan.py` | Full 28-pair cointegration scan, 2023-only, as a validity check |

## Running Tests

```
pytest tests/ -v
```

Covers data cleaning, stationarity detection, cointegration correctness (against synthetic data with a known answer), hedge ratio estimation, signal generation, backtest mechanics, and the risk stop-loss logic.

## Methodology Summary

1. **Data** — 8 NSE private bank tickers, 2018–2022 train / 2023 held-out test, via `yfinance`
2. **Statistical foundations** — ADF/KPSS stationarity, correlation filter, Engle-Granger + Johansen cointegration, spread diagnostics (Jarque-Bera, Ljung-Box), OU-process half-life
3. **Strategy** — static OLS and adaptive Kalman-filtered hedge ratios, rolling z-score entry/exit
4. **Backtesting** — vectorized, both legs, 0.05% transaction cost per leg
5. **Risk management** — divergence stop-loss, rolling cointegration re-test
6. **Robustness** — 2023 held-out window, second candidate pair, full-universe validity check

Full statistical writeup, backtest results, and risk summary are in `reports/`.

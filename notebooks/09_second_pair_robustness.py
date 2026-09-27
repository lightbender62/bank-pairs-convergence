import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN,
                     ZSCORE_LOOKBACK, ENTRY_ZSCORE, EXIT_ZSCORE, STOP_LOSS_ZSCORE)
from src.data_loader import DataLoader
from src.spread_analysis import SpreadAnalyzer
from src.hedge_ratio import HedgeRatioEstimator
from src.strategy import SpreadStrategy
from src.risk import RiskManager
from src.backtester import PairsBacktester

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

# Second pair: AXISBANK on FEDERALBNK (matches the winning EG direction: a_on_b)
ticker_dependent = "AXISBANK.NS"
ticker_independent = "FEDERALBNK.NS"

# --- Spread + OU half-life ---
analyzer = SpreadAnalyzer()
spread_static, alpha, beta_static = analyzer.compute_spread(
    prices[ticker_dependent], prices[ticker_independent]
)
print(f"Static OLS: alpha={alpha:.4f}, beta={beta_static:.4f}")

normality = analyzer.test_normality(spread_static)
autocorr = analyzer.test_autocorrelation(spread_static)
ou_fit = analyzer.fit_ou_half_life(spread_static)
print(f"Normality: {normality}")
print(f"Autocorrelation: {autocorr}")
print(f"OU half-life fit: {ou_fit}")

# --- Kalman hedge ratio ---
estimator = HedgeRatioEstimator()
kalman_result = estimator.kalman_hedge_ratio(prices[ticker_dependent], prices[ticker_independent])
spread_dynamic = prices[ticker_dependent] - (kalman_result["alpha"] + kalman_result["beta"] * prices[ticker_independent])

# --- Strategy signal (reusing existing config thresholds for now) ---
strategy = SpreadStrategy(lookback=ZSCORE_LOOKBACK, entry_z=ENTRY_ZSCORE, exit_z=EXIT_ZSCORE)
zscore = strategy.compute_zscore(spread_dynamic)
signal = strategy.generate_signal(zscore)
print(f"\nSignal distribution:\n{signal.value_counts()}")

# --- Risk management ---
risk_manager = RiskManager(stop_loss_z=STOP_LOSS_ZSCORE)
final_signal = risk_manager.apply_risk_filters(
    signal, zscore, prices[ticker_dependent], prices[ticker_independent]
)

# --- Backtest: raw signal vs risk-managed signal ---
bt_raw = PairsBacktester(
    price_a=prices[ticker_dependent], price_b=prices[ticker_independent],
    signal=signal, hedge_ratio=kalman_result["beta"]
)
bt_raw.runbacktester()
print(f"\nRaw (no risk mgmt) metrics: {bt_raw.metrics()}")

bt_risk_managed = PairsBacktester(
    price_a=prices[ticker_dependent], price_b=prices[ticker_independent],
    signal=final_signal, hedge_ratio=kalman_result["beta"]
)
bt_risk_managed.runbacktester()
print(f"\nRisk-managed metrics: {bt_risk_managed.metrics()}")
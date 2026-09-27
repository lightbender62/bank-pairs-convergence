import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (TICKERS, TRAIN_START, TEST_END, TEST_START, PRICE_COLUMN,
                     ZSCORE_LOOKBACK, ENTRY_ZSCORE, EXIT_ZSCORE, STOP_LOSS_ZSCORE,
                     SIGNIFICANCE_LEVEL)
from src.data_loader import DataLoader
from src.hedge_ratio import HedgeRatioEstimator
from src.strategy import SpreadStrategy
from src.risk import RiskManager
from src.backtester import PairsBacktester
from statsmodels.tsa.stattools import coint

loader = DataLoader(TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN)
prices = loader.load()

ticker_dependent = "AXISBANK.NS"
ticker_independent = "FEDERALBNK.NS"

estimator = HedgeRatioEstimator()
kalman_result = estimator.kalman_hedge_ratio(prices[ticker_dependent], prices[ticker_independent])
spread = prices[ticker_dependent] - (kalman_result["alpha"] + kalman_result["beta"] * prices[ticker_independent])

strategy = SpreadStrategy(lookback=ZSCORE_LOOKBACK, entry_z=ENTRY_ZSCORE, exit_z=EXIT_ZSCORE)
zscore = strategy.compute_zscore(spread)
signal = strategy.generate_signal(zscore)

risk_manager = RiskManager(stop_loss_z=STOP_LOSS_ZSCORE)
final_signal = risk_manager.apply_risk_filters(
    signal, zscore, prices[ticker_dependent], prices[ticker_independent]
)

test_mask = prices.index >= TEST_START
test_price_a = prices[ticker_dependent][test_mask]
test_price_b = prices[ticker_independent][test_mask]
test_signal = final_signal[test_mask]
test_beta = kalman_result["beta"][test_mask]

bt_test = PairsBacktester(
    price_a=test_price_a, price_b=test_price_b,
    signal=test_signal, hedge_ratio=test_beta
)
bt_test.runbacktester()
print("AXISBANK-FEDERALBNK 2023 held-out test metrics:", bt_test.metrics())

stat, p_value, _ = coint(test_price_a, test_price_b)
print(f"\n2023-only Engle-Granger: statistic={stat:.4f}, p_value={p_value:.4f}, "
      f"cointegrated={p_value < SIGNIFICANCE_LEVEL}")
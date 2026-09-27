import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN, ZSCORE_LOOKBACK, ENTRY_ZSCORE, EXIT_ZSCORE
from src.data_loader import DataLoader
from src.hedge_ratio import HedgeRatioEstimator
from src.strategy import SpreadStrategy
from src.backtester import PairsBacktester

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

estimator = HedgeRatioEstimator()
kalman_result = estimator.kalman_hedge_ratio(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])

spread = prices["KOTAKBANK.NS"] - (kalman_result["alpha"] + kalman_result["beta"] * prices["HDFCBANK.NS"])

strategy = SpreadStrategy(lookback=ZSCORE_LOOKBACK, entry_z=ENTRY_ZSCORE, exit_z=EXIT_ZSCORE)
zscore = strategy.compute_zscore(spread)
signal = strategy.generate_signal(zscore)

# price_a = KOTAKBANK, price_b = HDFCBANK, matching your spread's construction
bt = PairsBacktester(
    price_a=prices["KOTAKBANK.NS"],
    price_b=prices["HDFCBANK.NS"],
    signal=signal,
    hedge_ratio=kalman_result["beta"],
)
bt.runbacktester()
print(bt.metrics())

# Compare static vs Kalman
bt_static = PairsBacktester(
    price_a=prices["KOTAKBANK.NS"], price_b=prices["HDFCBANK.NS"],
    signal=signal, hedge_ratio=0.5132
)
bt_static.runbacktester()
print("Static hedge ratio metrics:", bt_static.metrics())

# Plot both equity curves
plt.figure(figsize=(12, 6))
plt.plot(bt.equity_curve, label="Kalman hedge ratio")
plt.plot(bt_static.equity_curve, label="Static hedge ratio")
plt.axhline(1.0, color="gray", linestyle="--", alpha=0.5)
plt.legend()
plt.title("Equity Curve Comparison")
plt.show()
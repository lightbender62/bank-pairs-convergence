import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN, ZSCORE_LOOKBACK, ENTRY_ZSCORE, EXIT_ZSCORE
from src.data_loader import DataLoader
from src.hedge_ratio import HedgeRatioEstimator
from src.strategy import SpreadStrategy

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

estimator = HedgeRatioEstimator()
kalman_result = estimator.kalman_hedge_ratio(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])

spread = prices["KOTAKBANK.NS"] - (kalman_result["alpha"] + kalman_result["beta"] * prices["HDFCBANK.NS"])

strategy = SpreadStrategy(lookback=ZSCORE_LOOKBACK, entry_z=ENTRY_ZSCORE, exit_z=EXIT_ZSCORE)
zscore = strategy.compute_zscore(spread)
signal = strategy.generate_signal(zscore)

print(signal.value_counts())
print(f"\nNumber of trades (position changes): {(signal.diff() != 0).sum()}")

print(zscore.describe())
print(f"\nMax absolute z-score: {zscore.abs().max()}")
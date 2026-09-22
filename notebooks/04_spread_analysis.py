import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN
from src.data_loader import DataLoader
from src.spread_analysis import SpreadAnalyzer

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

analyzer = SpreadAnalyzer()

# Winning direction from Engle-Granger: b_on_a -> KOTAKBANK regressed on HDFCBANK
spread, alpha, beta = analyzer.compute_spread(
    prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"]
)

print(f"Alpha (intercept): {alpha:.4f}")
print(f"Beta (hedge ratio): {beta:.4f}")
print(f"\nSpread summary:")
print(spread.describe())

normality_result = analyzer.test_normality(spread)
print(f"\nJarque-Bera (normality): {normality_result}")

autocorr_result = analyzer.test_autocorrelation(spread)
print(f"Ljung-Box (autocorrelation): {autocorr_result}")

ou_result = analyzer.fit_ou_half_life(spread)
print(f"\nOU half-life fit: {ou_result}")
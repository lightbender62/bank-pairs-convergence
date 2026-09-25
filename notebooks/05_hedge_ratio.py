import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN
from src.data_loader import DataLoader
from src.hedge_ratio import HedgeRatioEstimator

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

estimator = HedgeRatioEstimator()

static = estimator.static_ols(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])
print(f"Static OLS: {static}")

kalman_result = estimator.kalman_hedge_ratio(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])
print(f"\nKalman filter beta over time:")
print(kalman_result["beta"].describe())
print(f"\nFirst 5 days:\n{kalman_result.head()}")
print(f"\nLast 5 days:\n{kalman_result.tail()}")


import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

axes[0].plot(kalman_result.index, kalman_result["beta"], label="Kalman beta")
axes[0].axhline(static["beta"], color="red", linestyle="--", label="Static OLS beta")
axes[0].set_title("Hedge Ratio (Beta) Over Time")
axes[0].legend()

axes[1].plot(kalman_result.index, kalman_result["alpha"], label="Kalman alpha", color="green")
axes[1].axhline(static["alpha"], color="red", linestyle="--", label="Static OLS alpha")
axes[1].set_title("Intercept (Alpha) Over Time")
axes[1].legend()

plt.tight_layout()
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report_path = os.path.join(project_root, "reports", "kalman_hedge_ratio.png")

os.makedirs(os.path.dirname(report_path), exist_ok=True)
plt.savefig(report_path)
plt.show()
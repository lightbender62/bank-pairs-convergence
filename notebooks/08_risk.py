import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN,
                     ZSCORE_LOOKBACK, ENTRY_ZSCORE, EXIT_ZSCORE, STOP_LOSS_ZSCORE)
from src.data_loader import DataLoader
from src.hedge_ratio import HedgeRatioEstimator
from src.strategy import SpreadStrategy
from src.risk import RiskManager
from src.backtester import PairsBacktester

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

estimator = HedgeRatioEstimator()
kalman_result = estimator.kalman_hedge_ratio(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])
spread = prices["KOTAKBANK.NS"] - (kalman_result["alpha"] + kalman_result["beta"] * prices["HDFCBANK.NS"])

strategy = SpreadStrategy(lookback=ZSCORE_LOOKBACK, entry_z=ENTRY_ZSCORE, exit_z=EXIT_ZSCORE)
zscore = strategy.compute_zscore(spread)
signal = strategy.generate_signal(zscore)

risk_manager = RiskManager(stop_loss_z=STOP_LOSS_ZSCORE)
cointegration_flag = risk_manager.rolling_cointegration_flag(prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"])

print("Cointegration flag value counts:")
print(cointegration_flag.value_counts())

final_signal = risk_manager.apply_risk_filters(
    signal, zscore, prices["KOTAKBANK.NS"], prices["HDFCBANK.NS"]
)

# Re-run backtest with risk-managed signal
bt_risk_managed = PairsBacktester(
    price_a=prices["KOTAKBANK.NS"], price_b=prices["HDFCBANK.NS"],
    signal=final_signal, hedge_ratio=kalman_result["beta"]
)
bt_risk_managed.runbacktester()
print("\nRisk-managed metrics:", bt_risk_managed.metrics())

stopped_out_days = (zscore.abs() >= risk_manager.stop_loss_z).sum()
print(f"\nDays where zscore breached stop-loss threshold: {stopped_out_days}")
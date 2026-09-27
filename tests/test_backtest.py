import pandas as pd
import numpy as np
from src.backtester import PairsBacktester


def test_no_trades_means_zero_return():
    dates = pd.date_range("2022-01-01", periods=50)
    price_a = pd.Series(100 + np.arange(50), index=dates, dtype=float)
    price_b = pd.Series(50 + np.arange(50) * 0.5, index=dates, dtype=float)
    flat_signal = pd.Series(0, index=dates)

    bt = PairsBacktester(price_a, price_b, flat_signal, hedge_ratio=0.5)
    bt.runbacktester()
    metrics = bt.metrics()

    assert metrics["Total Return"] == 0.0
    assert metrics["Total Trades"] == 0
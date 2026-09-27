import pandas as pd
import numpy as np
from src.strategy import SpreadStrategy


def test_signal_enters_long_on_low_zscore():
    zscore = pd.Series([0.0, -1.0, -2.5, -1.0, 0.0]) 

    strategy = SpreadStrategy(lookback=1, entry_z=2.0, exit_z=0.5)
    signal = strategy.generate_signal(zscore)

    assert signal.iloc[2] == 1  
    assert signal.iloc[4] == 0 


def test_signal_enters_short_on_high_zscore():
    zscore = pd.Series([0.0, 1.0, 2.5, 1.0, 0.0])

    strategy = SpreadStrategy(lookback=1, entry_z=2.0, exit_z=0.5)
    signal = strategy.generate_signal(zscore)

    assert signal.iloc[2] == -1
    assert signal.iloc[4] == 0
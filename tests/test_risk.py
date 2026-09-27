import pandas as pd
import numpy as np
from src.risk import RiskManager


def test_stop_loss_forces_flat_on_extreme_zscore():
    signal = pd.Series([1, 1, 1, 1, 1])
    zscore = pd.Series([2.0, 2.5, 4.5, 2.0, 1.0]) 

    risk_manager = RiskManager(stop_loss_z=4.0)
    adjusted = risk_manager.apply_stop_loss(signal, zscore)

    assert adjusted.iloc[2] == 0 
    assert adjusted.iloc[0] == 1  
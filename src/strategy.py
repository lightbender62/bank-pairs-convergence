"""
Strategy: rolling z-score signal generation and entry/exit logic.
"""

import numpy as np
import pandas as pd

class SpreadStrategy:
    def __init__(self , lookback , entry_z , exit_z):
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z

    """Rolling z-score of the spread."""
    def compute_zscore(self , spread:pd.Series) -> pd.Series:
        rolling_mean = spread.rolling(self.lookback).mean()
        rolling_std = spread.rolling(self.lookback).std()

        zscore = (spread - rolling_mean)/rolling_std
        return zscore

    """
    Stateful signal generation: +1 = long spread, -1 = short spread, 0 = flat.
    """
    def generate_signal(self , zscore: pd.Series) -> pd.Series:
        signal = pd.Series(0 , index = zscore.index)
        position = 0

        for i in range(len(zscore)):
            z = zscore.iloc[i]

            if(pd.isna(z)):
                signal.iloc[i] = 0
                continue

            if position==0:
                if z<= -self.entry_z:
                    position = 1
                elif z>= self.entry_z:
                    position = -1
            elif position == 1:
                if z>= -self.exit_z:
                    position = 0
            elif position == -1:
                if z<= self.exit_z:
                    position = 0

            signal.iloc[i] = position

        return signal
    
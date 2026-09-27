"""
Risk management: divergence stop-loss and rolling cointegration re-test.
"""

import pandas as pd
from statsmodels.tsa.stattools import coint

class RiskManager:
    def __init__(self , stop_loss_z , significance_level = 0.05 , reeval_window=252 , reeval_frequency = 30):
        self.stop_loss_z = stop_loss_z
        self.significance_level = significance_level
        self.reeval_window = reeval_window
        self.reeval_frequency = reeval_frequency

    """Force exit to flat if zscore breaches the stop-loss threshold while in a position."""
    def apply_stop_loss(self , signal: pd.Series , zscore: pd.Series) -> pd.Series:
        adjusted_signal = signal.copy()
        stopped_out = zscore.abs() >= self.stop_loss_z
        adjusted_signal[stopped_out] = 0
        return adjusted_signal

    """
    Every `reeval_frequency` days, re-test cointegration on the trailing `reeval_window`.
    Returns a series: True = cointegrated (safe to trade), False = not (sit out).
    """
    def rolling_cointegration_flag(self , price_a : pd.Series , price_b: pd.Series) -> pd.Series:
        flag = pd.Series(True , index = price_a.index)

        for i in range(self.reeval_window , len(price_a) , self.reeval_frequency):
            window_a = price_a.iloc[i-self.reeval_window: i]
            window_b = price_b.iloc[i-self.reeval_window: i]

            _ , p_value , _ = coint(window_a , window_b)
            is_cointegrated = p_value < self.significance_level

            end_idx = min(i + self.reeval_frequency , len(price_a))
            flag.iloc[i:end_idx] = is_cointegrated

        return flag

    
    """Combine stop-loss and rolling cointegration check into a final adjusted signal."""
    def apply_risk_filters(self , signal: pd.Series , zscore : pd.Series, price_a : pd.Series , price_b:pd.Series) -> pd.Series:
        signal_after_stop = self.apply_stop_loss(signal , zscore)
        cointegration_ok = self.rolling_cointegration_flag(price_a , price_b)

        final_signal = signal_after_stop.copy()
        final_signal[~cointegration_ok] = 0
        return final_signal
        
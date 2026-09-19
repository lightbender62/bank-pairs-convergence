"""
Spread analysis: build the spread, test normality/autocorrelation, fit OU process for half-life.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

class SpreadAnalyzer:
    def __init__(self , significance_level = 0.05):
        self.significance_level = significance_level


    def compute_spread(self , series_dependent: pd.Series , series_independent: pd.Series) -> tuple:
        X = sm.add_constant(series_independent)
        model = sm.OLS(series_dependent , X).fit()

        alpha = model.params.iloc[0]
        beta = model.params.iloc[1]
        spread = model.resid

        return spread , alpha , beta
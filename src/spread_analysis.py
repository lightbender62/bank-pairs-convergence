"""
Spread analysis: build the spread, test normality/autocorrelation, fit OU process for half-life.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import jarque_bera
from statsmodels.stats.diagnostic import acorr_ljungbox

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

    """Jarque-Bera test for normality of the spread."""
    def test_normality(self , spread: pd.Series) -> dict:
        statistic , p_val = jarque_bera(spread)
        return{
            "jb_statistic" : statistic,
            "jb_p_value" : p_val,
            "jb_normal" : p_val >= self.significance_level,
        }

    """Ljung-Box test for autocorrelation in the spread."""
    def test_autocorrelation(self , spread:pd.Series, lags:int = 10) -> dict:
        result = acorr_ljungbox(spread , lags = [lags] , return_df= True)
        p_val = result["lb_pvalue"].iloc[0]

        return{
            "lb_statistic" : result["lb_stat"].iloc[0],
            "lb_p_value": p_val,
            "lb_no_autocorrelation": p_val >= self.significance_level

        }

    """Fit AR(1) to the spread, derive OU speed of reversion (theta) and half-life."""
    def fit_ou_half_life(self , spread: pd.Series) -> dict:
        spread_lag = spread.shift(1).dropna()
        spread_current = spread.loc[spread_lag.index]

        X = sm.add_constant(spread_lag)
        model = sm.OLS(spread_current , X).fit()

        b= model.params.iloc[1]
        theta = -np.log(b)
        half_life = np.log(2)/theta

        return {
            "ar1_slope" : b,
            "theta" : theta,
            "half_life_days" : half_life,
        }

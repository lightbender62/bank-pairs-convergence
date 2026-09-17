"""
Stationarity tests (ADF, KPSS) for confirming I(1) behavior in price series.
"""
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

""" To filter out weird terminal warnings"""
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class StationarityTester:
    def __init__(self , significance_level = 0.05):
        self.significance_level = significance_level

    """Run ADF test"""
    def run_adf(self , series:pd.Series) -> dict:
        result = adfuller(series.dropna())
        statistic, p_val = result[0] , result[1]
        return {
            "adf_statistic": statistic,
            "p_value" : p_val,
            "adf_stationarity": p_val < self.significance_level,
        }

    """Run KPSS test"""
    def run_kpss(self , series: pd.set_eng_float_format) -> dict:
        statistic , p_val , _ , _ = kpss(series.dropna() , regression='c')
        return{
            "kpss_statistic" : statistic,
            "p_value" : p_val,
            "kpss_stationarity" : p_val >= self.significance_level,
        }

    """Run ADF + KPSS on raw and differenced series for one ticker."""
    def test_series(self , series: pd.Series , name:str) -> dict:
        differenced = series.diff().dropna()

        raw_adf = self.run_adf(series)
        raw_kpss = self.run_kpss(series)
        diff_adf = self.run_adf(differenced)
        diff_kpss = self.run_kpss(differenced)

        i1 = (
            not raw_adf["adf_stationarity"]
            and not raw_kpss["kpss_stationarity"]
            and diff_adf["adf_stationarity"]
            and diff_kpss["kpss_stationarity"]
        )

        return{
            "ticker" : name,
            "raw_adf_p": raw_adf["p_value"],
            "raw_kpss_p": raw_kpss["p_value"],
            "diff_adf_p": diff_adf["p_value"],
            "diff_kpss_p": diff_kpss["p_value"],
            "is_I1" : i1,
        }

    """Run stationarity tests on every column (ticker) in the price dataframe."""
    def test(self , price_df: pd.DataFrame) -> pd.DataFrame:
        results = [self.test_series(price_df[col] , col) for col in price_df.columns]
        return pd.DataFrame(results)

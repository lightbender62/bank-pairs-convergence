"""
Pair selection: correlation filter + cointegration testing across the bank universe.
"""
import itertools
import pandas as pd
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=np.exceptions.ComplexWarning)

class PairSelector:
    def __init__(self , correlation_threshold=0.5):
        self.correlation_threshold = correlation_threshold

    """Convert prices to daily percentage returns."""
    def compute_returns(self , price_df: pd.DataFrame) -> pd.DataFrame:
        return price_df.pct_change().dropna()

    """Compute correlation for every unique pair of tickers."""
    def compute_pairwise_correlations(self , returns_df: pd.DataFrame) -> pd.DataFrame : 
        tickers = returns_df.columns
        results = []

        for ticker_a , ticker_b in itertools.combinations(tickers , 2):
            corr = returns_df[ticker_a].corr(returns_df[ticker_b])
            results.append({
                "ticker_a" : ticker_a,
                "ticker_b" : ticker_b,
                "correlation": corr,
            })
        return pd.DataFrame(results).sort_values("correlation" , ascending=False)

    """Keep only pairs at or above the correlation threshold."""
    def filter_candidates(self , corr_table: pd.DataFrame) -> pd.DataFrame:
        return corr_table[corr_table["correlation"] >= self.correlation_threshold]

    """Run Engle-Granger cointegration test in both directions, keep the stronger result."""
    def engle_granger_test(self , series_a:pd.Series , series_b: pd.Series) -> dict:
        stat_ab, p_ab, _ = coint(series_a , series_b)
        stat_ba , p_ba , _ = coint(series_b , series_a)
        if p_ab <= p_ba:
            return {"eg_statistic" : stat_ab,   "eg_p_value" : p_ab , "direction" : "a_on_b"}
        else:
            return{"eg_statistic" : stat_ba , "eg_p_value" : p_ba , "direction" : "b_on_a"}

    """Run Engle-Granger on every candidate pair, ranked by p-value."""
    def run_cointegration_scan (self , price_df: pd.DataFrame , candidates: pd.DataFrame) -> pd.DataFrame:
        results = []
        for _, row in candidates.iterrows():
            a,b = row["ticker_a"] , row["ticker_b"]
            eg_result = self.engle_granger_test(price_df[a] , price_df[b])
            results.append({
                "ticker_a" : a,
                "ticker_b" : b,
                "correlation" : row["correlation"],
                **eg_result,
            })
        return pd.DataFrame(results).sort_values("eg_p_value")

    """Run Johansen cointegration test on a 2-column price dataframe."""
    def johansen_test(self , price_df: pd.DataFrame) -> dict:
        result = coint_johansen(price_df , det_order=0 , k_ar_diff=1)

        trace_stat = result.lr1[0]
        critical_values = result.cvt[0]

        return{
            "trace statistic" : trace_stat,
            "critical_value_95" : critical_values[1],
            "cointegrated_at_95" : trace_stat > critical_values[1],
        }
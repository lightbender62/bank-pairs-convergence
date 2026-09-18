"""
Pair selection: correlation filter + cointegration testing across the bank universe.
"""
import itertools
import pandas as pd

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

    
    
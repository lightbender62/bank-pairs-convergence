"""
Fetches, cleans, and caches price data for the pairs trading universe.
"""
import os
import pandas as pd
import yfinance as yf

class DataLoader:
    def __init__(self, tickers, start, end, price_column="Close", cache_dir="data/raw"):
        self.tickers = tickers
        self.start = start
        self.end = end
        self.price_column = price_column
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_path = os.path.join(
            self.cache_dir, f"prices_{self.start}_{self.end}.csv"
        )

    """Download raw OHLCV data for all tickers in one call."""
    def fetch(self) -> pd.DataFrame:
        data = yf.download(
            self.tickers , start= self.start , end = self.end, auto_adjust=True
        )
        prices = data[self.price_column]
        return prices

    """Align calendars and handle missing sessions."""
    def clean(self , raw: pd.DataFrame) -> pd.DataFrame:
        cleaned = raw.dropna(how="all")
        cleaned = cleaned.ffill()
        cleaned = cleaned.dropna(how = "any")
        return cleaned

    """Load from cache if available, else fetch + clean + cache."""
    def load(self , force_refresh=False) -> pd.DataFrame:
        if not force_refresh and os.path.exists(self.cache_path):
            return pd.read_csv(self.cache_path, index_col=0, parse_dates=True)
        raw = self.fetch()
        prices = self.clean(raw)
        prices.to_csv(self.cache_path)
        return prices
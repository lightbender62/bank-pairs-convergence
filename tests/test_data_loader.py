import pandas as pd
import numpy as np
from src.data_loader import DataLoader


def test_clean_drops_fully_empty_rows():
    dates = pd.date_range("2022-01-01", periods=5)
    raw = pd.DataFrame({
        "A": [1.0, np.nan, 3.0, 4.0, 5.0],
        "B": [1.0, np.nan, 3.0, 4.0, 5.0],
    }, index=dates)

    loader = DataLoader(tickers=["A", "B"], start="2022-01-01", end="2022-01-05")
    cleaned = loader.clean(raw)

    assert len(cleaned) == 4
    assert cleaned.isna().sum().sum() == 0


def test_clean_forward_fills_isolated_gap():
    dates = pd.date_range("2022-01-01", periods=5)
    raw = pd.DataFrame({
        "A": [1.0, np.nan, 3.0, 4.0, 5.0],
        "B": [1.0, 2.0, 3.0, 4.0, 5.0],
    }, index=dates)

    loader = DataLoader(tickers=["A", "B"], start="2022-01-01", end="2022-01-05")
    cleaned = loader.clean(raw)

    assert cleaned.loc[dates[1], "A"] == 1.0 
    assert cleaned.isna().sum().sum() == 0
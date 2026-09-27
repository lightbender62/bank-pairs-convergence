import numpy as np
import pandas as pd
from src.pair_selection import PairSelector


def test_engle_granger_detects_known_cointegrated_pair():
    np.random.seed(42)
    n = 500
    b = pd.Series(np.cumsum(np.random.randn(n)) + 100)
    a = 2 * b + np.random.randn(n) 

    selector = PairSelector()
    result = selector.engle_granger_test(a, b)

    assert result["eg_p_value"] < 0.05


def test_engle_granger_rejects_independent_random_walks():
    np.random.seed(42)
    n = 500
    c = pd.Series(np.cumsum(np.random.randn(n)) + 50)
    d = pd.Series(np.cumsum(np.random.randn(n)) + 200)

    selector = PairSelector()
    result = selector.engle_granger_test(c, d)

    assert result["eg_p_value"] >= 0.05
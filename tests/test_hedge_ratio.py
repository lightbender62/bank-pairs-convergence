import numpy as np
import pandas as pd
from src.hedge_ratio import HedgeRatioEstimator


def test_static_ols_recovers_known_beta():
    np.random.seed(42)
    n = 500
    independent = pd.Series(np.cumsum(np.random.randn(n)) + 100)
    true_beta = 1.5
    dependent = true_beta * independent + np.random.randn(n) * 0.1 

    estimator = HedgeRatioEstimator()
    result = estimator.static_ols(dependent, independent)

    assert abs(result["beta"] - true_beta) < 0.05  
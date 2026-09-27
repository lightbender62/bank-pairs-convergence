import numpy as np
import pandas as pd
from src.stationarity import StationarityTester


def test_random_walk_is_not_stationary():
    np.random.seed(42)
    random_walk = pd.Series(np.cumsum(np.random.randn(500)) + 100)

    tester = StationarityTester()
    result = tester.run_adf(random_walk)

    assert result["adf_stationarity"] is False


def test_white_noise_is_stationary():
    np.random.seed(42)
    white_noise = pd.Series(np.random.randn(500))

    tester = StationarityTester()
    result = tester.run_adf(white_noise)

    assert result["adf_stationarity"] is True
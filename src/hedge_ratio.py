"""
Hedge ratio estimation: static OLS baseline + adaptive Kalman filter.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from pykalman import KalmanFilter

class HedgeRatioEstimator :
    def __init__(self):
        pass

    def static_ols(self , series_dependent: pd.Series, series_indpendent: pd.Series) -> dict:
        X = sm.add_constant(series_indpendent)
        model = sm.OLS(series_dependent , X).fit()
        return{
            "alpha" : model.params.iloc[0],
            "beta" : model.params.iloc[1]
        }

    """
    Estimate a time-varying hedge ratio using a Kalman filter.
    State: [alpha, beta] at each time step.
    Observation: series_dependent = alpha + beta * series_independent
    """
    def kalman_hedge_ratio(self , series_dependent: pd.Series , series_independent: pd.Series, delta : float = 1e-4) -> pd.DataFrame:
        n = len(series_independent)

        # Observation matrix: at each time step, maps [alpha, beta] -> predicted price
        obs_mat = np.vstack([
            np.ones(n),
            series_independent.values
        ]).T[: , np.newaxis , :]

        # Process noise: controls how fast alpha/beta are allowed to drift
        trans_cov = delta/ (1- delta)*np.eye(2)


        kf = KalmanFilter(
            n_dim_obs=1,
            n_dim_state=2,
            initial_state_mean=np.zeros(2),
            initial_state_covariance=np.eye(2) * 1000,
            transition_matrices=np.eye(2),
            observation_matrices=obs_mat,
            observation_covariance=1.0,
            transition_covariance=trans_cov,
        )

        state_means , state_covs = kf.filter(series_dependent.values)

        result = pd.DataFrame(
            state_means , index=series_dependent.index , columns =[ "alpha" , "beta"]
        )
        return result

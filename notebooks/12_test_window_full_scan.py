import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TEST_END, TEST_START, PRICE_COLUMN, CORRELATION_THRESHOLD
from src.data_loader import DataLoader
from src.pair_selection import PairSelector

loader = DataLoader(TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN)
prices = loader.load()

test_mask = prices.index >= TEST_START
test_prices = prices[test_mask]

selector = PairSelector(correlation_threshold=CORRELATION_THRESHOLD)
returns_test = selector.compute_returns(test_prices)
corr_table_test = selector.compute_pairwise_correlations(returns_test)
candidates_test = selector.filter_candidates(corr_table_test)

print(f"Candidates in 2023 window: {len(candidates_test)}")

cointegration_test_2023 = selector.run_cointegration_scan(test_prices, candidates_test)
print("\n2023-only cointegration results (ranked by p-value):")
print(cointegration_test_2023)

import itertools

all_pairs_test = []
for ticker_a, ticker_b in itertools.combinations(test_prices.columns, 2):
    all_pairs_test.append({"ticker_a": ticker_a, "ticker_b": ticker_b, "correlation": None})

import pandas as pd
all_pairs_df = pd.DataFrame(all_pairs_test)

cointegration_all_2023 = selector.run_cointegration_scan(test_prices, all_pairs_df)
print("2023-only cointegration on ALL 28 pairs (no correlation filter):")
print(cointegration_all_2023)
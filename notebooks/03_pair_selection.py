import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN, CORRELATION_THRESHOLD
from src.data_loader import DataLoader
from src.pair_selection import PairSelector

loader = DataLoader(TICKERS, TRAIN_START, TRAIN_END, PRICE_COLUMN)
prices = loader.load()

selector = PairSelector(correlation_threshold=CORRELATION_THRESHOLD)
returns = selector.compute_returns(prices)

corr_table = selector.compute_pairwise_correlations(returns)
print(corr_table)

candidates = selector.filter_candidates(corr_table)
print("\nCandidates above threshold:")
print(candidates)

cointegration_results = selector.run_cointegration_scan(prices, candidates)
print("\nCointegration results (ranked by p-value):")
print(cointegration_results)

best_pair = cointegration_results.iloc[0]
pair_prices = prices[[best_pair["ticker_a"], best_pair["ticker_b"]]]

johansen_result = selector.johansen_test(pair_prices)
print(f"\nJohansen test on {best_pair['ticker_a']} / {best_pair['ticker_b']}:")
print(johansen_result)
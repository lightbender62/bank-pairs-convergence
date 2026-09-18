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
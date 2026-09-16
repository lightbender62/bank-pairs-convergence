import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN
from src.data_loader import DataLoader

loader = DataLoader(TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN)
prices = loader.load()

print(prices.shape)
print(prices.head())
print(prices.isna().sum())
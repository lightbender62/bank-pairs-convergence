import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN
from src.data_loader import DataLoader
from src.stationarity import StationarityTester

loader = DataLoader(TICKERS, TRAIN_START, TEST_END, PRICE_COLUMN)
prices = loader.load()

tester = StationarityTester()
results = tester.test(prices)
print(results)
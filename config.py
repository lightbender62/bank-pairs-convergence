"""
Central configuration for the pairs trading pipeline.
We will import from here rather than coding it again and again in diff modules.
"""

# --- Universe ---
TICKERS = [
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "KOTAKBANK.NS",
    "AXISBANK.NS",
    "INDUSINDBK.NS",
    "SBIN.NS",
    "IDFCFIRSTB.NS",
    "FEDERALBNK.NS",
]

# --- Date ranges ---
TRAIN_START = "2018-01-01"
TRAIN_END = "2022-12-31"
TEST_START = "2023-01-01"
TEST_END = "2023-12-31"

# --- Data ---
PRICE_COLUMN = "Close"

# --- Stationarity / cointegration ---
ADF_REGRESSION = "c" 
SIGNIFICANCE_LEVEL = 0.05
CORRELATION_THRESHOLD = 0.8 

# --- Spread / signal ---
ZSCORE_LOOKBACK = 30      
ENTRY_ZSCORE = 2.0
EXIT_ZSCORE = 0.5
STOP_LOSS_ZSCORE = 4.0   

# --- Backtest ---
TRANSACTION_COST_PER_LEG = 0.0005
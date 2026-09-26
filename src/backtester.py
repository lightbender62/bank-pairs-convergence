import pandas as pd
import numpy as np
from config import TRANSACTION_COST_PER_LEG

class PairsBacktester:
    def __init__(self, price_a, price_b, signal, hedge_ratio, transaction_cost=None):  
        self.price_a=price_a
        self.price_b=price_b
        self.signal=signal
        self.hedge_ratio=hedge_ratio
        #for constant valur or just taking it from config file
        self.transaction_cost=transaction_cost if transaction_cost is not None else TRANSACTION_COST_PER_LEG
        
    def runbacktester(self):
        #stopping incase dumb eklavya did some mistake in data handling
        if isinstance(self.hedge_ratio, pd.Series):
            if not self.price_a.index.equals(self.hedge_ratio.index):
                raise ValueError("Indices of price_a and dynamic hedge_ratio do not perfectly match")
        if isinstance(self.hedge_ratio, pd.Series):
            if not self.price_b.index.equals(self.hedge_ratio.index):
                raise ValueError("Indices of price_b and dynamic hedge_ratio do not perfectly match")
                
        self.positions = self.signal.shift(1).fillna(0) 
        if isinstance(self.hedge_ratio, pd.Series):
            exec_beta = self.hedge_ratio.shift(1).fillna(method='bfill')
        else:
            exec_beta = self.hedge_ratio
        
        #daily price changes
        price_diff_a = self.price_a.diff().fillna(0)
        price_diff_b = self.price_b.diff().fillna(0)
        
        spread_dollar_pnl = price_diff_a - (exec_beta * price_diff_b)
        gross_dollar_pnl = self.positions * spread_dollar_pnl#money we made we rich baby..
        
        position_change = self.positions.diff().fillna(0).abs() 
        change_a = position_change * self.price_a
        change_b = position_change * (abs(exec_beta) * self.price_b)
        #since change in cost so transcation cost together
        costs = (change_a + change_b) * self.transaction_cost
        
        capital_base = self.price_a.shift(1) + (abs(exec_beta) * self.price_b.shift(1))
        #small epsilon to prevent division by zero on the first day
        self.net_return = (gross_dollar_pnl - costs) / (capital_base + 1e-9)
        self.net_return = self.net_return.fillna(0)
        
        self.equity_curve = (1 + self.net_return).cumprod()    
        return self.equity_curve
                 
    def metrics(self):
        if not hasattr(self, 'net_return'):
            #once again incase eklavya is dumb
            raise RuntimeError("You must execute runbacktester() before calculating metrics")
        
        total_return = self.equity_curve.iloc[-1] - 1
        portfolio_returns = self.net_return 
        
        mean_ret = portfolio_returns.mean()
        volatility = portfolio_returns.std()
        sharpe = 0.0
        if volatility > 0:
            sharpe = (mean_ret / volatility) * np.sqrt(252)
    
        downside_sq = np.minimum(portfolio_returns, 0) ** 2
        neg_vol = np.sqrt(downside_sq.mean())
        
        sortino = 0.0
        if neg_vol > 0:
            sortino = (mean_ret / neg_vol) * np.sqrt(252)
        
        rolling_max = self.equity_curve.cummax()
        drawdown = (self.equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        calmar = 0.0
        if max_drawdown < 0:
            calmar = annualized_return / abs(max_drawdown)
        
        winning_days = (portfolio_returns > 0).sum()
        total_days_active = (portfolio_returns != 0).sum()
        
        winrate = 0.0
        if total_days_active > 0:
            winrate = winning_days / total_days_active
        
        prev = self.positions.shift(1).fillna(0)
        trade_entries = ((self.positions != prev) & (self.positions != 0)).sum()
        total_trades = trade_entries
        
        return {
            "Total Return": total_return,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Max Drawdown": max_drawdown,
            "Calmar Ratio": calmar,
            "Daily Win Rate": winrate,
            "Total Trades": int(total_trades)
        }
        
    if __name__ == "__main__":
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", periods=100)
        p_a= pd.Series(np.random.normal(100, 2, 100), index=dates)
        p_b = pd.Series(np.random.normal(50, 1, 100), index=dates)
        sigs = pd.Series(np.random.choice([1, 0, -1], size=100), index=dates)
        backtester = PairsBacktester(p_a, p_b, sigs, hedge_ratio=0.5)
        eq = backtester.runbacktester()
        metrics = backtester.metrics()
        print("Performance Metrics:\n", metrics)      
    
"""
Backtesting Module
Test strategy on historical data
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from trading_strategy import TradingStrategy
from alpaca_trader import AlpacaTrader
from config import Config
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Backtester:
    def __init__(self):
        self.config = Config()
        self.trader = AlpacaTrader(
            api_key=self.config.ALPACA_API_KEY,
            secret_key=self.config.ALPACA_SECRET_KEY,
            paper=True
        )
        self.strategy = TradingStrategy(self.config)
        
    def run_backtest(self, symbol, start_date, end_date, initial_capital=10000):
        """Run backtest on historical data"""
        logger.info(f"Starting backtest for {symbol}")
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${initial_capital}")
        
        # Get historical data
        bars = self.get_historical_data(symbol, start_date, end_date)
        if bars is None or len(bars) < 100:
            logger.error("Insufficient data for backtesting")
            return None
        
        # Initialize tracking variables
        capital = initial_capital
        position = None
        trades = []
        equity_curve = []
        
        # Simulate trading
        for i in range(100, len(bars)):
            current_bars = bars.iloc[:i+1]
            current_price = current_bars['close'].iloc[-1]
            current_date = current_bars.index[-1]
            
            # Generate signal
            signal = self.strategy.generate_signal(current_bars.tail(100), symbol)
            
            # Execute trades
            if signal == 'BUY' and position is None:
                # Buy
                shares = int((capital * self.config.POSITION_SIZE_PCT) / current_price)
                if shares > 0:
                    position = {
                        'entry_price': current_price,
                        'shares': shares,
                        'entry_date': current_date
                    }
                    capital -= shares * current_price
                    logger.info(f"BUY: {shares} shares @ ${current_price:.2f} on {current_date}")
                    
            elif position is not None:
                # Check exit conditions
                pnl_pct = (current_price - position['entry_price']) / position['entry_price'] * 100
                
                should_exit = False
                exit_reason = ""
                
                if signal == 'SELL':
                    should_exit = True
                    exit_reason = "SELL signal"
                elif pnl_pct <= -self.config.STOP_LOSS_PCT:
                    should_exit = True
                    exit_reason = "Stop-loss"
                elif pnl_pct >= self.config.TAKE_PROFIT_PCT:
                    should_exit = True
                    exit_reason = "Take-profit"
                
                if should_exit:
                    # Sell
                    capital += position['shares'] * current_price
                    pnl = (current_price - position['entry_price']) * position['shares']
                    
                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'shares': position['shares'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'reason': exit_reason
                    })
                    
                    logger.info(f"SELL: {position['shares']} shares @ ${current_price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:.2f}%) | Reason: {exit_reason}")
                    position = None
            
            # Track equity
            current_equity = capital
            if position:
                current_equity += position['shares'] * current_price
            equity_curve.append({
                'date': current_date,
                'equity': current_equity
            })
        
        # Close any open position
        if position:
            final_price = bars['close'].iloc[-1]
            capital += position['shares'] * final_price
            pnl = (final_price - position['entry_price']) * position['shares']
            pnl_pct = (final_price - position['entry_price']) / position['entry_price'] * 100
            
            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': bars.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'shares': position['shares'],
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'reason': 'End of backtest'
            })
        
        # Calculate statistics
        results = self.calculate_statistics(trades, equity_curve, initial_capital, capital)
        self.print_results(results, symbol)
        
        return results
    
    def get_historical_data(self, symbol, start_date, end_date):
        """Get historical data for backtesting"""
        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame(5, 'Min'),
                start=datetime.strptime(start_date, '%Y-%m-%d'),
                end=datetime.strptime(end_date, '%Y-%m-%d')
            )
            
            bars = self.trader.data_client.get_stock_bars(request_params)
            
            if symbol in bars.data:
                df = pd.DataFrame([{
                    'timestamp': bar.timestamp,
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume
                } for bar in bars.data[symbol]])
                
                df.set_index('timestamp', inplace=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None
    
    def calculate_statistics(self, trades, equity_curve, initial_capital, final_capital):
        """Calculate backtest statistics"""
        if not trades:
            return None
        
        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame(equity_curve)
        
        total_return = (final_capital - initial_capital) / initial_capital * 100
        total_trades = len(trades)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Calculate max drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': trades_df,
            'equity_curve': equity_df
        }
    
    def print_results(self, results, symbol):
        """Print backtest results"""
        if not results:
            return
        
        print("\n" + "="*60)
        print(f"BACKTEST RESULTS - {symbol}")
        print("="*60)
        print(f"Initial Capital:    ${results['initial_capital']:,.2f}")
        print(f"Final Capital:      ${results['final_capital']:,.2f}")
        print(f"Total Return:       {results['total_return']:.2f}%")
        print(f"Max Drawdown:       {results['max_drawdown']:.2f}%")
        print("-"*60)
        print(f"Total Trades:       {results['total_trades']}")
        print(f"Winning Trades:     {results['winning_trades']}")
        print(f"Losing Trades:      {results['losing_trades']}")
        print(f"Win Rate:           {results['win_rate']:.2f}%")
        print(f"Avg Win:            ${results['avg_win']:.2f}")
        print(f"Avg Loss:           ${results['avg_loss']:.2f}")
        print(f"Profit Factor:      {results['profit_factor']:.2f}")
        print("="*60 + "\n")


if __name__ == "__main__":
    backtester = Backtester()
    
    # Run backtest
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-11-30"
    
    results = backtester.run_backtest(symbol, start_date, end_date, initial_capital=10000)

"""
Trading Bot Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Alpaca API Credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', 'your_api_key_here')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'your_secret_key_here')
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Trading Parameters
    SYMBOLS = os.getenv('SYMBOLS', 'AAPL,TSLA,MSFT,GOOGL,AMZN').split(',')
    TIMEFRAME = os.getenv('TIMEFRAME', '5Min')  # 1Min, 5Min, 15Min, 1Hour, 1Day
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds
    
    # Risk Management
    POSITION_SIZE_PCT = float(os.getenv('POSITION_SIZE_PCT', '0.1'))  # 10% of buying power per trade
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', '2.0'))  # 2% stop loss
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', '4.0'))  # 4% take profit
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '5'))  # Maximum concurrent positions
    
    # Strategy Parameters
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))
    
    BB_PERIOD = int(os.getenv('BB_PERIOD', '20'))
    BB_STD = int(os.getenv('BB_STD', '2'))
    
    EMA_FAST = int(os.getenv('EMA_FAST', '9'))
    EMA_SLOW = int(os.getenv('EMA_SLOW', '21'))
    
    # Backtesting
    BACKTEST_START_DATE = os.getenv('BACKTEST_START_DATE', '2024-01-01')
    BACKTEST_END_DATE = os.getenv('BACKTEST_END_DATE', '2024-12-31')
    BACKTEST_INITIAL_CAPITAL = float(os.getenv('BACKTEST_INITIAL_CAPITAL', '10000'))

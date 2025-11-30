"""
Alpaca Trading Interface
Handles all broker interactions
"""

import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlpacaTrader:
    def __init__(self, api_key, secret_key, paper=True):
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        
    def get_account(self):
        """Get account information"""
        try:
            return self.trading_client.get_account()
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return None
    
    def is_market_open(self):
        """Check if market is open"""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def get_bars(self, symbol, timeframe='5Min', limit=100):
        """Get historical bars"""
        try:
            # Map timeframe string to TimeFrame enum
            timeframe_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, 'Min'),
                '15Min': TimeFrame(15, 'Min'),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day
            }
            
            tf = timeframe_map.get(timeframe, TimeFrame(5, 'Min'))
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=datetime.now() - timedelta(days=7),
                limit=limit
            )
            
            bars = self.data_client.get_stock_bars(request_params)
            
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
            logger.error(f"Error getting bars for {symbol}: {e}")
            return None
    
    def get_position(self, symbol):
        """Get current position for symbol"""
        try:
            return self.trading_client.get_open_position(symbol)
        except:
            return None
    
    def get_all_positions(self):
        """Get all open positions"""
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def place_order(self, symbol, qty, side, order_type='market', limit_price=None):
        """Place an order"""
        try:
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            if order_type == 'market':
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=TimeInForce.DAY
                )
            elif order_type == 'limit' and limit_price:
                order_data = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=TimeInForce.DAY,
                    limit_price=limit_price
                )
            else:
                logger.error("Invalid order type or missing limit price")
                return None
            
            order = self.trading_client.submit_order(order_data)
            logger.info(f"Order placed: {order.id} - {side} {qty} {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def cancel_all_orders(self):
        """Cancel all open orders"""
        try:
            self.trading_client.cancel_orders()
            logger.info("All orders cancelled")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")
    
    def close_all_positions(self):
        """Close all open positions"""
        try:
            self.trading_client.close_all_positions(cancel_orders=True)
            logger.info("All positions closed")
        except Exception as e:
            logger.error(f"Error closing positions: {e}")

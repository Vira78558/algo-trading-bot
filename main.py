"""
Advanced Algorithmic Trading Bot
Multi-indicator strategy with risk management
"""

import os
import time
import logging
from datetime import datetime
from trading_strategy import TradingStrategy
from alpaca_trader import AlpacaTrader
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self):
        self.config = Config()
        self.trader = AlpacaTrader(
            api_key=self.config.ALPACA_API_KEY,
            secret_key=self.config.ALPACA_SECRET_KEY,
            paper=self.config.PAPER_TRADING
        )
        self.strategy = TradingStrategy(self.config)
        self.active_positions = {}
        
    def run(self):
        """Main trading loop"""
        logger.info("🚀 Trading Bot Started")
        logger.info(f"Mode: {'PAPER' if self.config.PAPER_TRADING else 'LIVE'}")
        logger.info(f"Symbols: {self.config.SYMBOLS}")
        
        while True:
            try:
                # Check if market is open
                if not self.trader.is_market_open():
                    logger.info("Market is closed. Waiting...")
                    time.sleep(300)  # Check every 5 minutes
                    continue
                
                # Process each symbol
                for symbol in self.config.SYMBOLS:
                    self.process_symbol(symbol)
                
                # Wait before next iteration
                time.sleep(self.config.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(60)
    
    def process_symbol(self, symbol):
        """Process trading signals for a symbol"""
        try:
            # Get market data
            bars = self.trader.get_bars(symbol, self.config.TIMEFRAME, limit=100)
            if bars is None or len(bars) == 0:
                return
            
            # Get current position
            position = self.trader.get_position(symbol)
            current_price = bars['close'].iloc[-1]
            
            # Generate signal
            signal = self.strategy.generate_signal(bars, symbol)
            
            # Execute trades based on signal
            if signal == 'BUY' and position is None:
                self.execute_buy(symbol, current_price)
            elif signal == 'SELL' and position is not None:
                self.execute_sell(symbol, current_price, position)
            elif position is not None:
                # Check stop-loss and take-profit
                self.check_exit_conditions(symbol, current_price, position)
                
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    def execute_buy(self, symbol, price):
        """Execute buy order"""
        try:
            # Calculate position size
            account = self.trader.get_account()
            buying_power = float(account.buying_power)
            position_size = (buying_power * self.config.POSITION_SIZE_PCT) / price
            position_size = int(position_size)
            
            if position_size < 1:
                logger.warning(f"Insufficient buying power for {symbol}")
                return
            
            # Place order
            order = self.trader.place_order(
                symbol=symbol,
                qty=position_size,
                side='buy',
                order_type='market'
            )
            
            if order:
                logger.info(f"✅ BUY {position_size} {symbol} @ ${price:.2f}")
                self.active_positions[symbol] = {
                    'entry_price': price,
                    'qty': position_size,
                    'entry_time': datetime.now()
                }
                
        except Exception as e:
            logger.error(f"Error executing buy for {symbol}: {e}")
    
    def execute_sell(self, symbol, price, position):
        """Execute sell order"""
        try:
            qty = int(float(position.qty))
            order = self.trader.place_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                order_type='market'
            )
            
            if order:
                entry_price = self.active_positions.get(symbol, {}).get('entry_price', 0)
                pnl_pct = ((price - entry_price) / entry_price * 100) if entry_price else 0
                logger.info(f"✅ SELL {qty} {symbol} @ ${price:.2f} | P&L: {pnl_pct:.2f}%")
                
                if symbol in self.active_positions:
                    del self.active_positions[symbol]
                    
        except Exception as e:
            logger.error(f"Error executing sell for {symbol}: {e}")
    
    def check_exit_conditions(self, symbol, current_price, position):
        """Check stop-loss and take-profit"""
        try:
            entry_price = float(position.avg_entry_price)
            pnl_pct = (current_price - entry_price) / entry_price * 100
            
            # Stop-loss
            if pnl_pct <= -self.config.STOP_LOSS_PCT:
                logger.warning(f"🛑 Stop-loss triggered for {symbol}: {pnl_pct:.2f}%")
                self.execute_sell(symbol, current_price, position)
            
            # Take-profit
            elif pnl_pct >= self.config.TAKE_PROFIT_PCT:
                logger.info(f"🎯 Take-profit triggered for {symbol}: {pnl_pct:.2f}%")
                self.execute_sell(symbol, current_price, position)
                
        except Exception as e:
            logger.error(f"Error checking exit conditions for {symbol}: {e}")


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()

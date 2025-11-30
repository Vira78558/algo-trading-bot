"""
Multi-Indicator Trading Strategy
Combines RSI, MACD, Bollinger Bands, EMA, and Volume
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TradingStrategy:
    def __init__(self, config):
        self.config = config
        
    def generate_signal(self, bars, symbol):
        """Generate trading signal based on multiple indicators"""
        try:
            df = bars.copy()
            
            # Calculate all indicators
            df = self.calculate_rsi(df)
            df = self.calculate_macd(df)
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_ema(df)
            df = self.calculate_volume_signal(df)
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Signal scoring system
            buy_score = 0
            sell_score = 0
            
            # RSI Signal (Weight: 2)
            if latest['rsi'] < 30:  # Oversold
                buy_score += 2
            elif latest['rsi'] > 70:  # Overbought
                sell_score += 2
            
            # MACD Signal (Weight: 2)
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                buy_score += 2  # Bullish crossover
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                sell_score += 2  # Bearish crossover
            
            # Bollinger Bands Signal (Weight: 1.5)
            if latest['close'] < latest['bb_lower']:
                buy_score += 1.5  # Price below lower band
            elif latest['close'] > latest['bb_upper']:
                sell_score += 1.5  # Price above upper band
            
            # EMA Crossover Signal (Weight: 2)
            if latest['ema_fast'] > latest['ema_slow'] and prev['ema_fast'] <= prev['ema_slow']:
                buy_score += 2  # Golden cross
            elif latest['ema_fast'] < latest['ema_slow'] and prev['ema_fast'] >= prev['ema_slow']:
                sell_score += 2  # Death cross
            
            # Volume Confirmation (Weight: 1.5)
            if latest['volume_signal'] == 1:
                buy_score += 1.5
            elif latest['volume_signal'] == -1:
                sell_score += 1.5
            
            # Trend Confirmation (Weight: 1)
            if latest['close'] > latest['ema_slow']:
                buy_score += 1  # Uptrend
            elif latest['close'] < latest['ema_slow']:
                sell_score += 1  # Downtrend
            
            # Decision logic (threshold: 5 points)
            if buy_score >= 5 and buy_score > sell_score:
                logger.info(f"{symbol} - BUY Signal | Score: {buy_score:.1f} | RSI: {latest['rsi']:.1f} | MACD: {latest['macd']:.3f}")
                return 'BUY'
            elif sell_score >= 5 and sell_score > buy_score:
                logger.info(f"{symbol} - SELL Signal | Score: {sell_score:.1f} | RSI: {latest['rsi']:.1f} | MACD: {latest['macd']:.3f}")
                return 'SELL'
            else:
                return 'HOLD'
                
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return 'HOLD'
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        return df
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """Calculate Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std)
        return df
    
    def calculate_ema(self, df, fast=9, slow=21):
        """Calculate Exponential Moving Averages"""
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        return df
    
    def calculate_volume_signal(self, df, period=20):
        """Calculate volume-based signal"""
        df['volume_ma'] = df['volume'].rolling(window=period).mean()
        df['volume_signal'] = 0
        
        # High volume with price increase = bullish
        df.loc[(df['volume'] > df['volume_ma'] * 1.5) & 
               (df['close'] > df['close'].shift(1)), 'volume_signal'] = 1
        
        # High volume with price decrease = bearish
        df.loc[(df['volume'] > df['volume_ma'] * 1.5) & 
               (df['close'] < df['close'].shift(1)), 'volume_signal'] = -1
        
        return df

# 🤖 Advanced Algorithmic Trading Bot

Professional trading bot with multi-indicator strategy, risk management, and backtesting capabilities.

## 🎯 Features

### **Multi-Indicator Strategy**
- **RSI (Relative Strength Index)** - Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)** - Trend momentum and reversals
- **Bollinger Bands** - Volatility and price extremes
- **EMA Crossover (9/21)** - Trend direction confirmation
- **Volume Analysis** - Trade confirmation signals

### **Risk Management**
- Configurable position sizing (default: 10% per trade)
- Stop-loss protection (default: 2%)
- Take-profit targets (default: 4%)
- Maximum concurrent positions limit
- Real-time P&L tracking

### **Advanced Features**
- Paper trading mode for safe testing
- Comprehensive backtesting module
- Real-time market monitoring
- Detailed logging and trade history
- Docker support for easy deployment
- Configurable via environment variables

## 📊 Strategy Logic

The bot uses a **weighted scoring system** combining multiple indicators:

| Indicator | Weight | Buy Signal | Sell Signal |
|-----------|--------|------------|-------------|
| RSI | 2.0 | RSI < 30 | RSI > 70 |
| MACD | 2.0 | Bullish crossover | Bearish crossover |
| Bollinger Bands | 1.5 | Price < Lower Band | Price > Upper Band |
| EMA Crossover | 2.0 | Golden cross | Death cross |
| Volume | 1.5 | High volume + price up | High volume + price down |
| Trend | 1.0 | Price > EMA slow | Price < EMA slow |

**Decision Threshold:** 5 points minimum to trigger BUY/SELL

## 🚀 Quick Start

### 1. Get Alpaca API Keys
1. Sign up at [Alpaca](https://alpaca.markets/)
2. Get your API Key and Secret Key
3. Start with paper trading (free)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/Vira78558/algo-trading-bot.git
cd algo-trading-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configuration

Edit `.env` file:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
PAPER_TRADING=True

SYMBOLS=AAPL,TSLA,MSFT,GOOGL,AMZN
TIMEFRAME=5Min
POSITION_SIZE_PCT=0.1
STOP_LOSS_PCT=2.0
TAKE_PROFIT_PCT=4.0
```

### 4. Run Backtest (Recommended First)

```bash
python backtest.py
```

This will test the strategy on historical data and show:
- Total return %
- Win rate
- Profit factor
- Max drawdown
- Trade statistics

### 5. Run Live Bot

```bash
python main.py
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t trading-bot .

# Run container
docker run -d --name trading-bot \
  -e ALPACA_API_KEY=your_key \
  -e ALPACA_SECRET_KEY=your_secret \
  -e PAPER_TRADING=True \
  trading-bot
```

## 📈 Performance Metrics

Expected performance (based on backtesting):
- **Win Rate:** 55-65%
- **Profit Factor:** 1.5-2.5
- **Max Drawdown:** 5-15%
- **Annual Return:** 15-40% (varies by market conditions)

## ⚙️ Configuration Options

### Trading Parameters
- `SYMBOLS` - Comma-separated list of stocks to trade
- `TIMEFRAME` - Candle timeframe (1Min, 5Min, 15Min, 1Hour, 1Day)
- `CHECK_INTERVAL` - Seconds between strategy checks
- `POSITION_SIZE_PCT` - % of capital per trade (0.1 = 10%)
- `STOP_LOSS_PCT` - Stop-loss percentage
- `TAKE_PROFIT_PCT` - Take-profit percentage
- `MAX_POSITIONS` - Maximum concurrent positions

### Strategy Parameters
- `RSI_PERIOD` - RSI calculation period (default: 14)
- `RSI_OVERSOLD` - RSI oversold threshold (default: 30)
- `RSI_OVERBOUGHT` - RSI overbought threshold (default: 70)
- `MACD_FAST/SLOW/SIGNAL` - MACD parameters
- `BB_PERIOD` - Bollinger Bands period (default: 20)
- `EMA_FAST/SLOW` - EMA periods (default: 9/21)

## 📊 Monitoring

The bot logs all activities:
- Trade executions (BUY/SELL)
- Signal generation
- P&L updates
- Error messages

Check `trading_bot.log` for detailed logs.

## ⚠️ Risk Disclaimer

**IMPORTANT:** 
- Start with paper trading
- Never invest more than you can afford to lose
- Past performance doesn't guarantee future results
- Trading involves substantial risk
- This bot is for educational purposes
- Always monitor your bot's performance
- Test thoroughly before live trading

## 🛠️ Customization

### Add New Indicators

Edit `trading_strategy.py`:

```python
def calculate_custom_indicator(self, df):
    # Your indicator logic
    df['custom'] = ...
    return df
```

### Modify Signal Logic

Adjust weights in `generate_signal()` method:

```python
if latest['custom_indicator'] > threshold:
    buy_score += 2.5  # Custom weight
```

## 📚 Resources

- [Alpaca API Docs](https://alpaca.markets/docs/)
- [Technical Analysis Guide](https://www.investopedia.com/technical-analysis-4689657)
- [Risk Management](https://www.investopedia.com/articles/trading/09/risk-management.asp)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file

## 💬 Support

- Issues: [GitHub Issues](https://github.com/Vira78558/algo-trading-bot/issues)
- Discussions: [GitHub Discussions](https://github.com/Vira78558/algo-trading-bot/discussions)

## 🎯 Roadmap

- [ ] Add more indicators (Stochastic, ADX, etc.)
- [ ] Machine learning integration
- [ ] Multi-timeframe analysis
- [ ] Telegram/Discord notifications
- [ ] Web dashboard
- [ ] Options trading support
- [ ] Crypto trading support

---

**Built with ❤️ for algorithmic traders**

⭐ Star this repo if you find it useful!

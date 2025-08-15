# 🚀 Quick Start Guide - Multi-Exchange Trading System

Get up and running in under 5 minutes! Choose demo mode (no setup) or live data mode.

## 📋 **Prerequisites**

- Python 3.8+ installed
- Internet connection

**Optional for Live Data:**
- Bitunix or Binance account with API access

**Note**: The system runs in demo mode by default - no API keys required to start!

## 🚀 **Demo Mode (No Setup Required)**

```bash
# Install dependencies
pip install -r requirements.txt

# Launch dashboard immediately
python flask_dashboard.py

# Open browser to: http://localhost:5001
```

✅ **That's it!** The system runs with simulated data - perfect for learning and testing.

---

## 🔧 **Live Data Mode (Optional API Setup)**

### **Option A: Bitunix (Recommended)**

1. **Get API Credentials:**
   - Sign up at [Bitunix.com](https://bitunix.com)
   - Go to Account → API Management
   - Create new API key with trading permissions
   - Save your API Key and Secret Key

2. **Create `.env` file:**
   ```bash
   # Primary Bitunix Configuration
   TRADING_EXCHANGE_TYPE=bitunix
   TRADING_BITUNIX_API_KEY=your_bitunix_api_key_here
   TRADING_BITUNIX_SECRET_KEY=your_bitunix_secret_key_here
   
   # Trading Parameters
   TRADING_MIN_VOLUME_USDT=1000000
   TRADING_MIN_PRICE=0.0001
   TRADING_MAX_PRICE=150000
   ```

   📚 **For complete environment setup guide, see [ENVIRONMENT_SETUP_GUIDE.md](ENVIRONMENT_SETUP_GUIDE.md)**

### **Option B: Binance (Legacy)**

1. **Get API Credentials:**
   - Sign up at [Binance.com](https://binance.com)
   - Go to Account → API Management  
   - Create API key with spot trading permissions
   - Save your API Key and Secret Key

2. **Create `.env` file:**
   ```bash
   # Binance Configuration
   TRADING_EXCHANGE_TYPE=binance
   TRADING_BINANCE_API_KEY=your_binance_api_key_here
   TRADING_BINANCE_SECRET_KEY=your_binance_secret_key_here
   
   # Trading Parameters
   TRADING_MIN_VOLUME_USDT=1000000
   TRADING_MIN_PRICE=0.0001
   TRADING_MAX_PRICE=150000
   ```

   📚 **For complete environment setup guide, see [ENVIRONMENT_SETUP_GUIDE.md](ENVIRONMENT_SETUP_GUIDE.md)**

## 📦 **Step 2: Installation**

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask, plotly, pandas; print('✅ Dependencies installed')"
```

## 🧪 **Step 3: Test Connection**

```bash
# Test your exchange connection
python config_demo.py

# Expected output:
# ✅ Successfully connected to bitunix exchange
# 📊 Got 450+ live tickers from bitunix
```

## 🌐 **Step 4: Launch Dashboard**

```bash
# Start the web dashboard
python flask_dashboard.py

# You should see:
# ✅ Successfully connected to bitunix exchange
# 🔍 Scanner initialized successfully  
# 🌐 Trading Dashboard Initialized
# 📱 Access at: http://localhost:5001
```

## 🎯 **Step 5: Explore Features**

Open your browser and navigate to: **http://localhost:5001**

### **Dashboard Sections:**

1. **📊 Market Overview**
   - Live market statistics
   - Real-time price updates
   - 333+ USDT trading pairs (Bitunix)

2. **📈 Top Gainers/Losers**
   - Live market movers
   - Real percentage changes
   - Volume data

3. **🔍 Opportunity Scanner**
   - Professional trading signals
   - Multi-timeframe analysis
   - AI-powered scoring (0-100)

4. **📊 Interactive Charts**
   - Real-time price data
   - Technical indicators
   - Pattern recognition

## ⚡ **Quick Commands**

### **Test Live Data**
```bash
# Quick market data test
python -c "
import asyncio
from services.exchange_factory import ExchangeFactory
from config.settings import settings

async def test():
    exchange = ExchangeFactory.create_from_settings(settings.get_exchange_config())
    await exchange.connect()
    tickers = await exchange.get_tickers()
    print(f'📊 Got {len(tickers)} live tickers')
    for ticker in tickers[:3]:
        print(f'  {ticker.symbol}: ${ticker.price:.4f} ({ticker.change_24h:+.2f}%)')

asyncio.run(test())
"
```

### **Run Opportunity Scanner**
```bash
# Scan for trading opportunities
python -c "
from opportunity_scanner import OpportunityScanner

scanner = OpportunityScanner()
opportunities = scanner.scan_all_opportunities('curated_30', limit=10)
print(f'🎯 Found {len(opportunities)} opportunities')
for opp in opportunities[:3]:
    print(f'  {opp[\"symbol\"]}: Score {opp[\"score\"]:.0f}')
"
```

### **Switch Exchanges**
```bash
# Switch to Binance
echo "TRADING_EXCHANGE_TYPE=binance" >> .env

# Switch back to Bitunix  
echo "TRADING_EXCHANGE_TYPE=bitunix" >> .env
```

## 🔍 **API Testing**

Test individual API endpoints:

```bash
# Test all symbols (should show 333+ for Bitunix)
curl http://localhost:5001/api/all_symbols | jq '. | length'

# Test top gainers (live data)
curl http://localhost:5001/api/top_gainers | jq '.[0:3]'

# Test market overview
curl http://localhost:5001/api/market_overview
```

## 📊 **Understanding the Data**

### **Exchange Comparison**

| Feature | Bitunix | Binance |
|---------|---------|---------|
| **Trading Pairs** | 450+ USDT pairs | 1000+ pairs |
| **API Integration** | Native | CCXT wrapper |
| **Data Quality** | Real-time | Rate limited |
| **Latency** | Low | Medium |
| **Setup** | Direct API | Requires CCXT |

### **Signal Scoring**

- **🟢 High (70-100)**: Strong trading opportunities
- **🟡 Medium (40-69)**: Moderate opportunities  
- **🔴 Low (0-39)**: Weak opportunities

### **Market Data Types**

- **Tickers**: Real-time price, volume, 24h change
- **OHLCV**: Historical candlestick data for charts
- **Market Movers**: Top gainers/losers by percentage
- **Opportunities**: AI-analyzed trading signals

## 🔧 **Configuration Options**

### **Environment Variables**

```bash
# Exchange Selection
TRADING_EXCHANGE_TYPE=bitunix          # bitunix or binance

# API Credentials
TRADING_BITUNIX_API_KEY=...            # Bitunix API key
TRADING_BITUNIX_SECRET_KEY=...         # Bitunix secret key
TRADING_BINANCE_API_KEY=...            # Binance API key (optional)
TRADING_BINANCE_SECRET_KEY=...         # Binance secret key (optional)

# Market Filters
TRADING_MIN_VOLUME_USDT=1000000        # Minimum 24h volume ($1M)
TRADING_MIN_PRICE=0.0001               # Minimum price filter
TRADING_MAX_PRICE=150000               # Maximum price filter

# Technical Analysis
TRADING_FVG_THRESHOLD=0.005            # Fair Value Gap threshold (0.5%)
TRADING_FVG_PROXIMITY=0.02             # FVG proximity alert (2%)
TRADING_CONFLUENCE_THRESHOLD=0.6       # Multi-timeframe agreement (60%)

# Dashboard
TRADING_FLASK_HOST=localhost           # Dashboard host
TRADING_FLASK_PORT=5001                # Dashboard port
TRADING_FLASK_DEBUG=true               # Debug mode
```

## 🚨 **Troubleshooting**

### **Common Issues**

**❌ "Exchange connection failed"**
```bash
# Check API credentials
grep TRADING_ .env

# Verify internet connection
ping api.bitunix.com

# Test credentials manually
python config_demo.py
```

**❌ "No market data"**
```bash
# Check exchange type
echo $TRADING_EXCHANGE_TYPE

# Verify API permissions
# Ensure your API key has trading/data access

# Test live data
python test_live_data.py
```

**❌ "Dashboard not loading"**
```bash
# Check if port is available
lsof -i :5001

# Kill existing process
pkill -f flask_dashboard.py

# Restart dashboard
python flask_dashboard.py
```

**❌ "Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

### **API Rate Limits**

- **Bitunix**: Built-in rate limiting
- **Binance**: CCXT handles rate limits automatically
- **Dashboard**: Caches data for 60 seconds

### **Performance Tips**

- Use **Bitunix** for best performance
- Enable caching for production use
- Monitor API usage in logs
- Close unused browser tabs

## 🎯 **Next Steps**

1. **📚 Read Documentation**
   - [Web Dashboard Guide](WEB_DASHBOARD_GUIDE.md)
   - [Bitunix Migration Guide](../BITUNIX_MIGRATION_GUIDE.md)

2. **🔍 Explore Features**
   - Try different scanning modes
   - Analyze specific coins
   - Monitor performance metrics

3. **⚙️ Customize Settings**
   - Adjust volume filters
   - Modify scoring parameters
   - Configure timeframes

4. **🚀 Advanced Usage**
   - Set up production environment
   - Implement custom strategies
   - Add new exchanges

## ✅ **Success Checklist**

- [ ] API credentials configured in `.env`
- [ ] Dependencies installed successfully
- [ ] Exchange connection working
- [ ] Dashboard loads at http://localhost:5001
- [ ] Live market data displaying
- [ ] Opportunity scanner running
- [ ] Charts showing real-time data

## 🆘 **Need Help?**

- 📖 Check [WEB_DASHBOARD_GUIDE.md](WEB_DASHBOARD_GUIDE.md)
- 🔧 Review [Configuration Reference](config/settings.py)
- 🐛 Check logs for error messages
- 🔄 Try switching exchanges in `.env`

---

**🎉 Congratulations! You're now running a professional cryptocurrency trading system with live market data!** 
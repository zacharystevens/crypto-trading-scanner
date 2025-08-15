# 🎭 Demo Scripts Guide

This document explains all the demo scripts included in the trading system and their purposes.

## 📚 **Overview**

The trading system includes several demo scripts to help you:
- Test system components
- Learn how features work
- Verify your setup
- Explore advanced functionality

---

## 🚀 **Quick Start Demos**

### `config_demo.py`
**Purpose**: Test configuration management system
**Usage**: `python config_demo.py`
**What it shows**:
- ✅ Configuration loading
- ✅ Environment detection
- ✅ Service factory initialization
- ✅ Shared configuration across services

**Output Example**:
```
🔧 CONFIGURATION MANAGEMENT DEMO
==================================================
✅ Configuration loaded successfully!
Environment: development
Timeframes: ['5m', '15m', '30m', '1h', '4h']
Min Volume USDT: 1,000,000
FVG Threshold: 0.005
Cache Durations: {'default': 900, 'market': 300, 'analysis': 1800}
```

**When to use**: First step to verify your installation

---

## 🌐 **Exchange Integration Demos**

### `bitunix_demo.py`
**Purpose**: Test Bitunix exchange integration
**Requirements**: Bitunix API keys in `.env` file
**Usage**: `python bitunix_demo.py`
**What it demonstrates**:
- ✅ Exchange connection and authentication
- ✅ Live market data retrieval
- ✅ Real-time ticker information
- ✅ OHLCV data fetching
- ✅ Symbol validation and formatting

**Key Features Tested**:
- Connection to Bitunix API
- Fetching 450+ trading pairs
- Real-time price data
- Volume and market data
- Error handling and validation

**Output Example**:
```
🚀 BITUNIX TRADING SYSTEM DEMO
============================================================
📊 Exchange Type: bitunix
🌍 Environment: development
🔗 Creating bitunix exchange connection...
✅ Successfully connected to Bitunix exchange
📊 Got 450+ live tickers from Bitunix
💰 Sample Ticker: BTC/USDT: $45,250.50 (+2.35%)
```

**When to use**: Test live Bitunix API integration

---

## 📊 **Analysis & Strategy Demos**

### `btc_professional_demo.py`
**Purpose**: Professional BTC analysis demonstration
**Usage**: `python btc_professional_demo.py`
**What it shows**:
- ✅ Multi-timeframe analysis (15m, 1h, 4h, 1d)
- ✅ Fair Value Gap (FVG) detection
- ✅ Confluence scoring system
- ✅ Professional trading signals
- ✅ Risk assessment and confidence levels

**Analysis Features**:
- FVG proximity alerts
- Trendline analysis
- Volume confirmation
- Multi-timeframe confluence
- Entry/exit recommendations

**Output Example**:
```
📈 BTC PROFESSIONAL ANALYSIS
════════════════════════════════════
🎯 Symbol: BTC/USDT
💰 Current Price: $45,250.50
📊 Analysis Score: 75/100 (Strong Signal)
🔍 Signal Type: BULLISH
⏰ Timeframes: 3/4 Bullish Confluence
📈 FVG Zones: 2 Bullish, 1 Bearish
🎯 Entry: $44,800 - $45,200
🛑 Stop Loss: $44,200
🎯 Take Profit: $46,500
```

**When to use**: Learn professional analysis techniques

### `extended_analysis_demo.py`
**Purpose**: Compare quick vs. extended analysis modes
**Usage**: `python extended_analysis_demo.py`
**What it demonstrates**:
- ✅ Curated 30-coin analysis (fast)
- ✅ Extended 400+ coin analysis (comprehensive)
- ✅ Performance timing comparison
- ✅ Throttling system demonstration
- ✅ Analysis depth differences

**Comparison Features**:
- Speed vs. thoroughness trade-offs
- Throttling to prevent API overload
- Different scanning strategies
- Time estimation for full scans

**When to use**: Understand scanning performance and options

---

## 🔄 **Confirmation System Demos**

### `confirmation_demo.py`
**Purpose**: Test the 5-minute confirmation candle system
**Requirements**: Exchange connection (uses Binance via CCXT)
**Usage**: `python confirmation_demo.py`
**What it shows**:
- ✅ Signal confirmation workflow
- ✅ 5-minute candle analysis
- ✅ Confirmation scoring system
- ✅ Time-based validation
- ✅ Signal strength assessment

**Confirmation Process**:
1. Simulates trading signal detection
2. Waits for 5-minute confirmation
3. Analyzes price action post-signal
4. Scores confirmation strength
5. Provides final recommendation

**When to use**: Understand signal confirmation process

### `confirmation_demo_offline.py`
**Purpose**: Offline confirmation system testing
**Usage**: `python confirmation_demo_offline.py`
**What it shows**:
- ✅ Confirmation system without live data
- ✅ Historical data simulation
- ✅ Backtesting confirmation logic
- ✅ Validation of confirmation algorithms

**When to use**: Test confirmation logic without API access

---

## 🌐 **Web Interface Demos**

### `web_dashboard_demo.py`
**Purpose**: Simplified web dashboard for testing
**Usage**: `python web_dashboard_demo.py`
**What it provides**:
- ✅ Lightweight dashboard version
- ✅ Basic market data display
- ✅ Core functionality testing
- ✅ Development environment

**Features**:
- Simplified UI for testing
- Core market data endpoints
- Basic charting functionality
- Reduced complexity for debugging

**When to use**: Debug web interface issues or test basic functionality

---

## ⚡ **Quick Demo Commands**

### Test Basic Setup
```bash
# 1. Test configuration
python config_demo.py

# 2. Test web interface (demo mode)
python web_dashboard_demo.py
# Open: http://localhost:5001

# 3. Test extended analysis
python extended_analysis_demo.py
```

### Test With Live Data (Requires API Keys)
```bash
# 1. Configure .env file first
echo "TRADING_EXCHANGE_TYPE=bitunix" > .env
echo "TRADING_BITUNIX_API_KEY=your_key" >> .env
echo "TRADING_BITUNIX_SECRET_KEY=your_secret" >> .env

# 2. Test exchange connection
python bitunix_demo.py

# 3. Test confirmation system
python confirmation_demo.py

# 4. Run professional analysis
python btc_professional_demo.py
```

### Full System Demo
```bash
# Run the complete dashboard (best experience)
python flask_dashboard.py
# Open: http://localhost:5001
```

---

## 🎯 **Demo Sequence Recommendations**

### **First Time Users**
1. `config_demo.py` - Verify installation
2. `web_dashboard_demo.py` - Test web interface
3. `extended_analysis_demo.py` - Learn analysis features
4. `flask_dashboard.py` - Experience full system

### **API Testing** 
1. `config_demo.py` - Verify configuration
2. `bitunix_demo.py` - Test exchange connection
3. `btc_professional_demo.py` - Test live analysis
4. `flask_dashboard.py` - Full live system

### **Advanced Users**
1. `confirmation_demo.py` - Signal confirmation
2. `extended_analysis_demo.py` - Performance testing
3. Custom modifications to demo scripts
4. Production deployment testing

---

## 🔧 **Troubleshooting Demo Scripts**

### **Common Issues**

**"ModuleNotFoundError"**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask, plotly, pandas; print('✅ All modules installed')"
```

**"Exchange connection failed"**
```bash
# Check API credentials
grep TRADING_ .env

# Test internet connection
ping api.bitunix.com

# Use demo mode instead
python web_dashboard_demo.py
```

**"No data showing"**
```bash
# Use offline demo for testing
python confirmation_demo_offline.py

# Check exchange status
python config_demo.py
```

### **Demo Script Status**

| Script | Mode | Requirements | Purpose |
|--------|------|-------------|---------|
| `config_demo.py` | ✅ Offline | None | Configuration test |
| `web_dashboard_demo.py` | ✅ Demo | None | Web interface test |
| `extended_analysis_demo.py` | ✅ Demo/Live | Optional API | Analysis comparison |
| `bitunix_demo.py` | 🔐 Live | API Keys | Exchange testing |
| `btc_professional_demo.py` | 🔐 Live | API Keys | Professional analysis |
| `confirmation_demo.py` | 🔐 Live | API Keys | Confirmation system |
| `confirmation_demo_offline.py` | ✅ Offline | None | Offline confirmation |

**Legend:**
- ✅ Works without API keys
- 🔐 Requires API keys
- Demo: Uses simulated data
- Live: Uses real market data
- Offline: No internet required

---

## 📚 **Learning Path**

1. **Start Here**: `config_demo.py` - Verify your setup works
2. **Web Interface**: `web_dashboard_demo.py` - See the dashboard
3. **Analysis**: `extended_analysis_demo.py` - Learn analysis features
4. **Professional**: `btc_professional_demo.py` - Advanced analysis
5. **Full System**: `flask_dashboard.py` - Complete experience

Each demo builds on the previous one, teaching you different aspects of the trading system.

---

**🎉 Ready to explore? Start with `python config_demo.py` to verify your setup!**

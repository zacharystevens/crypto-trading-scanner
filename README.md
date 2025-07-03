# Professional Trading System with Multi-Exchange Support

A comprehensive cryptocurrency trading system featuring professional-grade technical analysis, opportunity scanning, and multi-exchange integration with live market data.

## 🚀 **Key Features**

### **Multi-Exchange Architecture**
- ✅ **Bitunix Integration** - Primary exchange with full API support
- ✅ **Binance Support** - Backward compatibility via CCXT
- ✅ **Exchange Abstraction Layer** - Easy switching between exchanges
- ✅ **Unified API Interface** - Consistent data formats across exchanges

### **Professional Trading Tools**
- 📊 **Real-Time Market Data** - Live prices, volumes, and market movements
- 🔍 **Opportunity Scanner** - Advanced pattern detection and scoring
- 📈 **Technical Analysis** - FVG, trendlines, RSI, EMA indicators
- 🌐 **Web Dashboard** - Interactive charts and real-time monitoring
- ⚡ **Multi-Timeframe Analysis** - 15m, 1h, 4h, 1d confluence system

### **Configuration Management**
- 🔧 **Environment-Based Config** - Development/Production modes
- 🔐 **Secure Authentication** - API keys via environment variables
- ⚙️ **Flexible Settings** - Easy customization of all parameters
- 📝 **Comprehensive Logging** - Detailed system monitoring

## 🔧 **Quick Setup**

### **1. Authentication Configuration**

Create a `.env` file with your exchange credentials:

```bash
# Exchange Configuration
TRADING_EXCHANGE_TYPE=bitunix  # or 'binance'

# Bitunix API Credentials (Primary)
TRADING_BITUNIX_API_KEY=your_bitunix_api_key
TRADING_BITUNIX_SECRET_KEY=your_bitunix_secret_key

# Binance API Credentials (Optional)
TRADING_BINANCE_API_KEY=your_binance_api_key
TRADING_BINANCE_SECRET_KEY=your_binance_secret_key

# Trading Parameters
TRADING_MIN_VOLUME_USDT=1000000
TRADING_MIN_PRICE=0.0001
TRADING_MAX_PRICE=150000
```

### **2. Installation**

```bash
# Install dependencies
pip install -r requirements.txt

# Verify configuration
python config_demo.py
```

### **3. Launch Dashboard**

```bash
# Start web dashboard with live data
python flask_dashboard.py

# Access at: http://localhost:5001
```

## 📖 **API Choice & Exchange Configuration**

### **Supported Exchanges**

| Exchange | Status | Features | Authentication |
|----------|--------|----------|----------------|
| **Bitunix** | ✅ Primary | Full API, Live Data, 450+ Pairs | API Key + Secret |
| **Binance** | ✅ Legacy | CCXT Integration, Backup | API Key + Secret |

### **Switching Exchanges**

Simply change the `TRADING_EXCHANGE_TYPE` in your `.env` file:

```bash
# Use Bitunix (Recommended)
TRADING_EXCHANGE_TYPE=bitunix

# Use Binance (Legacy)
TRADING_EXCHANGE_TYPE=binance
```

### **Exchange-Specific Features**

**Bitunix Advantages:**
- 450+ USDT trading pairs
- Real-time market data
- Advanced order types
- Low latency API

**Binance Compatibility:**
- CCXT library integration
- Historical data access
- Global market coverage

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │───▶│ Exchange Factory │───▶│ Exchange Adapter│
│                 │    │                  │    │                 │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • Dashboard     │    │ • Configuration  │    │ • Bitunix API   │
│ • Scanner       │    │ • Registry       │    │ • Binance CCXT  │
│ • Analyzer      │    │ • Error Handling │    │ • Symbol Format │
│ • Executor      │    │ • Validation     │    │ • Data Transform│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 **Core Components**

### **1. OpportunityScanner**
- Multi-timeframe confluence analysis
- Fair Value Gap (FVG) detection  
- Pattern recognition (Head & Shoulders, Flags, etc.)
- Volume analysis and market mover detection
- Professional scoring system (0-100)

### **2. Flask Dashboard**
- Real-time market overview
- Interactive price charts with indicators
- Top gainers/losers tracking
- Signal logging and performance tracking
- Responsive web interface

### **3. Exchange Adapters**
- **BitunixAdapter**: Native API integration
- **BinanceAdapter**: CCXT wrapper
- Unified data formats (Ticker, OHLCV)
- Automatic symbol conversion (BTC/USDT ↔ BTCUSDT)

### **4. Configuration System**
- Pydantic-based settings validation
- Environment variable management
- Multi-environment support (dev/prod)
- Comprehensive error handling

## 🔐 **Authentication Setup**

### **Getting Bitunix API Keys**

1. **Create Account**: Sign up at [Bitunix.com](https://bitunix.com)
2. **API Management**: Navigate to Account → API Management
3. **Create API Key**: Generate new API key with trading permissions
4. **Security**: Enable IP restrictions and 2FA
5. **Configure**: Add credentials to `.env` file

### **Getting Binance API Keys** (Optional)

1. **Create Account**: Sign up at [Binance.com](https://binance.com)
2. **API Management**: Go to Account → API Management
3. **Create API Key**: Generate key with spot trading permissions
4. **Configure**: Add credentials to `.env` file

## 📈 **Usage Examples**

### **Market Analysis**
```python
from opportunity_scanner import OpportunityScanner

scanner = OpportunityScanner()
opportunities = scanner.scan_all_opportunities('curated_30')
top_10 = sorted(opportunities, key=lambda x: x['score'], reverse=True)[:10]
```

### **Live Data Access**
```python
from services.exchange_factory import ExchangeFactory
from config.settings import settings

exchange = ExchangeFactory.create_from_settings(settings.get_exchange_config())
await exchange.connect()
tickers = await exchange.get_tickers()
```

### **Custom Analysis**
```python
symbol = 'BTC/USDT'
analysis = scanner.analyze_single_coin(symbol)
print(f"Score: {analysis['score']}, Signal: {analysis.get('signal_class')}")
```

## 📚 **Documentation**

- 📖 [Quick Start Guide](QUICK_START.md) - Get up and running in 5 minutes
- 🌐 [Web Dashboard Guide](WEB_DASHBOARD_GUIDE.md) - Dashboard features and usage
- 🔄 [Bitunix Migration Guide](../BITUNIX_MIGRATION_GUIDE.md) - Detailed migration instructions
- ⚙️ [Configuration Reference](config/settings.py) - All available settings

## 🛠️ **Development**

### **Running Tests**
```bash
# Unit tests
python -m pytest tests/

# Integration tests with live API
python tests/test_bitunix_adapter.py
```

### **Adding New Exchanges**
1. Create new adapter class inheriting from `ExchangeInterface`
2. Implement required methods: `connect()`, `get_tickers()`, `get_ohlcv()`
3. Register in `ExchangeFactory`
4. Add configuration support

## 🔧 **Troubleshooting**

### **Common Issues**

**Exchange Connection Failed:**
- Verify API credentials in `.env`
- Check internet connection
- Ensure API permissions are set correctly

**No Market Data:**
- Confirm exchange type is set correctly
- Check API rate limits
- Verify symbol format (BTC/USDT vs BTCUSDT)

**Dashboard Not Loading:**
- Ensure port 5001 is available
- Check Flask debug output
- Verify all dependencies installed

## 📊 **Performance Monitoring**

The system includes comprehensive logging and monitoring:
- Exchange connection status
- API response times
- Data quality validation
- Error tracking and recovery

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for professional cryptocurrency trading** 
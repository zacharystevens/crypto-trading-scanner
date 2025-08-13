# Professional Trading System with Multi-Exchange Support

A comprehensive cryptocurrency trading system featuring professional-grade technical analysis, opportunity scanning, and multi-exchange integration with live market data.

---

# 🚀 **QUICK START - GET RUNNING IN 5 MINUTES**

## **📋 Prerequisites**
- **Windows 10/11** (64-bit)
- **Internet connection** for data and dependencies
- **Basic computer knowledge**

---

## **🔧 INSTALLATION GUIDE**

### Cross-platform quick start

- macOS/Linux:
  - `bash scripts/setup_and_run_unix.sh`
- Windows (PowerShell):
  - `powershell -ExecutionPolicy Bypass -File scripts/setup_and_run_windows.ps1`
- Windows (CMD):
  - `scripts\setup_and_run_windows.bat`

These scripts create a `.venv`, install `requirements.txt`, and run `flask_dashboard.py`.

### **Step 1: Install Python (Required)**

#### **Download Python:**
1. **Go to**: [python.org/downloads](https://www.python.org/downloads/)
2. **Click**: "Download Python 3.x.x" (latest version)
3. **Save** the installer file

#### **Install Python:**
1. **Double-click** the downloaded Python installer
2. **IMPORTANT**: ✅ **Check "Add Python to PATH"** checkbox
3. **Click**: "Install Now"
4. **Wait** for installation to complete
5. **Click**: "Close"

#### **Verify Installation:**
1. **Press**: `Windows + R`
2. **Type**: `cmd` and press Enter
3. **Type**: `python --version`
4. **Expected**: `Python 3.x.x`

### **Step 2: Download & Extract Trading System**

#### **Download:**
1. **Download** the trading system ZIP file
2. **Right-click** the ZIP file
3. **Select**: "Extract All..."
4. **Choose**: Desktop or Documents folder
5. **Click**: "Extract"

#### **Verify Files:**
You should see these files in the extracted folder:
- ✅ `LAUNCH_DASHBOARD.bat`
- ✅ `flask_dashboard.py`
- ✅ `requirements.txt`
- ✅ `README.md`

### **Step 3: Launch the System**

#### **One-Click Launch (Easiest):**
1. **Navigate** to the extracted folder
2. **Double-click**: `LAUNCH_DASHBOARD.bat`
3. **Wait** for the system to start (2-3 minutes)
4. **Browser opens** automatically to `http://localhost:5001`

#### **What Happens:**
- ✅ **Dependencies install** automatically
- ✅ **System starts** in new CMD window
- ✅ **Browser opens** to dashboard
- ✅ **Real-time monitoring** begins

---

## **🎯 FIRST TIME SETUP**

### **If You See Errors:**

#### **"Python not found" Error:**
1. **Reinstall Python** with "Add to PATH" checked
2. **Restart** your computer
3. **Try again**

#### **"Port 5001 in use" Error:**
1. **Close** any other applications
2. **Restart** the batch file
3. **Or wait** 30 seconds and try again

#### **"Dependencies failed" Error:**
1. **Check** internet connection
2. **Try**: `pip install --user -r requirements.txt`
3. **Contact** support if issues persist

### **Success Indicators:**
- ✅ **CMD window shows**: "Running on http://localhost:5001"
- ✅ **Browser opens** to trading dashboard
- ✅ **Charts load** with data
- ✅ **No error messages** in CMD window

---

## **🌐 USING THE DASHBOARD**

### **Main Features:**
- **📊 Live Charts**: Interactive price charts with indicators
- **🚨 Real-time Alerts**: Audio and popup notifications
- **📈 Market Data**: Top gainers, losers, and movers
- **🔍 Symbol Search**: Search any cryptocurrency

### **Quick Navigation:**
1. **Search Box**: Type any coin (BTC, ETH, etc.)
2. **Timeframes**: Select 15m, 1h, 4h, 1d
3. **Charts**: Zoom, pan, and analyze
4. **Alerts**: Monitor CMD window for signals

---

## **🚨 ALERT SYSTEM**

### **What Triggers Alerts:**
- **📈 Bullish**: EMA20 crosses above EMA50 + RSI < 70 + Volume > 1.2x
- **📉 Bearish**: EMA20 crosses below EMA50 + RSI > 30 + Volume > 1.2x

### **Alert Types:**
- **🔊 Audio**: 3-second beeps (different tones for bullish/bearish)
- **📱 Popup**: Professional notification window with close button
- **📝 Console**: Detailed information in CMD window

### **Audio Controls:**
- **Toggle On/Off**: Use API endpoints
- **Default**: Audio is ON
- **Duration**: 3 seconds per alert

---

## **🛠️ TROUBLESHOOTING**

### **Common Issues:**

#### **System Won't Start:**
1. **Check Python**: `python --version`
2. **Check files**: Verify all files are present
3. **Check internet**: Ensure stable connection
4. **Try restart**: Close and reopen batch file

#### **Dashboard Not Loading:**
1. **Wait longer**: System takes 2-3 minutes to start
2. **Check CMD window**: Look for error messages
3. **Try manual**: `python flask_dashboard.py`
4. **Check browser**: Try different browser

#### **No Alerts:**
1. **Check monitoring**: CMD window should show "Monitoring"
2. **Wait for signals**: Alerts only trigger when conditions are met
3. **Check audio**: Verify system volume is on
4. **Check cooldown**: 5-minute cooldown between alerts

### **Getting Help:**
- **Read logs**: Check CMD window for error messages
- **Restart system**: Close all windows and try again
- **Check manual**: See detailed manual below
- **Contact support**: If issues persist

---

## **✅ SUCCESS CHECKLIST**

After installation, you should have:
- ✅ **Python installed** and working
- ✅ **Trading system extracted** to folder
- ✅ **Batch file launches** without errors
- ✅ **Dashboard opens** in browser
- ✅ **Charts display** with data
- ✅ **Alerts system** monitoring (CMD window)
- ✅ **Audio alerts** working (test with volume)

---

**🎉 Congratulations! You're ready to start trading analysis!**

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

# 📚 **COMPLETE INSTALLATION & USAGE MANUAL**

## 🚀 **Step-by-Step Installation Guide**

### **Step 1: Install Python (Required)**

#### **Windows Installation:**
1. **Download Python**: Go to [python.org](https://www.python.org/downloads/)
2. **Download Latest Version**: Click "Download Python 3.x.x"
3. **Run Installer**: Double-click the downloaded file
4. **Important**: ✅ **Check "Add Python to PATH"** during installation
5. **Complete Installation**: Click "Install Now"

#### **Verify Python Installation:**
```cmd
python --version
```
**Expected Output**: `Python 3.x.x`

### **Step 2: Download Trading System**

1. **Extract Files**: Unzip the trading system to your desired location
2. **Recommended Path**: `C:\Users\[YourUsername]\Desktop\tcss-trading-system-main\`
3. **Verify Files**: You should see `flask_dashboard.py`, `requirements.txt`, etc.

### **Step 3: Install Dependencies**

#### **Method 1: Using Batch File (Recommended)**
1. **Navigate** to the trading system folder
2. **Double-click** `LAUNCH_DASHBOARD.bat`
3. **The batch file will automatically install dependencies**

#### **Method 2: Manual Installation**
```cmd
cd "C:\Users\[YourUsername]\Desktop\tcss-trading-system-main"
pip install -r requirements.txt
```

### **Step 4: Configure Exchange (Optional)**

#### **For Live Trading (Optional):**
1. **Create `.env` file** in the trading system folder
2. **Add your API credentials**:

```bash
# Exchange Configuration
TRADING_EXCHANGE_TYPE=bitunix

# Bitunix API Credentials (Get from bitunix.com)
TRADING_BITUNIX_API_KEY=your_api_key_here
TRADING_BITUNIX_SECRET_KEY=your_secret_key_here

# Trading Parameters
TRADING_MIN_VOLUME_USDT=1000000
TRADING_MIN_PRICE=0.0001
TRADING_MAX_PRICE=150000
```

#### **For Demo Mode (No Setup Required):**
- **Skip this step** if you want to use demo data
- **System will run with sample data** automatically

### **Step 5: Launch the System**

#### **Easy Launch (Recommended):**
1. **Double-click** `LAUNCH_DASHBOARD.bat`
2. **Wait** for the system to start
3. **Browser will open** automatically to `http://localhost:5001`

#### **Manual Launch:**
```cmd
cd "C:\Users\[YourUsername]\Desktop\tcss-trading-system-main"
python flask_dashboard.py
```

---

## 📊 **TECHNICAL INDICATORS USED**

### **📈 Moving Averages**
- **EMA20** (Exponential Moving Average - 20 periods)
  - **Color**: Orange solid line
  - **Purpose**: Short-term trend identification
- **EMA50** (Exponential Moving Average - 50 periods)
  - **Color**: Blue solid line
  - **Purpose**: Medium-term trend identification
- **SMA20** (Simple Moving Average - 20 periods)
  - **Color**: Yellow dashed line
  - **Purpose**: Short-term support/resistance
- **SMA50** (Simple Moving Average - 50 periods)
  - **Color**: Purple dashed line
  - **Purpose**: Medium-term support/resistance

### **📊 RSI (Relative Strength Index)**
- **Period**: 14 (standard)
- **Overbought Level**: 70
- **Oversold Level**: 30
- **Purpose**: Momentum and reversal signals
- **Display**: Separate chart panel below price

### **📊 Volume Analysis**
- **Volume SMA** (20-period average)
  - **Color**: Green line on volume chart
  - **Purpose**: Volume trend identification
- **Volume Ratio**: Current volume vs. average
- **Volume Spike Detection**: Unusual volume activity

### **🎯 Fair Value Gaps (FVG)**
- **Bullish FVG**: Price gaps up (potential support)
- **Bearish FVG**: Price gaps down (potential resistance)
- **Display**: Transparent colored zones on chart
- **Purpose**: Identify potential reversal areas

### **📐 Trendlines**
- **Support Lines**: Connecting higher lows
- **Resistance Lines**: Connecting lower highs
- **Breakout Detection**: Price breaking through trendlines
- **Purpose**: Identify trend direction and potential reversals

### **🔍 Chart Patterns**
- **Head & Shoulders**: Reversal pattern
- **Double/Triple Tops/Bottoms**: Reversal patterns
- **Flags & Pennants**: Continuation patterns
- **Purpose**: Pattern-based trading signals

---

## 🌐 **DASHBOARD USAGE GUIDE**

### **🏠 Main Dashboard Features**

#### **1. Market Overview**
- **Top Gainers**: Coins with highest 24h gains
- **Top Losers**: Coins with highest 24h losses
- **Market Movers**: Most active coins by volume
- **Real-time Updates**: Data refreshes every 30 seconds

#### **2. Interactive Charts**
- **Multi-timeframe**: 15m, 1h, 4h, 1d
- **Technical Indicators**: All indicators displayed
- **Zoom & Pan**: Interactive chart navigation
- **Color Legend**: Top-left corner shows indicator colors

#### **3. Symbol Search**
- **Search Box**: Type any coin symbol (BTC, ETH, etc.)
- **Auto-complete**: Suggests available symbols
- **Quick Access**: Instant chart loading

#### **4. Real-time Data**
- **Live Prices**: Updated every 30 seconds
- **Volume Data**: Real-time volume information
- **Market Cap**: Current market capitalization
- **24h Changes**: Price changes over 24 hours

### **📊 Chart Navigation**

#### **Timeframe Selection**
- **15m**: Short-term analysis
- **1h**: Medium-term analysis (default)
- **4h**: Long-term analysis
- **1d**: Daily analysis

#### **Chart Controls**
- **Zoom**: Mouse wheel or zoom buttons
- **Pan**: Click and drag to move chart
- **Reset**: Double-click to reset view
- **Fullscreen**: Expand chart to full window

#### **Indicator Legend**
```
🟠 EMA20 (Orange) - Short-term trend
🔵 EMA50 (Blue) - Medium-term trend
🟡 SMA20 (Yellow Dash) - Short-term support/resistance
🟣 SMA50 (Purple Dash) - Medium-term support/resistance
🟢 Volume SMA (Green) - Volume trend
```

---

## ⏰ **UPDATE FREQUENCIES**

### **🔄 Real-time Updates**
- **Market Data**: Every 30 seconds
- **Price Charts**: Every 30 seconds
- **Volume Data**: Every 30 seconds
- **Top Movers**: Every 30 seconds

### **🚨 Alert Monitoring**
- **Signal Detection**: Every 30 seconds
- **Top 100 Coins**: Monitored continuously
- **Market Movers**: Top 40 gainers + 40 losers
- **Background Processing**: Non-stop monitoring

### **📊 Data Caching**
- **Chart Data**: Cached for 15 minutes
- **Market Movers**: Cached for 15 minutes
- **Technical Analysis**: Calculated in real-time
- **Alert History**: Stored in database

---

## 🚨 **ALERT SYSTEM GUIDE**

### **🎯 Alert Conditions**

#### **Bullish Signal (LONG)**
- **EMA20 crosses above EMA50**
- **RSI < 70** (not overbought)
- **Volume > 1.2x average**
- **Confidence Score**: Based on RSI and volume

#### **Bearish Signal (SHORT)**
- **EMA20 crosses below EMA50**
- **RSI > 30** (not oversold)
- **Volume > 1.2x average**
- **Confidence Score**: Based on RSI and volume

### **🔊 Audio Alerts**

#### **Audio Settings**
- **Duration**: 3 seconds total
- **Bullish Signal**: High-pitched beep (800Hz)
- **Bearish Signal**: Low-pitched beep (400Hz)
- **Default**: Audio alerts are **ON**

#### **Audio Control**
```bash
# Toggle audio on/off
POST http://localhost:5001/api/audio/toggle

# Check audio status
GET http://localhost:5001/api/audio/status

# Set audio on/off
POST http://localhost:5001/api/audio/set
Content-Type: application/json
{"enabled": false}
```

### **📱 Popup Notifications**

#### **Popup Features**
- **Professional Design**: Dark theme with clear information
- **Close Button**: ✕ button in top-right corner
- **Auto-close**: Automatically closes after 10 seconds
- **Always on Top**: Appears above other windows

#### **Popup Information**
```
🚨 TRADING ALERT - LONG/SHORT
📈/📉 BTC/USDT
💰 Price: $45,250.00
📊 RSI: 45.2
🔊 Volume: 1.5x average
🎯 Confidence: 85%
⏰ 1h | 14:30:25
```

### **📝 Console Alerts**
- **Detailed Information**: Full signal details
- **Real-time Output**: Appears in CMD window
- **Historical Log**: All alerts stored in database
- **Format**: Clear, easy-to-read format

### **💾 Alert Storage**
- **Database**: SQLite database (`trading_signals.db`)
- **Active Alerts**: Last 10 alerts in memory
- **API Access**: `/api/alerts` endpoint
- **Cooldown**: 5 minutes between alerts for same symbol

---

## 🛠️ **TROUBLESHOOTING GUIDE**

### **❌ Common Installation Issues**

#### **"Python is not recognized"**
**Solution:**
1. **Reinstall Python** with "Add to PATH" checked
2. **Restart Command Prompt** after installation
3. **Verify**: `python --version`

#### **"pip is not recognized"**
**Solution:**
1. **Install pip**: `python -m ensurepip --upgrade`
2. **Add to PATH**: Add Python Scripts folder to PATH
3. **Verify**: `pip --version`

#### **"ModuleNotFoundError"**
**Solution:**
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Use user installation**: `pip install --user -r requirements.txt`
3. **Check Python version**: Ensure Python 3.7+

### **❌ Runtime Issues**

#### **"Port 5001 already in use"**
**Solution:**
```cmd
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process
taskkill /PID [process_id] /F
```

#### **"Exchange connection failed"**
**Solution:**
1. **Check internet connection**
2. **Verify API credentials** in `.env` file
3. **Use demo mode** if no API keys
4. **Check firewall settings**

#### **"Audio alerts not working"**
**Solution:**
1. **Check system volume**
2. **Verify audio device** is working
3. **Test audio**: `winsound.Beep(800, 1000)`
4. **Toggle audio**: Use API endpoints

### **❌ Dashboard Issues**

#### **"Dashboard not loading"**
**Solution:**
1. **Check if server is running** in CMD window
2. **Verify URL**: `http://localhost:5001`
3. **Clear browser cache**
4. **Try different browser**

#### **"Charts not displaying"**
**Solution:**
1. **Check internet connection** (for chart libraries)
2. **Refresh page**
3. **Clear browser cache**
4. **Check browser console** for errors

#### **"No data showing"**
**Solution:**
1. **Wait 30 seconds** for initial data load
2. **Check CMD window** for error messages
3. **Verify exchange connection**
4. **Try demo mode** if live data fails

### **❌ Alert Issues**

#### **"No alerts appearing"**
**Solution:**
1. **Check if monitoring is active** in CMD window
2. **Verify alert conditions** are met
3. **Check cooldown period** (5 minutes)
4. **Test with known signals**

#### **"Popup not appearing"**
**Solution:**
1. **Check Windows notifications** are enabled
2. **Verify popup permissions** in browser
3. **Check if window is minimized**
4. **Test popup manually**

---

## 📞 **SUPPORT & HELP**

### **🔧 Getting Help**

#### **Check Logs**
- **CMD Window**: Real-time system logs
- **Error Messages**: Clear error descriptions
- **Status Updates**: System status information

#### **Common Commands**
```cmd
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check system status
netstat -ano | findstr :5001
```

#### **Reset System**
```cmd
# Stop all processes
taskkill /F /IM python.exe

# Clear cache (optional)
del trading_signals.db

# Restart system
LAUNCH_DASHBOARD.bat
```

### **📚 Additional Resources**
- **Quick Start**: `QUICK_START.md`
- **Web Dashboard**: `WEB_DASHBOARD_GUIDE.md`
- **Configuration**: `config/settings.py`
- **API Documentation**: Check API endpoints in code

---

## 🎯 **QUICK REFERENCE**

### **🚀 One-Click Launch**
1. **Double-click** `LAUNCH_DASHBOARD.bat`
2. **Wait** for system to start
3. **Browser opens** automatically
4. **Monitor** CMD window for alerts

### **🔊 Audio Controls**
- **Toggle**: Use API endpoint `/api/audio/toggle`
- **Status**: Check `/api/audio/status`
- **Set**: POST to `/api/audio/set`

### **📊 Key Indicators**
- **EMA20/50**: Trend direction
- **RSI**: Momentum and reversals
- **Volume**: Confirmation signals
- **FVG**: Support/resistance zones

### **🚨 Alert Types**
- **Bullish**: EMA20 crosses above EMA50 + RSI < 70 + Volume > 1.2x
- **Bearish**: EMA20 crosses below EMA50 + RSI > 30 + Volume > 1.2x

### **⏰ Update Schedule**
- **Data**: Every 30 seconds
- **Alerts**: Continuous monitoring
- **Cache**: 15 minutes
- **Cooldown**: 5 minutes per symbol

---

**🎉 You're now ready to use the Professional Trading System!**

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
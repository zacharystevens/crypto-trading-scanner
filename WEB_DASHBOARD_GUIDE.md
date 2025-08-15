# 🌐 Web Dashboard Documentation

## Overview
The **Opportunity Scanner Dashboard** is a professional-grade web interface for cryptocurrency trading analysis. It combines real-time market data, advanced technical analysis, and automated opportunity detection to help traders identify profitable trading setups.

## 🚀 Quick Start

### 1. Launch the Dashboard
```bash
cd crypto-trading-scanner
python flask_dashboard.py
```

### 2. Access the Interface
Open your browser and navigate to: **http://localhost:5001**

The dashboard will automatically start loading market data and scanning for opportunities.

## 📱 Dashboard Overview

### Header Navigation
- **Dashboard Title**: 🔍 Opportunity Scanner Dashboard with search icon
- **Current Time**: Live timestamp updated every second
- **Audio Toggle**: Toggle audio alerts ON/OFF with volume icon
- **Refresh Button**: Manual data refresh for all sections

### Main Layout
The dashboard is organized into 3 main sections:
1. **Search Bar & Scanner Controls** (top center)
2. **Market Movers** (left side - 5 columns wide)
3. **Trading Opportunities & Charts** (right side - 7 columns wide)

## 🔍 Features & Functionality

### 1. Coin Search & Scanner Controls
**Location**: Top center section

**Search Features**:
- Enter any cryptocurrency symbol (BTC, ETH, DOGE, etc.)
- Autocomplete dropdown with available symbols
- Automatically adds /USDT suffix if not present
- Displays detailed technical analysis for the searched coin

**Scanner Controls**:
- **Curated Analysis**: Quick analysis of top 30 coins
- **Extended Analysis**: Comprehensive analysis of 400+ coins
- **Live counters**: Shows analysis progress and counts

**Supported Formats**:
- `BTC` → `BTC/USDT`
- `ETH` → `ETH/USDT`
- `BTC/USDT` → Direct search

### 2. Market Movers Section
**Location**: Left side (5-column wide section)

**Contains Three Cards**:

#### **Top Gainers** (Green card)
- Shows top gainers in 24h period
- Real-time price updates
- 24h percentage change (green for gains)
- Trading volume in abbreviated format (M/B)
- Click any gainer to load its chart analysis

#### **Top Losers** (Red card)  
- Shows top losing cryptocurrencies in 24h
- Real-time price updates
- 24h percentage change (red for losses)
- Trading volume data

#### **Top Market Cap** (Blue card)
- Shows highest market cap cryptocurrencies
- Market capitalization data
- Current prices and changes

**Data Fields for Each**:
- Symbol (without /USDT suffix)
- Current price
- 24h change percentage
- 24h trading volume

### 3. Trading Opportunities & Analysis Section
**Location**: Right side (7-column wide section)

**Contains**:

#### **Trading Opportunities** (Main card)
- Real-time trading opportunities detected by AI
- Scoring system (0-100) for each opportunity
- Signal direction (BULLISH/BEARISH) with color coding
- Timeframe indicators showing multi-timeframe confluence
- Confidence levels and entry suggestions
- Click any opportunity to load detailed chart analysis

#### **Recent Alerts** (Alert feed)
- Live feed of detected trading signals
- Audio alert integration with visual notifications
- Historical alert tracking
- Alert cooldown system to prevent spam

#### **Interactive Charts** (Chart area)
- Full-featured Plotly charts with technical indicators
- Multiple timeframe selection (5m, 15m, 30m, 1h, 4h)
- Zoom, pan, and interactive analysis tools
- Technical indicators: EMA, SMA, RSI, Volume, FVG zones

## 🔊 Audio Alert System

### Audio Controls
**Location**: Top navigation bar (volume icon button)

**Features**:
- **Toggle Button**: Click volume icon to turn audio ON/OFF
- **Visual Status**: Shows "ON" or "OFF" status next to volume icon
- **Real-time Control**: Immediately enables/disables audio alerts

### Audio Alert Types
- **Bullish Signals**: High-pitched beep (800Hz)
- **Bearish Signals**: Low-pitched beep (400Hz)  
- **Duration**: 3 distinct beeps for emphasis
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Audio Behavior
- **Default State**: Audio alerts are ON when dashboard loads
- **Cooldown**: 10-minute cooldown between alerts for same symbol
- **Fallback**: Graceful degradation if audio hardware unavailable
- **Console Backup**: Alternative bell character if main audio fails

## 📊 Chart Navigation

### Timeframe Selection
- **5m**: Ultra short-term analysis
- **15m**: Short-term analysis
- **30m**: Short-medium term analysis
- **1h**: Medium-term analysis (default)
- **4h**: Long-term analysis

### Chart Controls
- **Zoom**: Mouse wheel or zoom buttons
- **Pan**: Click and drag to move chart
- **Reset**: Double-click to reset view
- **Fullscreen**: Expand chart to full window

### Technical Indicators Legend
```
🟠 EMA20 (Orange) - Short-term trend
🔵 EMA50 (Blue) - Medium-term trend
🟡 SMA20 (Yellow Dash) - Short-term support/resistance
🟣 SMA50 (Purple Dash) - Medium-term support/resistance
🟢 Volume SMA (Green) - Volume trend
📊 RSI (Separate panel) - Momentum indicator
🔳 FVG Zones (Transparent boxes) - Fair Value Gaps
```

## ⏰ Update Frequencies

### 🔄 Real-time Updates
- **Market Data**: Every 30 seconds
- **Price Charts**: Every 30 seconds
- **Volume Data**: Every 30 seconds
- **Top Movers**: Every 30 seconds

### 🚨 Alert Monitoring
- **Signal Detection**: Every 30 seconds
- **Top 100+ Coins**: Monitored continuously
- **Market Movers**: Top gainers + losers + market cap
- **Background Processing**: Non-stop monitoring

### 📊 Data Caching
- **Chart Data**: Cached for 15 minutes
- **Market Movers**: Cached for 15 minutes
- **Technical Analysis**: Calculated in real-time
- **Alert History**: Stored in database

## 🎯 Operating Modes

### Demo Mode (Default)
- **No Setup Required**: Works immediately after installation
- **Simulated Data**: Uses realistic demo data for testing
- **Full Functionality**: All features work with demo data
- **Perfect for Learning**: Test features without API keys

### Live Data Mode (Optional)
- **API Keys Required**: Bitunix or Binance credentials needed
- **Real Market Data**: Live prices, volumes, and changes
- **Professional Trading**: Real-time opportunities
- **Production Ready**: For actual trading analysis

## 🛠️ Troubleshooting

### Common Issues

#### **Dashboard not loading**
1. Check if Flask server is running in terminal
2. Verify URL: `http://localhost:5001`
3. Clear browser cache and refresh
4. Try different browser

#### **Charts not displaying**
1. Check internet connection (for chart libraries)
2. Refresh page (Ctrl+F5 or Cmd+Shift+R)
3. Clear browser cache
4. Check browser console for JavaScript errors

#### **No data showing**
1. Wait 30 seconds for initial data load
2. Check terminal for error messages
3. Verify exchange connection status
4. Try demo mode if live data fails

#### **Audio not working**
1. Check system volume and audio output
2. Verify audio toggle is ON in dashboard
3. Test with different browser
4. Check browser audio permissions

### Performance Tips
- **Close unused browser tabs** to improve performance
- **Use latest browser version** for best compatibility
- **Enable hardware acceleration** in browser settings
- **Monitor system resources** if dashboard seems slow

## 📚 API Endpoints

The dashboard exposes several API endpoints for integration:

- **GET** `/api/market_movers` - Top gainers/losers data
- **GET** `/api/opportunities` - Current trading opportunities
- **GET** `/api/top_market_cap` - Market cap leaders
- **GET** `/api/alerts/latest` - Recent trading alerts
- **GET** `/api/chart/{symbol}/{timeframe}` - Chart data
- **POST** `/api/audio/toggle` - Toggle audio alerts
- **GET** `/api/audio/status` - Check audio status

## 🎨 UI Features

### Dark Theme
- **Professional appearance** with dark color scheme
- **Reduced eye strain** for extended analysis sessions
- **High contrast** for clear data visibility
- **Modern design** with smooth animations

### Responsive Design
- **Mobile friendly** layout that adapts to screen size
- **Grid system** that reorganizes on smaller screens
- **Touch-friendly** controls for tablet use
- **Scalable elements** for different resolutions

### Interactive Elements
- **Hover effects** on clickable items
- **Loading animations** during data updates
- **Toast notifications** for user feedback
- **Modal dialogs** for detailed views

## 🔧 Customization

### Browser Settings
```javascript
// Disable auto-refresh (in browser console)
clearInterval(refreshInterval);

// Enable debug mode
localStorage.setItem('debug', 'true');

// Set custom refresh rate (in milliseconds)
localStorage.setItem('refreshRate', '60000'); // 1 minute
```

### URL Parameters
- `?symbol=BTC` - Load specific symbol on start
- `?timeframe=4h` - Set default timeframe
- `?audio=off` - Start with audio disabled

## 📖 Getting Help

### Debug Information
1. **Open browser console** (F12)
2. **Check for JavaScript errors** (red messages)
3. **Monitor network requests** (Network tab)
4. **Check local storage** (Application tab)

### Log Analysis
1. **Terminal output** shows server-side logs
2. **Exchange connection status** is logged
3. **API request/response** information available
4. **Error messages** provide debugging context

---

**🎉 You're now ready to use the Professional Trading Dashboard!**

For additional help, see:
- [Quick Start Guide](QUICK_START.md)
- [Demo Scripts Guide](DEMO_SCRIPTS_GUIDE.md)
- [Main README](README.md)
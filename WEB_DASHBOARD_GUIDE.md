# 🌐 Web Dashboard Documentation

## Overview
The **Opportunity Scanner Dashboard** is a professional-grade web interface for cryptocurrency trading analysis. It combines real-time market data, advanced technical analysis, and automated opportunity detection to help traders identify profitable trading setups.

## 🚀 Quick Start

### 1. Launch the Dashboard
```bash
cd tcss-trading-system
python flask_dashboard.py
```

### 2. Access the Interface
Open your browser and navigate to: **http://localhost:5001**

The dashboard will automatically start loading market data and scanning for opportunities.

## 📱 Dashboard Overview

### Header Navigation
- **Current Time**: Live timestamp updated every second
- **Refresh Button**: Manual data refresh for all sections
- **Dashboard Title**: Shows active status with 🔍 icon

### Main Layout
The dashboard is organized into 4 main sections:
1. **Search Bar** (top center)
2. **Market Movers** (left side)
3. **Trading Opportunities** (center)
4. **Scanner Controls & Charts** (right side)

## 🔍 Features & Functionality

### 1. Coin Search
**Location**: Top center search bar

**Usage**:
- Enter any cryptocurrency symbol (BTC, ETH, DOGE, etc.)
- Press Enter or click the search button
- Automatically adds /USDT suffix if not present
- Displays detailed technical analysis for the searched coin

**Supported Formats**:
- `BTC` → `BTC/USDT`
- `ETH` → `ETH/USDT`
- `BTC/USDT` → Direct search

### 2. Top Gainers Section
**Location**: Left side, green card

**Features**:
- Shows top 5 gaining cryptocurrencies in 24h
- Real-time price updates
- 24h percentage change (green for gains)
- Trading volume in abbreviated format (M/B)
- Click any gainer to load its chart analysis

**Data Fields**:
- Symbol (without /USDT suffix)
- Current price
- 24h change percentage
- 24h trading volume

### 3. Top Losers Section
**Location**: Left side, red card

**Features**:
- Shows top 5 losing cryptocurrencies in 24h
- Real-time price updates
- 24h percentage change (red for losses)
- Trading volume in abbreviated format
- Click any loser to load its chart analysis

### 4. Best Trading Opportunities
**Location**: Center, main focus area

**Purpose**: Displays the most promising trading setups identified by the opportunity scanner

**Opportunity Cards Include**:
- **Symbol**: Cryptocurrency pair
- **Score**: Numerical rating (0-100+)
- **Signal Class**: WEAK, MODERATE, STRONG
- **Direction**: BULLISH, BEARISH, NEUTRAL
- **Current Price**: Live market price
- **Timeframe**: Primary analysis timeframe

**Score Color Coding**:
- 🟢 **High (50+)**: Strong opportunities, high confidence
- 🟡 **Medium (30-49)**: Moderate opportunities, decent confidence  
- 🔴 **Low (<30)**: Weak opportunities, low confidence

**Signal Classifications**:
- **STRONG**: High confluence across multiple indicators
- **MODERATE**: Some technical alignment
- **WEAK**: Limited technical support

### 5. Scanner Controls
**Location**: Right side, top

**Controls Available**:
- **🔍 Run Full Scan**: Analyzes all configured cryptocurrencies
- **🔥 Scan Market Movers**: Focuses on trending coins
- **📥 Export Results**: Download opportunities data (coming soon)

### 6. Scanner Stats
**Location**: Right side, middle

**Metrics Displayed**:
- **Opportunities Found**: Number of trading setups detected
- **Coins Scanned**: Total cryptocurrencies analyzed
- **Last Scan**: Timestamp of most recent analysis

### 7. Chart Analysis
**Location**: Right side, bottom

**Features**:
- **Interactive Plotly Charts**: Professional trading charts
- **Multiple Timeframes**: 15m, 1h, 4h analysis
- **Technical Indicators**: 
  - Candlestick patterns
  - EMA 20/50 moving averages
  - Volume analysis
  - RSI indicator
- **Click-to-Analyze**: Select any coin from gainers/losers/opportunities

## 🎯 Technical Analysis Engine

### Multi-Timeframe Analysis
The scanner analyzes each cryptocurrency across multiple timeframes:
- **15 minutes**: Short-term momentum and precision entries
- **1 hour**: Medium-term trends (primary timeframe)  
- **4 hours**: Medium-term direction
- **1 day**: Long-term trend analysis

### Fair Value Gaps (FVG)
- Detects price imbalances in the market
- Identifies unfilled gaps that may act as support/resistance
- Measures gap strength and proximity to current price

### Confluence Analysis
- Combines signals from multiple timeframes
- Calculates agreement percentage between timeframes
- Identifies strong vs. conflicting signals

### Pattern Recognition
- **Head & Shoulders**: Reversal pattern detection
- **Double/Triple Tops/Bottoms**: Key reversal levels
- **Flags & Pennants**: Continuation patterns
- **Trendline Breaks**: Support/resistance violations

### Volume Analysis
- Volume spike detection
- Volume-price relationship analysis
- Above/below average volume confirmation

## 📊 Understanding the Data

### Opportunity Scores
Scores are calculated using a 100-point system with these components:
- **FVG Analysis**: 0-22 points (unfilled gaps near price get higher scores)
- **Pattern Recognition**: 0-22 points (clean breakouts, confirmed patterns)
- **Multi-Timeframe Confluence**: 0-18 points (agreement across timeframes)
- **Trendline Analysis**: 0-18 points (support/resistance break confirmations)
- **Volume Analysis**: 0-12 points (above-average volume confirmation)
- **Momentum Indicators**: 0-8 points (short-term directional strength)

### Signal Directions
- **BULLISH**: Upward price movement expected
- **BEARISH**: Downward price movement expected  
- **NEUTRAL**: Sideways/uncertain movement

### Confidence Levels
Based on multi-timeframe agreement (4 timeframes: 15m, 1h, 4h, 1d):
- **4/4 Agreement**: STRONG signal (80%+ confluence)
- **3/4 Agreement**: MODERATE signal (60-79% confluence)
- **2/4 Agreement**: WEAK signal (<60% confluence)

### Timeframe Weights
- **Daily (1d)**: 35% weight (long-term trend)
- **4-Hour (4h)**: 30% weight (medium-term direction)  
- **1-Hour (1h)**: 25% weight (primary analysis timeframe)
- **15-Minute (15m)**: 10% weight (entry precision)

## ⚙️ Auto-Refresh System

### Automatic Updates
- **Market data**: Refreshes every 30 seconds
- **Time display**: Updates every second
- **Opportunity scanning**: Triggered by user actions

### Manual Refresh Options
- **Header Refresh Button**: Updates all sections
- **Individual Section Clicks**: Refresh specific data
- **Scanner Controls**: Trigger new analysis

## 🚨 Error Handling

### Common Issues & Solutions

**"Failed to load gainers/losers"**:
- Check internet connection
- Verify Binance API access
- Disable VPN if restricted location error

**"Failed to load opportunities"**:
- Ensure opportunity scanner is running
- Check for sufficient market data
- Verify API endpoints are responding

**Charts not loading**:
- Ensure Plotly library is accessible
- Check browser console for errors
- Try refreshing the page

## 📈 Best Practices

### Using the Dashboard Effectively

1. **Start with Market Overview**:
   - Check top gainers/losers for market sentiment
   - Look for unusual volume or price movements

2. **Analyze Opportunities**:
   - Focus on STRONG signals with scores >50
   - Prefer opportunities with BULLISH/BEARISH clarity over NEUTRAL
   - Check multiple timeframe agreement

3. **Verify with Charts**:
   - Click on interesting opportunities to view charts
   - Look for confluence between indicators
   - Check volume confirmation

4. **Regular Monitoring**:
   - Use auto-refresh for live monitoring
   - Run full scans periodically for new opportunities
   - Export results for record keeping

### Risk Management
- **Never rely solely on automated signals**
- **Always confirm with additional analysis**
- **Use proper position sizing**
- **Set stop-losses based on technical levels**
- **Consider market conditions and news events**

## 🔧 Technical Specifications

### System Requirements
- **Python 3.7+**
- **Flask web framework**
- **Real-time API connections**
- **Modern web browser**

### API Endpoints
- `/api/market_movers`: Top gainers and losers
- `/api/opportunities`: Trading opportunity results  
- `/api/chart/{symbol}/{timeframe}`: Chart data
- `/api/search_coin/{symbol}`: Individual coin analysis

### Data Sources
- **Binance API**: Real-time market data
- **Technical Analysis**: Custom algorithms
- **Volume Data**: 24-hour trading volumes
- **Price History**: 100-candle lookback

## 🎛️ Customization Options

### Modifying Scanner Settings
Edit `opportunity_scanner.py` for:
- Minimum volume thresholds
- Score calculation weights
- Pattern detection sensitivity
- Timeframe combinations

### UI Modifications
Edit `templates/dashboard.html` for:
- Color schemes and styling
- Layout adjustments
- Additional data fields
- Custom indicators

## 📝 Troubleshooting

### Performance Issues
- Reduce number of coins scanned
- Increase refresh intervals
- Check system resources

### Data Quality Issues  
- Verify API key permissions
- Check network connectivity
- Monitor rate limiting

### Display Problems
- Clear browser cache
- Check JavaScript console
- Verify all dependencies loaded

## 🚀 Advanced Usage

### Integration Possibilities
- **Webhook Alerts**: Connect to Discord/Telegram
- **Database Logging**: Store results for backtesting
- **API Integration**: Connect to trading platforms
- **Custom Indicators**: Add proprietary analysis

### Performance Optimization
- **Caching**: Reduce API calls
- **Async Processing**: Parallel analysis
- **Load Balancing**: Multiple scanner instances

## 📞 Support & Development

### Getting Help
- Check the console logs for error messages
- Verify all dependencies are installed
- Ensure proper API access and permissions

### Contributing
- Fork the repository
- Submit pull requests for improvements
- Report bugs and feature requests
- Share configuration optimizations

---

**⚠️ Disclaimer**: This dashboard is for educational and analysis purposes. Always perform your own research and risk assessment before making trading decisions. Past performance does not guarantee future results. 
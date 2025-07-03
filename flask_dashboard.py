#!/usr/bin/env python3
"""
PROFESSIONAL TRADING DASHBOARD
Real-time web interface for cryptocurrency trading system
Features: Live charts, signal alerts, performance tracking, multi-timeframe sync
"""
print("=== FLASK DASHBOARD FILE LOADED ===")

from flask import Flask, render_template, jsonify, request, send_from_directory
import ccxt
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.utils
from plotly.subplots import make_subplots
import sqlite3
import threading
import time

# Import new service architecture
from config.service_factory import trading_system
from config.settings import settings

app = Flask(__name__)

class TradingDashboard:
    def __init__(self):
        # Use new service architecture
        self.trading_system = trading_system
        self.config = settings
        
        # Initialize exchange connection using our new architecture
        self.exchange = None
        self.exchange_connected = False
        
        try:
            # Import our exchange factory
            from services.exchange_factory import ExchangeFactory
            
            # Get exchange configuration from settings
            exchange_config = self.config.get_exchange_config()
            print(f"🔗 Initializing {exchange_config['exchange_type']} exchange...")
            
            # Create exchange using our factory
            self.exchange = ExchangeFactory.create_from_settings(exchange_config)
            
            # Test connection asynchronously
            import asyncio
            async def test_connection():
                try:
                    await self.exchange.connect()
                    return True
                except Exception as e:
                    print(f"⚠️ Exchange connection failed: {e}")
                    return False
            
            # Run the connection test
            self.exchange_connected = asyncio.run(test_connection())
            
            if self.exchange_connected:
                print(f"✅ Successfully connected to {exchange_config['exchange_type']} exchange")
            else:
                print("📱 Dashboard will run in DEMO MODE without live data")
                self.exchange = None
                
        except Exception as e:
            print(f"⚠️ Exchange initialization failed: {e}")
            print("📱 Dashboard will run in DEMO MODE without live data")
            self.exchange_connected = False
            self.exchange = None
        
        # Dashboard configuration from settings
        self.recently_accessed = set()
        self.timeframes = self.config.timeframes
        self.primary_timeframe = self.config.primary_timeframe
        
        # Initialize scanner with our new exchange interface
        try:
            from opportunity_scanner import OpportunityScanner
            self.scanner = OpportunityScanner()
            print("🔍 Scanner initialized successfully")
        except Exception as e:
            print(f"⚠️ Scanner initialization failed: {e}")
            self.scanner = None
        
        # Initialize with demo symbols for background updates
        for symbol in self.config.demo_symbols:
            self.recently_accessed.add(symbol)
        
        # Initialize database for signal tracking
        self.init_database()
        
        # Background data update thread
        self.data_cache = {}
        if self.exchange_connected:
            self.start_background_updates()
        else:
            self.create_demo_data()
        
        print("🌐 Trading Dashboard Initialized")
        print(f"📊 Using new service architecture")
        print(f"⏰ Timeframes: {', '.join(self.timeframes)}")
        print(f"🔍 Services ready: {self.exchange_connected and 'LIVE DATA' or 'DEMO MODE'}")
    
    def init_database(self):
        """Initialize SQLite database for signal and performance tracking"""
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        # Create signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                confidence REAL,
                status TEXT DEFAULT 'ACTIVE',
                pnl REAL DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Create performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_signals INTEGER DEFAULT 0,
                winning_signals INTEGER DEFAULT 0,
                losing_signals INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📊 Database initialized for signal tracking")
    
    def create_demo_data(self):
        """Create demo data for when exchange connection is not available"""
        print("🎭 Creating demo data for dashboard")
        
        # Use configured demo symbols and base prices
        demo_symbols = self.config.demo_symbols
        demo_timeframes = self.timeframes
        base_prices = self.config.demo_base_prices
        
        for symbol in demo_symbols:
            for timeframe in demo_timeframes:
                # Create synthetic OHLCV data
                dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
                
                # Get base price from configuration
                base_price = base_prices.get(symbol, 1000)  # Default fallback
                price_data = []
                current_price = base_price
                
                for i in range(100):
                    # Random walk with some volatility
                    change = np.random.normal(0, current_price * 0.01)
                    current_price = max(current_price + change, current_price * 0.95)
                    price_data.append(current_price)
                
                # Create OHLCV from price data
                ohlcv_data = []
                for i, price in enumerate(price_data):
                    high = price * (1 + abs(np.random.normal(0, 0.005)))
                    low = price * (1 - abs(np.random.normal(0, 0.005)))
                    open_price = price_data[i-1] if i > 0 else price
                    close = price
                    volume = np.random.randint(1000, 10000)
                    
                    df_row = {
                        'timestamp': dates[i],
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'close': close,
                        'volume': volume
                    }
                    ohlcv_data.append(df_row)
                
                # Create DataFrame and add technical indicators
                df = pd.DataFrame(ohlcv_data)
                df['ema20'] = df['close'].ewm(span=20).mean()
                df['ema50'] = df['close'].ewm(span=50).mean()
                df['rsi'] = self.calculate_rsi(df['close'])
                df['volume_sma'] = df['volume'].rolling(window=20).mean()
                
                # Cache the demo data
                cache_key = f"{symbol}_{timeframe}"
                self.data_cache[cache_key] = df
        
        print(f"🎯 Demo data created for {len(demo_symbols)} symbols across {len(demo_timeframes)} timeframes")
    
    def start_background_updates(self):
        """Start background thread for real-time data updates"""
        def update_data():
            while True:
                try:
                    # Update data for recently accessed symbols only
                    symbols_to_update = list(self.recently_accessed)
                    print(f"🔄 Updating {len(symbols_to_update)} recently accessed symbols")
                    
                    for symbol in symbols_to_update:
                        for timeframe in self.timeframes:
                            self.fetch_and_cache_data(symbol, timeframe)
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    print(f"Background update error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
        print("⚡ Background data updates started")
    
    def track_symbol_access(self, symbol):
        """Track that a symbol was accessed for background updates"""
        # Simply track the symbol (we'll validate it when needed)
        self.recently_accessed.add(symbol)
        print(f"📊 Tracking {symbol} for background updates")
    
    def fetch_and_cache_data(self, symbol, timeframe):
        """Fetch and cache market data with technical indicators"""
        try:
            # Use our new async exchange interface
            import asyncio
            
            async def fetch_data():
                return await self.exchange.get_ohlcv(symbol, timeframe, limit=100)
            
            # Run async call
            ohlcv_data = asyncio.run(fetch_data())
            
            # Convert our OHLCV objects to DataFrame
            df_data = []
            for ohlcv in ohlcv_data:
                df_data.append({
                    'timestamp': pd.to_datetime(ohlcv.timestamp, unit='ms'),
                    'open': ohlcv.open,
                    'high': ohlcv.high,
                    'low': ohlcv.low,
                    'close': ohlcv.close,
                    'volume': ohlcv.volume
                })
            
            df = pd.DataFrame(df_data)
            
            # Calculate technical indicators
            df['ema20'] = df['close'].ewm(span=20).mean()
            df['ema50'] = df['close'].ewm(span=50).mean()
            df['rsi'] = self.calculate_rsi(df['close'])
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Cache the data
            cache_key = f"{symbol}_{timeframe}"
            self.data_cache[cache_key] = df
            
        except Exception as e:
            print(f"[ERROR] Error caching {symbol} {timeframe}: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def create_interactive_chart(self, symbol, timeframe):
        """Create interactive Plotly chart with technical indicators"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key not in self.data_cache:
            return None
        
        df = self.data_cache[cache_key].copy()
        
        # Handle NaN values and convert to lists FIRST
        df = df.dropna()  # Remove rows with NaN values
        timestamps = df['timestamp'].tolist()
        
        # Get FVG data using the new technical analysis service
        fvg_zones = []
        try:
            technical_service = self.trading_system.technical_analysis
            fvg_zones = technical_service.detect_fair_value_gaps(df)
        except Exception as e:
            print(f"[ERROR] Error getting FVG data: {e}")
            fvg_zones = []
        
        # Ensure all data is converted to lists and handle any remaining NaN
        ohlc_data = {
            'open': df['open'].ffill().tolist(),
            'high': df['high'].ffill().tolist(),
            'low': df['low'].ffill().tolist(),
            'close': df['close'].ffill().tolist(),
        }
        
        # Technical indicators converted to lists
        ema20_data = df['ema20'].ffill().tolist()
        ema50_data = df['ema50'].ffill().tolist()
        rsi_data = df['rsi'].ffill().tolist()
        volume_data = df['volume'].tolist()
        volume_sma_data = df['volume_sma'].ffill().tolist()
        
        # Volume colors (green for up, red for down)
        volume_colors = []
        for i in range(len(df)):
            if i > 0 and df.iloc[i]['close'] > df.iloc[i]['open']:
                volume_colors.append('rgba(0, 255, 0, 0.6)')  # Green
            else:
                volume_colors.append('rgba(255, 0, 0, 0.6)')  # Red
        
        # Create subplots with optimized proportions for full visibility
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=('Price & EMAs', 'Volume', 'RSI'),
            row_heights=[0.62, 0.28, 0.10],  # More space for volume to prevent cutoff
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=timestamps,
                open=ohlc_data['open'],
                high=ohlc_data['high'],
                low=ohlc_data['low'],
                close=ohlc_data['close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='rgba(38, 166, 154, 0.3)',
                decreasing_fillcolor='rgba(239, 83, 80, 0.3)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # EMAs with proper data conversion
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ema20_data,
                mode='lines',
                name='EMA20',
                line=dict(color='#FFA726', width=2),
                connectgaps=True
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ema50_data,
                mode='lines',
                name='EMA50',
                line=dict(color='#42A5F5', width=2),
                connectgaps=True
            ),
            row=1, col=1
        )
        
        # Add Fair Value Gaps as transparent boxes
        if fvg_zones:
            for i, fvg in enumerate(fvg_zones):
                try:
                    # Determine color based on FVG type and status
                    if fvg['type'] == 'BULLISH_FVG':
                        color = 'rgba(38, 166, 154, 0.2)' if fvg.get('status') == 'UNFILLED' else 'rgba(38, 166, 154, 0.1)'
                        line_color = 'rgba(38, 166, 154, 0.5)'
                    else:  # BEARISH_FVG
                        color = 'rgba(239, 83, 80, 0.2)' if fvg.get('status') == 'UNFILLED' else 'rgba(239, 83, 80, 0.1)'
                        line_color = 'rgba(239, 83, 80, 0.5)'
                    
                    # Get the start and end x-coordinates for the box
                    # FVG starts from its formation index (the candle where it was established)
                    formation_idx = fvg.get('formation_index', 0)
                    
                    # Ensure formation_idx is within bounds
                    if formation_idx < 0:
                        formation_idx = 0
                    elif formation_idx >= len(timestamps):
                        formation_idx = len(timestamps) - 1
                        
                    if formation_idx < len(timestamps):
                        # Start from the exact formation candle, not later
                        x_start = timestamps[formation_idx]
                        x_end = timestamps[-1]  # Extend to current time
                        

                        
                        # Add rectangle shape for the FVG
                        fig.add_shape(
                            type="rect",
                            x0=x_start,
                            y0=fvg['gap_low'],
                            x1=x_end,
                            y1=fvg['gap_high'],
                            fillcolor=color,
                            line=dict(color=line_color, width=1, dash="dot"),
                            layer="below",
                            row=1, col=1
                        )
                        
                        # Add "FVG" text in the center of the zone
                        # Position text slightly to the right of formation start
                        text_offset = max(1, min(4, len(timestamps) - formation_idx - 1))
                        x_center = timestamps[min(formation_idx + text_offset, len(timestamps) - 1)]
                        y_center = (fvg['gap_low'] + fvg['gap_high']) / 2
                        
                        fig.add_annotation(
                            x=x_center,
                            y=y_center,
                            text="FVG",
                            showarrow=False,
                            font=dict(size=10, color=line_color),
                            bgcolor="rgba(0,0,0,0.3)",
                            bordercolor=line_color,
                            borderwidth=1,
                            row=1, col=1
                        )
                            
                except Exception as e:
                    print(f"[ERROR] Error adding FVG {i}: {e}")
                    continue
        
        # Volume with proper coloring (green for up, red for down candles)
        fig.add_trace(
            go.Bar(
                x=timestamps,
                y=volume_data,
                name='Volume',
                marker_color=volume_colors,
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Volume SMA (hidden from legend to reduce clutter)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=volume_sma_data,
                mode='lines',
                name='Volume SMA',
                line=dict(color='#FF7043', width=1),
                connectgaps=True,
                showlegend=False
            ),
            row=2, col=1
        )
        
        # RSI (hidden from legend to reduce clutter)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=rsi_data,
                mode='lines',
                name='RSI',
                line=dict(color='#AB47BC', width=2),
                connectgaps=True,
                showlegend=False
            ),
            row=3, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="#FF5252", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#66BB6A", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#BDBDBD", row=3, col=1)
        
        # Enhanced layout with proper interactivity
        price_min = min(ohlc_data['low'])
        price_max = max(ohlc_data['high'])
        price_padding = (price_max - price_min) * 0.05
        
        fig.update_layout(
            title=f'{symbol} - {timeframe.upper()} Timeframe Analysis',
            xaxis_rangeslider_visible=False,
            height=850,  # Increased height to show full volume section
            showlegend=True,
            template='plotly_dark',
            dragmode='zoom',
            # Clean X-axis without clutter
            xaxis=dict(
                type='date',
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                title='Price (USD)', 
                range=[price_min - price_padding, price_max + price_padding],
                fixedrange=False  # Allow Y-axis zooming
            ),
            xaxis2=dict(
                title='Date',
                title_font=dict(size=12)
            ),
            yaxis2=dict(
                title='Volume', 
                fixedrange=False,
                title_font=dict(size=12)
            ),
            yaxis3=dict(
                title='RSI', 
                range=[0, 100], 
                fixedrange=False,
                title_font=dict(size=12)
            ),
            # Simplified layout
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)"
            )
        )
        
        # Configure all axes for better interaction
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2E3A47')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2E3A47')
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def get_recent_signals(self, limit=10):
        """Get recent trading signals from database"""
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, symbol, signal_type, timeframe, entry_price, 
                   confidence, status, pnl, notes
            FROM signals 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        signals = cursor.fetchall()
        conn.close()
        
        return [{
            'timestamp': row[0],
            'symbol': row[1],
            'signal_type': row[2],
            'timeframe': row[3],
            'entry_price': row[4],
            'confidence': row[5],
            'status': row[6],
            'pnl': row[7],
            'notes': row[8]
        } for row in signals]
    
    def log_signal(self, symbol, signal_type, timeframe, entry_price, stop_loss, take_profit, confidence, notes=""):
        """Log a new trading signal to database"""
        conn = sqlite3.connect('trading_signals.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (symbol, signal_type, timeframe, entry_price, 
                               stop_loss, take_profit, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, signal_type, timeframe, entry_price, stop_loss, take_profit, confidence, notes))
        
        conn.commit()
        conn.close()
        print(f"📊 Signal logged: {signal_type} {symbol} @ ${entry_price}")

# Initialize dashboard
dashboard = TradingDashboard()

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    # Get symbols from cached data or demo symbols from config
    symbols = dashboard.config.demo_symbols  # Use configured demo symbols
    if dashboard.data_cache:
        # Extract unique symbols from cache keys
        cached_symbols = set()
        for cache_key in dashboard.data_cache.keys():
            symbol = cache_key.split('_')[0]
            cached_symbols.add(symbol)
        symbols = list(cached_symbols)
    
    return render_template('dashboard.html', 
                         symbols=symbols,
                         timeframes=dashboard.timeframes)

@app.route('/api/chart/<path:symbol>/<timeframe>')
def get_chart(symbol, timeframe):
    # Track that this symbol was accessed
    dashboard.track_symbol_access(symbol)
    
    cache_key = f"{symbol}_{timeframe}"
    # Force fetch if missing
    if cache_key not in dashboard.data_cache:
        dashboard.fetch_and_cache_data(symbol, timeframe)
    chart_json = dashboard.create_interactive_chart(symbol, timeframe)
    return jsonify({'chart': chart_json})

@app.route('/api/signals')
def get_signals():
    """API endpoint for recent signals"""
    signals = dashboard.get_recent_signals()
    return jsonify(signals)

@app.route('/api/market_overview')
def market_overview():
    """API endpoint for market overview data"""
    overview = {}
    # Use recently accessed symbols for market overview
    for symbol in dashboard.recently_accessed:
        cache_key = f"{symbol}_{dashboard.primary_timeframe}"
        if cache_key in dashboard.data_cache:
            df = dashboard.data_cache[cache_key]
            latest = df.iloc[-1]
            
            # Calculate 24h change
            price_24h_ago = df.iloc[-24]['close'] if len(df) >= 24 else df.iloc[0]['close']
            change_24h = ((latest['close'] - price_24h_ago) / price_24h_ago) * 100
            
            overview[symbol] = {
                'price': latest['close'],
                'change_24h': change_24h,
                'volume': latest['volume'],
                'rsi': latest['rsi'] if not pd.isna(latest['rsi']) else 50,
                'trend': 'BULLISH' if latest['close'] > latest['ema20'] else 'BEARISH'
            }
    
    return jsonify(overview)

@app.route('/api/log_signal', methods=['POST'])
def log_signal_api():
    """API endpoint to log new trading signals"""
    data = request.json
    dashboard.log_signal(
        data['symbol'],
        data['signal_type'],
        data['timeframe'],
        data['entry_price'],
        data.get('stop_loss'),
        data.get('take_profit'),
        data['confidence'],
        data.get('notes', '')
    )
    return jsonify({'status': 'success'})

@app.route('/api/top_gainers')
def get_top_gainers():
    """API endpoint for top gainers using live Bitunix data"""
    try:
        if not dashboard.scanner:
            return jsonify([])
        # Get live gainers from Bitunix
        gainers = dashboard.scanner.fetch_market_movers('gainers', 10)
        return jsonify(gainers)
    except Exception as e:
        print(f"Error fetching gainers: {e}")
        return jsonify([])

@app.route('/api/top_losers')
def get_top_losers():
    """API endpoint for top losers using live Bitunix data"""
    try:
        if not dashboard.scanner:
            return jsonify([])
        # Get live losers from Bitunix
        losers = dashboard.scanner.fetch_market_movers('losers', 10)
        return jsonify(losers)
    except Exception as e:
        print(f"Error fetching losers: {e}")
        return jsonify([])

@app.route('/api/market_movers')
def get_market_movers():
    """API endpoint for both gainers and losers using live Bitunix data"""
    try:
        if not dashboard.scanner:
            return jsonify({'gainers': [], 'losers': []})
        # Get live market movers from Bitunix
        gainers = dashboard.scanner.fetch_market_movers('gainers', 10)
        losers = dashboard.scanner.fetch_market_movers('losers', 10)
        return jsonify({'gainers': gainers, 'losers': losers})
    except Exception as e:
        print(f"Error fetching market movers: {e}")
        return jsonify({'gainers': [], 'losers': []})

@app.route('/api/opportunities')
def get_opportunities():
    """API endpoint for opportunity scanner results using live Bitunix data"""
    try:
        if not dashboard.scanner:
            return jsonify([])
        # Get live opportunities from Bitunix (curated 30 coins analysis)
        opportunities = dashboard.scanner.scan_all_opportunities('curated_30', limit=30)
        return jsonify(opportunities)
    except Exception as e:
        print(f"Error scanning opportunities: {e}")
        return jsonify([])

@app.route('/api/extended_analysis')
def get_extended_analysis():
    """API endpoint for extended analysis"""
    try:
        # Return simplified version of configured demo opportunities
        simplified = [
            {'symbol': opp['symbol'], 'score': opp['score'], 'signal': opp['signal']} 
            for opp in dashboard.config.demo_opportunities
        ]
        return jsonify(simplified)
    except Exception as e:
        print(f"Error in extended analysis: {e}")
        return jsonify([])

@app.route('/api/comprehensive_analysis')
def get_comprehensive_analysis():
    """API endpoint for comprehensive analysis"""
    try:
        # Return enhanced version of configured demo opportunities
        comprehensive = [
            {**opp, 'analysis': 'comprehensive'} 
            for opp in dashboard.config.demo_opportunities
        ]
        return jsonify(comprehensive)
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        return jsonify([])

@app.route('/api/analysis_status')
def get_analysis_status():
    """API endpoint to get status of current analysis operations"""
    try:
        # Check if scanner is available
        if not dashboard.scanner:
            return jsonify({
                "curated_coins": 0,
                "remaining_coins": 0,
                "total_coins": 0,
                "estimated_extended_time_hours": 0,
                "estimated_extended_time_minutes": 0,
                "throttle_delay_seconds": 30,
                "status": "scanner_unavailable"
            })
        
        # Get analysis statistics
        curated_data = dashboard.scanner.get_curated_30_coins()
        all_symbols = dashboard.scanner.get_all_usdt_symbols()
        remaining_count = len(all_symbols) - len(curated_data['all_symbols'])
        
        return jsonify({
            "curated_coins": len(curated_data['all_symbols']),
            "remaining_coins": remaining_count,
            "total_coins": len(all_symbols),
            "estimated_extended_time_hours": round(remaining_count * 30 / 3600, 1),  # 30 seconds per coin
            "estimated_extended_time_minutes": round(remaining_count * 30 / 60, 0),
            "throttle_delay_seconds": 30,
            "status": "ready"
        })
    except Exception as e:
        print(f"Error getting analysis status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/top_market_cap')
def get_top_market_cap():
    """API endpoint for top market cap coins"""
    try:
        if not dashboard.scanner:
            return jsonify([])
        market_cap_coins = dashboard.scanner.fetch_top_market_cap(limit=10)
        return jsonify(market_cap_coins)
    except Exception as e:
        print(f"Error fetching market cap coins: {e}")
        return jsonify([])

@app.route('/api/all_symbols')
def get_all_symbols():
    """API endpoint to get all available trading pairs"""
    try:
        # Check if scanner is available
        if not dashboard.scanner:
            # Return demo symbols if scanner is unavailable
            demo_symbols = dashboard.config.demo_symbols
            usdt_pairs = []
            for symbol in demo_symbols:
                base = symbol.replace('/USDT', '')
                symbol_info = {
                    'symbol': symbol,
                    'base': base,
                    'display': base  # Just the base asset for display
                }
                usdt_pairs.append(symbol_info)
            return jsonify(usdt_pairs)
        
        # Use the scanner's method to get all symbols
        symbols = dashboard.scanner.get_all_usdt_symbols()
        
        # Convert to format expected by frontend
        usdt_pairs = []
        for symbol in symbols:
            base = symbol.replace('/USDT', '')
            symbol_info = {
                'symbol': symbol,
                'base': base,
                'display': base  # Just the base asset for display
            }
            usdt_pairs.append(symbol_info)
        

        return jsonify(usdt_pairs)
    except Exception as e:
        print(f"Error fetching all symbols: {e}")
        return jsonify([])

@app.route('/api/search_coin/<symbol>')
def search_coin(symbol):
    """API endpoint to search and analyze a specific coin"""
    try:
        # Add USDT if not present
        if not symbol.endswith('/USDT'):
            symbol = f"{symbol.upper()}/USDT"
        
        # Track that this symbol was accessed
        dashboard.track_symbol_access(symbol)
        
        # Check if scanner is available
        if not dashboard.scanner:
            return jsonify({'error': 'Scanner unavailable', 'symbol': symbol})
        
        analysis = dashboard.scanner.analyze_single_coin(symbol)
        return jsonify(analysis)
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return jsonify({'error': f'Could not analyze {symbol}'})

if __name__ == '__main__':
    print("🌐 Starting Trading Dashboard...")
    print("📱 Access at: http://localhost:5001")
    from config.settings import settings
    app.run(
        host=settings.flask_host, 
        port=settings.flask_port, 
        debug=settings.flask_debug
    ) 
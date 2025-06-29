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
from opportunity_scanner import OpportunityScanner

app = Flask(__name__)

class TradingDashboard:
    def __init__(self):
        # Initialize opportunity scanner (primary functionality)
        self.scanner = OpportunityScanner()
        
        # Initialize exchange connection (for quick access)
        self.exchange = ccxt.binance({
            'sandbox': False,
            'enableRateLimit': True,
        })
        
        # Dashboard configuration
        self.active_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
        self.timeframes = ['15m', '1h', '4h', '1d']
        self.primary_timeframe = '1h'
        
        # Initialize database for signal tracking
        self.init_database()
        
        # Background data update thread
        self.data_cache = {}
        self.start_background_updates()
        
        print("🌐 Trading Dashboard Initialized")
        print(f"📊 Monitoring: {len(self.active_symbols)} symbols")
        print(f"⏰ Timeframes: {', '.join(self.timeframes)}")
        print("🔍 Opportunity Scanner Ready")
    
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
    
    def start_background_updates(self):
        """Start background thread for real-time data updates"""
        def update_data():
            while True:
                try:
                    for symbol in self.active_symbols:
                        for timeframe in self.timeframes:
                            self.fetch_and_cache_data(symbol, timeframe)
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    print(f"Background update error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
        print("⚡ Background data updates started")
    
    def fetch_and_cache_data(self, symbol, timeframe):
        """Fetch and cache market data with technical indicators"""
        try:
            print(f"[DEBUG] Fetching {symbol} {timeframe}...")
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            print(f"[DEBUG] Got {len(ohlcv)} candles for {symbol} {timeframe}")
            
            if len(ohlcv) > 0:
                print(f"[DEBUG] First candle: {ohlcv[0]}")
                print(f"[DEBUG] Last candle: {ohlcv[-1]}")
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Calculate technical indicators
            df['ema20'] = df['close'].ewm(span=20).mean()
            df['ema50'] = df['close'].ewm(span=50).mean()
            df['rsi'] = self.calculate_rsi(df['close'])
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Cache the data
            cache_key = f"{symbol}_{timeframe}"
            self.data_cache[cache_key] = df
            print(f"[DEBUG] Cached {symbol} {timeframe} with {len(df)} rows")
            
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
            print(f"[DEBUG] No data in cache for {cache_key}")
            return None
        
        df = self.data_cache[cache_key].copy()
        print(f"[DEBUG] Creating chart for {cache_key}, df shape: {df.shape}")
        print(f"[DEBUG] Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        print(f"[DEBUG] Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"[DEBUG] First 3 OHLC rows:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"  {i}: {row['timestamp']} O:{row['open']:.2f} H:{row['high']:.2f} L:{row['low']:.2f} C:{row['close']:.2f}")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & EMAs', 'Volume', 'RSI'),
            row_heights=[0.6, 0.2, 0.2],
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Candlestick chart - ensure data types are correct
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'].tolist(),
                open=df['open'].tolist(),
                high=df['high'].tolist(),
                low=df['low'].tolist(),
                close=df['close'].tolist(),
                name='Price',
                increasing_line_color='#00ff00',
                decreasing_line_color='#ff0000',
                increasing_fillcolor='rgba(0,255,0,0.3)',
                decreasing_fillcolor='rgba(255,0,0,0.3)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # EMAs
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema20'],
                mode='lines',
                name='EMA20',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema50'],
                mode='lines',
                name='EMA50',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color='rgba(158,202,225,0.6)'
            ),
            row=2, col=1
        )
        
        # Volume SMA
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['volume_sma'],
                mode='lines',
                name='Volume SMA',
                line=dict(color='red', width=1)
            ),
            row=2, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
        
        # Update layout with better Y-axis scaling for candlesticks
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_padding = (price_max - price_min) * 0.05  # 5% padding
        
        fig.update_layout(
            title=f'{symbol} - {timeframe.upper()} Timeframe Analysis',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template='plotly_dark',
            xaxis=dict(type='date'),
            yaxis=dict(
                title='Price (USD)', 
                range=[price_min - price_padding, price_max + price_padding],
                autorange=False
            ),
            xaxis2=dict(title='Date'),
            yaxis2=dict(title='Volume'),
            yaxis3=dict(title='RSI', range=[0, 100])
        )
        
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
    return render_template('dashboard.html', 
                         symbols=dashboard.active_symbols,
                         timeframes=dashboard.timeframes)

@app.route('/api/chart/<path:symbol>/<timeframe>')
def get_chart(symbol, timeframe):
    cache_key = f"{symbol}_{timeframe}"
    print(f"[DEBUG] Requested chart: {cache_key}")
    print(f"[DEBUG] Available cache keys: {list(dashboard.data_cache.keys())}")
    # Force fetch if missing
    if cache_key not in dashboard.data_cache:
        print(f"[DEBUG] Cache miss for {cache_key}, fetching now...")
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
    for symbol in dashboard.active_symbols:
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
    """API endpoint for top gainers"""
    try:
        gainers = dashboard.scanner.fetch_market_movers('gainers', limit=10)
        return jsonify(gainers)
    except Exception as e:
        print(f"Error fetching gainers: {e}")
        return jsonify([])

@app.route('/api/top_losers')
def get_top_losers():
    """API endpoint for top losers"""
    try:
        losers = dashboard.scanner.fetch_market_movers('losers', limit=10)
        return jsonify(losers)
    except Exception as e:
        print(f"Error fetching losers: {e}")
        return jsonify([])

@app.route('/api/market_movers')
def get_market_movers():
    """API endpoint for both gainers and losers"""
    try:
        gainers = dashboard.scanner.fetch_market_movers('gainers', limit=10)
        losers = dashboard.scanner.fetch_market_movers('losers', limit=10)
        return jsonify({
            'gainers': gainers,
            'losers': losers
        })
    except Exception as e:
        print(f"Error fetching market movers: {e}")
        return jsonify({'gainers': [], 'losers': []})

@app.route('/api/opportunities')
def get_opportunities():
    """API endpoint for opportunity scanner results"""
    try:
        opportunities = dashboard.scanner.scan_all_opportunities('static', limit=20)
        return jsonify(opportunities)
    except Exception as e:
        print(f"Error scanning opportunities: {e}")
        return jsonify([])

@app.route('/api/search_coin/<symbol>')
def search_coin(symbol):
    """API endpoint to search and analyze a specific coin"""
    try:
        # Add USDT if not present
        if not symbol.endswith('/USDT'):
            symbol = f"{symbol.upper()}/USDT"
        
        analysis = dashboard.scanner.analyze_single_coin(symbol)
        return jsonify(analysis)
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return jsonify({'error': f'Could not analyze {symbol}'})

if __name__ == '__main__':
    print("🌐 Starting Trading Dashboard...")
    print("📱 Access at: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 
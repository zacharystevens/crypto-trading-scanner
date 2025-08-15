#!/usr/bin/env python3
"""
PROFESSIONAL TRADING DASHBOARD
Real-time web interface for cryptocurrency trading system
Features: Live charts, signal alerts, performance tracking, multi-timeframe sync
"""
print("=== FLASK DASHBOARD FILE LOADED ===")

import argparse
import sys
from pathlib import Path
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
from typing import Dict, Any
# Cross-platform audio handled via services.audio_service
from services.audio_service import get_audio_player

# Import new service architecture
from config.service_factory import trading_system
from config.settings import settings

# Import confirmation candle system
from confirmation_candles import ConfirmationCandleSystem

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
        # Updated timeframes with new options
        self.timeframes = ['5m', '15m', '30m', '1h', '4h']
        self.primary_timeframe = '1h'  # 1h is the main timeframe for alerts
        
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
        
        # Audio alert settings
        self.audio_enabled = True
        
        # Initialize confirmation candle system
        self.confirmation_system = ConfirmationCandleSystem(self.exchange)
        print("✅ Confirmation candle system initialized")
        
        # Demo mode flag to avoid repeated exchange attempts
        self.demo_mode = False
        
        # Background data update thread
        self.data_cache = {}
        if self.exchange_connected:
            self.start_background_updates()
        else:
            self.create_demo_data()
        
        # NEW: Real-time Alert System
        self.alert_system = RealTimeAlertSystem(self)
        self.active_alerts = []
        self.last_crossover_signals = {}  # Track last crossover to avoid duplicates
        
        print("🌐 Trading Dashboard Initialized")
        print(f"📊 Using new service architecture")
        print(f"⏰ Available timeframes: {', '.join(self.timeframes)}")
        print(f"🎯 Primary timeframe: {self.primary_timeframe} (for alerts)")
        print(f"🔍 Services ready: {self.exchange_connected and 'LIVE DATA' or 'DEMO MODE'}")
        print(f"🚨 Real-time alerts: ENABLED (EMA/SMA + RSI + Volume)")
    
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
        
        # NEW: Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                price REAL,
                rsi REAL,
                volume_ratio REAL,
                ema_fast REAL,
                ema_slow REAL,
                confidence REAL,
                timeframe TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📊 Database initialized for signal tracking and alerts")
    
    def create_demo_data(self):
        """Create demo data for when exchange connection is not available"""
        print("🎭 Creating demo data for dashboard")
        
        # Use configured demo symbols and base prices
        demo_symbols = self.config.demo_symbols
        demo_timeframes = self.timeframes
        base_prices = self.config.demo_base_prices
        
        for symbol in demo_symbols:
            for timeframe in demo_timeframes:
                # Create synthetic OHLCV data (500 candles for SMA200)
                dates = pd.date_range(end=datetime.now(), periods=500, freq='1H')
                
                # Get base price from configuration
                base_price = base_prices.get(symbol, 1000)  # Default fallback
                price_data = []
                current_price = base_price
                
                for i in range(500):
                    # Reduced volatility to prevent false signals
                    change = np.random.normal(0, current_price * 0.002)  # Reduced from 0.01 to 0.002
                    current_price = max(current_price + change, current_price * 0.98)
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
                # Core indicators for demo data
                df['ema50'] = df['close'].ewm(span=50).mean()
                df['ema100'] = df['close'].ewm(span=100).mean()
                df['ema200'] = df['close'].ewm(span=200).mean()
                df['sma50'] = df['close'].rolling(window=50).mean()
                df['sma200'] = df['close'].rolling(window=200).mean()
                df['rsi'] = self.calculate_rsi(df['close'])
                df['volume_sma'] = df['volume'].rolling(window=20).mean()
                
                # Cache the demo data
                cache_key = f"{symbol}_{timeframe}"
                self.data_cache[cache_key] = df
        
        print(f"🎯 Demo data created for {len(demo_symbols)} symbols across {len(demo_timeframes)} timeframes")
    
    def create_demo_data_for_symbol(self, symbol, timeframe):
        """Create demo data for a specific symbol when exchange data fails"""
        import numpy as np
        from datetime import datetime, timedelta
        
        print(f"🎭 Creating demo data for {symbol} {timeframe} (exchange data unavailable)")
        
        # Generate 500 candles of demo data (enough for SMA200)
        n_candles = 500
        base_price = 100.0
        timestamps = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        current_time = datetime.now() - timedelta(hours=n_candles)
        
        for i in range(n_candles):
            # Generate realistic price movement with reduced volatility
            if i == 0:
                price = base_price
            else:
                # Reduced volatility to prevent false signals
                change = np.random.normal(0, 0.01)  # Reduced from 0.05 to 0.01 (1% volatility)
                price = closes[-1] * (1 + change)
            
            # Generate OHLC with more realistic spreads
            open_price = price
            # Create smaller spreads to reduce false signals
            spread = price * 0.01  # Reduced from 0.03 to 0.01 (1% spread)
            high_price = price + abs(np.random.normal(0, spread))
            low_price = price - abs(np.random.normal(0, spread))
            close_price = price + np.random.normal(0, spread * 0.5)
            
            # Ensure high >= max(open, close) and low <= min(open, close)
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Generate volume
            volume = np.random.uniform(1000, 10000)
            
            timestamps.append(current_time)
            opens.append(open_price)
            highs.append(high_price)
            lows.append(low_price)
            closes.append(close_price)
            volumes.append(volume)
            
            current_time += timedelta(hours=1)
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        })
        
        # Calculate technical indicators
        df['ema50'] = df['close'].ewm(span=50).mean()
        df['ema100'] = df['close'].ewm(span=100).mean()
        df['ema200'] = df['close'].ewm(span=200).mean()
        df['sma50'] = df['close'].rolling(window=50).mean()
        df['sma200'] = df['close'].rolling(window=200).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        # Market Cipher B components
        wt1, wt2 = self.calculate_wave_trend(df)
        df['wt1'] = wt1
        df['wt2'] = wt2
        df['mfi'] = self.calculate_mfi(df['high'], df['low'], df['close'], df['volume'])
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        
        # Cache the demo data
        cache_key = f"{symbol}_{timeframe}"
        self.data_cache[cache_key] = df
        
        print(f"✅ Created demo data for {symbol} {timeframe} with {len(df)} candles")
        return df
    
    def create_simple_chart(self, symbol, timeframe):
        """Create a simple chart for testing purposes"""
        try:
            print(f"Creating simple chart for {symbol} {timeframe}")
            
            # Create demo data
            demo_df = self.create_demo_data_for_symbol(symbol, timeframe)
            if demo_df is None:
                return None
            
            # Create a simple candlestick chart
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=demo_df['timestamp'],
                open=demo_df['open'],
                high=demo_df['high'],
                low=demo_df['low'],
                close=demo_df['close'],
                name='Price'
            ))
            
            # Add EMA lines
            fig.add_trace(go.Scatter(
                x=demo_df['timestamp'],
                y=demo_df['ema50'],
                name='EMA50',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=demo_df['timestamp'],
                y=demo_df['ema100'],
                name='EMA100',
                line=dict(color='purple', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=demo_df['timestamp'],
                y=demo_df['ema200'],
                name='EMA200',
                line=dict(color='red', width=2)
            ))
            
            # Add SMA overlays
            if 'sma50' not in demo_df.columns:
                demo_df['sma50'] = demo_df['close'].rolling(window=50).mean()
            if 'sma200' not in demo_df.columns:
                demo_df['sma200'] = demo_df['close'].rolling(window=200).mean()
            
            fig.add_trace(go.Scatter(
                x=demo_df['timestamp'],
                y=demo_df['sma50'],
                name='SMA50',
                line=dict(color='green', width=1.5, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=demo_df['timestamp'],
                y=demo_df['sma200'],
                name='SMA200',
                line=dict(color='orange', width=1.5, dash='dot')
            ))
            
            last_ema50 = demo_df['ema50'].iloc[-1]
            last_sma50 = demo_df['sma50'].iloc[-1]
            last_sma200 = demo_df['sma200'].iloc[-1]
            title_suffix = f" | EMA50: {last_ema50:.2f} · SMA50: {last_sma50:.2f} · SMA200: {last_sma200:.2f}"
            fig.update_layout(
                title=f'{symbol} - {timeframe.upper()} Chart{title_suffix}',
                template='plotly_dark',
                xaxis_title='Time',
                yaxis_title='Price'
            )
            
            chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            print(f"✅ Simple chart created for {symbol} {timeframe}")
            return chart_json
            
        except Exception as e:
            print(f"Error creating simple chart for {symbol} {timeframe}: {e}")
            return None
    
    def start_background_updates(self):
        """Start background thread for real-time data updates and alerts"""
        def update_data():
            # Add warm-up delay to prevent immediate false signals
            print("⏳ Warming up system - waiting 2 minutes before signal monitoring...")
            time.sleep(120)  # Wait 2 minutes before starting signal monitoring
            print("✅ System warmed up - starting signal monitoring")
            
            while True:
                try:
                    # Update data for recently accessed symbols only
                    symbols_to_update = list(self.recently_accessed)
                    print(f"🔄 Updating {len(symbols_to_update)} recently accessed symbols")
                    
                    for symbol in symbols_to_update:
                        # Focus on 1h timeframe for alerts and monitoring
                        self.fetch_and_cache_data(symbol, '1h')
                    
                    # NEW: Run real-time alert monitoring
                    self.alert_system.monitor_all_symbols()
                    
                    # NEW: Check pending confirmations (check more frequently)
                    self.alert_system.check_pending_confirmations()
                    
                    time.sleep(15)  # Update every 15 seconds for faster confirmation
                except Exception as e:
                    print(f"Background update error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
        print("⚡ Background data updates and alerts started (2-minute warm-up)")
    
    def track_symbol_access(self, symbol):
        """Track that a symbol was accessed for background updates"""
        # Simply track the symbol (we'll validate it when needed)
        self.recently_accessed.add(symbol)
        print(f"📊 Tracking {symbol} for background updates and alerts")
    
    def fetch_and_cache_data(self, symbol, timeframe):
        """Fetch and cache market data with technical indicators"""
        try:
            # Check if exchange is connected and not rate limited
            if not self.exchange_connected or self.demo_mode:
                print(f"📱 Using demo data for {symbol} {timeframe} (demo mode)")
                return self.create_demo_data_for_symbol(symbol, timeframe)
            
            # Use our new async exchange interface
            import asyncio
            import time
            
            # Add longer delay to prevent rate limiting
            time.sleep(1.0)  # 1 second delay between requests
            
            async def fetch_data():
                try:
                    # Try to get 1000 candles to ensure we have 500 for SMA200
                    return await self.exchange.get_ohlcv(symbol, timeframe, limit=1000)
                except Exception as e:
                    if "10006" in str(e) or "too frequently" in str(e):
                        # Don't print rate limit errors to reduce log spam
                        return None
                    else:
                        print(f"Error fetching {symbol} {timeframe}: {e}")
                        return None
            
            # Run async call
            ohlcv_data = asyncio.run(fetch_data())
            
            # Check if we got data
            if not ohlcv_data or len(ohlcv_data) == 0:
                print(f"📱 Using demo data for {symbol} {timeframe} (no exchange data)")
                # Set demo mode to avoid repeated exchange attempts
                self.demo_mode = True
                # Try to use demo data as fallback
                return self.create_demo_data_for_symbol(symbol, timeframe)
            
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
            
            # Check if we have enough data for SMA200
            if len(df) < 500:
                print(f"[WARNING] Insufficient data for {symbol} {timeframe}: {len(df)} candles, using demo data")
                return self.create_demo_data_for_symbol(symbol, timeframe)
            
            # Calculate technical indicators
            df['ema50'] = df['close'].ewm(span=50).mean()
            df['ema100'] = df['close'].ewm(span=100).mean()
            df['ema200'] = df['close'].ewm(span=200).mean()
            df['sma50'] = df['close'].rolling(window=50).mean()
            df['sma200'] = df['close'].rolling(window=200).mean()  # SMA 200
            df['rsi'] = self.calculate_rsi(df['close'])
            # Market Cipher B components
            wt1, wt2 = self.calculate_wave_trend(df)
            df['wt1'] = wt1
            df['wt2'] = wt2
            df['mfi'] = self.calculate_mfi(df['high'], df['low'], df['close'], df['volume'])
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Cache the data
            cache_key = f"{symbol}_{timeframe}"
            self.data_cache[cache_key] = df
            print(f"[SUCCESS] Cached {len(df)} candles for {symbol} {timeframe}")
            
        except Exception as e:
            print(f"[ERROR] Error caching {symbol} {timeframe}: {e}")
            import traceback
            traceback.print_exc()
            # Try to use demo data as fallback
            return self.create_demo_data_for_symbol(symbol, timeframe)
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_wave_trend(self, df: pd.DataFrame, channel_length: int = 9, average_length: int = 12):
        """Approximate WaveTrend (WT1, WT2) used in Market Cipher B.
        Based on LazyBear WaveTrend: https://www.tradingview.com/script/2KE8wTuF-WaveTrend-Oscillator/
        """
        hlc3 = (df['high'] + df['low'] + df['close']) / 3.0
        esa = hlc3.ewm(span=channel_length, adjust=False).mean()
        de = (hlc3 - esa).abs().ewm(span=channel_length, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * de.replace(0, np.nan))
        wt1 = ci.ewm(span=average_length, adjust=False).mean()
        wt2 = wt1.rolling(window=4).mean()
        return wt1, wt2

    def calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14):
        """Money Flow Index (0-100)."""
        tp = (high + low + close) / 3.0
        money_flow = tp * volume
        delta_tp = tp.diff()
        positive_mf = money_flow.where(delta_tp > 0, 0.0)
        negative_mf = money_flow.where(delta_tp < 0, 0.0)
        positive_mf_sum = positive_mf.rolling(window=period).sum()
        negative_mf_sum = negative_mf.rolling(window=period).sum().abs()
        # Avoid division by zero
        mfr = positive_mf_sum / negative_mf_sum.replace(0, np.nan)
        mfi = 100 - (100 / (1 + mfr))
        return mfi
    


    def create_interactive_chart(self, symbol, timeframe):
        """Create interactive Plotly chart with technical indicators"""
        try:
            cache_key = f"{symbol}_{timeframe}"
            if cache_key not in self.data_cache:
                # Try to fetch data if not in cache
                self.fetch_and_cache_data(symbol, timeframe)
                if cache_key not in self.data_cache:
                    print(f"No data available for {symbol} {timeframe}")
                    return None
            
            df = self.data_cache[cache_key].copy()
            print(f"Creating chart for {symbol} {timeframe} with {len(df)} candles")
            print(f"Sample data - Open: {df['open'].iloc[-5:].tolist()}")
            print(f"Sample data - Close: {df['close'].iloc[-5:].tolist()}")
            print(f"Sample data - High: {df['high'].iloc[-5:].tolist()}")
            print(f"Sample data - Low: {df['low'].iloc[-5:].tolist()}")
            
            # Handle NaN values and convert to lists FIRST
            df = df.dropna()  # Remove rows with NaN values
            print(f"After dropna: {len(df)} candles")
            
            # Check if we have enough data for SMA200
            if len(df) < 500:
                print(f"Warning: Insufficient data for {symbol} {timeframe} - need 500 candles, got {len(df)}")
                # Try to create demo data as fallback
                try:
                    print(f"Attempting to create demo data for {symbol} {timeframe}")
                    demo_df = self.create_demo_data_for_symbol(symbol, timeframe)
                    if demo_df is not None and len(demo_df) >= 500:
                        # Update cache with demo data
                        self.data_cache[cache_key] = demo_df
                        df = demo_df.copy()
                        print(f"✅ Using demo data for {symbol} {timeframe}")
                    else:
                        print(f"Demo data creation failed for {symbol} {timeframe}")
                        return None
                except Exception as e:
                    print(f"Error creating demo data for {symbol} {timeframe}: {e}")
                    return None
            
            timestamps = df['timestamp'].tolist()
            
            # Data cleaning function
            def clean_data(data):
                """Clean data by replacing NaN and infinite values"""
                import math
                cleaned = []
                for val in data:
                    if pd.isna(val) or (isinstance(val, (int, float)) and math.isinf(val)):
                        cleaned.append(None)
                    else:
                        cleaned.append(val)
                return cleaned
            
            # Ensure all data is converted to lists and handle any remaining NaN
            ohlc_data = {
                'open': clean_data(df['open'].ffill().tolist()),
                'high': clean_data(df['high'].ffill().tolist()),
                'low': clean_data(df['low'].ffill().tolist()),
                'close': clean_data(df['close'].ffill().tolist()),
            }
            
            # Technical indicators converted to lists with NaN handling
            rsi_data = clean_data(df['rsi'].ffill().tolist())
            volume_data = clean_data(df['volume'].tolist())
            volume_sma_data = clean_data(df['volume_sma'].ffill().tolist())
            
            # Volume colors (green for up, red for down)
            volume_colors = []
            for i in range(len(df)):
                if i > 0 and df.iloc[i]['close'] > df.iloc[i]['open']:
                    volume_colors.append('rgba(0, 255, 0, 0.6)')  # Green
                else:
                    volume_colors.append('rgba(255, 0, 0, 0.6)')  # Red
            
            # Create subplots with optimized proportions for full visibility
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.06,
                subplot_titles=('Price & EMAs', 'Volume', 'RSI', 'Market Cipher B (WT1/WT2 & MFI)'),
                row_heights=[0.55, 0.20, 0.10, 0.15],
                specs=[[{"secondary_y": False}],
                       [{"secondary_y": False}],
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
            
            # Volume SMA
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=volume_sma_data,
                    mode='lines',
                    name='Volume SMA',
                    line=dict(color='#FF9800', width=1),
                    connectgaps=True,
                    showlegend=False
                ),
                row=2, col=1
            )

            # Overlay EMA/SMA indicators on price chart
            ema50_data = clean_data(df['ema50'].ffill().tolist()) if 'ema50' in df.columns else []
            sma50_data = clean_data(df['sma50'].ffill().tolist()) if 'sma50' in df.columns else []
            sma200_data = clean_data(df['sma200'].ffill().tolist()) if 'sma200' in df.columns else []

            if ema50_data:
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

            if sma50_data:
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=sma50_data,
                        mode='lines',
                        name='SMA50',
                        line=dict(color='#66BB6A', width=1.5, dash='dash'),
                        connectgaps=True
                    ),
                    row=1, col=1
                )

            if sma200_data:
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=sma200_data,
                        mode='lines',
                        name='SMA200',
                        line=dict(color='#EF5350', width=1.5, dash='dot'),
                        connectgaps=True
                    ),
                    row=1, col=1
                )
            
            # RSI
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
            
            # Add RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

            # Market Cipher B pane
            wt1_data = clean_data(df['wt1'].ffill().tolist()) if 'wt1' in df.columns else []
            wt2_data = clean_data(df['wt2'].ffill().tolist()) if 'wt2' in df.columns else []
            mfi_data = clean_data(df['mfi'].ffill().tolist()) if 'mfi' in df.columns else []

            if wt1_data:
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=wt1_data,
                        mode='lines',
                        name='WT1',
                        line=dict(color='#00E676', width=1.8),
                        connectgaps=True,
                        showlegend=False
                    ),
                    row=4, col=1
                )
            if wt2_data:
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=wt2_data,
                        mode='lines',
                        name='WT2',
                        line=dict(color='#29B6F6', width=1.4, dash='dot'),
                        connectgaps=True,
                        showlegend=False
                    ),
                    row=4, col=1
                )
            if mfi_data:
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=mfi_data,
                        mode='lines',
                        name='MFI',
                        line=dict(color='#FFD54F', width=1),
                        connectgaps=True,
                        showlegend=False
                    ),
                    row=4, col=1
                )
            
            # Update layout
            last_close = df['close'].iloc[-1]
            last_ema50 = df['ema50'].iloc[-1] if 'ema50' in df.columns else None
            last_sma50 = df['sma50'].iloc[-1] if 'sma50' in df.columns else None
            last_sma200 = df['sma200'].iloc[-1] if 'sma200' in df.columns else None
            title_suffix_parts = []
            if last_ema50 is not None:
                title_suffix_parts.append(f"EMA50: {last_ema50:.2f}")
            if last_sma50 is not None:
                title_suffix_parts.append(f"SMA50: {last_sma50:.2f}")
            if last_sma200 is not None:
                title_suffix_parts.append(f"SMA200: {last_sma200:.2f}")
            title_suffix = " | " + " · ".join(title_suffix_parts) if title_suffix_parts else ""
            fig.update_layout(
                title=f'{symbol} - {timeframe.upper()} Chart{title_suffix}',
                template='plotly_dark',
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update axes
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1)
            fig.update_yaxes(title_text="MCB", row=4, col=1)
            
            # Clean the figure data to remove any NaN or infinite values
            fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            print(f"✅ Chart created successfully for {symbol} {timeframe}")
            return fig_json
            
        except Exception as e:
            print(f"Error in chart creation for {symbol} {timeframe}: {e}")
            return None

    
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

class RealTimeAlertSystem:
    """Real-time alert system for EMA/SMA crossovers with RSI and volume confirmation"""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.alert_cooldown = 600  # 10 minutes between alerts for same symbol (increased)
        self.last_alerts = {}
        self.alert_sounds = {
            'BULLISH': 800,  # Higher frequency for bullish
            'BEARISH': 400   # Lower frequency for bearish
        }
        self.system_start_time = time.time()  # Track when system started
        # Cross-platform audio player
        self.audio = get_audio_player()
    
    def monitor_all_symbols(self):
        """Monitor all tracked symbols for crossover signals"""
        # Check if system has been running long enough (warm-up period)
        current_time = time.time()
        if current_time - self.system_start_time < 180:  # 3 minutes warm-up
            return
        
        if not self.dashboard.exchange_connected:
            return
        
        try:
            # Get all symbols to monitor (use recently accessed + top movers)
            symbols_to_monitor = list(self.dashboard.recently_accessed)
            
            # Add top gainers and losers if scanner is available
            if self.dashboard.scanner:
                try:
                    # Get curated 100 coins for monitoring
                    curated_data = self.dashboard.scanner.get_curated_100_coins()
                    symbols_to_monitor.extend(curated_data['all_symbols'])
                    
                    # Also add top gainers and losers
                    gainers = self.dashboard.scanner.fetch_market_movers('gainers', 20)
                    losers = self.dashboard.scanner.fetch_market_movers('losers', 20)
                    for coin in gainers + losers:
                        symbols_to_monitor.append(coin['symbol'])
                except:
                    pass
            
            # Remove duplicates and limit to 100 for performance
            symbols_to_monitor = list(set(symbols_to_monitor))[:100]
            
            print(f"🔍 Monitoring {len(symbols_to_monitor)} symbols for 1h alerts")
            
            for symbol in symbols_to_monitor:
                self.check_symbol_for_signals(symbol)
                
        except Exception as e:
            print(f"Alert monitoring error: {e}")
    

    
    def _is_cross(self, series_a_prev, series_a_curr, series_b_prev, series_b_curr, direction='above'):
        """Detects crossover between two series on last step."""
        if direction == 'above':
            return series_a_prev <= series_b_prev and series_a_curr > series_b_curr
        else:
            return series_a_prev >= series_b_prev and series_a_curr < series_b_curr

    def _rsi_is_extreme(self, rsi_value, upper=70, lower=30, buffer=5):
        """RSI near outer bands (not mid)."""
        if pd.isna(rsi_value):
            return False
        return rsi_value >= (upper - buffer) or rsi_value <= (lower + buffer)

    def _eligible_by_cooldown(self, symbol, key_suffix=''):
        now_ts = time.time()
        key = f"{symbol}{key_suffix}"
        last = self.last_alerts.get(key)
        if last and (now_ts - last) < self.alert_cooldown:
            return False
        self.last_alerts[key] = now_ts
        return True

    def check_symbol_for_signals(self, symbol):
        """Check EMA50 cross vs SMA50 or SMA200 on 1h with RSI extremes and trigger alerts."""
        try:
            cache_key = f"{symbol}_{self.dashboard.primary_timeframe}"
            if cache_key not in self.dashboard.data_cache:
                return
            df = self.dashboard.data_cache[cache_key]
            if len(df) < 205:
                return

            # Ensure needed columns
            for col, expr in [
                ('ema50', df['close'].ewm(span=50).mean()),
                ('sma50', df['close'].rolling(window=50).mean()),
                ('sma200', df['close'].rolling(window=200).mean()),
                ('rsi', self.dashboard.calculate_rsi(df['close']))
            ]:
                if col not in df.columns:
                    df[col] = expr

            last_idx = -1
            prev_idx = -2

            ema50_prev, ema50_curr = df['ema50'].iloc[prev_idx], df['ema50'].iloc[last_idx]
            sma50_prev, sma50_curr = df['sma50'].iloc[prev_idx], df['sma50'].iloc[last_idx]
            sma200_prev, sma200_curr = df['sma200'].iloc[prev_idx], df['sma200'].iloc[last_idx]
            rsi_curr = df['rsi'].iloc[last_idx]

            price_curr = df['close'].iloc[last_idx]
            vol_curr = df['volume'].iloc[last_idx]
            vol_avg = df['volume'].rolling(window=20).mean().iloc[last_idx]
            volume_ratio = float(vol_curr / vol_avg) if vol_avg and not pd.isna(vol_avg) else 1.0

            # RSI filter: near outer bands, not middle
            if not self._rsi_is_extreme(rsi_curr, upper=70, lower=30, buffer=5):
                pass  # allow MCB alerts even if RSI is mid; RSI used for EMA/SMA alerts

            signals = []
            # EMA50 cross above/below SMA50
            if self._is_cross(ema50_prev, ema50_curr, sma50_prev, sma50_curr, 'above'):
                signals.append(('LONG', 'EMA50_cross_SMA50_up'))
            elif self._is_cross(ema50_prev, ema50_curr, sma50_prev, sma50_curr, 'below'):
                signals.append(('SHORT', 'EMA50_cross_SMA50_down'))

            # EMA50 cross above/below SMA200
            if self._is_cross(ema50_prev, ema50_curr, sma200_prev, sma200_curr, 'above'):
                signals.append(('LONG', 'EMA50_cross_SMA200_up'))
            elif self._is_cross(ema50_prev, ema50_curr, sma200_prev, sma200_curr, 'below'):
                signals.append(('SHORT', 'EMA50_cross_SMA200_down'))

            for direction, alert_type in signals:
                if not self._eligible_by_cooldown(symbol, key_suffix=f"_{alert_type}"):
                    continue
                confidence = 70.0
                signal_payload = {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'direction': direction,
                    'price': float(price_curr),
                    'rsi': float(rsi_curr) if not pd.isna(rsi_curr) else 50.0,
                    'volume_ratio': float(volume_ratio),
                    'confidence': confidence,
                    'timeframe': self.dashboard.primary_timeframe,
                    'alert_type': alert_type,
                    'ema_fast': float(ema50_curr),
                    'ema_slow': float(sma50_curr if 'SMA50' in alert_type.upper() else sma200_curr)
                }
                # Store signal for confirmation instead of immediate alert
                self.store_signal_for_confirmation(signal_payload)

            # Market Cipher B alert examples
            if 'wt1' in df.columns and 'wt2' in df.columns:
                wt1_prev, wt1_curr = df['wt1'].iloc[prev_idx], df['wt1'].iloc[last_idx]
                wt2_prev, wt2_curr = df['wt2'].iloc[prev_idx], df['wt2'].iloc[last_idx]
                mfi_curr = df['mfi'].iloc[last_idx] if 'mfi' in df.columns else np.nan

                mcb_signals = []
                # WT cross up from below -60 (bullish)
                if wt1_prev < wt2_prev and wt1_curr > wt2_curr and wt1_curr < -20:
                    mcb_signals.append(('LONG', 'MCB_WT_Bullish_Cross'))
                # WT cross down from above +60 (bearish)
                if wt1_prev > wt2_prev and wt1_curr < wt2_curr and wt1_curr > 20:
                    mcb_signals.append(('SHORT', 'MCB_WT_Bearish_Cross'))

                # Optional confirmation: MFI rising for long, falling for short
                for direction, alert_type in mcb_signals:
                    if not self._eligible_by_cooldown(symbol, key_suffix=f"_{alert_type}"):
                        continue
                    confidence = 65.0
                    signal_payload = {
                        'timestamp': datetime.now(),
                        'symbol': symbol,
                        'direction': direction,
                        'price': float(price_curr),
                        'rsi': float(rsi_curr) if not pd.isna(rsi_curr) else 50.0,
                        'volume_ratio': float(volume_ratio),
                        'confidence': confidence,
                        'timeframe': self.dashboard.primary_timeframe,
                        'alert_type': alert_type,
                        'ema_fast': float(wt1_curr),
                        'ema_slow': float(wt2_curr),
                        'notes': f"MFI: {mfi_curr:.1f}" if not pd.isna(mfi_curr) else ''
                    }
                    # Store signal for confirmation instead of immediate alert
                    self.store_signal_for_confirmation(signal_payload)
        except Exception as e:
            print(f"Error checking signals for {symbol}: {e}")

    def log_alert_to_database(self, signal):
        try:
            conn = sqlite3.connect('trading_signals.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (symbol, alert_type, direction, price, rsi, volume_ratio, ema_fast, ema_slow, confidence, timeframe, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('symbol'),
                signal.get('alert_type', 'ema50_cross'),
                signal.get('direction'),
                signal.get('price'),
                signal.get('rsi'),
                signal.get('volume_ratio'),
                signal.get('ema_fast'),
                signal.get('ema_slow'),
                signal.get('confidence', 0),
                signal.get('timeframe'),
                signal.get('notes', '')
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging alert: {e}")
    def trigger_alert(self, signal):
        """Trigger audio and visual alert for a signal with confirmation check"""
        try:
            # Add confirmation tracking to the signal
            signal['confirmation_status'] = 'PENDING'
            signal['confirmation_checked'] = False
            
            # Store signal for confirmation tracking
            self.dashboard.confirmation_system.update_confirmation_cache(
                signal['symbol'], 
                signal['direction'], 
                signal['price'], 
                signal['timestamp']
            )
            
            # Play audio alert only if enabled (cross-platform)
            if self.dashboard.audio_enabled:
                frequency = self.alert_sounds.get(signal['direction'], 600)
                duration = 500  # 500ms
                self.audio.beep(frequency, duration)
                time.sleep(0.1)
                self.audio.beep(frequency, duration)
            else:
                print("🔇 Audio alerts disabled")
            
            # Log alert to database
            self.log_alert_to_database(signal)
            
            # Add to active alerts
            self.dashboard.active_alerts.append(signal)
            
            # Keep only last 10 alerts
            if len(self.dashboard.active_alerts) > 10:
                self.dashboard.active_alerts = self.dashboard.active_alerts[-10:]
            
            # Print alert with confirmation notice
            direction_emoji = "📈" if signal['direction'] == 'LONG' else "📉"
            print(f"\n🚨 ALERT: {direction_emoji} {signal['symbol']} {signal['direction']} SIGNAL!")
            print(f"   💰 Price: ${signal['price']:.4f}")
            print(f"   📊 RSI: {signal['rsi']:.1f}")
            print(f"   🔊 Volume: {signal['volume_ratio']:.1f}x average")
            print(f"   🎯 Confidence: {signal['confidence']:.0f}%")
            print(f"   ⏰ Timeframe: {signal['timeframe']}")
            print(f"   🕐 Time: {signal['timestamp'].strftime('%H:%M:%S')}")
            print(f"   🔍 Confirmation: Waiting for 5m candles...")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error triggering alert: {e}")
    
    def store_signal_for_confirmation(self, signal):
        """Store signal for confirmation without triggering immediate alert"""
        try:
            # CHECK SYMBOL COOLDOWN FIRST
            in_cooldown, time_remaining = self.dashboard.confirmation_system.check_symbol_cooldown(signal['symbol'])
            if in_cooldown:
                print(f"⏰ SYMBOL COOLDOWN: {signal['symbol']} in cooldown for {time_remaining:.1f} more minutes - skipping signal")
                return
            
            # Add confirmation tracking to the signal
            signal['confirmation_status'] = 'PENDING'
            signal['confirmation_checked'] = False
            
            # Update symbol signal history to prevent conflicting signals
            self.dashboard.confirmation_system.update_symbol_signal_history(signal['symbol'])
            
            # Store signal for confirmation tracking
            self.dashboard.confirmation_system.update_confirmation_cache(
                signal['symbol'], 
                signal['direction'], 
                signal['price'], 
                signal['timestamp']
            )
            
            # Add to active alerts (but don't trigger audio yet)
            self.dashboard.active_alerts.append(signal)
            
            # Keep only last 10 alerts
            if len(self.dashboard.active_alerts) > 10:
                self.dashboard.active_alerts = self.dashboard.active_alerts[-10:]
            
            # PLAY IMMEDIATE AUDIO ALERT
            if self.dashboard.audio_enabled:
                frequency = self.alert_sounds.get(signal['direction'], 600)
                duration = 300  # Shorter duration for immediate alert
                print(f"🔊 IMMEDIATE AUDIO: Playing {frequency}Hz for {duration}ms")
                self.audio.beep(frequency, duration)
                time.sleep(0.05)
                self.audio.beep(frequency, duration)
            
            # Print signal detection
            direction_emoji = "📈" if signal['direction'] == 'LONG' else "📉"
            print(f"\n🔍 SIGNAL DETECTED: {direction_emoji} {signal['symbol']} {signal['direction']} SIGNAL!")
            print(f"   💰 Price: ${signal['price']:.4f}")
            print(f"   📊 RSI: {signal['rsi']:.1f}")
            print(f"   🔊 Volume: {signal['volume_ratio']:.1f}x average")
            print(f"   🎯 Confidence: {signal['confidence']:.0f}%")
            print(f"   ⏰ Timeframe: {signal['timeframe']}")
            print(f"   🕐 Time: {signal['timestamp'].strftime('%H:%M:%S')}")
            print(f"   🔍 Status: Waiting for 25-minute quadruple confirmation...")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error storing signal for confirmation: {e}")
    
    def check_pending_confirmations(self):
        """Check all pending confirmations with FOUR confirmation blocks"""
        try:
            pending = self.dashboard.confirmation_system.get_pending_confirmations()
            
            for signal_data in pending:
                # FIRST CONFIRMATION BLOCK
                first_confirmed, first_confidence, first_details = self.dashboard.confirmation_system.check_confirmation(
                    signal_data['symbol'],
                    signal_data['direction'],
                    signal_data['signal_price'],
                    signal_data['signal_time']
                )
                
                # SECOND CONFIRMATION BLOCK (more strict)
                second_confirmed, second_confidence, second_details = self.dashboard.confirmation_system.check_second_confirmation(
                    signal_data['symbol'],
                    signal_data['direction'],
                    signal_data['signal_price'],
                    signal_data['signal_time']
                )
                
                # THIRD CONFIRMATION BLOCK (ultra strict)
                third_confirmed, third_confidence, third_details = self.dashboard.confirmation_system.check_third_confirmation(
                    signal_data['symbol'],
                    signal_data['direction'],
                    signal_data['signal_price'],
                    signal_data['signal_time']
                )
                
                # FOURTH CONFIRMATION BLOCK (maximum strict)
                fourth_confirmed, fourth_confidence, fourth_details = self.dashboard.confirmation_system.check_fourth_confirmation(
                    signal_data['symbol'],
                    signal_data['direction'],
                    signal_data['signal_price'],
                    signal_data['signal_time']
                )
                
                # Find and update signal in active alerts
                for alert in self.dashboard.active_alerts:
                    if (alert['symbol'] == signal_data['symbol'] and 
                        alert['direction'] == signal_data['direction'] and
                        alert['timestamp'] == signal_data['signal_time']):
                        
                        # ALL FOUR confirmations must pass
                        fully_confirmed = first_confirmed and second_confirmed and third_confirmed and fourth_confirmed
                        combined_confidence = (first_confidence + second_confidence + third_confidence + fourth_confidence) / 4
                        combined_details = f"FIRST: {first_details} | SECOND: {second_details} | THIRD: {third_details} | FOURTH: {fourth_details}"
                        
                        alert['confirmation_status'] = 'CONFIRMED' if fully_confirmed else 'REJECTED'
                        alert['confirmation_confidence'] = combined_confidence
                        alert['confirmation_details'] = combined_details
                        alert['confirmation_checked'] = True
                        
                        # TRIGGER ALERT ONLY AFTER ALL FOUR CONFIRMATIONS
                        if fully_confirmed:
                            print(f"\n🎯 QUADRUPLE CONFIRMED: {signal_data['symbol']} {signal_data['direction']}")
                            print(f"   📊 First Confirmation: {first_confidence:.1f}%")
                            print(f"   📊 Second Confirmation: {second_confidence:.1f}%")
                            print(f"   📊 Third Confirmation: {third_confidence:.1f}%")
                            print(f"   📊 Fourth Confirmation: {fourth_confidence:.1f}%")
                            print(f"   📊 Combined Confidence: {combined_confidence:.1f}%")
                            self.trigger_confirmed_alert(alert)
                        else:
                            # Print rejection
                            print(f"\n❌ SIGNAL REJECTED: {signal_data['symbol']} {signal_data['direction']}")
                            print(f"   🎯 First Confirmation: {'PASS' if first_confirmed else 'FAIL'} ({first_confidence:.1f}%)")
                            print(f"   🎯 Second Confirmation: {'PASS' if second_confirmed else 'FAIL'} ({second_confidence:.1f}%)")
                            print(f"   🎯 Third Confirmation: {'PASS' if third_confirmed else 'FAIL'} ({third_confidence:.1f}%)")
                            print(f"   🎯 Fourth Confirmation: {'PASS' if fourth_confirmed else 'FAIL'} ({fourth_confidence:.1f}%)")
                            print(f"   📝 Details: {combined_details}")
                            print("=" * 50)
                        break
                        
        except Exception as e:
            print(f"Error checking confirmations: {e}")
    
    def trigger_confirmed_alert(self, signal):
        """Trigger audio and visual alert for a CONFIRMED signal"""
        try:
            print(f"🔊 TRIGGERING AUDIO ALERT for {signal['symbol']} {signal['direction']}")
            print(f"🔊 Audio enabled: {self.dashboard.audio_enabled}")
            
            # FORCE AUDIO TO PLAY IMMEDIATELY
            if self.dashboard.audio_enabled:
                frequency = self.alert_sounds.get(signal['direction'], 600)
                duration = 500  # 500ms
                
                print(f"🔊 Playing {frequency}Hz for {duration}ms")
                # Cross-platform beeps using audio service
                self.audio.beep(frequency, duration)
                time.sleep(0.1)
                self.audio.beep(frequency, duration)
                time.sleep(0.1)
                self.audio.beep(frequency, duration)
            else:
                print("🔇 Audio alerts disabled")
            
            # Log alert to database
            self.log_alert_to_database(signal)
            
            # Print CONFIRMED alert
            direction_emoji = "📈" if signal['direction'] == 'LONG' else "📉"
            print(f"\n🚨 CONFIRMED ALERT: {direction_emoji} {signal['symbol']} {signal['direction']} SIGNAL!")
            print(f"   💰 Price: ${signal['price']:.4f}")
            print(f"   📊 RSI: {signal['rsi']:.1f}")
            print(f"   🔊 Volume: {signal['volume_ratio']:.1f}x average")
            print(f"   🎯 Confidence: {signal['confidence']:.0f}%")
            print(f"   ⏰ Timeframe: {signal['timeframe']}")
            print(f"   🕐 Time: {signal['timestamp'].strftime('%H:%M:%S')}")
            print(f"   ✅ Confirmation: {signal['confirmation_confidence']:.1f}% confidence")
            print(f"   📝 Details: {signal['confirmation_details']}")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error triggering confirmed alert: {e}")
    



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
    try:
        print(f"📊 Chart request for {symbol} {timeframe}")
        
        # Track that this symbol was accessed
        dashboard.track_symbol_access(symbol)
        
        # Try the full interactive chart first
        chart_json = dashboard.create_interactive_chart(symbol, timeframe)
        if chart_json:
            print(f"✅ Interactive chart created successfully for {symbol} {timeframe}")
            return jsonify({'chart': chart_json})
        
        # If interactive chart fails, try the simple chart as fallback
        print(f"Interactive chart failed, trying simple chart for {symbol} {timeframe}")
        chart_json = dashboard.create_simple_chart(symbol, timeframe)
        if chart_json:
            print(f"✅ Simple chart created successfully for {symbol} {timeframe}")
            return jsonify({'chart': chart_json})
        
        # If both fail, try demo data fallback
        print(f"❌ Chart creation failed for {symbol} {timeframe}, trying demo data fallback")
        try:
            demo_df = dashboard.create_demo_data_for_symbol(symbol, timeframe)
            if demo_df is not None:
                cache_key = f"{symbol}_{timeframe}"
                dashboard.data_cache[cache_key] = demo_df
                chart_json = dashboard.create_simple_chart(symbol, timeframe)
                if chart_json:
                    print(f"✅ Chart created with demo data for {symbol} {timeframe}")
                    return jsonify({'chart': chart_json})
        except Exception as demo_error:
            print(f"Demo data fallback failed for {symbol} {timeframe}: {demo_error}")
        
        print(f"❌ All chart creation attempts failed for {symbol} {timeframe}")
        return jsonify({'error': 'Chart data unavailable'}), 500
        
    except Exception as e:
        print(f"❌ Error creating chart for {symbol} {timeframe}: {e}")
        return jsonify({'error': f'Failed to load chart - {str(e)}'}), 500

@app.route('/api/signals')
def get_signals():
    """API endpoint for recent signals"""
    signals = dashboard.get_recent_signals()
    return jsonify(signals)

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for real-time alerts"""
    return jsonify(dashboard.active_alerts)

@app.route('/api/alerts/latest')
def get_latest_alert():
    """API endpoint for latest alert (for polling)"""
    if dashboard.active_alerts:
        latest_alert = dashboard.active_alerts[-1]  # Get the most recent alert
        return jsonify({
            'alertId': f"{latest_alert['symbol']}_{latest_alert['timestamp'].strftime('%Y%m%d%H%M%S')}",
            'symbol': latest_alert['symbol'],
            'direction': latest_alert['direction'],
            'price': latest_alert['price'],
            'rsi': latest_alert['rsi'],
            'volume_ratio': latest_alert['volume_ratio'],
            'confidence': latest_alert['confidence'],
            'timestamp': latest_alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'timeframe': latest_alert['timeframe'],
            'confirmation_status': latest_alert.get('confirmation_status', 'UNKNOWN'),
            'confirmation_confidence': latest_alert.get('confirmation_confidence', 0)
        })
    return jsonify({})

@app.route('/api/confirmations')
def get_confirmations():
    """Get all pending and confirmed signals"""
    try:
        confirmations = []
        
        # Get pending confirmations
        pending = dashboard.confirmation_system.get_pending_confirmations()
        for signal_data in pending:
            confirmations.append({
                'symbol': signal_data['symbol'],
                'direction': signal_data['direction'],
                'signal_price': signal_data['signal_price'],
                'signal_time': signal_data['signal_time'].isoformat() if hasattr(signal_data['signal_time'], 'isoformat') else str(signal_data['signal_time']),
                'status': 'PENDING',
                'time_since_signal': f"{((datetime.now() - signal_data['signal_time']).total_seconds() / 60):.1f} minutes"
            })
        
        # Get confirmed/rejected signals from active alerts
        for alert in dashboard.active_alerts:
            if alert.get('confirmation_checked', False):
                confirmations.append({
                    'symbol': alert['symbol'],
                    'direction': alert['direction'],
                    'signal_price': alert['price'],
                    'signal_time': alert['timestamp'].isoformat() if hasattr(alert['timestamp'], 'isoformat') else str(alert['timestamp']),
                    'status': alert.get('confirmation_status', 'UNKNOWN'),
                    'confidence': alert.get('confirmation_confidence', 0),
                    'details': alert.get('confirmation_details', '')
                })
        
        return jsonify({
            'success': True,
            'confirmations': confirmations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/confirmation/<symbol>/<direction>')
def check_confirmation(symbol, direction):
    """Manually check confirmation for a specific signal"""
    try:
        # Find the signal in active alerts
        signal_data = None
        for alert in dashboard.active_alerts:
            if alert['symbol'] == symbol and alert['direction'] == direction:
                signal_data = {
                    'symbol': alert['symbol'],
                    'direction': alert['direction'],
                    'signal_price': alert['price'],
                    'signal_time': alert['timestamp']
                }
                break
        
        if not signal_data:
            return jsonify({
                'success': False,
                'message': 'Signal not found'
            })
        
        # Check confirmation
        confirmed, confidence, details = dashboard.confirmation_system.check_confirmation(
            signal_data['symbol'],
            signal_data['direction'],
            signal_data['signal_price'],
            signal_data['signal_time']
        )
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'direction': direction,
            'confirmed': confirmed,
            'confidence': confidence,
            'details': details,
            'recommendation': dashboard.confirmation_system._get_recommendation(confirmed, confidence, direction)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

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
        curated_data = dashboard.scanner.get_curated_50_coins()
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

@app.route('/api/audio/toggle', methods=['POST'])
def toggle_audio():
    """Toggle audio alerts on/off"""
    try:
        dashboard.audio_enabled = not dashboard.audio_enabled
        status = "enabled" if dashboard.audio_enabled else "disabled"
        print(f"🔊 Audio alerts {status}")
        return jsonify({
            'audio_enabled': dashboard.audio_enabled,
            'message': f'Audio alerts {status}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/status')
def get_audio_status():
    """Get current audio alert status"""
    return jsonify({
        'audio_enabled': dashboard.audio_enabled
    })

@app.route('/api/audio/set', methods=['POST'])
def set_audio_status():
    """Set audio alert status"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        dashboard.audio_enabled = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🔊 Audio alerts {status}")
        return jsonify({
            'audio_enabled': dashboard.audio_enabled,
            'message': f'Audio alerts {status}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coin_limit', methods=['GET', 'POST'])
def coin_limit():
    """API endpoint to get or set the maximum number of coins to scan"""
    try:
        if request.method == 'GET':
            # Return current limit
            return jsonify({'limit': dashboard.config.max_coins_limit})
        else:
            # Update limit
            data = request.get_json()
            new_limit = data.get('limit', 20)
            
            # Validate limit
            if not isinstance(new_limit, int) or new_limit < 1 or new_limit > 100:
                return jsonify({'error': 'Limit must be between 1 and 100'}), 400
            
            # Update the setting
            dashboard.config.max_coins_limit = new_limit
            
            # Clear scanner cache to force refresh with new limit
            if dashboard.scanner:
                dashboard.scanner.curated_cache = {
                    'opportunities': None,
                    'timestamp': None,
                    'cache_duration': 15 * 60
                }
                print(f"🔄 Scanner cache cleared, new coin limit: {new_limit}")
            
            return jsonify({'success': True, 'limit': new_limit})
    except Exception as e:
        print(f"Error handling coin limit: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting Trading Dashboard...")
    print("📱 Access at: http://localhost:5001")
    print("🚨 Real-time alerts: ENABLED")
    print("   - EMA50/EMA100 crossovers on 1h timeframe (primary)")
    print("   - RSI confirmation (30-70 range)")
    print("   - Volume confirmation (>1.2x average)")
    print("   - Audio alerts with toggle control")
    print("   - Monitoring 100 coins for signals")
    print("   - Available timeframes: 5m, 15m, 30m, 1h, 4h")
    print("   - 1h is default for alerts, other timeframes for analysis")


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Professional Crypto Trading Scanner Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flask_dashboard.py              # Normal startup (uses saved config or wizard)
  python flask_dashboard.py --demo       # Force demo mode (override saved config)
  python flask_dashboard.py --api-binance    # Force Binance API (needs env vars)
  python flask_dashboard.py --api-bitunix    # Force Bitunix API (needs env vars)
  python flask_dashboard.py --config     # Run configuration wizard
  python flask_dashboard.py --help       # Show this help message

The dashboard will automatically guide you through setup on first run.
        """
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Force demo mode (override saved configuration)'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Run configuration wizard (reconfigure settings)'
    )
    
    parser.add_argument(
        '--api-binance',
        action='store_true',
        help='Force use of Binance API (requires API keys in environment)'
    )
    
    parser.add_argument(
        '--api-bitunix',
        action='store_true',
        help='Force use of Bitunix API (requires API keys in environment)'
    )
    
    return parser.parse_args()


def setup_configuration(force_demo=False, force_config=False, force_exchange=None):
    """Setup configuration using wizard if needed."""
    from config.setup_wizard import ConfigurationWizard
    
    wizard = ConfigurationWizard()
    
    # Force demo mode if requested
    if force_demo:
        print("🎭 DEMO MODE REQUESTED")
        print("Using simulated data for this session...")
        
        # Create temporary demo config
        demo_config = {'mode': 'demo'}
        wizard.create_env_file(demo_config)
        return demo_config
    
    # Force specific exchange if requested
    if force_exchange:
        print(f"🔗 {force_exchange.upper()} API REQUESTED")
        print(f"Attempting to use {force_exchange} with environment credentials...")
        
        # Check for required environment variables
        api_key_env = f'TRADING_{force_exchange.upper()}_API_KEY'
        secret_key_env = f'TRADING_{force_exchange.upper()}_SECRET_KEY'
        
        api_key = os.getenv(api_key_env)
        secret_key = os.getenv(secret_key_env)
        
        if not api_key or not secret_key:
            print(f"❌ Missing required environment variables:")
            print(f"   {api_key_env}={api_key if api_key else 'NOT SET'}")
            print(f"   {secret_key_env}={'SET' if secret_key else 'NOT SET'}")
            print(f"\n💡 Please set these environment variables or run without --api-{force_exchange}")
            print("   Example:")
            print(f"   export {api_key_env}=your_api_key")
            print(f"   export {secret_key_env}=your_secret_key")
            sys.exit(1)
        
        # Create forced exchange config
        forced_config = {
            'mode': 'live',
            'exchange': force_exchange,
            'api_key': api_key,
            'secret_key': secret_key,
            'source': 'forced_exchange'
        }
        
        print(f"✅ Found {force_exchange} credentials in environment")
        print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
        print("   Secret Key: ***configured***")
        
        return forced_config
    
    # Force reconfiguration if requested
    if force_config or not wizard.has_existing_config():
        print("🔧 CONFIGURATION SETUP")
        if not wizard.has_existing_config():
            print("No configuration found - running setup wizard...")
        else:
            print("Reconfiguration requested...")
        
        return wizard.run_wizard()
    
    # Load existing configuration
    existing_config = wizard.load_existing_config()
    if existing_config:
        mode_name = "Demo Mode" if existing_config.get('mode') == 'demo' else "Live Data Mode"
        print(f"✅ Using saved configuration: {mode_name}")
        return existing_config
    
    # Fallback to wizard
    print("⚠️  Configuration file found but invalid - running setup wizard...")
    return wizard.run_wizard()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_command_line_args()
    
    # Validate mutually exclusive flags
    exclusive_flags = [args.demo, args.api_binance, args.api_bitunix]
    if sum(exclusive_flags) > 1:
        print("❌ ERROR: Cannot use multiple mode flags simultaneously")
        print("   Choose only one: --demo, --api-binance, or --api-bitunix")
        sys.exit(1)
    
    # Determine forced exchange if any
    force_exchange = None
    if args.api_binance:
        force_exchange = 'binance'
    elif args.api_bitunix:
        force_exchange = 'bitunix'
    
    # Setup configuration
    try:
        config = setup_configuration(
            force_demo=args.demo,
            force_config=args.config,
            force_exchange=force_exchange
        )
        
        print(f"\n🚀 Starting dashboard...")
        if config.get('mode') == 'demo':
            print("📊 Mode: Demo (simulated data)")
        else:
            exchange_name = config.get('exchange', 'unknown').title()
            print(f"📊 Mode: Live Data ({exchange_name})")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        print("Falling back to demo mode...")
        
        # Create emergency demo config
        from config.setup_wizard import ConfigurationWizard
        wizard = ConfigurationWizard()
        demo_config = {'mode': 'demo'}
        wizard.create_env_file(demo_config)
    
    # Start Flask application
    from config.settings import settings
    print(f"\n🌐 Dashboard starting at: http://{settings.flask_host}:{settings.flask_port}")
    print("📱 Open the above URL in your browser")
    print("🔊 Audio alerts are enabled by default")
    print("⚠️  Press Ctrl+C to stop the server")
    
    try:
        app.run(
            host=settings.flask_host, 
            port=settings.flask_port, 
            debug=settings.flask_debug
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
        sys.exit(1) 
#!/usr/bin/env python3
"""
PST NY Open Swing Trading Scanner
Focus: ADA, SOL, XRP (+ user's 4th choice)
Account Size: $2000
Risk Management: 1.5% risk per trade, 1:2 R/R
Trading Hours: NY Open (6:30-8:30 AM PST)
"""

import ccxt
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import pytz
import time
import warnings
warnings.filterwarnings('ignore')

class NYOpenSwingScanner:
    def __init__(self):
        # Account & Risk Management Settings
        self.ACCOUNT_SIZE = 2000
        self.RISK_PERCENT = 1.5  # 1.5% = $30 max loss per trade
        self.RISK_REWARD_RATIO = 2  # 1:2 Risk/Reward
        self.MAX_DAILY_TRADES = 3  # Prevent overtrading
        self.MAX_DAILY_RISK = 4.5  # 4.5% = $90 max daily loss
        
        # Trading Pairs - ADJUSTABLE
        self.COINS = [
            'ADA/USDT',
            'SOL/USDT', 
            'XRP/USDT',
            'AVAX/USDT'  # Solid L1 blockchain with good liquidity
        ]
        
        # Timeframes for analysis
        self.TIMEFRAMES = {
            'daily': '1d',
            'hourly': '1h', 
            'entry': '15m'
        }
        
        # NY Open Hours in PST
        self.pst = pytz.timezone('US/Pacific')
        self.ny_open_start = '06:30'  # 9:30 AM EST = 6:30 AM PST
        self.ny_open_end = '08:30'    # 11:30 AM EST = 8:30 AM PST
        
        # Technical Settings
        self.EMA_FAST = 20
        self.EMA_SLOW = 50
        self.ATR_PERIOD = 14
        self.VOLUME_THRESHOLD = 1.5  # 1.5x average volume
        
        # Initialize exchange
        self.exchange = ccxt.binance({
            'apiKey': 'your_api_key',  # Add later for live trading
            'secret': 'your_secret',   # Add later for live trading
            'sandbox': True,           # Use testnet initially
            'enableRateLimit': True,
        })
        
        print(f"🎯 NY Open Swing Scanner Initialized")
        print(f"💰 Account Size: ${self.ACCOUNT_SIZE}")
        print(f"⚠️  Max Risk Per Trade: ${self.ACCOUNT_SIZE * self.RISK_PERCENT / 100:.0f}")
        print(f"🎯 Target Profit Per Trade: ${self.ACCOUNT_SIZE * self.RISK_PERCENT / 100 * self.RISK_REWARD_RATIO:.0f}")
        print(f"⏰ Trading Window: {self.ny_open_start} - {self.ny_open_end} PST")
        print(f"📊 Watching: {', '.join(self.COINS)}")
    
    def is_ny_open_time(self):
        """Check if current time is within NY open trading window (PST)"""
        now = datetime.now(self.pst)
        current_time = now.strftime('%H:%M')
        
        return self.ny_open_start <= current_time <= self.ny_open_end
    
    def fetch_ohlcv_data(self, symbol, timeframe, limit=100):
        """Fetch OHLCV data for analysis"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Error fetching {symbol} {timeframe}: {e}")
            return None
    
    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period).mean()
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range for stop loss placement"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        return atr.iloc[-1]  # Return latest ATR
    
    def analyze_trend_confluence(self, symbol):
        """Analyze all timeframes for trend confluence"""
        analysis = {
            'symbol': symbol,
            'daily_trend': None,
            'hourly_trend': None,
            'entry_signal': None,
            'confluence': False,
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None,
            'position_size': None,
            'risk_amount': None
        }
        
        # Get data for all timeframes
        daily_df = self.fetch_ohlcv_data(symbol, self.TIMEFRAMES['daily'], 50)
        hourly_df = self.fetch_ohlcv_data(symbol, self.TIMEFRAMES['hourly'], 100)
        entry_df = self.fetch_ohlcv_data(symbol, self.TIMEFRAMES['entry'], 100)
        
        if daily_df is None or hourly_df is None or entry_df is None:
            return analysis
        
        # Calculate EMAs for each timeframe
        # Daily Analysis (Overall Bias)
        daily_df['ema20'] = self.calculate_ema(daily_df['close'], self.EMA_FAST)
        daily_df['ema50'] = self.calculate_ema(daily_df['close'], self.EMA_SLOW)
        daily_price = daily_df['close'].iloc[-1]
        daily_ema20 = daily_df['ema20'].iloc[-1]
        daily_ema50 = daily_df['ema50'].iloc[-1]
        
        if daily_price > daily_ema20 > daily_ema50:
            analysis['daily_trend'] = 'BULLISH'
        elif daily_price < daily_ema20 < daily_ema50:
            analysis['daily_trend'] = 'BEARISH'
        else:
            analysis['daily_trend'] = 'NEUTRAL'
        
        # Hourly Analysis (Setup)
        hourly_df['ema20'] = self.calculate_ema(hourly_df['close'], self.EMA_FAST)
        hourly_df['ema50'] = self.calculate_ema(hourly_df['close'], self.EMA_SLOW)
        hourly_price = hourly_df['close'].iloc[-1]
        hourly_ema20 = hourly_df['ema20'].iloc[-1]
        hourly_ema50 = hourly_df['ema50'].iloc[-1]
        
        if hourly_price > hourly_ema20 > hourly_ema50:
            analysis['hourly_trend'] = 'BULLISH'
        elif hourly_price < hourly_ema20 < hourly_ema50:
            analysis['hourly_trend'] = 'BEARISH'
        else:
            analysis['hourly_trend'] = 'NEUTRAL'
        
        # 15m Analysis (Entry Timing)
        entry_df['ema20'] = self.calculate_ema(entry_df['close'], self.EMA_FAST)
        entry_df['ema50'] = self.calculate_ema(entry_df['close'], self.EMA_SLOW)
        entry_price = entry_df['close'].iloc[-1]
        entry_ema20 = entry_df['ema20'].iloc[-1]
        entry_ema50 = entry_df['ema50'].iloc[-1]
        
        # Volume confirmation
        avg_volume = entry_df['volume'].rolling(20).mean().iloc[-1]
        current_volume = entry_df['volume'].iloc[-1]
        volume_spike = current_volume > (avg_volume * self.VOLUME_THRESHOLD)
        
        # Check for confluence and entry signals
        if analysis['daily_trend'] == 'BULLISH' and analysis['hourly_trend'] == 'BULLISH':
            # Look for bullish entry on 15m
            if entry_price > entry_ema20 and entry_ema20 > entry_ema50 and volume_spike:
                analysis['entry_signal'] = 'LONG'
                analysis['confluence'] = True
                analysis['entry_price'] = entry_price
                
                # Calculate stops and targets using ATR
                atr = self.calculate_atr(entry_df)
                analysis['stop_loss'] = entry_price - (atr * 1.5)  # 1.5 ATR stop
                analysis['take_profit'] = entry_price + (atr * 3)   # 1:2 R/R
                
        elif analysis['daily_trend'] == 'BEARISH' and analysis['hourly_trend'] == 'BEARISH':
            # Look for bearish entry on 15m
            if entry_price < entry_ema20 and entry_ema20 < entry_ema50 and volume_spike:
                analysis['entry_signal'] = 'SHORT'
                analysis['confluence'] = True
                analysis['entry_price'] = entry_price
                
                # Calculate stops and targets using ATR
                atr = self.calculate_atr(entry_df)
                analysis['stop_loss'] = entry_price + (atr * 1.5)  # 1.5 ATR stop
                analysis['take_profit'] = entry_price - (atr * 3)   # 1:2 R/R
        
        # Calculate position size if we have a signal
        if analysis['confluence'] and analysis['entry_price'] and analysis['stop_loss']:
            risk_per_trade = self.ACCOUNT_SIZE * (self.RISK_PERCENT / 100)
            
            if analysis['entry_signal'] == 'LONG':
                price_diff = analysis['entry_price'] - analysis['stop_loss']
            else:  # SHORT
                price_diff = analysis['stop_loss'] - analysis['entry_price']
            
            # Position size calculation
            analysis['position_size'] = risk_per_trade / price_diff
            analysis['risk_amount'] = risk_per_trade
        
        return analysis
    
    def format_signal_output(self, analysis):
        """Format trading signal for output"""
        if not analysis['confluence']:
            return None
        
        signal = f"""
🚨 {analysis['entry_signal']} SIGNAL: {analysis['symbol']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CONFLUENCE ANALYSIS:
   Daily Trend:  {analysis['daily_trend']}
   Hourly Setup: {analysis['hourly_trend']}
   Entry Signal: {analysis['entry_signal']}

💰 TRADE SETUP:
   Entry Price:  ${analysis['entry_price']:.4f}
   Stop Loss:    ${analysis['stop_loss']:.4f}
   Take Profit:  ${analysis['take_profit']:.4f}
   
💵 POSITION SIZING:
   Risk Amount:  ${analysis['risk_amount']:.2f}
   Position Size: {analysis['position_size']:.2f} {analysis['symbol'].split('/')[0]}
   
📈 RISK/REWARD:
   Risk: ${analysis['risk_amount']:.2f}
   Reward: ${analysis['risk_amount'] * self.RISK_REWARD_RATIO:.2f}
   R/R Ratio: 1:{self.RISK_REWARD_RATIO}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return signal
    
    def scan_for_signals(self):
        """Main scanning function"""
        print(f"\n🔍 Scanning at {datetime.now(self.pst).strftime('%Y-%m-%d %H:%M:%S PST')}")
        
        if not self.is_ny_open_time():
            print(f"⏰ Outside trading hours. NY Open: {self.ny_open_start}-{self.ny_open_end} PST")
            return
        
        signals_found = 0
        
        for symbol in self.COINS:
            print(f"📊 Analyzing {symbol}...")
            analysis = self.analyze_trend_confluence(symbol)
            
            if analysis['confluence']:
                signal_output = self.format_signal_output(analysis)
                print(signal_output)
                signals_found += 1
                
                # Log to file for record keeping
                with open('trading_signals.log', 'a') as f:
                    f.write(f"{datetime.now()} - {signal_output}\n")
            else:
                trend_status = f"Daily: {analysis['daily_trend']}, Hourly: {analysis['hourly_trend']}"
                print(f"   No confluence - {trend_status}")
        
        if signals_found == 0:
            print("❌ No confluence signals found this scan.")
        else:
            print(f"✅ Found {signals_found} confluence signal(s)!")
    
    def run_continuous_scan(self, scan_interval_minutes=5):
        """Run continuous scanning during NY open hours"""
        print(f"🚀 Starting continuous scanning every {scan_interval_minutes} minutes...")
        print(f"⏰ Active during: {self.ny_open_start}-{self.ny_open_end} PST")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.scan_for_signals()
                print(f"⏳ Next scan in {scan_interval_minutes} minutes...\n")
                time.sleep(scan_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Scanner stopped by user")

def main():
    """Main function"""
    print("🎯 PST NY Open Swing Trading Scanner")
    print("="*50)
    
    scanner = NYOpenSwingScanner()
    
    print("\nChoose scan mode:")
    print("1. Single scan now")
    print("2. Continuous scanning during NY open")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        scanner.scan_for_signals()
    elif choice == '2':
        scanner.run_continuous_scan()
    else:
        print("Invalid choice. Running single scan...")
        scanner.scan_for_signals()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
STAGE 2: STRATEGY EXECUTOR
Professional risk management for human-selected opportunities
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import json

class StrategyExecutor:
    def __init__(self, account_size=100000):
        self.ACCOUNT_SIZE = account_size
        self.RISK_PERCENT = 1.0  # 1% risk per trade
        self.RISK_REWARD_RATIO = 2.0  # 1:2 R/R
        
        # Multi-timeframe confluence
        self.TIMEFRAMES = {
            'weekly': '1w', 'daily': '1d', 'four_hour': '4h', 
            'hourly': '1h', 'entry': '15m'
        }
        
        self.EMA_FAST = 20
        self.EMA_SLOW = 50
        self.ATR_PERIOD = 14
        self.CONFLUENCE_THRESHOLD = 0.6  # 60% agreement needed
        
        # Initialize exchange
        try:
            self.exchange = ccxt.binance({
                'sandbox': False,
                'enableRateLimit': True,
            })
            print("✅ Exchange connected")
        except Exception as e:
            print(f"⚠️  Exchange warning: {e}")
            self.exchange = None
        
        print(f"🎯 STRATEGY EXECUTOR INITIALIZED")
        print(f"💰 Account: ${self.ACCOUNT_SIZE:,}")
        print(f"⚠️  Risk: ${self.ACCOUNT_SIZE * self.RISK_PERCENT / 100:,.0f} per trade")
    
    def fetch_timeframe_data(self, symbol, timeframe):
        """Fetch data for specific timeframe"""
        if not self.exchange:
            return None
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Error fetching {symbol} {timeframe}: {e}")
            return None
    
    def analyze_timeframe(self, df, timeframe_name):
        """Analyze single timeframe for trend"""
        if len(df) < self.EMA_SLOW:
            return {'trend': 'INSUFFICIENT_DATA', 'confidence': 0}
        
        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(span=self.EMA_FAST).mean()
        df['ema_slow'] = df['close'].ewm(span=self.EMA_SLOW).mean()
        
        # Calculate ATR for stops
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        df['atr'] = df['tr'].rolling(window=self.ATR_PERIOD).mean()
        
        latest = df.iloc[-1]
        price = latest['close']
        ema_fast = latest['ema_fast']
        ema_slow = latest['ema_slow']
        
        # Determine trend
        if price > ema_fast > ema_slow:
            trend = 'BULLISH'
            confidence = min(((price - ema_slow) / ema_slow) * 100, 100)
        elif price < ema_fast < ema_slow:
            trend = 'BEARISH'
            confidence = min(((ema_slow - price) / ema_slow) * 100, 100)
        else:
            trend = 'NEUTRAL'
            confidence = 0
        
        return {
            'timeframe': timeframe_name,
            'trend': trend,
            'confidence': confidence,
            'price': price,
            'atr': latest['atr'] if not pd.isna(latest['atr']) else 0
        }
    
    def multi_timeframe_confluence(self, symbol):
        """Analyze all timeframes for confluence"""
        print(f"📊 Multi-timeframe analysis: {symbol}")
        
        timeframe_analysis = {}
        
        for tf_name, tf_code in self.TIMEFRAMES.items():
            df = self.fetch_timeframe_data(symbol, tf_code)
            if df is not None:
                analysis = self.analyze_timeframe(df, tf_name)
                timeframe_analysis[tf_name] = analysis
                print(f"   {tf_name}: {analysis['trend']} ({analysis['confidence']:.1f}%)")
        
        # Calculate confluence
        bullish_count = sum(1 for tf in timeframe_analysis.values() if tf['trend'] == 'BULLISH')
        bearish_count = sum(1 for tf in timeframe_analysis.values() if tf['trend'] == 'BEARISH')
        total_timeframes = len(timeframe_analysis)
        
        if total_timeframes == 0:
            return None
        
        bullish_confluence = bullish_count / total_timeframes
        bearish_confluence = bearish_count / total_timeframes
        
        # Determine signal
        signal = None
        if bullish_confluence >= self.CONFLUENCE_THRESHOLD:
            signal = 'LONG'
        elif bearish_confluence >= self.CONFLUENCE_THRESHOLD:
            signal = 'SHORT'
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confluence_strength': max(bullish_confluence, bearish_confluence),
            'timeframe_analysis': timeframe_analysis,
            'bullish_timeframes': bullish_count,
            'total_timeframes': total_timeframes
        }
    
    def calculate_position_sizing(self, symbol, signal, entry_price, atr):
        """Calculate professional position sizing"""
        if not signal or not entry_price or not atr:
            return None
        
        risk_amount = self.ACCOUNT_SIZE * (self.RISK_PERCENT / 100)
        
        # ATR-based stops
        if signal == 'LONG':
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 3)  # 1:2 R/R
        else:  # SHORT
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 3)
        
        price_diff = abs(entry_price - stop_loss)
        if price_diff <= 0:
            return None
        
        position_size = risk_amount / price_diff
        profit_potential = risk_amount * self.RISK_REWARD_RATIO
        
        return {
            'signal': signal,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'risk_amount': risk_amount,
            'profit_potential': profit_potential
        }
    
    def execute_strategy(self, symbol):
        """Execute complete strategy analysis"""
        print(f"\n{'='*60}")
        print(f"🎯 EXECUTING STRATEGY: {symbol}")
        print(f"{'='*60}")
        
        confluence = self.multi_timeframe_confluence(symbol)
        if not confluence:
            print("❌ Unable to analyze confluence")
            return None
        
        print(f"\n📊 CONFLUENCE: {confluence['signal'] or 'NO SIGNAL'}")
        print(f"   Strength: {confluence['confluence_strength']:.1%}")
        print(f"   Agreement: {confluence['bullish_timeframes']}/{confluence['total_timeframes']} timeframes")
        
        if not confluence['signal']:
            print(f"❌ No signal - need {self.CONFLUENCE_THRESHOLD:.0%} agreement")
            return confluence
        
        # Get entry data for position sizing
        entry_df = self.fetch_timeframe_data(symbol, self.TIMEFRAMES['entry'])
        if entry_df is None:
            print("❌ No entry data available")
            return confluence
        
        entry_analysis = self.analyze_timeframe(entry_df, 'entry')
        
        position = self.calculate_position_sizing(
            symbol, 
            confluence['signal'], 
            entry_analysis['price'], 
            entry_analysis['atr']
        )
        
        if not position:
            print("❌ Unable to calculate position")
            return confluence
        
        print(f"\n🚨 SIGNAL: {position['signal']}")
        print(f"💰 Entry: ${position['entry_price']:.4f}")
        print(f"🛑 Stop: ${position['stop_loss']:.4f}")
        print(f"🎯 Target: ${position['take_profit']:.4f}")
        print(f"📊 Size: {position['position_size']:.4f} {symbol.split('/')[0]}")
        print(f"⚠️  Risk: ${position['risk_amount']:.2f}")
        print(f"💵 Target: ${position['profit_potential']:.2f}")
        
        confluence['position'] = position
        return confluence
    
    def load_opportunities(self):
        """Load Stage 1 opportunities"""
        try:
            with open('opportunities/latest_scan.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Run Stage 1 scanner first")
            return None
    
    def display_opportunities(self, opportunities):
        """Show available opportunities"""
        print("\n🔥 AVAILABLE OPPORTUNITIES:")
        print("="*50)
        
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{i:2d}. {opp['symbol']} - Score: {opp['score']:.0f}/100")
            print(f"     Price: ${opp['current_price']:.4f}")
        print()
    
    def interactive_selection(self):
        """Interactive opportunity selection"""
        opportunities = self.load_opportunities()
        if not opportunities:
            return
        
        self.display_opportunities(opportunities)
        
        selection = input("Select numbers (e.g., 1,3,5) or 'all': ").strip()
        
        if selection.lower() == 'all':
            selected = opportunities[:5]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected = [opportunities[i] for i in indices if 0 <= i < len(opportunities)]
            except:
                print("❌ Invalid selection")
                return
        
        results = []
        for opp in selected:
            result = self.execute_strategy(opp['symbol'])
            if result and result.get('signal'):
                results.append(result)
        
        if results:
            print(f"\n✅ Generated {len(results)} executable signals!")
        else:
            print("\n❌ No executable signals (confluence requirements not met)")

def main():
    try:
        account_size = float(input("Account size ($): ").strip())
    except:
        account_size = 100000
    
    executor = StrategyExecutor(account_size)
    executor.interactive_selection()

if __name__ == "__main__":
    main() 
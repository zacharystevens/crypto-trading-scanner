#!/usr/bin/env python3
"""
STAGE 1: OPPORTUNITY SCANNER
Multi-coin technical analysis to find the best trading opportunities
Combines FVG, trendlines, patterns, volume analysis with professional ranking
"""

import ccxt
import numpy as np
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import os
import warnings
warnings.filterwarnings('ignore')

class OpportunityScanner:
    def __init__(self):
        # Market Coverage - Cast wide net
        self.TOP_COINS = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
            'SOL/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT',
            'UNI/USDT', 'LTC/USDT', 'BCH/USDT', 'ATOM/USDT', 'FIL/USDT'
        ]
        
        # Technical Analysis Settings
        self.TIMEFRAMES = ['15m', '1h', '4h', '1d']
        self.PRIMARY_TIMEFRAME = '1h'  # Main analysis timeframe
        
        # FVG Detection Settings (restored from original)
        self.FVG_THRESHOLD = 0.005  # 0.5% minimum gap
        self.FVG_PROXIMITY = 0.02   # 2% proximity for alerts
        
        # Initialize exchange
        try:
            self.exchange = ccxt.binance({
                'sandbox': False,
                'enableRateLimit': True,
                'timeout': 10000,
            })
            print("✅ Exchange connected: Binance")
        except Exception as e:
            print(f"⚠️  Exchange connection warning: {e}")
            self.exchange = None
        
        # Create output directories
        os.makedirs('opportunities', exist_ok=True)
        os.makedirs('charts', exist_ok=True)
        
        print("🔍 OPPORTUNITY SCANNER INITIALIZED")
        print(f"📊 Scanning {len(self.TOP_COINS)} coins")
        print(f"🎯 Looking for: FVG setups, trendline breaks, patterns, volume spikes")
        print()
    
    def fetch_ohlcv_data(self, symbol, timeframe, limit=100):
        """Fetch OHLCV data with error handling"""
        if not self.exchange:
            return None
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"⚠️  Error fetching {symbol} {timeframe}: {e}")
            return None
    
    def detect_fair_value_gaps(self, df):
        """Detect Fair Value Gaps (original FVG logic restored)"""
        fvg_zones = []
        
        for i in range(1, len(df)):
            prev_high = df.iloc[i-1]['high']
            curr_low = df.iloc[i]['low']
            prev_low = df.iloc[i-1]['low'] 
            curr_high = df.iloc[i]['high']
            
            # Bullish FVG (gap up)
            if curr_low > prev_high:
                gap_size = (curr_low - prev_high) / prev_high
                if gap_size > self.FVG_THRESHOLD:
                    fvg_zones.append({
                        'type': 'BULLISH_FVG',
                        'gap_low': prev_high,
                        'gap_high': curr_low,
                        'gap_size': gap_size,
                        'strength': min(gap_size * 100, 10)
                    })
            
            # Bearish FVG (gap down)  
            elif curr_high < prev_low:
                gap_size = (prev_low - curr_high) / prev_low
                if gap_size > self.FVG_THRESHOLD:
                    fvg_zones.append({
                        'type': 'BEARISH_FVG',
                        'gap_low': curr_high,
                        'gap_high': prev_low,
                        'gap_size': gap_size,
                        'strength': min(gap_size * 100, 10)
                    })
        
        return fvg_zones
    
    def calculate_trendlines(self, df):
        """Calculate trendline using linear regression (original logic restored)"""
        if len(df) < 20:
            return None
        
        # Use last 20 periods for trendline calculation
        recent_df = df.tail(20).copy()
        recent_df.reset_index(drop=True, inplace=True)
        
        highs = recent_df['high'].values
        lows = recent_df['low'].values
        x = np.arange(len(recent_df))
        
        # Calculate trendlines
        slope_high, intercept_high, r_high, _, _ = linregress(x, highs)
        slope_low, intercept_low, r_low, _, _ = linregress(x, lows)
        
        # Current price vs trendlines
        current_price = df.iloc[-1]['close']
        current_x = len(recent_df) - 1
        
        resistance_level = slope_high * current_x + intercept_high
        support_level = slope_low * current_x + intercept_low
        
        # Detect breakouts
        resistance_break = current_price > resistance_level * 1.01
        support_break = current_price < support_level * 0.99
        
        return {
            'resistance_level': resistance_level,
            'support_level': support_level,
            'resistance_break': resistance_break,
            'support_break': support_break
        }
    
    def analyze_volume(self, df):
        """Analyze volume patterns"""
        if len(df) < 20:
            return {'volume_spike': False, 'volume_ratio': 1.0}
        
        df['volume_avg'] = df['volume'].rolling(window=20).mean()
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume_avg'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        return {
            'volume_spike': volume_ratio > 2.0,
            'volume_ratio': volume_ratio
        }
    
    def score_opportunity(self, analysis):
        """Score opportunity based on all factors"""
        score = 0
        
        # FVG Score (0-30 points)
        fvg_score = sum(fvg['strength'] for fvg in analysis['fvg_zones'])
        score += min(fvg_score * 3, 30)
        
        # Trendline Score (0-25 points)
        if analysis['trendlines']:
            if analysis['trendlines']['resistance_break'] or analysis['trendlines']['support_break']:
                score += 25
        
        # Volume Score (0-25 points)
        if analysis['volume']['volume_spike']:
            score += min(analysis['volume']['volume_ratio'] * 5, 25)
        
        # Price momentum (0-20 points)
        if len(analysis.get('price_data', [])) >= 5:
            recent_change = (analysis['price_data'][-1] - analysis['price_data'][-5]) / analysis['price_data'][-5]
            score += min(abs(recent_change) * 100, 20)
        
        return min(score, 100)
    
    def analyze_single_coin(self, symbol):
        """Complete analysis for a single coin"""
        print(f"🔍 Analyzing {symbol}...")
        
        # Fetch data
        df = self.fetch_ohlcv_data(symbol, self.PRIMARY_TIMEFRAME, 100)
        if df is None or len(df) < 50:
            print(f"❌ Insufficient data for {symbol}")
            return None
        
        # Perform all analysis
        analysis = {
            'symbol': symbol,
            'current_price': df['close'].iloc[-1],
            'fvg_zones': self.detect_fair_value_gaps(df),
            'trendlines': self.calculate_trendlines(df),
            'volume': self.analyze_volume(df),
            'price_data': df['close'].tolist()
        }
        
        # Calculate overall score
        analysis['score'] = self.score_opportunity(analysis)
        
        return analysis
    
    def scan_all_opportunities(self):
        """Scan all coins and rank opportunities"""
        print(f"🚀 SCANNING {len(self.TOP_COINS)} COINS FOR OPPORTUNITIES")
        print("="*60)
        
        opportunities = []
        
        for symbol in self.TOP_COINS:
            try:
                analysis = self.analyze_single_coin(symbol)
                if analysis:
                    opportunities.append(analysis)
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
    
    def display_top_opportunities(self, opportunities, top_n=10):
        """Display top opportunities in formatted output"""
        print(f"\n🔥 TOP {min(top_n, len(opportunities))} OPPORTUNITIES:")
        print("="*80)
        
        for i, opp in enumerate(opportunities[:top_n], 1):
            print(f"\n#{i}. {opp['symbol']} - Score: {opp['score']:.0f}/100")
            print(f"    💰 Current Price: ${opp['current_price']:.4f}")
            
            # FVG Summary
            if opp['fvg_zones']:
                fvg_count = len(opp['fvg_zones'])
                strongest_fvg = max(opp['fvg_zones'], key=lambda x: x['strength'])
                print(f"    📊 FVG: {fvg_count} zones, strongest {strongest_fvg['type']} ({strongest_fvg['gap_size']:.1%})")
            
            # Trendline Summary
            if opp['trendlines']:
                tl = opp['trendlines']
                if tl['resistance_break']:
                    print(f"    📈 RESISTANCE BREAKOUT at ${tl['resistance_level']:.4f}")
                if tl['support_break']:
                    print(f"    📉 SUPPORT BREAKDOWN at ${tl['support_level']:.4f}")
            
            # Volume Summary
            if opp['volume']['volume_spike']:
                print(f"    🔊 Volume: {opp['volume']['volume_ratio']:.1f}x average (SPIKE)")

def main():
    """Main scanning function"""
    print("🔍 OPPORTUNITY SCANNER - STAGE 1")
    print("="*50)
    print("Finding the best trading opportunities across the market")
    print()
    
    scanner = OpportunityScanner()
    
    print("Choose scan mode:")
    print("1. Full market scan")
    print("2. Quick scan (top 10)")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == '1':
        opportunities = scanner.scan_all_opportunities()
    else:
        scanner.TOP_COINS = scanner.TOP_COINS[:10]
        opportunities = scanner.scan_all_opportunities()
    
    scanner.display_top_opportunities(opportunities)
    
    # Save for Stage 2
    with open('opportunities/latest_scan.json', 'w') as f:
        json.dump(opportunities, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to opportunities/latest_scan.json")
    print("🎯 Ready for Stage 2: Human selection and strategy execution")

if __name__ == "__main__":
    main() 
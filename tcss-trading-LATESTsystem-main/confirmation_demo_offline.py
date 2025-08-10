#!/usr/bin/env python3
"""
CONFIRMATION CANDLE SYSTEM DEMO (OFFLINE VERSION)
Demonstrates the 5-minute candle confirmation system with simulated data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from confirmation_candles import ConfirmationCandleSystem

class MockExchange:
    """Mock exchange for demo purposes"""
    
    def fetch_ohlcv(self, symbol, timeframe, limit=20):
        """Generate simulated 5-minute candle data"""
        if timeframe != '5m':
            return []
        
        # Generate realistic candle data
        base_price = 50000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 0.5
        
        data = []
        current_time = datetime.now() - timedelta(minutes=limit * 5)
        
        for i in range(limit):
            # Simulate price movement
            price_change = np.random.normal(0, base_price * 0.01)  # 1% volatility
            open_price = base_price + price_change
            
            # Generate high, low, close
            high = open_price + abs(np.random.normal(0, base_price * 0.005))
            low = open_price - abs(np.random.normal(0, base_price * 0.005))
            close = np.random.uniform(low, high)
            
            # Generate volume
            volume = np.random.uniform(1000, 5000)
            
            # Add some bullish/bearish bias for demo
            if i >= limit - 4:  # Last 4 candles for confirmation demo
                if 'LONG' in symbol:  # Simulate bullish confirmation
                    close = open_price + abs(np.random.normal(0, base_price * 0.003))
                    high = max(high, close)
                elif 'SHORT' in symbol:  # Simulate bearish confirmation
                    close = open_price - abs(np.random.normal(0, base_price * 0.003))
                    low = min(low, close)
            
            data.append([
                int(current_time.timestamp() * 1000),  # timestamp in ms
                open_price,
                high,
                low,
                close,
                volume
            ])
            
            current_time += timedelta(minutes=5)
            base_price = close  # Use close as next open
        
        return data

def main():
    print("🔍 CONFIRMATION CANDLE SYSTEM DEMO (OFFLINE)")
    print("=" * 60)
    
    # Initialize mock exchange
    mock_exchange = MockExchange()
    print("✅ Mock exchange initialized")
    
    # Initialize confirmation system
    confirmation_system = ConfirmationCandleSystem(mock_exchange)
    print("✅ Confirmation system initialized")
    
    # Test symbols with different scenarios
    test_scenarios = [
        ('BTC/USDT_LONG', 'LONG', 50000),   # Bullish confirmation
        ('BTC/USDT_SHORT', 'SHORT', 50000), # Bearish confirmation
        ('ETH/USDT_LONG', 'LONG', 3000),    # Another bullish
        ('ETH/USDT_SHORT', 'SHORT', 3000)   # Another bearish
    ]
    
    for symbol, direction, signal_price in test_scenarios:
        print(f"\n📊 Testing {symbol}")
        print("-" * 40)
        
        # Simulate a signal
        signal_time = datetime.now() - timedelta(minutes=15)  # Signal 15 minutes ago
        
        print(f"🎯 Testing {direction} signal:")
        print(f"   Signal Price: ${signal_price:,.2f}")
        print(f"   Signal Time: {signal_time.strftime('%H:%M:%S')}")
        
        # Get confirmation summary
        summary = confirmation_system.get_confirmation_summary(
            symbol, direction, signal_price, signal_time
        )
        
        print(f"\n📊 Confirmation Results:")
        print(f"   Symbol: {summary['symbol']}")
        print(f"   Direction: {summary['direction']}")
        print(f"   Confirmed: {summary['confirmed']}")
        print(f"   Confidence: {summary['confidence']:.1f}%")
        print(f"   Recommendation: {summary['recommendation']}")
        
        if summary['details'] != "Insufficient data":
            print(f"\n📝 Detailed Analysis:")
            print(summary['details'])
        else:
            print(f"\n📝 Details: {summary['details']}")
        
        # Test manual confirmation check
        confirmed, confidence, details = confirmation_system.check_confirmation(
            symbol, direction, signal_price, signal_time
        )
        
        print(f"\n🔍 Manual Check Results:")
        print(f"   - Confirmed: {confirmed}")
        print(f"   - Confidence: {confidence:.1f}%")
        if details != "Insufficient data":
            print(f"   - Details:\n{details}")
        else:
            print(f"   - Details: {details}")
        
        print("\n" + "=" * 60)
    
    # Test pending confirmations
    print("\n⏰ Testing Pending Confirmations:")
    print("-" * 40)
    
    # Add some test signals to cache
    test_signals = [
        {'symbol': 'BTC/USDT', 'direction': 'LONG', 'signal_price': 50000, 'signal_time': datetime.now() - timedelta(minutes=5)},
        {'symbol': 'ETH/USDT', 'direction': 'SHORT', 'signal_price': 3000, 'signal_time': datetime.now() - timedelta(minutes=12)},
        {'symbol': 'ADA/USDT', 'direction': 'LONG', 'signal_price': 0.5, 'signal_time': datetime.now() - timedelta(minutes=20)}
    ]
    
    for signal in test_signals:
        confirmation_system.update_confirmation_cache(
            signal['symbol'],
            signal['direction'],
            signal['signal_price'],
            signal['signal_time']
        )
        print(f"   Added signal: {signal['symbol']} {signal['direction']} at {signal['signal_time'].strftime('%H:%M:%S')}")
    
    # Get pending confirmations
    pending = confirmation_system.get_pending_confirmations()
    print(f"\n📋 Found {len(pending)} pending confirmations:")
    
    for signal in pending:
        time_since = (datetime.now() - signal['signal_time']).total_seconds() / 60
        print(f"   - {signal['symbol']} {signal['direction']}: {time_since:.1f} minutes ago")
    
    # Demonstrate confirmation criteria
    print(f"\n📋 Confirmation Criteria Summary:")
    print("-" * 40)
    print("For LONG signals:")
    print("   ✓ Bullish candle (close > open)")
    print("   ✓ Strong body (body ratio > 60%)")
    print("   ✓ High volume (>120% of average)")
    print("   ✓ Price above signal price")
    print("\nFor SHORT signals:")
    print("   ✓ Bearish candle (close < open)")
    print("   ✓ Strong body (body ratio > 60%)")
    print("   ✓ High volume (>120% of average)")
    print("   ✓ Price below signal price")
    print("\nScoring: 0-4 points per candle, 60% threshold for confirmation")
    
    print("\n✅ Offline demo completed!")
    print("\n💡 This demo shows how the confirmation system:")
    print("   - Analyzes 5-minute candles after signals")
    print("   - Scores confirmation criteria")
    print("   - Provides detailed feedback")
    print("   - Tracks pending confirmations")
    print("   - Reduces false signals")

if __name__ == "__main__":
    main()

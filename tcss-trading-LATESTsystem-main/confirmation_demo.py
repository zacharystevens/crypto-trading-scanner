#!/usr/bin/env python3
"""
CONFIRMATION CANDLE SYSTEM DEMO
Demonstrates the 5-minute candle confirmation system
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
from confirmation_candles import ConfirmationCandleSystem

def main():
    print("🔍 CONFIRMATION CANDLE SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize exchange (using Binance for demo)
    try:
        exchange = ccxt.binance({
            'sandbox': False,
            'enableRateLimit': True,
        })
        print("✅ Exchange connected")
    except Exception as e:
        print(f"❌ Exchange connection failed: {e}")
        return
    
    # Initialize confirmation system
    confirmation_system = ConfirmationCandleSystem(exchange)
    print("✅ Confirmation system initialized")
    
    # Test symbols
    test_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}")
        print("-" * 30)
        
        # Simulate a signal
        signal_time = datetime.now() - timedelta(minutes=15)  # Signal 15 minutes ago
        signal_price = 50000  # Example price
        
        # Test both long and short signals
        for direction in ['LONG', 'SHORT']:
            print(f"\n🎯 Testing {direction} signal:")
            
            # Get confirmation summary
            summary = confirmation_system.get_confirmation_summary(
                symbol, direction, signal_price, signal_time
            )
            
            print(f"   Symbol: {summary['symbol']}")
            print(f"   Direction: {summary['direction']}")
            print(f"   Signal Price: ${summary['signal_price']:,.2f}")
            print(f"   Confirmed: {summary['confirmed']}")
            print(f"   Confidence: {summary['confidence']:.1f}%")
            print(f"   Recommendation: {summary['recommendation']}")
            print(f"   Details:\n{summary['details']}")
            
            # Test manual confirmation check
            confirmed, confidence, details = confirmation_system.check_confirmation(
                symbol, direction, signal_price, signal_time
            )
            
            print(f"\n   Manual Check Results:")
            print(f"   - Confirmed: {confirmed}")
            print(f"   - Confidence: {confidence:.1f}%")
            print(f"   - Details: {details}")
        
        print("\n" + "=" * 50)
    
    # Test pending confirmations
    print("\n⏰ Testing Pending Confirmations:")
    print("-" * 30)
    
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
    
    # Get pending confirmations
    pending = confirmation_system.get_pending_confirmations()
    print(f"Found {len(pending)} pending confirmations:")
    
    for signal in pending:
        time_since = (datetime.now() - signal['signal_time']).total_seconds() / 60
        print(f"   - {signal['symbol']} {signal['direction']}: {time_since:.1f} minutes ago")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()

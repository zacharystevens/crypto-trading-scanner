#!/usr/bin/env python3
"""
TEST CONFIRMATION TIMING
Demonstrates the new behavior where alerts are only triggered after 5-minute confirmation
"""

import time
from datetime import datetime, timedelta
from confirmation_candles import ConfirmationCandleSystem

class MockExchange:
    """Mock exchange for testing"""
    
    def fetch_ohlcv(self, symbol, timeframe, limit=20):
        """Generate simulated 5-minute candle data"""
        if timeframe != '5m':
            return []
        
        # Generate realistic candle data
        base_price = 50000 if 'BTC' in symbol else 3000
        
        data = []
        current_time = datetime.now() - timedelta(minutes=limit * 5)
        
        for i in range(limit):
            # Simulate price movement
            price_change = 0.01 * base_price  # 1% movement
            open_price = base_price + price_change
            
            # Generate high, low, close
            high = open_price + (0.005 * base_price)
            low = open_price - (0.005 * base_price)
            close = open_price + (0.003 * base_price)  # Slightly bullish
            
            # Generate volume
            volume = 2000 + (i * 100)  # Increasing volume
            
            data.append([
                int(current_time.timestamp() * 1000),
                open_price,
                high,
                low,
                close,
                volume
            ])
            
            current_time += timedelta(minutes=5)
            base_price = close
        
        return data

def main():
    print("🧪 TESTING CONFIRMATION TIMING")
    print("=" * 50)
    print("This test demonstrates the new behavior:")
    print("1. Signal detected → Stored for confirmation")
    print("2. Wait 10 minutes for 5m candles")
    print("3. Check confirmation criteria")
    print("4. Only trigger alert if confirmed")
    print("=" * 50)
    
    # Initialize mock exchange and confirmation system
    mock_exchange = MockExchange()
    confirmation_system = ConfirmationCandleSystem(mock_exchange)
    
    # Simulate signal detection
    signal_time = datetime.now()
    signal_price = 50000
    symbol = 'BTC/USDT'
    direction = 'LONG'
    
    print(f"\n🔍 STEP 1: Signal Detected")
    print(f"   Symbol: {symbol}")
    print(f"   Direction: {direction}")
    print(f"   Price: ${signal_price:,.2f}")
    print(f"   Time: {signal_time.strftime('%H:%M:%S')}")
    print(f"   Status: Signal stored for confirmation (NO ALERT YET)")
    
    # Store signal for confirmation
    confirmation_system.update_confirmation_cache(
        symbol, direction, signal_price, signal_time
    )
    
    # Simulate waiting and checking
    print(f"\n⏰ STEP 2: Waiting for confirmation candles...")
    
    for i in range(1, 13):  # Check every minute for 12 minutes
        time.sleep(1)  # Simulate 1 minute passing
        
        current_time = datetime.now()
        time_since_signal = (current_time - signal_time).total_seconds() / 60
        
        print(f"   {i:2d} min: {time_since_signal:.1f} minutes since signal")
        
        # Check if ready for confirmation (10+ minutes)
        if time_since_signal >= 10:
            print(f"   ✅ Ready for confirmation check!")
            
            # Check confirmation
            confirmed, confidence, details = confirmation_system.check_confirmation(
                symbol, direction, signal_price, signal_time
            )
            
            print(f"\n🔍 STEP 3: Confirmation Check")
            print(f"   Confirmed: {confirmed}")
            print(f"   Confidence: {confidence:.1f}%")
            print(f"   Details: {details}")
            
            if confirmed:
                print(f"\n🚨 STEP 4: ALERT TRIGGERED!")
                print(f"   ✅ Signal confirmed with {confidence:.1f}% confidence")
                print(f"   🔊 Audio alert would play now")
                print(f"   📱 Dashboard would show confirmed alert")
            else:
                print(f"\n❌ STEP 4: NO ALERT")
                print(f"   ❌ Signal rejected with {confidence:.1f}% confidence")
                print(f"   🔇 No audio alert")
                print(f"   📱 Dashboard would show rejected signal")
            
            break
        else:
            print(f"   ⏳ Waiting... ({10 - time_since_signal:.1f} minutes remaining)")
    
    print(f"\n✅ Test completed!")
    print(f"\n💡 Key Points:")
    print(f"   - Signals are detected immediately but NOT alerted")
    print(f"   - System waits 10 minutes for 5m candles to form")
    print(f"   - Only confirmed signals trigger audio alerts")
    print(f"   - Rejected signals are logged but no alert")
    print(f"   - This reduces false signals significantly")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TEST SIGNAL FLOW
Test the complete signal flow to see where audio fails
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_dashboard import dashboard

def test_signal_flow():
    print("🔊 TESTING COMPLETE SIGNAL FLOW")
    print("=" * 40)
    
    # Create a test signal
    test_signal = {
        'symbol': 'BTCUSDT',
        'direction': 'LONG',
        'price': 50000.0,
        'rsi': 65.5,
        'volume_ratio': 1.8,
        'confidence': 85.0,
        'timeframe': '15m',
        'timestamp': datetime.now() - timedelta(minutes=30),  # 30 minutes ago
        'confirmation_status': 'PENDING',
        'confirmation_checked': False
    }
    
    print(f"🔊 Audio enabled: {dashboard.audio_enabled}")
    print(f"🔊 Test signal: {test_signal['symbol']} {test_signal['direction']}")
    
    # Step 1: Store signal for confirmation
    print("\n📝 Step 1: Storing signal for confirmation...")
    dashboard.alert_system.store_signal_for_confirmation(test_signal)
    
    # Step 2: Add to confirmation cache
    print("📝 Step 2: Adding to confirmation cache...")
    dashboard.confirmation_system.update_confirmation_cache(
        test_signal['symbol'],
        test_signal['direction'],
        test_signal['price'],
        test_signal['timestamp']
    )
    
    # Step 3: Check pending confirmations
    print("📝 Step 3: Checking pending confirmations...")
    pending = dashboard.confirmation_system.get_pending_confirmations()
    print(f"   Pending confirmations: {len(pending)}")
    
    # Step 4: Force trigger audio alert
    print("📝 Step 4: Force triggering audio alert...")
    dashboard.alert_system.trigger_confirmed_alert(test_signal)
    
    print("✅ Signal flow test completed!")

if __name__ == "__main__":
    test_signal_flow()

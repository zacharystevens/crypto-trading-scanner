#!/usr/bin/env python3
"""
FORCE AUDIO TEST
Force trigger an audio alert to test if it works
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_dashboard import dashboard

def force_audio_test():
    print("🔊 FORCE AUDIO TEST")
    print("=" * 30)
    
    # Create a test signal
    test_signal = {
        'symbol': 'BTCUSDT',
        'direction': 'LONG',
        'price': 50000.0,
        'rsi': 65.5,
        'volume_ratio': 1.8,
        'confidence': 85.0,
        'timeframe': '15m',
        'timestamp': datetime.now(),
        'confirmation_confidence': 95.0,
        'confirmation_details': 'Force test confirmation'
    }
    
    print(f"🔊 Audio enabled: {dashboard.audio_enabled}")
    print(f"🔊 Test signal: {test_signal['symbol']} {test_signal['direction']}")
    
    # Force trigger the audio alert
    print("🔊 Force triggering audio alert...")
    dashboard.alert_system.trigger_confirmed_alert(test_signal)
    
    print("✅ Force audio test completed!")

if __name__ == "__main__":
    force_audio_test()

#!/usr/bin/env python3
"""
AUDIO ALERT TEST
Test the actual audio alert system from the trading dashboard
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_dashboard import dashboard

def test_audio_alert():
    print("🔊 Testing Audio Alert System")
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
        'timestamp': datetime.now(),
        'confirmation_confidence': 92.0,
        'confirmation_details': 'Strong bullish confirmation'
    }
    
    print(f"🔊 Audio enabled: {dashboard.audio_enabled}")
    print(f"🔊 Test signal: {test_signal['symbol']} {test_signal['direction']}")
    
    # Force trigger the audio alert
    print("🔊 Triggering audio alert...")
    dashboard.alert_system.trigger_confirmed_alert(test_signal)
    
    print("✅ Audio alert test completed!")

if __name__ == "__main__":
    test_audio_alert()

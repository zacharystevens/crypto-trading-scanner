#!/usr/bin/env python3
"""
AUDIO TEST
Simple test to verify audio is working
"""

import winsound
import time

def test_audio():
    print("🔊 Testing Audio System")
    print("=" * 30)
    
    try:
        print("🔊 Playing test beep...")
        winsound.Beep(800, 500)  # 800Hz for 500ms
        print("✅ Audio test successful!")
        
        print("🔊 Playing second beep...")
        winsound.Beep(400, 500)  # 400Hz for 500ms
        print("✅ Second audio test successful!")
        
        print("🔊 Testing alert sounds...")
        # Test the same frequencies used in the trading system
        winsound.Beep(800, 500)  # BULLISH frequency
        time.sleep(0.1)
        winsound.Beep(800, 500)
        
        time.sleep(1)
        
        winsound.Beep(400, 500)  # BEARISH frequency
        time.sleep(0.1)
        winsound.Beep(400, 500)
        
        print("✅ All audio tests passed!")
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        print("🔧 Possible solutions:")
        print("   - Check if speakers are connected")
        print("   - Check if volume is turned up")
        print("   - Check if Windows audio is working")

if __name__ == "__main__":
    test_audio()

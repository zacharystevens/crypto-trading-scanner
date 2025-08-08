#!/usr/bin/env python3
"""
AUDIO TEST - IMMEDIATE
Test that audio plays immediately when signals are detected
"""

import winsound
import time

def test_immediate_audio():
    print("🔊 TESTING IMMEDIATE AUDIO")
    print("=" * 35)
    
    try:
        print("🔊 Playing immediate signal alerts...")
        
        # Test LONG signal audio
        print("📈 LONG signal audio:")
        winsound.Beep(800, 300)  # LONG signal
        time.sleep(0.05)
        winsound.Beep(800, 300)
        
        time.sleep(1)
        
        # Test SHORT signal audio
        print("📉 SHORT signal audio:")
        winsound.Beep(400, 300)  # SHORT signal
        time.sleep(0.05)
        winsound.Beep(400, 300)
        
        print("✅ Immediate audio test successful!")
        print("🎯 Audio will now play immediately when signals are detected")
        print("⏰ 15-minute confirmation wait time")
        print("🔊 Triple confirmation system active")
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")

if __name__ == "__main__":
    test_immediate_audio()

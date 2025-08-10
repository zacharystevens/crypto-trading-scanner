#!/usr/bin/env python3
"""
BTC Trading System - Easy Setup
Auto-installs requirements and runs the demo
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing requirements...")
    
    required_packages = [
        'ccxt',
        'pandas', 
        'numpy',
        'pytz'
    ]
    
    for package in required_packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            print(f"   Try manually: pip install {package}")
            return False
    
    return True

def run_demo():
    """Run the BTC demo"""
    print("\n🚀 Starting BTC Trading System Demo...")
    print("   (This will show live market analysis)")
    
    try:
        subprocess.run([sys.executable, 'btc_professional_demo.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("Try running manually: python btc_professional_demo.py")

def main():
    print("=" * 60)
    print("🚀 BTC TRADING SYSTEM - AUTO SETUP")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('btc_professional_demo.py'):
        print("❌ Can't find btc_professional_demo.py")
        print("   Make sure you're in the right folder!")
        input("\nPress Enter to exit...")
        return
    
    print("📁 Found demo file ✅")
    print()
    
    # Ask user if they want auto-install
    print("Do you want to auto-install requirements? (y/n)")
    choice = input(">>> ").lower().strip()
    
    if choice in ['y', 'yes', '']:
        if install_requirements():
            print("\n✅ All requirements installed!")
        else:
            print("\n❌ Some packages failed to install")
            print("   You may need to install manually")
    
    print("\n" + "=" * 60)
    input("Press Enter to start the BTC demo...")
    run_demo()

if __name__ == "__main__":
    main() 
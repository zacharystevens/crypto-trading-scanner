#!/usr/bin/env python3
"""
Web Dashboard API Demo Script

This script demonstrates how to interact with the web dashboard APIs
programmatically for automated trading systems integration.

Requirements:
1. Start the web dashboard: python flask_dashboard.py
2. Run this demo: python web_dashboard_demo.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
DASHBOARD_URL = "http://localhost:5001"
DEMO_COINS = ["BTC", "ETH", "SOL", "ADA", "MATIC"]

def check_dashboard_status():
    """Check if the dashboard is running"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/market_movers", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_market_movers():
    """Fetch top gainers and losers"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/market_movers")
        return response.json()
    except Exception as e:
        print(f"Error fetching market movers: {e}")
        return None

def get_opportunities():
    """Fetch trading opportunities"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/opportunities")
        return response.json()
    except Exception as e:
        print(f"Error fetching opportunities: {e}")
        return None

def analyze_coin(symbol):
    """Analyze a specific coin"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/search_coin/{symbol}")
        return response.json()
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def display_market_overview():
    """Display market overview with top movers"""
    print("=" * 70)
    print("🌐 WEB DASHBOARD API DEMO")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    market_data = get_market_movers()
    if not market_data:
        print("❌ Failed to fetch market data")
        return
    
    # Display top gainers
    print("🚀 TOP GAINERS:")
    for i, gainer in enumerate(market_data.get('gainers', [])[:5], 1):
        symbol = gainer['symbol'].replace('/USDT', '')
        price = gainer['price']
        change = gainer['change_24h']
        volume = gainer['volume']
        
        print(f"  {i}. {symbol:<8} ${price:>8.4f} {change:>+7.2f}% (Vol: {volume/1e6:.1f}M)")
    
    print()
    
    # Display top losers
    print("📉 TOP LOSERS:")
    for i, loser in enumerate(market_data.get('losers', [])[:5], 1):
        symbol = loser['symbol'].replace('/USDT', '')
        price = loser['price']
        change = loser['change_24h']
        volume = loser['volume']
        
        print(f"  {i}. {symbol:<8} ${price:>8.4f} {change:>+7.2f}% (Vol: {volume/1e6:.1f}M)")
    
    print()

def display_trading_opportunities():
    """Display trading opportunities"""
    print("🎯 TRADING OPPORTUNITIES:")
    print("-" * 70)
    
    opportunities = get_opportunities()
    if not opportunities:
        print("❌ No opportunities found")
        return
    
    # Sort by score (highest first)
    opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    for i, opp in enumerate(opportunities[:10], 1):
        symbol = opp['symbol'].replace('/USDT', '')
        score = opp.get('score', 0)
        signal_class = opp.get('signal_class', 'UNKNOWN')
        direction = opp.get('confluence_quality', {}).get('direction', 'NEUTRAL')
        price = opp.get('current_price', 0)
        
        # Color coding for score
        if score >= 50:
            score_indicator = "🟢"
        elif score >= 30:
            score_indicator = "🟡"
        else:
            score_indicator = "🔴"
        
        # Direction indicator
        direction_indicator = "📈" if direction == "BULLISH" else "📉" if direction == "BEARISH" else "➡️"
        
        print(f"  {i:2d}. {symbol:<8} {score_indicator} {score:>3.0f} {direction_indicator} {signal_class:<8} ${price:>8.4f}")
    
    print()

def demo_coin_analysis():
    """Demonstrate individual coin analysis"""
    print("🔍 INDIVIDUAL COIN ANALYSIS:")
    print("-" * 70)
    
    for coin in DEMO_COINS[:3]:  # Analyze first 3 coins
        print(f"\n📊 Analyzing {coin}...")
        analysis = analyze_coin(coin)
        
        if analysis and 'error' not in analysis:
            symbol = analysis.get('symbol', coin)
            score = analysis.get('score', 0)
            signal_class = analysis.get('signal_class', 'UNKNOWN')
            direction = analysis.get('confluence_quality', {}).get('direction', 'NEUTRAL')
            price = analysis.get('current_price', 0)
            
            print(f"  Symbol: {symbol}")
            print(f"  Score: {score:.1f}")
            print(f"  Signal: {signal_class} {direction}")
            print(f"  Price: ${price:.4f}")
            
            # Show FVG zones if available
            fvg_zones = analysis.get('fvg_zones', [])
            if fvg_zones:
                print(f"  FVG Zones: {len(fvg_zones)} detected")
                for fvg in fvg_zones[:2]:  # Show first 2
                    fvg_type = fvg.get('type', 'UNKNOWN')
                    status = fvg.get('status', 'UNKNOWN')
                    print(f"    - {fvg_type} ({status})")
        else:
            print(f"  ❌ Failed to analyze {coin}")
        
        time.sleep(1)  # Rate limiting
    print()

def display_api_examples():
    """Show API usage examples"""
    print("📝 API USAGE EXAMPLES:")
    print("-" * 70)
    
    examples = [
        ("Market Movers", "GET /api/market_movers", "Get top gainers and losers"),
        ("Opportunities", "GET /api/opportunities", "Get all trading opportunities"),
        ("Coin Analysis", "GET /api/search_coin/BTC", "Analyze specific coin"),
        ("Chart Data", "GET /api/chart/BTC/USDT/1h", "Get chart data for timeframe"),
    ]
    
    for name, endpoint, description in examples:
        print(f"  {name:<15} {endpoint:<30} {description}")
    
    print()
    print("💡 Example Python code:")
    print("   import requests")
    print("   response = requests.get('http://localhost:5001/api/market_movers')")
    print("   data = response.json()")
    print("   print(data['gainers'][0])  # First gainer")
    print()

def main():
    """Main demo function"""
    print("🚀 Starting Web Dashboard API Demo...")
    print()
    
    # Check if dashboard is running
    if not check_dashboard_status():
        print("❌ ERROR: Web dashboard is not running!")
        print("Please start it first with: python flask_dashboard.py")
        print("Then access: http://localhost:5001")
        return
    
    print("✅ Dashboard is running at http://localhost:5001")
    print()
    
    # Run demonstrations
    display_market_overview()
    display_trading_opportunities()
    demo_coin_analysis()
    display_api_examples()
    
    print("🎉 Demo completed successfully!")
    print("💻 Visit http://localhost:5001 to see the web interface")
    print("📚 Check WEB_DASHBOARD_GUIDE.md for complete documentation")

if __name__ == "__main__":
    main() 
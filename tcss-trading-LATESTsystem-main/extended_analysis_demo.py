#!/usr/bin/env python3
"""
Extended Analysis Demo
Test the new extended analysis functionality with throttling
"""

from opportunity_scanner import OpportunityScanner
import time

def main():
    print("🚀 Extended Analysis Demo")
    print("=" * 50)
    
    scanner = OpportunityScanner()
    
    # Show analysis statistics first
    curated_data = scanner.get_curated_30_coins()
    all_symbols = scanner.get_all_usdt_symbols()
    remaining_count = len(all_symbols) - len(curated_data['all_symbols'])
    
    print(f"📊 Analysis Overview:")
    print(f"   • Curated coins: {len(curated_data['all_symbols'])}")
    print(f"   • Remaining coins: {remaining_count}")
    print(f"   • Total available: {len(all_symbols)}")
    print(f"   • Estimated extended time: {round(remaining_count * 30 / 3600, 1)} hours")
    print()
    
    # Option 1: Quick curated analysis
    print("🎯 Option 1: Quick Curated Analysis (30 coins)")
    print("-" * 30)
    start_time = time.time()
    curated_opportunities = scanner.scan_all_opportunities(scan_type='curated_30')
    curated_time = time.time() - start_time
    
    print(f"✅ Curated analysis complete in {curated_time:.1f} seconds")
    print(f"🔥 Found {len(curated_opportunities)} opportunities from curated coins")
    
    # Show top 5 curated opportunities
    curated_opportunities.sort(key=lambda x: x['score'], reverse=True)
    print(f"\n🏆 Top 5 Curated Opportunities:")
    for i, opp in enumerate(curated_opportunities[:5], 1):
        signal_class = opp.get('signal_class', 'UNKNOWN')
        direction = opp.get('confluence_quality', {}).get('direction', 'NEUTRAL')
        print(f"   {i}. {opp['symbol']:12} - {signal_class:8} {direction:7} (Score: {opp['score']:.0f})")
    
    print()
    
    # Option 2: Extended analysis (ask user first due to time)
    print("⚠️  Option 2: Extended Analysis (All Remaining Coins)")
    print("-" * 40)
    print(f"This will analyze {remaining_count} additional coins")
    print(f"Estimated time: {round(remaining_count * 30 / 60, 0)} minutes")
    print("Each coin waits 30 seconds to avoid API rate limits")
    
    response = input("\nDo you want to run extended analysis? (y/N): ").strip().lower()
    
    if response == 'y':
        print(f"\n🔍 Starting extended analysis...")
        print("💡 You can stop anytime with Ctrl+C")
        
        try:
            start_time = time.time()
            extended_opportunities = scanner.scan_all_opportunities(scan_type='extended_all')
            extended_time = time.time() - start_time
            
            print(f"\n✅ Extended analysis complete in {extended_time/60:.1f} minutes")
            print(f"🔥 Found {len(extended_opportunities)} additional opportunities")
            
            # Combine results
            all_opportunities = curated_opportunities + extended_opportunities
            all_opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"\n📈 COMBINED RESULTS:")
            print(f"   • Total opportunities: {len(all_opportunities)}")
            print(f"   • From curated coins: {len(curated_opportunities)}")
            print(f"   • From extended analysis: {len(extended_opportunities)}")
            
            print(f"\n🏆 Top 10 Overall Opportunities:")
            for i, opp in enumerate(all_opportunities[:10], 1):
                signal_class = opp.get('signal_class', 'UNKNOWN')
                direction = opp.get('confluence_quality', {}).get('direction', 'NEUTRAL')
                source = "Curated" if opp['symbol'] in curated_data['all_symbols'] else "Extended"
                print(f"   {i:2}. {opp['symbol']:12} - {signal_class:8} {direction:7} (Score: {opp['score']:.0f}) [{source}]")
                
        except KeyboardInterrupt:
            print(f"\n⚠️  Extended analysis interrupted by user")
            print(f"📊 Using curated results only")
    else:
        print("📊 Using curated analysis results only")
    
    print(f"\n🎯 Demo complete!")

if __name__ == "__main__":
    main() 
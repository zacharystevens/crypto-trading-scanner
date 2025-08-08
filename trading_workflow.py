#!/usr/bin/env python3
"""
TRADING WORKFLOW COORDINATOR
Manages the complete two-stage trading system:
Stage 1: Opportunity Scanner (find opportunities)
Stage 2: Strategy Executor (professional execution)
"""

import os
import sys
from datetime import datetime
import json

# Import our two stages
from opportunity_scanner import OpportunityScanner
from strategy_executor import StrategyExecutor

class TradingWorkflow:
    def __init__(self):
        self.scanner = None
        self.executor = None
        self.current_opportunities = []
        
        print("🚀 PROFESSIONAL TRADING SYSTEM WORKFLOW")
        print("="*60)
        print("Two-Stage Approach:")
        print("  Stage 1: Opportunity Scanner (find setups)")
        print("  Stage 2: Strategy Executor (professional execution)")
        print()
    
    def initialize_scanner(self):
        """Initialize Stage 1 scanner"""
        print("🔍 Initializing Stage 1: Opportunity Scanner...")
        self.scanner = OpportunityScanner()
        return True
    
    def initialize_executor(self, account_size=100000):
        """Initialize Stage 2 executor"""
        print(f"🎯 Initializing Stage 2: Strategy Executor...")
        self.executor = StrategyExecutor(account_size)
        return True
    
    def run_stage_1_scan(self, scan_mode='quick'):
        """Run Stage 1 opportunity scanning"""
        if not self.scanner:
            self.initialize_scanner()
        
        print("\n" + "="*60)
        print("🔍 STAGE 1: OPPORTUNITY SCANNING")
        print("="*60)
        
        if scan_mode == 'full':
            print("Running full market scan...")
            opportunities = self.scanner.scan_all_opportunities()
        else:
            print("Running quick scan (top 50 coins)...")
            opportunities = self.scanner.scan_all_opportunities(scan_type='curated_30')
        
        self.scanner.display_top_opportunities(opportunities)
        
        # Save results
        os.makedirs('opportunities', exist_ok=True)
        with open('opportunities/latest_scan.json', 'w') as f:
            json.dump(opportunities, f, indent=2, default=str)
        
        self.current_opportunities = opportunities
        
        print(f"\n💾 Stage 1 complete - {len(opportunities)} opportunities found")
        print("📁 Results saved to opportunities/latest_scan.json")
        
        return opportunities
    
    def run_stage_2_execution(self, account_size=None):
        """Run Stage 2 strategy execution"""
        if not self.current_opportunities:
            print("❌ No opportunities available. Run Stage 1 first.")
            return
        
        if account_size and not self.executor:
            self.initialize_executor(account_size)
        elif not self.executor:
            self.initialize_executor()
        
        print("\n" + "="*60)
        print("🎯 STAGE 2: STRATEGY EXECUTION")
        print("="*60)
        
        self.executor.interactive_selection()
    
    def complete_workflow(self):
        """Run complete two-stage workflow"""
        print("🚀 COMPLETE TWO-STAGE WORKFLOW")
        print("="*60)
        
        # Get user preferences
        print("\nWorkflow Configuration:")
        print("1. Scan type:")
        print("   1. Quick scan (top 50 coins)")
        print("   2. Full scan (all coins)")
        
        scan_choice = input("Choose scan type (1 or 2): ").strip()
        scan_mode = 'full' if scan_choice == '2' else 'quick'
        
        print("\n2. Account size for position sizing:")
        try:
            account_size = float(input("Account size ($): ").strip())
        except:
            account_size = 100000
            print(f"Using default: ${account_size:,}")
        
        # Stage 1: Scan for opportunities
        opportunities = self.run_stage_1_scan(scan_mode)
        
        if not opportunities:
            print("❌ No opportunities found. Try again later.")
            return
        
        # Human decision point
        print(f"\n{'='*60}")
        print("🤔 HUMAN DECISION POINT")
        print(f"{'='*60}")
        print(f"Stage 1 found {len(opportunities)} opportunities.")
        print("Do you want to proceed to Stage 2 (strategy execution)?")
        
        proceed = input("Proceed to Stage 2? (y/n): ").strip().lower()
        
        if proceed in ['y', 'yes']:
            # Stage 2: Execute strategy on selected opportunities
            self.run_stage_2_execution(account_size)
        else:
            print("Workflow stopped. You can run Stage 2 later using option 3.")
    
    def show_latest_opportunities(self):
        """Show latest scan results"""
        try:
            with open('opportunities/latest_scan.json', 'r') as f:
                opportunities = json.load(f)
            
            print(f"\n📊 LATEST SCAN RESULTS ({len(opportunities)} opportunities)")
            print("="*60)
            
            for i, opp in enumerate(opportunities[:10], 1):
                print(f"{i:2d}. {opp['symbol']} - Score: {opp['score']:.0f}/100")
                print(f"     💰 Price: ${opp['current_price']:.4f}")
                
                if opp['fvg_zones']:
                    print(f"     📊 {len(opp['fvg_zones'])} FVG zones")
                
                if opp['trendlines']:
                    tl = opp['trendlines']
                    if tl and (tl.get('resistance_break') or tl.get('support_break')):
                        print(f"     📈 Trendline breakout")
                
                if opp['volume']['volume_spike']:
                    print(f"     🔊 Volume: {opp['volume']['volume_ratio']:.1f}x")
                print()
            
            return opportunities
            
        except FileNotFoundError:
            print("❌ No previous scan results found. Run Stage 1 first.")
            return None
    
    def interactive_menu(self):
        """Interactive menu system"""
        while True:
            print("\n" + "="*60)
            print("🚀 PROFESSIONAL TRADING SYSTEM")
            print("="*60)
            print("1. Run Stage 1: Opportunity Scanner")
            print("2. Run Stage 2: Strategy Executor")
            print("3. Complete Two-Stage Workflow")
            print("4. Show Latest Opportunities")
            print("5. System Status")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                # Stage 1 only
                print("\nStage 1 Options:")
                print("1. Quick scan (top 15 coins)")
                print("2. Full market scan")
                
                scan_choice = input("Choose (1 or 2): ").strip()
                scan_mode = 'full' if scan_choice == '2' else 'quick'
                
                self.run_stage_1_scan(scan_mode)
            
            elif choice == '2':
                # Stage 2 only
                try:
                    account_size = float(input("Account size ($): ").strip())
                except:
                    account_size = 100000
                
                self.run_stage_2_execution(account_size)
            
            elif choice == '3':
                # Complete workflow
                self.complete_workflow()
            
            elif choice == '4':
                # Show latest results
                self.show_latest_opportunities()
            
            elif choice == '5':
                # System status
                self.show_system_status()
            
            elif choice == '6':
                print("\n👋 Thank you for using the Professional Trading System!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    def show_system_status(self):
        """Show system status and configuration"""
        print("\n📊 SYSTEM STATUS")
        print("="*50)
        
        # Scanner status
        if self.scanner:
            print("✅ Stage 1 Scanner: Initialized")
            print(f"   Coins to scan: {len(self.scanner.TOP_COINS)}")
            print(f"   Timeframes: {', '.join(self.scanner.TIMEFRAMES)}")
        else:
            print("❌ Stage 1 Scanner: Not initialized")
        
        # Executor status
        if self.executor:
            print("✅ Stage 2 Executor: Initialized")
            print(f"   Account size: ${self.executor.ACCOUNT_SIZE:,}")
            print(f"   Risk per trade: {self.executor.RISK_PERCENT}%")
            print(f"   R/R ratio: 1:{self.executor.RISK_REWARD_RATIO}")
        else:
            print("❌ Stage 2 Executor: Not initialized")
        
        # Opportunities status
        if os.path.exists('opportunities/latest_scan.json'):
            try:
                with open('opportunities/latest_scan.json', 'r') as f:
                    opportunities = json.load(f)
                print(f"📁 Latest scan: {len(opportunities)} opportunities available")
            except:
                print("❌ Latest scan: File corrupted")
        else:
            print("❌ Latest scan: No scan results available")
        
        # Exchange status
        scanner_exchange = self.scanner.exchange if self.scanner else None
        executor_exchange = self.executor.exchange if self.executor else None
        
        if scanner_exchange or executor_exchange:
            print("✅ Exchange connection: Available")
        else:
            print("❌ Exchange connection: Not available")

def main():
    """Main entry point"""
    workflow = TradingWorkflow()
    
    print("Welcome to the Professional Trading System!")
    print("This system uses a two-stage approach:")
    print("  1. Find opportunities across the market")
    print("  2. Apply professional execution to selected trades")
    print()
    
    workflow.interactive_menu()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import sys
print("Starting fresh test...")

# Force fresh import
import importlib
import opportunity_scanner
importlib.reload(opportunity_scanner)

print("Creating scanner...")
scanner = opportunity_scanner.OpportunityScanner()

print(f"Testing with 1 coin...")
scanner.TOP_COINS = ['BTC/USDT']

try:
    print("About to call scan_all_opportunities()...")
    result = scanner.scan_all_opportunities()
    print(f"ERROR: Should have exited! Got {len(result)} results")
except SystemExit as e:
    print(f"SUCCESS: System exited as expected with code: {e.code}")
except Exception as e:
    print(f"UNEXPECTED: Exception occurred: {e}")

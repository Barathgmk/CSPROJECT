#!/usr/bin/env python
"""
quick_test.py

Simplified testing script to verify the trader works without the web dashboard.

Usage:
    python quick_test.py --dry-run        (test without real trades)
    python quick_test.py --live            (DANGER: real money!)
"""

import sys
import argparse
from pathlib import Path

from simple_trader import (
    SimpleTrader,
    load_and_plan_trades,
    execute_trades,
)

def main():
    parser = argparse.ArgumentParser(
        description="Test the trading system directly"
    )
    parser.add_argument(
        "--csv",
        default="penny_candidates.csv",
        help="Path to screener CSV (default: penny_candidates.csv)"
    )
    parser.add_argument(
        "--equity",
        type=float,
        default=10_000.0,
        help="Account equity (default: $10,000)"
    )
    parser.add_argument(
        "--risk",
        type=float,
        default=0.02,
        help="Risk per trade as decimal (default: 0.02 = 2%%)"
    )
    parser.add_argument(
        "--max-pos",
        type=int,
        default=10,
        help="Max positions (default: 10)"
    )
    parser.add_argument(
        "--min-sentiment",
        type=float,
        default=0.10,
        help="Min sentiment filter (default: 0.10)"
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        default=3,
        help="Min mentions filter (default: 3)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="ENABLE LIVE TRADING (default: dry-run only)"
    )
    
    args = parser.parse_args()
    
    # Check if CSV exists
    if not Path(args.csv).exists():
        print(f"❌ Error: CSV not found: {args.csv}")
        print("   Run the screener first to generate penny_candidates.csv")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("PENNY BUZZ TRADER - QUICK TEST")
    print("="*80)
    print(f"Mode: {'LIVE TRADING ⚠️⚠️⚠️' if args.live else 'DRY-RUN (safe)'}")
    print(f"CSV: {args.csv}")
    print(f"Equity: ${args.equity:,.2f}")
    print(f"Risk per trade: {args.risk*100:.1f}%")
    print(f"Max positions: {args.max_pos}")
    print(f"Min sentiment: {args.min_sentiment}")
    print(f"Min mentions: {args.min_mentions}")
    print("="*80 + "\n")
    
    if args.live:
        response = input("⚠️  LIVE TRADING ENABLED. Type 'yes' to confirm: ")
        if response.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)
    
    # Load and plan trades
    print("Step 1: Loading screener CSV...")
    trades = load_and_plan_trades(
        csv_path=args.csv,
        account_equity=args.equity,
        risk_per_trade=args.risk,
        max_positions=args.max_pos,
        min_sentiment=args.min_sentiment,
        min_mentions=args.min_mentions
    )
    
    if not trades:
        print("❌ No trades planned. Check filters or run screener first.")
        sys.exit(0)
    
    print(f"✅ Planned {len(trades)} trades\n")
    
    # Show planned trades
    print("Step 2: Planned trades:")
    print("-" * 80)
    for i, t in enumerate(trades, 1):
        print(
            f"{i}. {t.symbol:6s} | "
            f"{t.shares:4d} shares @ ${t.price:7.2f} "
            f"| ${t.dollars:9.2f} | "
            f"Mentions: {t.mentions} | "
            f"Sentiment: {t.sentiment:+.2f}"
        )
    print("-" * 80)
    print(f"Total: ${sum(t.dollars for t in trades):,.2f}\n")
    
    # Initialize trader
    print("Step 3: Initializing Alpaca connection...")
    try:
        trader = SimpleTrader(paper_trading=not args.live)
        print(f"✅ Connected to {'LIVE' if args.live else 'PAPER'} trading\n")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Get account info
    equity = trader.get_account_equity()
    if equity > 0:
        print(f"📊 Account equity: ${equity:,.2f}\n")
    
    # Execute trades
    print("Step 4: Executing trades...")
    result = execute_trades(
        trades=trades,
        trader=trader,
        side="buy",
        dry_run=not args.live
    )
    
    # Summary
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Status: {result['message']}")
    print(f"Executed: {result['executed']}/{len(trades)}")
    print(f"Failed: {result['failed']}")
    print(f"Total notional: ${result['total_dollars']:,.2f}")
    print("="*80 + "\n")
    
    if args.live:
        print("⚠️  Check your Alpaca account for orders!")
    else:
        print("✅ Dry-run complete. Check output above.")
        print("   Ready to go live? Change --dry-run to --live")


if __name__ == "__main__":
    main()

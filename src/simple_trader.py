"""
simple_trader.py

Simplified trading engine: load screener CSV → size positions → execute trades on Alpaca

This module directly handles:
- Loading screener results
- Computing position sizes
- Submitting market orders to Alpaca (paper or live)

No complex abstractions. Just execution.
"""

import os
import math
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

from alpaca_trade_api import REST, TimeFrame

@dataclass
class TradeOrder:
    """A single trade to execute"""
    symbol: str
    shares: int
    price: float
    mentions: int
    sentiment: float
    rank_score: float
    dollars: float


class SimpleTrader:
    """Direct Alpaca trading interface"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        paper_trading: bool = True
    ):
        # Get credentials from environment or parameters
        self.api_key = api_key or os.getenv("ALPACA_API_KEY", "").strip()
        self.api_secret = api_secret or os.getenv("ALPACA_API_SECRET", "").strip()
        
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Missing ALPACA_API_KEY or ALPACA_API_SECRET in .env or parameters")
        
        # Set base URL based on paper trading flag
        self.base_url = "https://paper-api.alpaca.markets" if paper_trading else "https://api.alpaca.markets"
        
        # Initialize REST client
        self.api = REST(
            key_id=self.api_key,
            secret_key=self.api_secret,
            base_url=self.base_url,
            api_version="v2"
        )
        self.paper_trading = paper_trading
    
    def get_account_equity(self) -> float:
        """Get current account buying power"""
        try:
            acct = self.api.get_account()
            return float(acct.equity)
        except Exception as e:
            print(f"Error getting account equity: {e}")
            return 0.0
    
    def can_trade(self, symbol: str) -> bool:
        """Check if symbol is tradable"""
        try:
            asset = self.api.get_asset(symbol)
            return bool(asset.tradable)
        except Exception:
            return False
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get latest stock price"""
        try:
            # Try to get latest quote
            barset = self.api.get_bars(symbol, TimeFrame.Minute, limit=1)
            if barset:
                return float(barset[-1].c)
        except Exception:
            pass
        return None
    
    def buy(self, symbol: str, shares: int, dry_run: bool = True) -> bool:
        """Place a market buy order"""
        if shares <= 0:
            print(f"Invalid share count for {symbol}: {shares}")
            return False
        
        if dry_run:
            print(f"[DRY-RUN] BUY {shares} {symbol}")
            return True
        
        try:
            print(f"Submitting: BUY {shares} {symbol}")
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side="buy",
                type="market",
                time_in_force="day"
            )
            print(f"Order submitted: {order.id}")
            return True
        except Exception as e:
            print(f"Error buying {symbol}: {e}")
            return False
    
    def sell(self, symbol: str, shares: int, dry_run: bool = True) -> bool:
        """Place a market sell order"""
        if shares <= 0:
            print(f"Invalid share count for {symbol}: {shares}")
            return False
        
        if dry_run:
            print(f"[DRY-RUN] SELL {shares} {symbol}")
            return True
        
        try:
            print(f"Submitting: SELL {shares} {symbol}")
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side="sell",
                type="market",
                time_in_force="day"
            )
            print(f"Order submitted: {order.id}")
            return True
        except Exception as e:
            print(f"Error selling {symbol}: {e}")
            return False


def load_and_plan_trades(
    csv_path: str,
    account_equity: float = 10_000.0,
    risk_per_trade: float = 0.02,
    max_positions: int = 10,
    min_sentiment: float = 0.10,
    min_mentions: int = 3
) -> List[TradeOrder]:
    """
    Load screener CSV and create position-sizing plan
    
    Returns list of TradeOrder objects ready to execute
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path)
    
    # Verify required columns
    required = {"ticker", "last", "mentions", "avg_sentiment", "rank_score"}
    missing = required - set(df.columns)
    if missing:
        print(f"Error: CSV missing columns: {missing}")
        return []
    
    # Apply filters
    df = df.copy()
    df = df[df["avg_sentiment"] >= min_sentiment]
    df = df[df["mentions"] >= min_mentions]
    df = df.sort_values(
        ["rank_score", "mentions", "avg_sentiment"],
        ascending=[False, False, False]
    )
    
    # Calculate position size
    dollars_per_trade = account_equity * risk_per_trade
    
    # Create trade plan
    trades = []
    for _, row in df.head(max_positions).iterrows():
        price = float(row["last"])
        if price <= 0:
            continue
        
        shares = math.floor(dollars_per_trade / price)
        if shares < 1:
            continue
        
        trade = TradeOrder(
            symbol=str(row["ticker"]).upper(),
            shares=shares,
            price=price,
            mentions=int(row["mentions"]),
            sentiment=float(row["avg_sentiment"]),
            rank_score=float(row["rank_score"]),
            dollars=shares * price
        )
        trades.append(trade)
    
    return trades


def execute_trades(
    trades: List[TradeOrder],
    trader: SimpleTrader,
    side: str = "buy",
    dry_run: bool = True
) -> dict:
    """
    Execute a list of trades
    
    Returns summary dict with execution results
    """
    if not trades:
        return {"success": False, "message": "No trades to execute", "executed": 0}
    
    executed = 0
    failed = 0
    total_dollars = 0.0
    
    print("\n" + "="*80)
    print(f"Executing {len(trades)} trades (DRY-RUN={dry_run})")
    print("="*80)
    
    for trade in trades:
        # Check if tradable
        if not trader.can_trade(trade.symbol):
            print(f"❌ {trade.symbol}: not tradable on Alpaca")
            failed += 1
            continue
        
        # Execute based on side
        if side.lower() == "buy":
            success = trader.buy(trade.symbol, trade.shares, dry_run=dry_run)
        elif side.lower() == "sell":
            success = trader.sell(trade.symbol, trade.shares, dry_run=dry_run)
        else:
            print(f"Invalid side: {side}")
            failed += 1
            continue
        
        if success:
            executed += 1
            total_dollars += trade.dollars
        else:
            failed += 1
    
    print("="*80)
    print(f"Executed: {executed}/{len(trades)} | Failed: {failed}")
    print(f"Total notional: ${total_dollars:,.2f}")
    print("="*80)
    
    return {
        "success": executed > 0,
        "message": f"Executed {executed} trades",
        "executed": executed,
        "failed": failed,
        "total_dollars": total_dollars
    }

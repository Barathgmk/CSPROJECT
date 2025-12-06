"""
mock_trader.py

Simulated trading engine - no real Alpaca connection.
Shows what trading would look like with realistic simulation.

For demonstration and practice purposes only.

Classes:
  - MockPosition: Represents one open stock position
  - TradeOrder: Represents one executed trade order
  - MockTradeResult: Result of a trade execution
  - MockTrader: Main trading engine (buy, sell, portfolio management)

Functions:
  - get_mock_trader(): Get global MockTrader instance
  - reset_mock_trader(): Reset to initial $25,000
  - load_and_plan_trades(): Plan trades from CSV data
  - execute_mock_trades(): Execute planned trades and update portfolio
"""

import os
import math
import uuid
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class MockPosition:
    """
    Represents one open stock position in the portfolio.
    
    Attributes:
      symbol: Stock ticker (e.g., "ATER")
      entry_price: Price we bought at
      shares: Number of shares held
      entry_time: When we bought (ISO timestamp)
      current_price: Current market price (updates during day)
    
    Properties:
      notional: Current position value (shares × current_price)
      entry_notional: Original position value (shares × entry_price)
      pnl: Profit/Loss in dollars
      pnl_percent: Profit/Loss in percentage
    """
    symbol: str
    entry_price: float
    shares: int
    entry_time: str
    current_price: float = 0.0
    
    @property
    def notional(self) -> float:
        """Current position value in dollars"""
        return self.shares * self.current_price
    
    @property
    def entry_notional(self) -> float:
        """Entry position value in dollars"""
        return self.shares * self.entry_price
    
    @property
    def pnl(self) -> float:
        """Profit/loss in dollars"""
        return self.notional - self.entry_notional
    
    @property
    def pnl_percent(self) -> float:
        """Profit/loss as percentage"""
        if self.entry_notional == 0:
            return 0.0
        return (self.pnl / self.entry_notional) * 100

@dataclass
class TradeOrder:
    """
    Represents one planned trade order from the screener.
    
    Attributes:
      symbol: Stock ticker
      shares: Number of shares to buy
      price: Price per share
      mentions: Reddit mentions count
      sentiment: Sentiment score (-1 to +1)
      rank_score: Screener rank score
      dollars: Total notional value (shares × price)
    """
    symbol: str
    shares: int
    price: float
    mentions: int
    sentiment: float
    rank_score: float
    dollars: float

@dataclass
class MockTradeResult:
    """
    Result of a simulated trade execution.
    
    Attributes:
      order_id: Unique order ID (UUID)
      symbol: Stock ticker
      shares: Shares executed
      price: Execution price
      timestamp: When executed (ISO timestamp)
      status: Order status ("filled", "pending", "cancelled")
    """
    order_id: str
    symbol: str
    shares: int
    price: float
    timestamp: str
    status: str = "filled"  # filled, pending, cancelled

class MockTrader:
    """
    Simulated trading engine with realistic price movements.
    No real Alpaca connection - just local in-memory simulation.
    
    Features:
      - Buy/sell orders with position tracking
      - Realistic P&L calculations
      - Portfolio value snapshots
      - Trade history logging
      - Price simulation with random walk
      - Multiple concurrent positions
    
    Usage:
      trader = MockTrader(starting_equity=25_000)
      trader.buy(symbol="ATER", shares=100, price=2.50)
      print(trader.get_account_equity())  # Current account value
      print(trader.positions["ATER"].pnl)  # Position P&L
    """
    
    def __init__(self, starting_equity: float = 25_000.0):
        """
        Initialize the mock trading account.
        
        Args:
          starting_equity: Starting cash balance (default $25,000)
        """
        self.starting_equity = starting_equity
        self.cash = starting_equity
        # Dictionary to track all open positions by symbol
        self.positions: Dict[str, MockPosition] = {}
        # List of all executed trades (for history)
        self.trade_history: List[MockTradeResult] = []
        # Portfolio value over time for performance tracking
        self.portfolio_values: List[tuple] = [(datetime.now().isoformat(), starting_equity)]
    
    def get_account_equity(self) -> float:
        """
        Calculate total account value.
        
        Returns:
          float: Cash + all positions current value
        """
        positions_value = sum(p.notional for p in self.positions.values())
        return self.cash + positions_value
    
    def get_available_cash(self) -> float:
        """
        Get cash available for trading.
        
        Returns:
          float: Available cash balance
        """
        return self.cash
    
    def can_trade(self, symbol: str) -> bool:
        """
        Check if symbol is tradable (always True in mock).
        
        Args:
          symbol: Stock ticker
        
        Returns:
          bool: True if can trade
        """
        return True
    
    def get_price(self, symbol: str, current_price: Optional[float] = None) -> float:
        """
        Get current price for a symbol.
        
        Args:
          symbol: Stock ticker
          current_price: If provided, use this price
        
        Returns:
          float: Price per share
        """
        if current_price:
            return current_price
        # Simulate realistic penny stock price ($0.50 - $5.00)
        return round(np.random.uniform(0.50, 5.00), 2)
    
    def simulate_price_movement(self, position: MockPosition, hours: int = 24) -> float:
        """
        Simulate realistic price movement using random walk.
        
        Args:
          position: MockPosition object to update
          hours: Time period for simulation
        
        Returns:
          float: New simulated price
        """
        # Small positive drift (0.1%) + volatility (2%)
        pct_change = np.random.normal(0.001, 0.02)
        new_price = position.current_price * (1 + pct_change)
        # Prevent negative prices
        new_price = max(new_price, 0.01)
        return round(new_price, 2)
    
    def buy(self, symbol: str, shares: int, price: float, dry_run: bool = False) -> Optional[MockTradeResult]:
        """
        Place a simulated market buy order.
        
        Args:
          symbol: Stock ticker to buy
          shares: Number of shares
          price: Price per share
          dry_run: If True, don't actually execute (just return what would happen)
        
        Returns:
          MockTradeResult: Trade execution result or None if failed
        """
        if shares <= 0:
            return None
        
        # Calculate total cost
        cost = shares * price
        
        # Check if we have enough cash
        if cost > self.cash and not dry_run:
            print(f"❌ Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}")
            return None
        
        # Create trade record
        order_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        result = MockTradeResult(
            order_id=order_id,
            symbol=symbol,
            shares=shares,
            price=price,
            timestamp=timestamp,
            status="filled"
        )
        
        if not dry_run:
            # Deduct cash from account
            self.cash -= cost
            
            # Create or update position
            if symbol in self.positions:
                # Position exists: increase size and update average entry price
                pos = self.positions[symbol]
                old_cost = pos.notional
                pos.entry_price = (old_cost + cost) / (pos.shares + shares)
                pos.shares += shares
                pos.current_price = price
            else:
                # New position: create it
                self.positions[symbol] = MockPosition(
                    symbol=symbol,
                    entry_price=price,
                    shares=shares,
                    entry_time=timestamp,
                    current_price=price
                )
            

            self.trade_history.append(result)
        
        return result
    
    def sell(self, symbol: str, shares: int, price: float, dry_run: bool = False) -> Optional[MockTradeResult]:
        """Place a simulated market sell order"""
        if symbol not in self.positions:
            print(f"❌ No position in {symbol}")
            return None
        
        pos = self.positions[symbol]
        if shares > pos.shares:
            print(f"❌ Trying to sell {shares}, but only own {pos.shares}")
            return None
        
        order_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        result = MockTradeResult(
            order_id=order_id,
            symbol=symbol,
            shares=shares,
            price=price,
            timestamp=timestamp,
            status="filled"
        )
        
        if not dry_run:
            # Add cash from sale
            proceeds = shares * price
            self.cash += proceeds
            
            # Update position
            if shares == pos.shares:
                # Close position
                del self.positions[symbol]
            else:
                # Partial close
                pos.shares -= shares
            
            self.trade_history.append(result)
        
        return result
    
    def update_position_prices(self, price_map: Dict[str, float]):
        """Update all position prices (called periodically)"""
        for symbol, price in price_map.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price
    
    def get_portfolio_summary(self) -> dict:
        """Get current portfolio state"""
        total_equity = self.get_account_equity()
        positions = [asdict(p) for p in self.positions.values()]
        
        # Calculate totals
        total_pnl = sum(p.pnl for p in self.positions.values())
        total_invested = sum(p.entry_notional for p in self.positions.values())
        
        return {
            "cash": self.cash,
            "equity": total_equity,
            "starting_equity": self.starting_equity,
            "total_pnl": total_pnl,
            "total_pnl_percent": (total_pnl / self.starting_equity * 100) if self.starting_equity > 0 else 0,
            "total_invested": total_invested,
            "num_positions": len(self.positions),
            "positions": positions
        }
    
    def get_trade_history(self) -> List[dict]:
        """Get history of all trades"""
        return [asdict(t) for t in self.trade_history]


# Global mock trader instance (for demo)
_global_trader: Optional[MockTrader] = None

def get_mock_trader() -> MockTrader:
    """Get or create global trader instance"""
    global _global_trader
    if _global_trader is None:
        _global_trader = MockTrader(starting_equity=25_000.0)
    return _global_trader

def reset_mock_trader():
    """Reset trader to starting state"""
    global _global_trader
    _global_trader = MockTrader(starting_equity=25_000.0)


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
    (Same as before, but returns mock TradeOrder)
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


def execute_mock_trades(
    trades: List[TradeOrder],
    trader: MockTrader,
    side: str = "buy",
    dry_run: bool = True
) -> dict:
    """
    Execute a list of mock trades (no real Alpaca connection)
    """
    if not trades:
        return {
            "success": False,
            "message": "No trades to execute",
            "executed": 0,
            "orders": []
        }
    
    executed = 0
    failed = 0
    total_dollars = 0.0
    orders = []
    
    print("\n" + "="*80)
    print(f"Executing {len(trades)} mock trades (DRY-RUN={dry_run})")
    print("="*80)
    
    for trade in trades:
        # Validate
        if not trader.can_trade(trade.symbol):
            print(f"❌ {trade.symbol}: not available")
            failed += 1
            continue
        
        # Execute based on side
        if side.lower() == "buy":
            result = trader.buy(trade.symbol, trade.shares, trade.price, dry_run=dry_run)
        elif side.lower() == "sell":
            result = trader.sell(trade.symbol, trade.shares, trade.price, dry_run=dry_run)
        else:
            print(f"Invalid side: {side}")
            failed += 1
            continue
        
        if result:
            executed += 1
            total_dollars += trade.dollars
            orders.append({
                "order_id": result.order_id,
                "symbol": result.symbol,
                "shares": result.shares,
                "price": result.price,
                "timestamp": result.timestamp,
                "status": result.status
            })
            status = "DRY-RUN" if dry_run else "✅"
            print(f"{status} {side.upper()} {trade.shares} {trade.symbol} @ ${trade.price:.2f}")
        else:
            failed += 1
    
    print("="*80)
    print(f"Executed: {executed}/{len(trades)} | Failed: {failed}")
    print(f"Total notional: ${total_dollars:,.2f}")
    print("="*80)
    
    return {
        "success": executed > 0,
        "message": f"Mock traded {executed} positions",
        "executed": executed,
        "failed": failed,
        "total_dollars": total_dollars,
        "orders": orders,
        "portfolio": trader.get_portfolio_summary()
    }

# Code Comparison: Before vs After

## Position Sizing Example

### ❌ Before (Complex)

```python
# In trader_config.py
@dataclass
class TraderConfig:
    account_equity: float = 10_000.0
    risk_per_trade: float = 0.02
    
    def dollars_per_trade(self) -> float:
        return self.account_equity * self.risk_per_trade

# In stock_trader.py
def pick_trades(df: pd.DataFrame, cfg: TraderConfig) -> List[TradeCandidate]:
    dollars_per_trade = cfg.dollars_per_trade()  # Get from config
    picks: List[TradeCandidate] = []
    
    for _, row in df.head(cfg.max_positions).iterrows():
        price = float(row["last"])
        if price <= 0:
            continue
        shares = math.floor(dollars_per_trade / price)
        if shares < 1:
            continue
        picks.append(
            TradeCandidate(
                symbol=row["ticker"],
                price=price,
                mentions=int(row["mentions"]),
                sentiment=float(row["avg_sentiment"]),
                rank_score=float(row["rank_score"]),
                dollars=shares * price,
                shares=shares,
            )
        )
    
    return picks

# In api.py - need to create config object
cfg = TraderConfig()
if params.equity is not None:
    cfg.account_equity = float(params.equity)
if params.risk_per_trade is not None:
    cfg.risk_per_trade = float(params.risk_per_trade)
# ... more config setup ...

picks = pick_trades(df, cfg)
```

**Issues:**
- Config object scattered logic
- Multiple files involved
- Hard to see position sizing calculation
- TradeCandidate object needed

### ✅ After (Simple)

```python
# In simple_trader.py - all in one function
def load_and_plan_trades(
    csv_path: str,
    account_equity: float = 10_000.0,
    risk_per_trade: float = 0.02,
    max_positions: int = 10,
    min_sentiment: float = 0.10,
    min_mentions: int = 3
) -> List[TradeOrder]:
    """Load screener CSV and create position-sizing plan"""
    
    df = pd.read_csv(csv_path)
    
    # Filter
    df = df[df["avg_sentiment"] >= min_sentiment]
    df = df[df["mentions"] >= min_mentions]
    
    # Calculate position size
    dollars_per_trade = account_equity * risk_per_trade
    
    # Create trades
    trades = []
    for _, row in df.head(max_positions).iterrows():
        price = float(row["last"])
        if price <= 0:
            continue
        
        shares = math.floor(dollars_per_trade / price)
        if shares < 1:
            continue
        
        trades.append(TradeOrder(
            symbol=str(row["ticker"]).upper(),
            shares=shares,
            price=price,
            mentions=int(row["mentions"]),
            sentiment=float(row["avg_sentiment"]),
            rank_score=float(row["rank_score"]),
            dollars=shares * price
        ))
    
    return trades

# In api.py - simple function call
trades = load_and_plan_trades(
    csv_path=csv_path,
    account_equity=equity,
    risk_per_trade=risk_per_trade,
    max_positions=max_positions,
    min_sentiment=min_sentiment,
    min_mentions=min_mentions
)
```

**Benefits:**
- Single function, all logic visible
- Parameters clear and obvious
- Calculation right there: `dollars_per_trade = equity × risk`
- Shares: `floor(dollars_per_trade / price)`
- Returns ready-to-trade TradeOrder list

---

## Broker Integration Example

### ❌ Before (Wrapped)

```python
# In broker_alpaca.py
class AlpacaBroker:
    def __init__(self, creds: AlpacaCredentials):
        self.creds = creds
        self.api = REST(
            key_id=creds.api_key,
            secret_key=creds.api_secret,
            base_url=creds.base_url,
            api_version="v2",
        )
    
    @classmethod
    def from_env(cls, key_env: str, secret_env: str, base_url: str):
        key = os.getenv(key_env, "").strip()
        secret = os.getenv(secret_env, "").strip()
        if not key or not secret:
            raise RuntimeError(f"Missing {key_env}/{secret_env}")
        return cls(AlpacaCredentials(api_key=key, api_secret=secret, base_url=base_url))
    
    def submit_market_order(self, symbol: str, qty: int, side: str, dry_run: bool = True):
        # ... validation ...
        if dry_run:
            print(f"[DRY-RUN] {side.upper()} {qty} {symbol}")
            return None
        
        order = self.api.submit_order(...)
        return order

# In stock_trader.py
def place_trades(picks: List[TradeCandidate], cfg: TraderConfig):
    broker = AlpacaBroker.from_env(
        cfg.alpaca_key_env,
        cfg.alpaca_secret_env,
        cfg.alpaca_base_url
    )
    
    for p in picks:
        try:
            broker.submit_market_order(p.symbol, p.shares, side="buy", dry_run=False)
        except Exception as e:
            print(f"Error: {e}")
```

**Issues:**
- Broker abstraction adds complexity
- Credentials handling in two places
- dry_run parameter scattered
- Hard to tell what AlpacaBroker does

### ✅ After (Direct)

```python
# In simple_trader.py - all in one class
class SimpleTrader:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, paper_trading: bool = True):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY", "").strip()
        self.api_secret = api_secret or os.getenv("ALPACA_API_SECRET", "").strip()
        
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Missing ALPACA_API_KEY or ALPACA_API_SECRET in .env")
        
        # Clear: paper vs live determined by URL
        self.base_url = "https://paper-api.alpaca.markets" if paper_trading else "https://api.alpaca.markets"
        
        self.api = REST(
            key_id=self.api_key,
            secret_key=self.api_secret,
            base_url=self.base_url,
            api_version="v2"
        )
    
    def buy(self, symbol: str, shares: int, dry_run: bool = True) -> bool:
        if dry_run:
            print(f"[DRY-RUN] BUY {shares} {symbol}")
            return True
        
        try:
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

# In api.py
trader = SimpleTrader(paper_trading=not live)
result = execute_trades(trades, trader, side="buy", dry_run=not live)
```

**Benefits:**
- Direct REST client, no wrapper
- Clear paper_trading parameter
- One file, easy to see API interaction
- Obvious error handling
- Simple true/false return

---

## Execution Flow Comparison

### ❌ Before: Multiple Hops

```
API Request
    ↓
Create TraderConfig object
    ↓
Call load_candidates(cfg)  → reads CSV
    ↓
Call pick_trades(df, cfg)  → creates TradeCandidate list
    ↓
Call place_trades(picks, cfg)
    ↓
    Create AlpacaBroker from env
    ↓
    For each pick:
        broker.submit_market_order()
            ↓
            AlpacaCredentials dataclass
            ↓
            REST client call
    ↓
Return result
```

**Problem:** Long chain, easy to break, hard to debug

### ✅ After: Direct Path

```
API Request
    ↓
Call load_and_plan_trades(csv_path, ...)  → returns TradeOrder list
    ↓
Create SimpleTrader(paper_trading=...)  → ready to trade
    ↓
Call execute_trades(trades, trader)
    ↓
    For each trade:
        trader.buy()  → direct REST call
    ↓
Return result
```

**Benefit:** 3 steps, clear at each level

---

## Configuration Comparison

### ❌ Before

```python
# trader_config.py
@dataclass
class TraderConfig:
    candidates_csv: Path = Path("penny_candidates.csv")
    account_equity: float = 10_000.0
    risk_per_trade: float = 0.02
    max_positions: int = 10
    min_sentiment: float = 0.10
    min_mentions: int = 3
    dry_run: bool = True
    broker_name: str = "alpaca"
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    alpaca_key_env: str = "ALPACA_API_KEY"
    alpaca_secret_env: str = "ALPACA_API_SECRET"
    
    def dollars_per_trade(self) -> float:
        return self.account_equity * self.risk_per_trade

# Then in api.py
cfg = TraderConfig()
if params.equity is not None:
    cfg.account_equity = float(params.equity)
if params.risk_per_trade is not None:
    cfg.risk_per_trade = float(params.risk_per_trade)
# ... 5 more if statements ...
cfg.dry_run = not params.live
```

**Issues:**
- Config file with too many options
- Many manual overrides in code
- dry_run as boolean (confusing)
- Constants mixed with parameters

### ✅ After

```python
# simple_trader.py - pass parameters directly
trades = load_and_plan_trades(
    csv_path="penny_candidates.csv",
    account_equity=10_000.0,
    risk_per_trade=0.02,
    max_positions=10,
    min_sentiment=0.10,
    min_mentions=3
)

trader = SimpleTrader(paper_trading=True)  # Clear: True = paper, False = live

execute_trades(trades, trader, dry_run=True)  # Obvious: dry_run boolean
```

**Benefits:**
- Parameters passed directly (obvious)
- No config file needed
- paper_trading boolean is clear
- dry_run boolean is clear
- Easy to change values

---

## Error Handling

### ❌ Before

```python
# Scattered across multiple files
try:
    broker = AlpacaBroker.from_env(cfg.alpaca_key_env, cfg.alpaca_secret_env, cfg.alpaca_base_url)
except RuntimeError:
    # Missing credentials
    pass

if not broker.can_trade(p.symbol):
    print(f"Skipping {p.symbol}: not tradable")
    continue

try:
    broker.submit_market_order(p.symbol, p.shares, side="buy", dry_run=False)
except Exception as e:
    print(f"Error submitting order: {e}")
```

**Issues:**
- Errors in different places
- Hard to trace what failed
- Multiple exception types

### ✅ After

```python
# All in one place, clear flow
try:
    trader = SimpleTrader(paper_trading=not args.live)
    print(f"✅ Connected to Alpaca")
except RuntimeError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

for trade in trades:
    if not trader.can_trade(trade.symbol):
        print(f"❌ {trade.symbol}: not tradable")
        failed += 1
        continue
    
    success = trader.buy(trade.symbol, trade.shares, dry_run=dry_run)
    if success:
        executed += 1
    else:
        failed += 1
```

**Benefits:**
- Clear error messages with status symbols (✅ ❌)
- Obvious what failed and why
- Simple execution path

---

## Summary: Why Simpler Is Better

| Metric | Before | After |
|--------|--------|-------|
| **Files involved** | 4 | 1 |
| **Classes/objects** | TraderConfig, TradeCandidate, AlpacaBroker | SimpleTrader, TradeOrder |
| **Functions** | load_candidates, pick_trades, place_trades | load_and_plan_trades, execute_trades |
| **Import statements** | Multiple from different files | Single: from simple_trader import |
| **Position sizing** | In TraderConfig.dollars_per_trade() | Visible in function |
| **Credentials** | Multiple env vars + config | Direct from env via SimpleTrader |
| **Paper vs live** | cfg.dry_run boolean + base_url | paper_trading parameter |
| **Error messages** | Vague | Clear + status indicators |
| **Debugging path** | Jump between 4 files | Single file to trace |
| **Time to understand** | 30+ minutes | 5 minutes |

---

## The Point

**Before:** Abstraction hell made it hard to actually trade
**After:** Simple, direct code that makes trading obvious

Same functionality, way easier to understand and debug.

Trade execution is now **simple and clear** ✅

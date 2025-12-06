# System Architecture - Simplified

## Before Simplification

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Dashboard                            │
│                       (index.html)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                        HTTP / JSON
                             │
        ┌────────────────────▼────────────────────┐
        │       FastAPI Backend (api.py)           │
        └────────┬─────────────────────────┬───────┘
                 │                         │
         ┌───────▼────────┐       ┌───────▼───────┐
         │  Reddit Scan   │       │ Finance Data  │
         │  + Sentiment   │       │ (yfinance)    │
         └───────┬────────┘       └───────┬───────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                   ┌─────────▼──────────┐
                   │  trader_config.py  │  ◄── Config
                   └────────┬───────────┘
                            │
                 ┌──────────▼──────────┐
                 │  stock_trader.py    │  ◄── Complex logic
                 └────────┬────────────┘
                          │
                 ┌────────▼──────────┐
                 │ broker_alpaca.py  │  ◄── Wrapper
                 └────────┬──────────┘
                          │
                 ┌────────▼──────────┐
                 │  Alpaca REST API  │  ◄── Orders
                 └───────────────────┘

Problem: Too many abstraction layers, hard to debug
```

## After Simplification

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Dashboard                            │
│                       (index.html)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                        HTTP / JSON
                             │
        ┌────────────────────▼────────────────────┐
        │       FastAPI Backend (api.py)           │
        └────────┬─────────────────────────┬───────┘
                 │                         │
         ┌───────▼────────┐       ┌───────▼───────┐
         │  Reddit Scan   │       │ Finance Data  │
         │  + Sentiment   │       │ (yfinance)    │
         └───────┬────────┘       └───────┬───────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                   penny_candidates.csv
                             │
                   ┌─────────▼──────────────┐
                   │  simple_trader.py      │
                   │  ├─ load_and_plan()   │
                   │  ├─ SimpleTrader()     │
                   │  └─ execute_trades()   │
                   └────────┬───────────────┘
                            │
                   ┌────────▼──────────┐
                   │  Alpaca REST API  │  ◄── Orders
                   └───────────────────┘

Benefit: Single, clear file handles all trading logic
```

---

## Data Flow Simplified

### 1. Screener Phase (POST /scan)

```
Request with params
    ↓
[reddit_scan]      → Extract tickers from posts + comments
    ↓
[finance_filter]   → Get real prices/volumes, filter penny stocks
    ↓
[rank_trades]      → Sort by mentions × sentiment
    ↓
Save CSV + return results to dashboard
```

### 2. Trading Phase (POST /trade)

```
Request with params
    ↓
[load_and_plan_trades]
    ├─ Read CSV
    ├─ Filter by sentiment/mentions
    ├─ Calculate position sizes ($ equity × risk %)
    ├─ Determine # shares ($ / price)
    └─ Return TradeOrder list
    ↓
[SimpleTrader]
    ├─ Initialize Alpaca REST client (paper or live)
    ├─ Validate each trade (is it tradable?)
    └─ Submit market orders
    ↓
[execute_trades]
    ├─ Loop through TradeOrder list
    ├─ Call trader.buy() for each
    └─ Return summary (executed count, total $)
    ↓
Return results to dashboard
```

---

## Key Classes

### SimpleTrader

```python
trader = SimpleTrader(paper_trading=True)  # Paper or live

# Get info
equity = trader.get_account_equity()
price = trader.get_price("AAPL")
tradable = trader.can_trade("AAPL")

# Execute
trader.buy("AAPL", 10, dry_run=True)   # Dry-run: just logs
trader.buy("AAPL", 10, dry_run=False)  # Real: sends order
```

### TradeOrder (dataclass)

```python
@dataclass
class TradeOrder:
    symbol: str        # Ticker symbol
    shares: int        # Number of shares to buy
    price: float       # Current price
    mentions: int      # Reddit mentions
    sentiment: float   # Sentiment score (-1 to +1)
    rank_score: float  # Overall rank
    dollars: float     # Total notional (shares × price)
```

### Key Functions

```python
# Load and plan trades from CSV
trades = load_and_plan_trades(
    csv_path="penny_candidates.csv",
    account_equity=10_000,
    risk_per_trade=0.02,  # 2%
    max_positions=10,
    min_sentiment=0.10,
    min_mentions=3
)

# Execute the trades
result = execute_trades(
    trades=trades,
    trader=trader,
    side="buy",
    dry_run=not live
)
# Returns: {success, message, executed, failed, total_dollars}
```

---

## Position Sizing Example

```
Account equity:    $10,000
Risk per trade:    2%
Max positions:     10

Dollars per position = $10,000 × 2% = $200

For ticker ABCD @ $3.50:
  Shares = floor($200 / $3.50) = 57 shares
  Notional = 57 × $3.50 = $199.50

For ticker WXYZ @ $0.50:
  Shares = floor($200 / $0.50) = 400 shares
  Notional = 400 × $0.50 = $200.00
```

---

## Testing Flow

```
1. Run Screener
   ↓
   Generates penny_candidates.csv
   
2. Review CSV
   ↓
   Look for: good mentions, positive sentiment, reasonable price
   
3. Dry-run Trade
   ↓
   Shows what WOULD happen (safe to test)
   
4. Check Alpaca Account
   ↓
   Paper orders should appear if setup correct
   
5. Go Live (if confident)
   ↓
   Enable LIVE checkbox, run trade again
   Real orders submitted to Alpaca
```

---

## Error Handling

### What if something breaks?

1. **CSV not found**: Run screener first
2. **Missing Alpaca key**: Check `.env` file
3. **No tradable symbols**: Stock might be delisted or not on Alpaca
4. **Insufficient buying power**: Check account balance
5. **Sentiment too high/low**: Adjust min_sentiment filter

### Debugging

Check server logs when running API:
```
[ERROR] Missing ALPACA_API_KEY in .env
[INFO] BUY 57 ABCD
[ERROR] ABCD: not tradable on Alpaca
```

---

## File Sizes (Simplified)

| File | Lines | Purpose |
|------|-------|---------|
| `simple_trader.py` | ~250 | Trading engine (NEW, concise) |
| `api.py` | ~330 | FastAPI backend |
| `index.html` | ~220 | Web dashboard |
| `quick_test.py` | ~150 | CLI testing tool |
| Total | ~950 | Complete system |

**vs. Before:**
- `stock_trader.py`: ~200
- `broker_alpaca.py`: ~100
- `trader_config.py`: ~50
- `api.py`: ~330
- Total: ~680 (more scattered)

**Benefit**: Same functionality, but easier to understand in one file.

---

## Next: Make It Work

1. ✅ Code simplified
2. ⏳ Test it:
   ```bash
   # Start API
   uvicorn api:app --reload
   
   # In another terminal, test screener
   curl -X POST http://127.0.0.1:8000/scan \
     -H "Content-Type: application/json" \
     -d '{"subreddits":["pennystocks"],"lookback_days":1}'
   
   # Then test trading (dry-run)
   python quick_test.py --csv penny_candidates.csv
   ```
3. Monitor logs for errors
4. Adjust filters if needed
5. When ready, go live

---

**Remember**: Start small, test thoroughly, only use LIVE mode when confident!

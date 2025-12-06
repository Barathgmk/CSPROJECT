# 📝 Code Comments & Explanations

This document explains the major functions and classes in the Penny Buzz system.

## 📁 File Structure

```
api.py              - FastAPI backend (REST endpoints)
mock_trader.py      - Simulated trading engine
simple_ml.py        - Machine learning price predictions
index.html          - Frontend dashboard (HTML/CSS/JavaScript)
```

---

## 🔌 api.py - Backend API Server

### **get_reddit_client()**
Connects to Reddit using PRAW (Python Reddit API Wrapper).

```python
def get_reddit_client() -> praw.Reddit:
    # Reads REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET from .env
    # Returns PRAW Reddit object for API access
    # Raises RuntimeError if credentials missing
```

**What it does:**
- Loads credentials from `.env` file
- Creates authenticated Reddit API connection
- Returns object to query Reddit posts

---

### **get_demo_reddit_data()**
Returns mock stock data when Reddit API fails.

```python
def get_demo_reddit_data() -> pd.DataFrame:
    # Returns hardcoded demo stocks:
    # ATER: 245 mentions, 0.68 sentiment
    # SRNE: 198 mentions, 0.52 sentiment
    # ... 8 more stocks
    # Allows system to work without Reddit credentials
```

**What it does:**
- Provides fallback data when Reddit unavailable
- Contains 10 popular penny stocks from demo
- Ensures system never completely breaks

---

### **extract_tickers(text: str) -> List[str]**
Finds stock ticker symbols in text.

```python
def extract_tickers(text: str) -> List[str]:
    # Uses regex to find 2-5 uppercase letters: [A-Z]{2,5}
    # Filters out common words (I, A, AND, CEO, FOMO, etc)
    # Returns list like ["ATER", "MULN", "SRNE"]
```

**Algorithm:**
1. Find all 2-5 character uppercase words
2. Remove common non-ticker words
3. Return remaining as probable stock tickers

**Example:**
```python
text = "ATER is a great penny stock. MULN is also good."
tickers = extract_tickers(text)
# Returns: ["ATER", "MULN"]
```

---

### **reddit_scan(params: ScanParams) -> pd.DataFrame**
Main function to scan Reddit for stock mentions.

```python
def reddit_scan(params: ScanParams) -> pd.DataFrame:
    # 1. Connect to Reddit API
    # 2. Loop through subreddits (pennystocks, wallstreetbets, etc)
    # 3. Get recent posts (last N days)
    # 4. Extract tickers and calculate sentiment
    # 5. Count mentions per ticker
    # 6. Average sentiment per ticker
    # 7. Return DataFrame with results
    
    # FALLBACK: If Reddit fails, return get_demo_reddit_data()
```

**Process:**
1. Calculate cutoff date (now - lookback_days)
2. For each subreddit:
   - Get N most recent posts
   - For each post:
     - Check if created after cutoff
     - Extract tickers from title + body
     - Calculate sentiment using VADER
     - Count mention and sum sentiment
3. Return DataFrame: ticker, mentions, avg_sentiment

**Output Example:**
```
ticker  mentions  avg_sentiment
ATER    245       0.68
SRNE    198       0.52
MULN    142       0.38
```

---

### **finance_filter(raw: pd.DataFrame) -> pd.DataFrame**
Add price & volume data, then filter and rank.

```python
def finance_filter(raw: pd.DataFrame, price_max: float, min_dollar_vol: float):
    # 1. Load real prices from yfinance (last month)
    # 2. Calculate average dollar volume
    # 3. Filter by: price <= $5, volume >= $200K
    # 4. Calculate rank_score = 50% mentions + 30% sentiment + 20% volume
    # 5. Sort by rank_score
    
    # FALLBACK: If yfinance fails, generate demo prices
```

**Price Filtering:**
- Only keep stocks under $5 (penny stock definition)
- Only keep stocks with $200K+ daily volume (liquidity requirement)

**Ranking Formula:**
```
rank_score = 0.5 * norm(mentions) 
           + 0.3 * norm(avg_sentiment) 
           + 0.2 * norm(avg_dollar_vol)
```

Where `norm()` normalizes each metric to 0-1 scale.

**Output Example:**
```
ticker  mentions  avg_sentiment  last   avg_dollar_vol  rank_score
ATER    245       0.68          2.45   500000.00       0.85
SRNE    198       0.52          3.10   450000.00       0.72
```

---

### **POST /scan Endpoint**
HTTP endpoint to trigger screener.

```python
@app.post("/scan")
async def scan(params: ScanParams):
    # 1. Call reddit_scan() to get mentions
    # 2. Call finance_filter() to add prices
    # 3. Save results to penny_candidates.csv
    # 4. Return top results as JSON
    
    # Returns:
    # {
    #   "rows": [...],  # Top stocks
    #   "count_raw": 50,  # Mentions found
    #   "count_ranked": 12  # After filters
    # }
```

**Used by:** Frontend "Run Screener" button

---

### **POST /trade Endpoint**
HTTP endpoint to execute mock trades.

```python
@app.post("/trade")
async def trade(params: TradeParams):
    # 1. Load penny_candidates.csv from previous scan
    # 2. Size positions using Kelly-like formula
    # 3. Apply sentiment and mention filters
    # 4. Execute mock buy orders via MockTrader
    # 5. Return orders and updated portfolio
    
    # Returns:
    # {
    #   "success": true,
    #   "executed": 5,  # Trades executed
    #   "orders": [...],  # Order details
    #   "portfolio": {...}  # Updated account state
    # }
```

**Risk Sizing:**
```
position_size = (equity × risk_per_trade) / distance_to_stop_loss
```

**Used by:** Frontend "Execute Trades" button

---

## 🎮 mock_trader.py - Simulated Trading Engine

### **MockPosition Dataclass**
Represents one open stock position.

```python
@dataclass
class MockPosition:
    symbol: str              # "ATER"
    entry_price: float       # $2.50
    shares: int             # 100
    entry_time: str         # ISO timestamp
    current_price: float    # $2.65 (updates)
    
    @property
    def notional(self) -> float:
        # Current value = shares × current_price
        # Example: 100 × $2.65 = $265
    
    @property
    def pnl(self) -> float:
        # Profit/Loss = notional - entry_notional
        # Example: $265 - $250 = +$15
    
    @property
    def pnl_percent(self) -> float:
        # P&L as percentage = (pnl / entry_notional) × 100
        # Example: ($15 / $250) × 100 = +6%
```

---

### **TradeOrder Dataclass**
Represents one planned trade order.

```python
@dataclass
class TradeOrder:
    symbol: str         # "ATER"
    shares: int         # 100
    price: float        # $2.50
    mentions: int       # 245 (from Reddit scan)
    sentiment: float    # 0.68 (positive)
    rank_score: float   # 0.85 (screener rank)
    dollars: float      # $250 (notional value)
```

---

### **MockTrader Class**
Main trading engine for simulating buys/sells.

```python
class MockTrader:
    def __init__(self, starting_equity=25_000):
        self.cash = 25_000              # Available cash
        self.positions = {}             # Dict of open positions
        self.trade_history = []         # List of all trades
        self.portfolio_values = [...]   # Value over time
    
    def buy(symbol, shares, price, dry_run=False):
        # Execute a simulated buy order
        # Deducts from cash, creates/updates position
        # Returns MockTradeResult with order details
        # If dry_run=True, shows what would happen without executing
    
    def sell(symbol, shares, price):
        # Close part or all of a position
        # Adds cash back to account
        # Records trade in history
    
    def get_account_equity():
        # Returns total account value
        # = cash + all positions current value
    
    def get_portfolio_summary():
        # Returns complete portfolio state
        # {equity, cash, positions, total_pnl, pnl_percent}
```

**Example Usage:**
```python
trader = MockTrader(25_000)

# Execute buy order
trader.buy(symbol="ATER", shares=100, price=2.50)
# Cash: $25,000 - $250 = $24,750
# Position: ATER × 100 @ $2.50

# Update price
trader.positions["ATER"].current_price = 2.75
# P&L = (100 × $2.75) - (100 × $2.50) = +$25

# Check equity
equity = trader.get_account_equity()
# = $24,750 + (100 × $2.75) = $25,025
```

---

## 🤖 simple_ml.py - Machine Learning Predictions

### **SimpleStockPredictor Class**
Predicts stock prices using technical analysis.

```python
class SimpleStockPredictor:
    def __init__(self, lookback_days=20):
        # Initialize with 20-day lookback window
    
    def predict_next_price(prices, current_price):
        # Input: List of recent prices
        # Output: Prediction with confidence
        #
        # Uses:
        # 1. Moving averages (MA5, MA10, MA20) - trend
        # 2. Momentum - rate of change
        # 3. Volatility - price variance
        # 4. Linear regression - direction fit
        #
        # Returns dict:
        # {
        #   "predicted_price": 2.75,
        #   "confidence": 0.68,  # 0-1 scale
        #   "trend": "up",
        #   "momentum": 0.12,
        #   "volatility": 0.03,
        #   "support": 2.40,
        #   "resistance": 3.10
        # }
    
    def classify_signal(predicted_price, current_price):
        # Generate trading signal based on prediction
        # 
        # Returns:
        # "STRONG_BUY" - prediction >> current (>10% gain expected)
        # "BUY" - prediction > current (positive)
        # "HOLD" - prediction ≈ current (neutral)
        # "SELL" - prediction < current (negative)
        # "STRONG_SELL" - prediction << current (>10% loss expected)
```

**Algorithm for predict_next_price():**
1. Calculate moving averages (5, 10, 20 day)
2. Calculate momentum (% change over time)
3. Calculate volatility (std dev of returns)
4. Fit linear regression to trend
5. Combine signals with weights
6. Calculate confidence based on trend strength
7. Calculate support/resistance levels

---

## 💻 index.html - Frontend Dashboard

### **Key JavaScript Functions**

#### **updateStats()**
Fetch current portfolio from `/portfolio` endpoint and update UI.

```javascript
function updateStats() {
    // 1. Call API /portfolio endpoint
    // 2. Extract: equity, P&L, positions, invested
    // 3. Update HTML elements:
    //    - Account Balance card
    //    - Total P&L card
    //    - Open Positions count
    //    - Total Invested amount
    // 4. Color-code P&L (green if +, red if -)
}
```

**Updates:**
- `#equity` - Total account value
- `#pnl-value` - Profit/Loss amount
- `#pnl-change` - P&L percentage
- `#positions-count` - Number of open positions

---

#### **runScan()**
Execute screener by calling `/scan` endpoint.

```javascript
async function runScan() {
    // 1. Get screener parameters from form:
    //    - subreddits
    //    - lookback_days
    //    - post_limit_each
    //    - price_max
    //    - min_dollar_vol
    
    // 2. Call API POST /scan with params
    
    // 3. On success:
    //    - Store results in global scanResults
    //    - Display in "Screener Results" tab
    //    - Auto-load ML predictions
    //    - Log success message
    
    // 4. On error:
    //    - Display error message
    //    - Log to system log
}
```

**Process:**
1. Gather form inputs
2. Build request body
3. POST to `/scan`
4. Render results table
5. Auto-load predictions

---

#### **runTrade()**
Execute mock trades using `/trade` endpoint.

```javascript
async function runTrade() {
    // 1. Check screener results exist (must scan first)
    
    // 2. Get trading parameters from form:
    //    - risk_per_trade
    //    - max_positions
    //    - min_sentiment
    //    - min_mentions
    
    // 3. Call API POST /trade with params
    
    // 4. On success:
    //    - Execute N trades from screener results
    //    - Update portfolio display
    //    - Update stats (equity, P&L)
    //    - Log executed trades
    
    // 5. On error:
    //    - Display error to user
}
```

**Executes:**
- Buy orders for qualifying stocks
- Updates portfolio position
- Recalculates P&L
- Updates UI stats

---

#### **switchTab(tabName)**
Switch between results tabs (Screener/Predictions/Portfolio/Trades).

```javascript
function switchTab(tabName) {
    // 1. Hide all tab content divs
    // 2. Remove "active" class from all buttons
    // 3. Show selected tab div
    // 4. Add "active" class to clicked button
}
```

**Tabs:**
- `screener-results` - Top stock opportunities
- `predictions` - ML price predictions
- `portfolio` - Open positions with P&L
- `trades` - Recent trade history

---

#### **log(msg, type)**
Write message to system log with color coding.

```javascript
function log(msg, type = 'info') {
    // Types: 'success' (green), 'error' (red), 'info' (blue), 'warn' (yellow)
    // 1. Create new log entry div
    // 2. Add timestamp: [HH:MM:SS]
    // 3. Add message and color class
    // 4. Insert at top of log
    // 5. Keep only last 100 entries
}
```

**Example:**
```javascript
log("✅ Executed 5 trades", 'success');
log("❌ Insufficient cash", 'error');
log("🔍 Scanning Reddit...", 'info');
```

---

## 📊 Data Flow Diagram

```
Frontend (HTML)
      |
      | HTTP REST API
      |
    API (FastAPI)
      |
      +-- Reddit (PRAW)
      +-- Yahoo Finance (yfinance)
      +-- MockTrader (in-memory)
      +-- SimpleML (predictions)
      |
   Results
      |
   Display
```

---

## 🔄 Complete Trading Workflow

```
1. User opens index.html
   |
2. Frontend displays dashboard with form inputs
   |
3. User clicks "Run Screener"
   |
4. runScan() → POST /scan → API
   ├── reddit_scan() - Get mentions from Reddit
   ├── finance_filter() - Add prices, filter, rank
   └── Return top 20 stocks
   |
5. Display results in "Screener Results" tab
   |
6. Frontend auto-calls /predictions
   |
7. Display predictions in "ML Predictions" tab
   |
8. User clicks "Execute Trades"
   |
9. runTrade() → POST /trade → API
   ├── load_and_plan_trades() - Size positions
   ├── MockTrader.buy() - Execute mock orders
   └── Return executed trades
   |
10. Update portfolio display
    |
11. Show P&L in stats grid
    |
12. User can reset and start over
```

---

## 🎯 Key Design Patterns

### **Fallback Pattern**
Every external dependency has a fallback:
```python
# Reddit fails → use demo data
# yfinance fails → use demo prices
# Both fail → system still works with demo data
```

### **Position Sizing Pattern**
Uses risk-based position sizing (Kelly Criterion derivative):
```
position_size = (account_equity × risk_per_trade) / stop_loss_distance
```

### **API-First Architecture**
Frontend is stateless - all logic in backend:
```
Frontend: Thin UI + JavaScript
Backend: All business logic (screener, trading, predictions)
```

### **Async/Await Pattern**
All API calls are non-blocking:
```javascript
async function runScan() {
    const response = await fetch(API_BASE + "/scan", {...});
    const data = await response.json();
}
```

---

## 📚 Further Reading

See README.md for:
- Installation instructions
- Usage guide
- Troubleshooting
- Next steps for enhancements

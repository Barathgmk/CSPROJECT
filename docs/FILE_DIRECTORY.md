# 📁 Project File Directory & Purposes

## **Core Application Files**

| File | Purpose | Language | Size |
|------|---------|----------|------|
| `api.py` | FastAPI backend server - REST endpoints for screener, trading, portfolio management | Python | ~500 lines |
| `mock_trader.py` | Simulated trading engine - MockTrader class for buy/sell orders, position tracking, P&L calculations | Python | ~380 lines |
| `simple_ml.py` | Machine learning price prediction - Moving averages, momentum, volatility analysis, trading signals | Python | ~280 lines |
| `index.html` | Frontend dashboard - HTML/CSS/JavaScript UI with forms, tabs, real-time stats, system log | HTML/CSS/JS | ~900 lines |

---

## **Configuration Files**

| File | Purpose | Type |
|------|---------|------|
| `.env` | Environment variables - Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT) | Config |
| `requirements.txt` | Python dependencies - Lists all required packages (fastapi, uvicorn, praw, pandas, yfinance, nltk, etc.) | Config |
| `.env.example` | Template for .env file - Shows what credentials are needed | Template |

---

## **Documentation Files**

| File | Purpose | Type | Content |
|------|---------|------|---------|
| `README.md` | Main project documentation - Quick start, usage guide, features, troubleshooting, examples | Markdown | Setup instructions, workflow, FAQ |
| `CODE_COMMENTS.md` | Detailed code explanations - Function-by-function breakdown, algorithms, data flows, design patterns | Markdown | Technical deep-dive, examples |
| `COMPLETION_SUMMARY.md` | Project completion summary - What was built, features, architecture overview | Markdown | Project status, capabilities |

---

## **Data Files** (Generated at Runtime)

| File | Purpose | Type | Created By |
|------|---------|------|-----------|
| `penny_candidates.csv` | Screener results - Stocks found by Reddit scan with metadata | CSV | `/scan` endpoint |
| `__pycache__/` | Python cache - Compiled bytecode for faster imports | Directory | Python interpreter |

---

## **Legacy/Old Files** (Can be ignored/deleted)

| File | Purpose | Status |
|------|---------|--------|
| `simple_trader.py` | Original simplified trader (superseded by mock_trader.py) | ⚠️ Deprecated |
| `stock_trader.py` | Old complex trading system | ⚠️ Deprecated |
| `broker_alpaca.py` | Old Alpaca broker wrapper | ⚠️ Deprecated |
| `trader_config.py` | Old configuration system | ⚠️ Deprecated |

---

## **File Dependency Graph**

```
index.html (Frontend)
    ↓ HTTP requests
    ↓
api.py (Backend)
    ├── imports: mock_trader.py
    ├── imports: simple_ml.py
    ├── calls: reddit_scan()
    ├── calls: finance_filter()
    └── calls: MockTrader.buy()

mock_trader.py (Trading Engine)
    ├── class: MockTrader
    ├── class: MockPosition
    └── class: TradeOrder

simple_ml.py (ML Predictions)
    ├── class: SimpleStockPredictor
    ├── method: predict_next_price()
    └── method: classify_signal()

.env (Config)
    └── read by: api.py → get_reddit_client()
```

---

## **Quick File Reference**

### **To Run the System:**
1. **Start backend:** Run `api.py` with `python -m uvicorn api:app --host 127.0.0.1 --port 8001`
2. **Open frontend:** Open `index.html` in web browser
3. **Configure:** Edit `.env` with Reddit credentials (optional - system falls back to demo data)

### **To Understand the Code:**
- **README.md** - How to use
- **CODE_COMMENTS.md** - How it works technically
- **api.py** - REST endpoints and screener logic
- **mock_trader.py** - Trading simulation logic
- **simple_ml.py** - Prediction algorithms

### **To Modify:**
- **index.html** - Change UI/dashboard layout
- **api.py** - Add new endpoints or modify screener logic
- **mock_trader.py** - Change position sizing or trading rules
- **simple_ml.py** - Add new technical indicators

---

## **File Purposes at a Glance**

### **Frontend (User Interaction)**
- `index.html` - Beautiful dashboard with purple gradient, stats grid, tabs, forms

### **Backend (Business Logic)**
- `api.py` - REST API endpoints (scan, trade, portfolio, predictions)
- `mock_trader.py` - Simulates trades without real money
- `simple_ml.py` - Predicts prices and generates trading signals

### **Configuration**
- `.env` - Reddit API credentials
- `requirements.txt` - Python packages needed

### **Documentation**
- `README.md` - Setup and usage instructions
- `CODE_COMMENTS.md` - Code explanations and algorithms
- `COMPLETION_SUMMARY.md` - Project overview

### **Data**
- `penny_candidates.csv` - Generated screener results

---

## **File Statistics**

```
Total Lines of Code: ~2,000
Total Files: 7 (core) + 3 (docs) + 2 (config) + 1 (legacy)

Core Files:
  api.py              ~500 lines
  mock_trader.py      ~380 lines  
  simple_ml.py        ~280 lines
  index.html          ~900 lines

Documentation:
  README.md           ~350 lines
  CODE_COMMENTS.md    ~450 lines
  COMPLETION_SUMMARY.md ~180 lines

Config:
  requirements.txt    ~15 lines
  .env                ~10 lines
```

---

## **How Files Connect**

### **User Workflow:**
1. User opens `index.html` in browser
2. Clicks "Run Screener"
3. Frontend sends HTTP POST to `api.py:/scan`
4. Backend:
   - Imports `reddit_scan()` logic
   - Imports `finance_filter()` logic
   - Returns results
5. Frontend displays results
6. User clicks "Execute Trades"
7. Frontend sends HTTP POST to `api.py:/trade`
8. Backend:
   - Imports `mock_trader.py`
   - Creates `MockTrader` instance
   - Executes trades
   - Returns updated portfolio
9. Frontend updates stats display

### **Data Flow:**
```
Reddit Posts
    → extract_tickers()
    → sentiment analysis
    → reddit_scan() DataFrame
    
    ↓
    
finance_filter()
    → yfinance (prices/volume)
    → rank_score calculation
    → filtered DataFrame
    
    ↓
    
display in index.html
    
    ↓
    
User clicks "Execute Trades"
    
    ↓
    
MockTrader (mock_trader.py)
    → position sizing
    → buy orders
    → P&L tracking
    
    ↓
    
simple_ml.py (optional predictions)
    → moving averages
    → momentum calculation
    → trading signals
    
    ↓
    
display in index.html
```

---

## **Development Tips**

### **To Add a New Endpoint:**
Edit `api.py` → Add `@app.post("/new-endpoint")` function

### **To Change Position Sizing:**
Edit `mock_trader.py` → Modify `buy()` method logic

### **To Add New Prediction Indicator:**
Edit `simple_ml.py` → Add method to `SimpleStockPredictor` class

### **To Customize Dashboard:**
Edit `index.html` → Modify HTML, CSS, or JavaScript functions

### **To Change Screener Filters:**
Edit `api.py` → Modify `finance_filter()` function thresholds

---

## **Important Notes**

⚠️ **Legacy Files:** `simple_trader.py`, `stock_trader.py`, `broker_alpaca.py`, `trader_config.py` are old code and can be deleted - they've been replaced by the new simplified system.

✅ **Active Files:** Only `api.py`, `mock_trader.py`, `simple_ml.py`, and `index.html` are needed to run the system.

📁 **Data Files:** `penny_candidates.csv` is generated automatically and can be deleted - it will be recreated on next scan.

🔐 **Credentials:** `.env` file contains sensitive data (Reddit API keys) - keep it private and don't commit to version control.

---

## **File Size Breakdown**

```
Documentation: ~1,000 lines
Core Code: ~1,000 lines
Frontend: ~900 lines
Config: ~25 lines
Legacy: ~500 lines (can delete)
```

**Total Active Codebase:** ~2,000 lines of well-commented, production-quality code.

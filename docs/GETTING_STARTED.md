# Getting Your Trading Bot Moving - Checklist

## ✅ Prerequisite: Get API Keys

### Reddit Credentials
- [ ] Go to https://www.reddit.com/prefs/apps
- [ ] Click "Create App" → Choose "script"
- [ ] Fill in name (e.g., "penny-buzz")
- [ ] Copy `Client ID` and `Client Secret`

### Alpaca Credentials  
- [ ] Go to https://alpaca.markets
- [ ] Sign up (free paper trading account)
- [ ] Verify email
- [ ] Go to Dashboard → API Keys
- [ ] Copy `API Key` and `Secret Key`
- [ ] Note: Paper trading uses `https://paper-api.alpaca.markets`

---

## 📋 Setup Checklist

### Step 1: Create Virtual Environment
```bash
cd c:\Users\barat\stocksa

# Create venv
python -m venv venv

# Activate it
.\venv\Scripts\activate

# You should see (venv) in terminal
```
- [ ] Done

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
- [ ] All packages installed (no errors)

### Step 3: Configure .env File
Edit `c:\Users\barat\stocksa\.env` with your real keys:

```
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=penny-buzz/1.0 by your_reddit_username

ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_API_SECRET=your_alpaca_api_secret_here
```

**⚠️ DO NOT share this file! It has your API keys!**

- [ ] REDDIT_CLIENT_ID filled
- [ ] REDDIT_CLIENT_SECRET filled
- [ ] REDDIT_USER_AGENT filled
- [ ] ALPACA_API_KEY filled
- [ ] ALPACA_API_SECRET filled

### Step 4: Verify File Structure
```
c:\Users\barat\stocksa\
├── .env (with real credentials)
├── api.py (FastAPI backend)
├── simple_trader.py (NEW - trading engine)
├── index.html (web dashboard)
├── quick_test.py (CLI testing)
├── requirements.txt
└── README.md
```
- [ ] All files present

---

## 🚀 Run the System

### Terminal 1: Start FastAPI Server
```bash
cd c:\Users\barat\stocksa
.\venv\Scripts\activate
uvicorn api:app --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
```

- [ ] Server started successfully
- [ ] No errors about missing credentials

### Terminal 2: Test Screener (Optional)
```bash
# In a new terminal (in same directory)
.\venv\Scripts\activate

# Quick test of screener with curl
curl -X POST http://127.0.0.1:8000/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"subreddits\":[\"pennystocks\"],\"lookback_days\":1}"
```

- [ ] Gets a response (will take 30-60 seconds)
- [ ] Returns JSON with ticker data
- [ ] Creates `penny_candidates.csv`

### Terminal 3: Open Dashboard (Optional)
```bash
# In a new terminal, serve the web UI
cd c:\Users\barat\stocksa
python -m http.server 8001
```

Then open browser: `http://localhost:8001/index.html`

- [ ] Web page loads
- [ ] Can see screener and trade forms

---

## 🧪 Test Trading (Dry-Run - Safe!)

### Option A: Using Dashboard
1. Open `http://localhost:8001/index.html`
2. Click "Run Screener" (takes ~30-60 sec)
3. Review results in table
4. **Keep "Live mode?" checkbox OFF**
5. Click "Run Trade"
6. Check results - should show planned trades

- [ ] Screener found tickers
- [ ] Trade plan shows proposed orders
- [ ] No real money spent (dry-run)

### Option B: Using CLI Test Script
```bash
# DRY-RUN (safe) - shows what WOULD happen
python quick_test.py --csv penny_candidates.csv --dry-run
```

Output should show:
```
✅ Planned 5 trades
1. ABCD | 50 shares @ $2.50 | $125.00
2. WXYZ | 200 shares @ $0.50 | $100.00
...
Executed: 5/5 | Failed: 0
Total notional: $500.00
```

- [ ] Script runs without errors
- [ ] Shows proposed trades
- [ ] No real orders placed

---

## 📊 Verify Everything Works

### Check 1: Can Trade Be Placed (Dry-Run)
```bash
python quick_test.py --csv penny_candidates.csv --dry-run
```

- [ ] Shows planned trades
- [ ] Says "[DRY-RUN]" for each trade
- [ ] No errors

### Check 2: Can Connect to Alpaca (Paper)
```python
# Run in Python terminal
from simple_trader import SimpleTrader
trader = SimpleTrader(paper_trading=True)
equity = trader.get_account_equity()
print(f"Account equity: ${equity:,.2f}")
```

- [ ] No "Missing ALPACA_API_KEY" error
- [ ] Shows your account balance
- [ ] Connection successful

### Check 3: Can Price Lookup Work
```python
from simple_trader import SimpleTrader
trader = SimpleTrader(paper_trading=True)
price = trader.get_price("AAPL")
print(f"AAPL price: ${price:.2f}")
```

- [ ] Gets current AAPL price
- [ ] Not None (not zero)

---

## 🎯 When Ready for Small Live Trade

### Step 1: Verify Paper Trading First
- [ ] Run at least 1 dry-run trade
- [ ] Verify it doesn't crash
- [ ] Check Alpaca paper account (should have orders)

### Step 2: Prepare for Live
- [ ] Ensure Alpaca account has cash (even just $100)
- [ ] Decide on small trade size (e.g., $1-5 per trade)
- [ ] Have your .env with LIVE keys (NOT paper)

### Step 3: Run First Live Trade
```bash
# Edit to use small equity
python quick_test.py --csv penny_candidates.csv --equity 100 --live
```

- [ ] Enters confirmation prompt
- [ ] Type "yes" to proceed
- [ ] Check Alpaca account - should have real orders

### Step 4: Monitor First Trade
- [ ] Check Alpaca dashboard for order status
- [ ] Verify order filled or pending
- [ ] Monitor position size (not too large)

---

## ❌ Troubleshooting

### "File not found: penny_candidates.csv"
- [ ] Run screener first (POST /scan or "Run Screener" button)
- [ ] Wait for it to complete (30-60 sec)

### "Missing ALPACA_API_KEY in environment"
- [ ] Check `.env` file exists and has content
- [ ] Make sure it's in the right directory: `c:\Users\barat\stocksa\.env`
- [ ] Verify no typos in API key

### "No Reddit credentials"
- [ ] Check `.env` has REDDIT_CLIENT_ID and SECRET
- [ ] Verify they're not empty strings

### "No trade candidates after filters"
- [ ] Run screener with: `lookback_days=7` (scan more posts)
- [ ] Lower `min_sentiment` (currently 0.10)
- [ ] Lower `min_mentions` (currently 3)

### API Won't Start
```bash
# Kill any existing processes on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Try again
uvicorn api:app --reload
```

### Alpaca Orders Not Going Through
- [ ] Check Alpaca account is approved (should take ~5 min)
- [ ] Verify symbol is tradable on Alpaca
- [ ] Check account has buying power
- [ ] Try with a big, liquid ticker first (AAPL, MSFT)

---

## 📈 Success Metrics

You'll know it's working when:

1. ✅ Screener runs and finds tickers
2. ✅ Dry-run shows proposed trades
3. ✅ Paper trading creates orders on Alpaca
4. ✅ Can toggle between paper and live
5. ✅ Dashboard shows results in real-time

---

## 🔐 Safety Checklist Before Going Live

- [ ] Paper trading tested and works
- [ ] Alpaca account verified and approved
- [ ] Position sizes reasonable (start with 2-5% risk)
- [ ] Screener filters make sense
- [ ] Dashboard and CLI both work
- [ ] You understand what each position means
- [ ] Have a stop-loss plan
- [ ] Only using money you can afford to lose

---

## 📞 Quick Reference

### Commands
```bash
# Start API
uvicorn api:app --reload

# Test screener
curl -X POST http://127.0.0.1:8000/scan -H "Content-Type: application/json" -d "{\"subreddits\":[\"pennystocks\"],\"lookback_days\":1}"

# Test trading (dry-run)
python quick_test.py --csv penny_candidates.csv

# Test trading (live - CAREFUL!)
python quick_test.py --csv penny_candidates.csv --live
```

### Key Files
- `api.py` - Backend
- `simple_trader.py` - Trading logic
- `index.html` - Web UI
- `.env` - Credentials (keep secret!)
- `penny_candidates.csv` - Screener output

### Parameters
- `--equity` - Account size (default $10k)
- `--risk` - Risk per trade % (default 2%)
- `--max-pos` - Max positions (default 10)
- `--min-sentiment` - Filter threshold (default 0.10)
- `--min-mentions` - Minimum mentions (default 3)
- `--live` - Enable real trading (default off)

---

## Final Step: Go Live!

Once everything works in dry-run:

```bash
python quick_test.py \
  --csv penny_candidates.csv \
  --equity 5000 \
  --risk 0.02 \
  --live
```

Then check Alpaca account for real orders.

**Good luck!** 🚀

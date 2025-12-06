# 📈 Penny Buzz Stock Trader

A modern, AI-powered penny stock screener and trading simulator with a beautiful dashboard interface. Scan Reddit for trending stocks, analyze them with machine learning, execute mock trades, and track your portfolio—all without real money involved.

> **📁 NEW:** Project is now organized in a logical directory structure. See [QUICK_START_NEW_STRUCTURE.md](QUICK_START_NEW_STRUCTURE.md) or [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for details.

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install -r config/requirements.txt

# 2. Start the API server
python run_api.py

# 3. Open frontend/index.html in your browser
```

That's it! 🎉

---

## 📁 Project Structure

The project is now organized into logical directories:
- **`/src`** - Python backend (api.py, mock_trader.py, simple_ml.py, etc.)
- **`/frontend`** - Web dashboard (index.html)
- **`/config`** - Configuration (.env, requirements.txt)
- **`/data`** - Generated files (penny_candidates.csv)
- **`/docs`** - Documentation (README, guides, architecture)

👉 **For full details see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**

---

## 📺 Project Demo

Youtube video -
git 

---

## 📋 Project Overview

**Penny Buzz** is an educational stock trading platform that demonstrates:
- Real-time data scraping from Reddit using NLP sentiment analysis
- Financial data filtering and ranking algorithms
- Machine learning price prediction models
- Simulated trading with realistic position sizing
- Modern full-stack web architecture (Python + FastAPI + Vanilla JS)

**Perfect for:** Learning trading concepts, testing strategies, understanding market sentiment analysis, and practicing with zero financial risk.

**Not for:** Real money trading - this is strictly educational/demo mode.

---

## 🎯 Features

✅ **Reddit Stock Screener** - Find trending penny stocks discussed on r/pennystocks, r/smallstreetbets, r/wallstreetbets  
✅ **Sentiment Analysis** - Analyze positive/negative sentiment for each stock using NLP  
✅ **AI Price Predictions** - ML-based price forecasting using moving averages, momentum, and volatility  
✅ **Mock Trading** - Practice trading with simulated $25,000 portfolio (no real money)  
✅ **Real-Time Portfolio** - Track positions, P&L, and trading history  
✅ **Modern Dashboard** - Beautiful gradient UI with responsive design  
✅ **Zero Dependencies** - No broker credentials needed, fully self-contained demo  

---

## 🚀 Quick Start

### 1. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework for the API
- `uvicorn` - ASGI server to run the API
- `praw` - Reddit API client
- `pandas` - Data processing
- `yfinance` - Stock price data
- `nltk` - Sentiment analysis
- `python-dotenv` - Environment variables

### 2. **Setup Reddit API Credentials (Optional)**

To use real Reddit data, create a Reddit app:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" → Select "script"
3. Fill in name, app type, and redirect URI (`http://localhost`)
4. Copy your credentials into `.env`:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=stock-trader-bot/0.1 by your_username
```

**Note:** If you don't have Reddit credentials or they fail, the system automatically uses demo data.

### 3. **Start the API Server**

```bash
cd c:\Users\barat\stocksa
python -m uvicorn api:app --host 127.0.0.1 --port 8001
```

You'll see:
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 4. **Open the Frontend**

Open `index.html` in your web browser:
- Double-click the file in Windows Explorer
- Or drag it into your browser
- Or use: `start index.html` in PowerShell

You should see the Penny Buzz dashboard with purple gradient design.

## 📖 How to Use

### **Step 1: Run the Screener**

1. Set your screener parameters (left panel):
   - **Subreddits**: Reddit communities to scan (default: pennystocks, smallstreetbets, wallstreetbets)
   - **Lookback Days**: How far back to scan (default: 3 days)
   - **Posts per Subreddit**: Number of posts to analyze (default: 400)
   - **Max Stock Price**: Only stocks under this price (default: $5)
   - **Min Dollar Volume**: Minimum daily trading volume (default: $200,000)

2. Click **"🔍 Run Screener"**

3. View results in **"📊 Screener Results"** tab showing:
   - Ticker symbol
   - Number of mentions on Reddit
   - Sentiment score (-1 to +1)
   - Current price
   - Average dollar volume
   - Rank score (combined metric)

### **Step 2: Review AI Predictions**

Click the **"🤖 ML Predictions"** tab to see:
- Current vs predicted price
- Confidence level (0-100%)
- Trend direction (UP/DOWN/NEUTRAL)
- Trading signal (BUY/SELL/HOLD)
- Risk/Reward ratio

### **Step 3: Execute Mock Trades**

1. Set trading parameters (left panel):
   - **Risk per Trade**: What % of portfolio to risk (default: 2%)
   - **Max Positions**: Maximum concurrent trades (default: 10)
   - **Min Sentiment Score**: Only trade stocks with higher sentiment (default: 0.1)
   - **Min Mentions**: Only trade stocks mentioned N times (default: 3)

2. Click **"🚀 Execute Trades (Demo)"**

3. Watch your portfolio update in real-time with P&L

### **Step 4: Monitor Portfolio**

Click **"💼 Portfolio"** tab to see:
- Open positions with entry price and current price
- Number of shares held
- Current value
- Profit/Loss ($ and %)

### **Step 5: Track Trade History**

Click **"📝 Trade Log"** tab to see all executed trades with timestamps.

### **Step 6: Reset and Practice**

Click **"🔄 Reset Portfolio"** to reset back to $25,000 and start over.

## 🏗️ Project Structure

```
stocksa/
├── api.py                 # FastAPI backend (screener, trading, portfolio)
├── mock_trader.py         # MockTrader class for simulated trading
├── simple_ml.py           # SimpleStockPredictor for AI analysis
├── index.html             # Frontend dashboard (HTML/CSS/JavaScript)
├── .env                   # Reddit API credentials
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Core Components

### **api.py - Backend API**
The FastAPI server that handles all requests:
- **POST /scan** - Scan Reddit for stock mentions, filter by price/volume, return ranked list
- **POST /trade** - Execute mock trades based on screened stocks
- **GET /portfolio** - Get current account balance, P&L, positions
- **GET /trade-history** - Get all executed trades
- **POST /predictions** - Get ML price predictions for stocks
- **POST /reset-portfolio** - Reset portfolio to $25,000

### **mock_trader.py - Trading Simulator**
In-memory trading engine with:
- `MockTrader` class - Manages positions, executes buy/sell orders
- `MockPosition` - Tracks entry price, shares, current value, P&L
- Position sizing based on risk percentage
- Full trade history with timestamps
- Portfolio summary with equity, P&L, number of positions

### **simple_ml.py - AI Predictor**
Machine learning price prediction using:
- **Moving Averages** (MA5, MA10, MA20) - Trend detection
- **Momentum** - Price velocity calculation
- **Volatility** - Standard deviation of returns
- **Linear Regression** - Trend fitting
- Returns: predicted price, confidence, trend, support/resistance levels, trading signals

### **index.html - Frontend Dashboard**
Modern responsive UI with:
- **Stats Grid** - Real-time account metrics (equity, P&L, positions, invested)
- **Screener Form** - Adjust Reddit scan parameters
- **Trading Form** - Set trading rules and execute trades
- **Tabbed Results Panel** - View screener results, predictions, portfolio, trades
- **System Log** - Color-coded messages with timestamps
- **Vanilla JavaScript** - No frameworks, pure API integration

## 💡 How It Works Behind the Scenes

### **Screener Pipeline**
1. Connect to Reddit via PRAW (Python Reddit API Wrapper)
2. Scan specified subreddits for recent posts (last N days)
3. Extract stock ticker symbols using regex patterns
4. Analyze sentiment of each post using VADER (Valence Aware Dictionary and sEntiment Reasoner)
5. Count mentions and average sentiment per ticker
6. Fetch real price/volume data from yfinance
7. Filter by price ($0-$5 by default) and volume ($200K+ by default)
8. Calculate rank score (50% mentions, 30% sentiment, 20% volume)
9. Return top ranked stocks sorted by score

### **Trading Pipeline**
1. Load screened stocks from previous scan
2. Generate trading signals using SimpleStockPredictor
3. Size positions using risk-per-trade formula: `position_size = (account_equity × risk_pct) / stop_loss_distance`
4. Create buy orders for qualifying stocks (sentiment > min, mentions > min)
5. Simulate order execution at current market price
6. Track positions in memory with entry prices
7. Calculate P&L as market prices update (demo prices increment slightly each trade)
8. Maintain trade history with full details

### **Fallback System**
- **Reddit fails** → Use hardcoded demo stock list
- **yfinance fails** → Use generated demo prices
- **Both fail** → System still works with demo data end-to-end

## 🎓 What You'll Learn

- **Web APIs** - How FastAPI creates REST endpoints
- **Web Scraping** - How to use PRAW to access Reddit data
- **NLP** - How sentiment analysis works with VADER
- **Data Processing** - How to use pandas to filter and rank data
- **Trading Logic** - Position sizing, risk management, P&L calculations
- **Frontend Integration** - How JavaScript communicates with Python backends
- **Machine Learning** - How to build simple predictive models with moving averages

## 🚨 Troubleshooting

### **"Failed to fetch" error**
- Make sure API server is running: `python -m uvicorn api:app --host 127.0.0.1 --port 8001`
- Make sure browser has `index.html` open (not loading it from file:// in old way)
- Check browser console (F12) for more details

### **Reddit API returns 401 error**
- Credentials in `.env` are incorrect or expired
- No worries! System automatically falls back to demo data
- To fix: Update credentials in `.env` file

### **yfinance "Too Many Requests" error**
- Yahoo Finance rate-limited your requests
- System falls back to demo prices automatically
- Wait a few minutes and try again

### **Port 8000 already in use**
- Another process is using port 8000
- Solution: Use port 8001 instead (already configured)
- Or kill the old process: `Get-Process -Name python | Stop-Process`

## 📊 Example Workflow

```
1. Start API:        python -m uvicorn api:app --host 127.0.0.1 --port 8001
2. Open dashboard:   Double-click index.html
3. Scan Reddit:      Click "Run Screener" → Wait 30-60 seconds
4. View results:     Click "Screener Results" tab
5. Load predictions: Click "ML Predictions" tab
6. Trade:            Click "Execute Trades (Demo)" button
7. Monitor P&L:      Check stats grid at top (equity, P&L, positions)
8. View portfolio:   Click "Portfolio" tab
9. Reset:            Click "Reset Portfolio" when done
```

## 🔐 Security & Privacy

- **No real trading** - All trades are simulated in memory
- **No money at risk** - Uses fake $25,000 account
- **No data stored** - Everything runs locally, nothing uploaded
- **No credentials needed** - Works with or without Reddit API
- **Educational only** - Built for learning, not production use

## 📚 Code Examples

### **Start the API Server**
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8001
```

### **Scan for stocks programmatically**
```python
import requests

response = requests.post("http://127.0.0.1:8001/scan", json={
    "subreddits": ["pennystocks"],
    "lookback_days": 3,
    "price_max": 5.0,
    "min_dollar_vol": 200000
})

stocks = response.json()["rows"]
for stock in stocks:
    print(f"{stock['ticker']}: {stock['mentions']} mentions, {stock['avg_sentiment']:.2f} sentiment")
```

### **Execute mock trades**
```python
response = requests.post("http://127.0.0.1:8001/trade", json={
    "equity": 25000,
    "risk_per_trade": 0.02,
    "max_positions": 10,
    "min_sentiment": 0.1,
    "min_mentions": 3,
    "live": False
})

portfolio = response.json()["portfolio"]
print(f"Equity: ${portfolio['equity']:.2f}")
print(f"P&L: ${portfolio['total_pnl']:.2f}")
```

## 🚀 Next Steps (Optional Enhancements)

- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Integrate TradingView Charts with Chart.js
- Add backtesting engine to test strategies on historical data
- Create strategy templates (momentum, mean reversion, etc.)
- Add real-time WebSocket updates for live price data
- Export trades to CSV for analysis
- Build performance analytics dashboard
- Add multiple account support

---

## 💻 Technologies & Libraries Used

### **Backend Stack**
| Technology | Purpose | Version |
|-----------|---------|---------|
| Python 3 | Core programming language | 3.8+ |
| FastAPI | Web framework for REST APIs | Latest |
| Uvicorn | ASGI server to run FastAPI | Latest |
| PRAW | Python Reddit API Wrapper | Latest |
| pandas | Data processing and analysis | Latest |
| NumPy | Numerical computing | Latest |
| yfinance | Yahoo Finance API client | Latest |
| NLTK | Natural Language Processing | Latest |
| python-dotenv | Environment variable management | Latest |

### **Frontend Stack**
| Technology | Purpose |
|-----------|---------|
| HTML5 | Markup and structure |
| CSS3 | Styling and responsive design |
| Vanilla JavaScript | Client-side logic (no frameworks) |
| Chart.js | Data visualization (included) |

### **Key Libraries & APIs**
- **VADER (Valence Aware Dictionary and sEntiment Reasoner)** - Sentiment analysis
- **Regex** - Ticker symbol extraction
- **CORS Middleware** - Cross-origin request handling
- **Reddit API (PRAW)** - Reddit data access
- **Yahoo Finance** - Stock price and volume data

### **Architecture Pattern**
- **REST API** - Stateless backend endpoints
- **Async/Await** - Non-blocking operations
- **Position Sizing** - Kelly Criterion derivative for risk management
- **Fallback System** - Demo data when external APIs fail

---

## 📖 How to Reproduce Results

### **Step 1: Setup Environment**
```bash
# Clone or download the project
cd stocksa

# Create Python virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configure Credentials**
```bash
# Edit .env file with Reddit API credentials (optional)
# If skipped, system uses demo data automatically
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=stock-trader-bot/0.1 by username
```

### **Step 3: Run Backend**
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8001
```

You should see:
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### **Step 4: Open Frontend**
1. Double-click `index.html` in the project folder
2. Or drag it into your browser
3. Or use: `start index.html` in PowerShell

### **Step 5: Run a Complete Workflow**
1. Click **"🔍 Run Screener"** - Scans Reddit for penny stocks
2. Wait 30-60 seconds for results
3. Click **"📊 Screener Results"** tab to view stocks found
4. Click **"🤖 ML Predictions"** tab to see AI analysis
5. Click **"🚀 Execute Trades (Demo)"** to simulate buying stocks
6. Click **"💼 Portfolio"** tab to see your positions and P&L
7. Click **"🔄 Reset Portfolio"** to start over

### **Expected Results**
- Screener should find 10-50 penny stocks from Reddit
- Each stock shows mentions count, sentiment (-1 to +1), and price
- Executing trades should show realistic position sizing
- Portfolio should show P&L updates
- System should stay responsive even if Reddit/yfinance fails (uses demo data)

---

## 👨‍💻 Author(s) & Contribution Summary

### **Project Creator**
- **Name:** Barath
- **Email:** [Your Email Here]
- **GitHub:** [Your GitHub Profile](#)
- **LinkedIn:** [Your LinkedIn Profile](#)

### **Project Repository**
- **Repository URL:** [https://github.com/username/penny-buzz](#)
- **Issues & Contributions:** [GitHub Issues](#)
- **Discussions:** [GitHub Discussions](#)

### **Contribution Timeline**
| Phase | Date | Contribution |
|-------|------|--------------|
| Phase 1: Simplification | Dec 2025 | Simplified complex multi-file trading system into focused modules |
| Phase 2: Modern UI | Dec 2025 | Redesigned frontend with gradient backgrounds and modern layout |
| Phase 3: ML Integration | Dec 2025 | Added SimpleStockPredictor for price forecasting |
| Phase 4: Documentation | Dec 2025 | Created comprehensive README, comments, and guides |

### **Key Features Implemented**
✅ Reddit sentiment analysis screener
✅ Financial data filtering and ranking
✅ Mock trading simulator (no real money)
✅ ML price predictions with confidence scores
✅ Beautiful responsive dashboard
✅ Real-time portfolio tracking
✅ Complete REST API with 6 endpoints
✅ Fallback system for API failures

### **Code Quality**
- 📝 2,000+ lines of well-commented code
- 🧪 Error handling and fallbacks throughout
- 📊 Comprehensive documentation (README, CODE_COMMENTS, FILE_DIRECTORY)
- 🎨 Modern, responsive UI design
- 🔒 No financial risk (fully simulated)

### **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Suggested Contributions**
- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Implement backtesting engine
- Create Docker containerization
- Add more sentiment sources (Twitter, StockTwits)
- Build analytics dashboard
- Add strategy templates
- Implement paper trading with real market data
- Create mobile app version

---

## 📞 Support & Contact

- **Issues:** Open an issue on GitHub
- **Discussions:** Start a discussion in the GitHub repo
- **Email:** [Your Email](#)
- **Discord/Slack:** [Join our community](#)

---

## 📄 License

Educational project - Free to use, modify, and learn from.

```
MIT License - See LICENSE file for details
```

---

## 🙏 Acknowledgments

- **Reddit** for providing API access to community discussions
- **PRAW** for excellent Python Reddit API wrapper
- **yfinance** for stock price data
- **VADER** for sentiment analysis
- **FastAPI** for modern web framework
- **NLTK** for NLP tools

---

**Happy Trading! (in demo mode)** 📊💡

*Last Updated: December 6, 2025*
*Version: 1.0.0*



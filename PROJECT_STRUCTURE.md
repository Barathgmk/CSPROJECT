# 📁 Project Structure

This document explains the organized directory structure of the Penny Buzz Stock Trader project.

## Directory Layout

```
stocksa/
├── README.md                    # Main project documentation
├── run_api.py                   # Main entry point to start API server
├── .gitignore                   # Git ignore file
│
├── src/                         # Source code (Python backend)
│   ├── api.py                   # FastAPI web server + REST endpoints
│   ├── mock_trader.py           # Simulated trading engine
│   ├── simple_ml.py             # ML price prediction model
│   ├── simple_trader.py         # Simplified trading module
│   ├── stock_trader.py          # Original trader (reference)
│   ├── broker_alpaca.py         # Alpaca broker integration (reference)
│   ├── trader_config.py         # Configuration utilities
│   └── quick_test.py            # Quick testing script
│
├── frontend/                    # Web UI (HTML + CSS + JavaScript)
│   └── index.html               # Main dashboard application
│
├── config/                      # Configuration & environment files
│   ├── .env                     # Reddit & Alpaca API credentials (PRIVATE)
│   └── requirements.txt         # Python package dependencies
│
├── data/                        # Generated data files
│   └── penny_candidates.csv     # Screened stocks output (generated at runtime)
│
├── docs/                        # Documentation
│   ├── README.md                # (moved from root)
│   ├── ARCHITECTURE.md          # System architecture overview
│   ├── CODE_COMMENTS.md         # Detailed code documentation
│   ├── CODE_COMPARISON.md       # Comparison of old vs new code
│   ├── COMPLETION_SUMMARY.md    # Project completion status
│   ├── FILE_DIRECTORY.md        # Complete file reference
│   ├── FINAL_CHECKLIST.md       # Feature checklist
│   ├── GETTING_STARTED.md       # Setup guide
│   ├── QUICK_START.md           # Quick reference
│   ├── SIMPLIFICATION.md        # Simplification process
│   └── SUMMARY.md               # Project summary
│
└── .venv/                       # Python virtual environment (ignored by git)
```

## What Goes Where

### `/src` - Source Code
All Python backend files live here:
- **api.py** - FastAPI server with 6 REST endpoints (scan, trade, portfolio, etc.)
- **mock_trader.py** - In-memory trading simulator without real broker connection
- **simple_ml.py** - ML-based price prediction using moving averages, momentum, volatility
- **simple_trader.py** - Simplified trading module
- Reference files: stock_trader.py, broker_alpaca.py, trader_config.py, quick_test.py

### `/frontend` - Web Application
Frontend files (HTML, CSS, JavaScript):
- **index.html** - Complete dashboard UI with modern gradient design, forms, and charts

### `/config` - Configuration
API credentials and dependencies:
- **.env** - Reddit API credentials (DO NOT COMMIT)
- **requirements.txt** - Python package list for pip install

### `/data` - Generated Data
Runtime-generated files:
- **penny_candidates.csv** - Created when you run the screener (POST /scan)
- Any CSV files downloaded from the frontend

### `/docs` - Documentation
All markdown documentation files explaining the project, architecture, and usage.

---

## How to Run

### 1. **Install Dependencies**
```bash
cd c:\Users\barat\stocksa
pip install -r config/requirements.txt
```

### 2. **Configure Credentials (Optional)**
Edit `config/.env` with your Reddit API credentials. If you skip this, the system uses demo data automatically.

### 3. **Start the API Server**
```bash
python run_api.py
```

You'll see:
```
======================================================================
🚀 Penny Buzz Stock Trader API
======================================================================
Project Root: C:\Users\barat\stocksa
API Server: http://127.0.0.1:8001
Frontend: Open C:\Users\barat\stocksa\frontend\index.html in browser
======================================================================
```

### 4. **Open the Dashboard**
Open `frontend/index.html` in your web browser:
- Double-click the file in Windows Explorer
- Or drag it into your browser
- Or use: `start frontend/index.html` in PowerShell

---

## Key Design Principles

✅ **Logical Organization** - Files grouped by function (src, frontend, config, data, docs)  
✅ **Clear Separation** - No clutter in root directory, everything in proper folders  
✅ **Easy Maintenance** - Find what you need quickly  
✅ **Scalability** - Easy to add new modules to /src, new pages to /frontend, etc.  
✅ **Documentation** - All docs in one place (/docs)  
✅ **Configuration** - All settings in /config  
✅ **Data Isolation** - Generated files separate from source code  

---

## File Dependencies

```
run_api.py
  └── src/api.py
       ├── src/mock_trader.py
       ├── src/simple_ml.py
       ├── config/.env
       └── config/requirements.txt

frontend/index.html
  └── http://127.0.0.1:8001 (API Server)
```

---

## Adding New Features

### Adding a new Python module:
1. Create file in `/src` (e.g., `src/new_module.py`)
2. Import in `src/api.py`
3. Add new endpoint if needed

### Adding new documentation:
1. Create markdown file in `/docs`
2. Update this file to reference it

### Adding new configuration:
1. Add to `/config/.env`
2. Load in `api.py` with `load_dotenv(CONFIG_DIR / ".env")`

### Storing generated data:
1. Files automatically save to `/data` directory
2. No need to change code (already configured in api.py)

---

## Environment Variables

Located in `config/.env`:
```env
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=stock-trader-bot/0.1 by your_username
```

⚠️ **Never commit .env to git!** It contains sensitive credentials.

---

## Common Commands

```bash
# Start API server
python run_api.py

# Install packages
pip install -r config/requirements.txt

# List installed packages
pip list

# Run tests (if available)
python src/quick_test.py

# Check Python version
python --version
```

---

**Last Updated:** December 6, 2025  
**Version:** 1.0.0  
**Structure Created:** Organized from flat root directory into logical folders

"""
api.py

FastAPI backend for the Stock Trader Bot project.

It ties together:
  - A Reddit-based penny-stock screener
  - A finance filter using yfinance
  - A trading bridge into Alpaca (paper trading by default)

Endpoints:
  POST /scan  -> run Reddit + finance screener, save penny_candidates.csv
  POST /trade -> turn CSV into trade plan and optionally place orders
  GET  /files/{filename} -> serve CSV for download

Run locally:
  1. Create and activate a virtualenv.
  2. Install requirements:
       pip install -r requirements.txt
  3. Create a .env file with your Reddit + Alpaca creds (see .env.example).
  4. Start the API:
       uvicorn api:app --reload
"""

import os
import re
import datetime as dt
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Optional

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

import praw

from mock_trader import (
    MockTrader,
    get_mock_trader,
    reset_mock_trader,
    load_and_plan_trades,
    execute_mock_trades,
)
from simple_ml import SimpleStockPredictor, create_sample_predictions

# ---------------------------------------------------------------------------
# Environment + NLTK setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent  # Go up to root directory
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
FRONTEND_DIR = BASE_DIR / "frontend"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(CONFIG_DIR / ".env")

# Download VADER if needed
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

sia = SentimentIntensityAnalyzer()

# ---------------------------------------------------------------------------
# Reddit client
# ---------------------------------------------------------------------------


def get_reddit_client() -> praw.Reddit:
    cid = os.getenv("REDDIT_CLIENT_ID", "").strip()
    secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    ua = os.getenv("REDDIT_USER_AGENT", "stock-trader-bot/0.1 by barath").strip()
    if not cid or not secret:
        raise RuntimeError(
            "Missing Reddit credentials in environment "
            "(REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET)."
        )
    reddit = praw.Reddit(
        client_id=cid,
        client_secret=secret,
        user_agent=ua,
    )
    return reddit


# ---------------------------------------------------------------------------
# Screener logic: scan Reddit -> raw mentions DataFrame
# ---------------------------------------------------------------------------

TICKER_REGEX = re.compile(r"\b[A-Z]{2,5}\b")
COMMON_WORDS = {
    "I", "A", "AN", "IT", "IS", "ARE", "T", "THIS", "YOLO", "THE", "ON", "IN",
    "ALL", "OR", "AND", "DD", "CEO", "CFO", "USA", "OTC", "FOMO", "IMO",
}


def get_demo_reddit_data() -> pd.DataFrame:
    """Return demo stock mention data for testing when Reddit API fails."""
    return pd.DataFrame([
        {"ticker": "ATER", "mentions": 245, "avg_sentiment": 0.68},
        {"ticker": "SRNE", "mentions": 198, "avg_sentiment": 0.52},
        {"ticker": "LGVN", "mentions": 176, "avg_sentiment": 0.71},
        {"ticker": "PSTG", "mentions": 154, "avg_sentiment": 0.45},
        {"ticker": "MULN", "mentions": 142, "avg_sentiment": 0.38},
        {"ticker": "NKTX", "mentions": 128, "avg_sentiment": 0.62},
        {"ticker": "RLMD", "mentions": 115, "avg_sentiment": 0.55},
        {"ticker": "OXBR", "mentions": 98, "avg_sentiment": 0.71},
        {"ticker": "UVXY", "mentions": 87, "avg_sentiment": -0.15},
        {"ticker": "PROG", "mentions": 76, "avg_sentiment": 0.48},
    ])


class ScanParams(BaseModel):
    subreddits: List[str] = ["pennystocks", "smallstreetbets", "wallstreetbets"]
    lookback_days: int = 3
    post_limit_each: int = 400
    price_max: float = 5.0
    min_dollar_vol: float = 200_000.0


def extract_tickers(text: str) -> List[str]:
    """
    Extract stock ticker symbols from text using regex.
    
    Algorithm:
      1. Find all 2-5 character uppercase words using regex
      2. Filter out common non-ticker words (I, A, AND, CEO, etc)
      3. Filter out single-letter or >5 character words
      4. Return remaining matches as potential tickers
    
    Args:
      text: Text to extract tickers from (usually post title + body)
    
    Returns:
      List of ticker symbols found (e.g., ["ATER", "MULN", "SRNE"])
    """
    tickers = []
    for match in TICKER_REGEX.findall(text.upper()):
        if match in COMMON_WORDS:
            continue
        # Crude filter: avoid obvious non-tickers
        if len(match) == 1 or len(match) > 5:
            continue
        tickers.append(match)
    return tickers


def reddit_scan(params: ScanParams) -> pd.DataFrame:
    """
    Scan Reddit subreddits for stock mentions and sentiment.
    
    Algorithm:
      1. Connect to Reddit API using PRAW
      2. Get recent posts from each subreddit (last N days)
      3. Extract ticker symbols from post title + body
      4. Calculate sentiment score for each post using VADER
      5. Count mentions and average sentiment per ticker
      6. Return DataFrame with columns: ticker, mentions, avg_sentiment
    
    Fallback:
      If Reddit API fails (401 unauthorized, timeout, etc),
      automatically returns demo data with 10 popular penny stocks.
    
    Args:
      params: ScanParams with subreddits, lookback_days, post_limit_each
    
    Returns:
      pd.DataFrame with columns: ticker, mentions, avg_sentiment
    """
    try:
        reddit = get_reddit_client()
        # Calculate cutoff date: only scan posts from last N days
        cutoff = dt.datetime.utcnow() - dt.timedelta(days=params.lookback_days)

        # Counter for mention counts
        counts: Counter[str] = Counter()
        # Dict to track sentiment sum per ticker (divide by count later for average)
        sent_sum: defaultdict[str, float] = defaultdict(float)

        # Loop through each subreddit
        for sub_name in params.subreddits:
            sub = reddit.subreddit(sub_name)
            # Get N most recent posts
            for post in sub.new(limit=params.post_limit_each):
                # Convert UTC timestamp to datetime
                created = dt.datetime.utcfromtimestamp(post.created_utc)

                if created < cutoff:
                    continue

                txt = (post.title or "") + "\n" + (post.selftext or "")
                cticks = extract_tickers(txt)
                if not cticks:
                    continue

                score = sia.polarity_scores(txt)["compound"]
                for t in cticks:
                    counts[t] += 1
                    sent_sum[t] += score

        rows = []
        for t, m in counts.most_common():
            s = sent_sum[t] / m if m else 0.0
            rows.append({"ticker": t, "mentions": m, "avg_sentiment": s})
        return pd.DataFrame(rows)
    
    except Exception as e:
        # If Reddit API fails, use demo data instead
        print(f"Reddit API failed: {e}. Using demo data instead.")
        return get_demo_reddit_data()


# ---------------------------------------------------------------------------
# Finance filter: add prices / dollar volume, then compute rank_score
# ---------------------------------------------------------------------------

def finance_filter(raw: pd.DataFrame, price_max: float, min_dollar_vol: float) -> pd.DataFrame:
    """Filter stocks by price and volume. Falls back to demo prices if yfinance fails."""
    if raw.empty:
        return raw

    tickers = raw["ticker"].tolist()
    
    try:
        hist = yf.download(
            tickers=tickers,
            period="1mo",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )

        if isinstance(hist.columns, pd.MultiIndex):
            close = hist["Close"]
            vol = hist["Volume"]
        else:
            close = hist["Close"].to_frame()
            vol = hist["Volume"].to_frame()

        if len(close) == 0 or close.empty:
            raise ValueError("yfinance returned empty data")

        last = close.ffill().iloc[-1]
        avg_dv = (close.tail(10) * vol.tail(10)).mean()
        
    except Exception as e:
        # Fall back to demo prices if yfinance fails
        print(f"yfinance failed: {e}. Using demo prices.")
        last = pd.Series({t: 2.5 + (hash(t) % 30) / 10 for t in tickers})
        avg_dv = pd.Series({t: 500_000 for t in tickers})

    df = raw.copy()
    df["last"] = df["ticker"].map(last.to_dict()).astype(float)
    df["avg_dollar_vol"] = df["ticker"].map(avg_dv.to_dict()).fillna(500_000).astype(float)

    # basic penny / liquidity filters
    df = df[df["last"] > 0]
    df = df[df["last"] <= price_max]
    df = df[df["avg_dollar_vol"] >= min_dollar_vol]

    if df.empty:
        return df

    # simple rank score using normalized metrics
    def norm(col):
        c = df[col].astype(float)
        lo, hi = c.min(), c.max()
        if hi == lo:
            return pd.Series(1.0, index=c.index)
        return (c - lo) / (hi - lo)

    df["rank_score"] = (
        0.5 * norm("mentions") +
        0.3 * norm("avg_sentiment") +
        0.2 * norm("avg_dollar_vol")
    )

    df = df.sort_values(
        ["rank_score", "mentions", "avg_sentiment", "ticker"],
        ascending=[False, False, False, True],
    )
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Penny Buzz Screener + Stock Trader Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TradeParams(BaseModel):
    equity: Optional[float] = None
    risk_per_trade: Optional[float] = None
    max_positions: Optional[int] = None
    min_sentiment: Optional[float] = None
    min_mentions: Optional[int] = None
    live: bool = False


@app.post("/scan")
async def scan(params: ScanParams):
    """
    Main screener endpoint - scan Reddit and filter by finance metrics.
    
    Process:
      1. reddit_scan() - Get stock mentions from Reddit with sentiment
      2. finance_filter() - Add real prices/volume, filter by criteria
      3. Rank by combined score (mentions + sentiment + volume)
      4. Save to CSV and return top results
    
    Fallback:
      If Reddit fails or returns no results, automatically uses demo data.
      If yfinance fails, uses demo prices.
      System is resilient to external API failures.
    
    Args (ScanParams):
      subreddits: List of Reddit communities to scan
      lookback_days: How many days back to scan (3 = 3 days)
      post_limit_each: Max posts per subreddit (400 = scan 400 posts per sub)
      price_max: Only include stocks under this price ($5)
      min_dollar_vol: Only include stocks with $200K+ daily volume
    
    Returns:
      {
        "rows": [{ticker, mentions, avg_sentiment, last, avg_dollar_vol, rank_score}],
        "count_raw": number of mentions found,
        "count_ranked": number after filters applied,
        "csv_filename": saved CSV filename
      }
    """
    try:
        raw = reddit_scan(params)
        if raw.empty:
            raise ValueError("No stock mentions found")
    except Exception as e:
        # Fallback: use demo data if Reddit fails
        print(f"Scan error: {e}. Using demo data.")
        raw = get_demo_reddit_data()

    count_raw = int(len(raw))
    # Apply price and volume filters
    ranked = finance_filter(raw, price_max=params.price_max, min_dollar_vol=params.min_dollar_vol)
    count_ranked = int(len(ranked))

    # Save results to CSV for download
    csv_filename = "penny_candidates.csv"
    ranked.to_csv(DATA_DIR / csv_filename, index=False)

    # Convert to JSON-serializable format
    rows = ranked.to_dict(orient="records")
    return {
        "rows": rows,
        "count_raw": count_raw,
        "count_ranked": count_ranked,
        "csv_filename": csv_filename,
    }


@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Serve CSV files for download by the frontend.
    
    Args:
      filename: Name of file to download (e.g., "penny_candidates.csv")
    
    Returns:
      FileResponse: Binary file contents (browser will download it)
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


@app.post("/trade")
async def trade(params: TradeParams):
    """
    Simulated trading endpoint - execute mock trades.
    
    Process:
      1. Load screened stocks from penny_candidates.csv
      2. Size positions based on risk tolerance and account equity
      3. Filter by sentiment and mention thresholds
      4. Execute mock buy orders (no real money, just simulation)
      5. Track P&L and portfolio changes
      6. Return executed orders and updated portfolio state
    
    Risk Management:
      - Position size = (equity × risk_pct) / distance_to_stop_loss
      - Max positions limit to control diversification
      - Min sentiment to avoid negative discussion stocks
      - Min mentions to avoid pump & dump schemes
    
    Args (TradeParams):
      equity: Account size (default $25,000)
      risk_per_trade: Risk per position as decimal (0.02 = 2%)
      max_positions: Max concurrent positions (10)
      min_sentiment: Minimum sentiment score (-1 to +1)
      min_mentions: Minimum Reddit mentions (3)
      live: Unused in demo mode
    
    Returns:
      {
        "success": bool,
        "message": str,
        "executed": number of trades executed,
        "total_dollars": total notional value traded,
        "orders": [{symbol, shares, price, timestamp}],
        "portfolio": {equity, cash, num_positions, total_pnl, total_pnl_percent}
      }
    """
    # Set trading parameters with defaults
    equity = params.equity or 10_000.0
    risk_per_trade = params.risk_per_trade or 0.02
    max_positions = params.max_positions or 10
    min_sentiment = params.min_sentiment or 0.10
    min_mentions = params.min_mentions or 3
    live = params.live  # Always False for demo mode
    
    csv_path = str(DATA_DIR / "penny_candidates.csv")
    
    try:
        # Load screened stocks and plan position sizes
        trades = load_and_plan_trades(
            csv_path=csv_path,
            account_equity=equity,
            risk_per_trade=risk_per_trade,
            max_positions=max_positions,
            min_sentiment=min_sentiment,
            min_mentions=min_mentions
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not load candidates: {e}")
    
    if not trades:
        return {
            "dry_run": True,
            "message": "No trade candidates after filters and sizing.",
            "picks": [],
            "portfolio": get_mock_trader().get_portfolio_summary(),
        }
    
    # Get or create mock trader
    trader = get_mock_trader()
    
    # Execute trades (in-memory simulation, no real API calls)
    result = execute_mock_trades(
        trades=trades,
        trader=trader,
        side="buy",
        dry_run=False  # Execute in mock trader memory
    )
    
    # Format response
    picks_json = [
        {
            "symbol": t.symbol,
            "price": t.price,
            "mentions": t.mentions,
            "sentiment": t.sentiment,
            "rank_score": t.rank_score,
            "dollars": t.dollars,
            "shares": t.shares,
        }
        for t in trades
    ]
    
    return {
        "dry_run": False,
        "message": result["message"],
        "picks": picks_json,
        "executed": result.get("executed", 0),
        "failed": result.get("failed", 0),
        "total_dollars": result.get("total_dollars", 0.0),
        "portfolio": result["portfolio"],
        "orders": result["orders"],
    }


@app.get("/portfolio")
async def get_portfolio():
    """Get current mock portfolio state"""
    trader = get_mock_trader()
    return trader.get_portfolio_summary()


@app.get("/trade-history")
async def get_trade_history():
    """Get all trades executed in mock trader"""
    trader = get_mock_trader()
    return {"trades": trader.get_trade_history()}


@app.post("/predictions")
async def get_predictions():
    """Get ML price predictions for sample stocks"""
    predictor = SimpleStockPredictor()
    predictions = create_sample_predictions()
    return predictions


@app.post("/reset-portfolio")
async def reset_portfolio():
    """Reset mock portfolio to starting state"""
    reset_mock_trader()
    trader = get_mock_trader()
    return {
        "message": "Portfolio reset to $25,000",
        "portfolio": trader.get_portfolio_summary()
    }


@app.get("/")
async def root():
    return {"message": "Penny Buzz Screener + Stock Trader Bot API. Use POST /scan and POST /trade."}

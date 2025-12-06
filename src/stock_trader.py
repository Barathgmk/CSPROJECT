"""
stock_trader.py

Take the output of your Reddit-based penny screener (penny_candidates.csv)
and turn the top names into position sizes + optional Alpaca market orders.

Workflow:
  1. Run your screener (via POST /scan or separate script) so it overwrites
     `penny_candidates.csv`.
  2. Review the CSV manually.
  3. Run this script in DRY-RUN mode:
        python stock_trader.py --dry-run
  4. If you really want, run with `--live` after testing and with small size.

This is educational, NOT financial advice.
"""

import argparse
import math
from dataclasses import dataclass
from typing import List

import pandas as pd

from trader_config import TraderConfig
from broker_alpaca import AlpacaBroker


@dataclass
class TradeCandidate:
    symbol: str
    price: float
    mentions: int
    sentiment: float
    rank_score: float
    dollars: float
    shares: int


def load_candidates(cfg: TraderConfig) -> pd.DataFrame:
    df = pd.read_csv(cfg.candidates_csv)
    required = {"ticker", "last", "mentions", "avg_sentiment", "rank_score"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    # apply filters
    df = df.copy()
    df = df[df["avg_sentiment"] >= cfg.min_sentiment]
    df = df[df["mentions"] >= cfg.min_mentions]
    df = df.sort_values(
        ["rank_score", "mentions", "avg_sentiment", "ticker"],
        ascending=[False, False, False, True],
    )
    return df.reset_index(drop=True)


def pick_trades(df: pd.DataFrame, cfg: TraderConfig) -> List[TradeCandidate]:
    dollars_per_trade = cfg.dollars_per_trade()
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


def place_trades(picks: List[TradeCandidate], cfg: TraderConfig):
    if not picks:
        print("No trade candidates after filters & sizing.")
        return

    print("\nPlanned trades:")
    print("------------------------------------------")
    for p in picks:
        print(
            f"{p.symbol:6s}  price={p.price:7.3f}  "
            f"shares={p.shares:5d}  notional=${p.dollars:9.2f}  "
            f"mentions={p.mentions:3d}  sent={p.sentiment:+.3f}  rank={p.rank_score:.3f}"
        )
    print("------------------------------------------")
    print(f"Dry-run mode: {cfg.dry_run}")

    if cfg.dry_run:
        print("DRY-RUN: no orders will be sent.")
        return

    # Create broker + send market buy orders
    broker = AlpacaBroker.from_env(cfg.alpaca_key_env, cfg.alpaca_secret_env, cfg.alpaca_base_url)

    for p in picks:
        if not broker.can_trade(p.symbol):
            print(f"Skipping {p.symbol}: not tradable on Alpaca.")
            continue
        try:
            broker.submit_market_order(p.symbol, p.shares, side="buy", dry_run=False)
        except Exception as e:
            print(f"Error submitting order for {p.symbol}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Turn screener CSV into basic trade orders.")
    parser.add_argument(
        "--equity",
        type=float,
        help="Override account equity for sizing (else uses TraderConfig.account_equity).",
    )
    parser.add_argument(
        "--risk-per-trade",
        type=float,
        help="Override risk per trade fraction (e.g. 0.02 = 2%%).",
    )
    parser.add_argument(
        "--max-positions",
        type=int,
        help="Override max positions.",
    )
    parser.add_argument(
        "--min-sentiment",
        type=float,
        help="Override minimum avg_sentiment filter.",
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        help="Override minimum mentions filter.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Turn OFF dry-run and send real market orders (dangerous).",
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Path to screener output CSV (default: penny_candidates.csv).",
    )

    args = parser.parse_args()
    cfg = TraderConfig()

    if args.equity is not None:
        cfg.account_equity = float(args.equity)
    if args.risk_per_trade is not None:
        cfg.risk_per_trade = float(args.risk_per_trade)
    if args.max_positions is not None:
        cfg.max_positions = int(args.max_positions)
    if args.min_sentiment is not None:
        cfg.min_sentiment = float(args.min_sentiment)
    if args.min_mentions is not None:
        cfg.min_mentions = int(args.min_mentions)
    if args.csv_path is not None:
        from pathlib import Path
        cfg.candidates_csv = Path(args.csv_path)

    cfg.dry_run = not bool(args.live)

    print("Using config:")
    print(f"  CSV path       : {cfg.candidates_csv}")
    print(f"  account_equity : ${cfg.account_equity:,.2f}")
    print(f"  risk_per_trade : {cfg.risk_per_trade:.3f} (dollars_per_trade={cfg.dollars_per_trade():.2f})")
    print(f"  max_positions  : {cfg.max_positions}")
    print(f"  min_sentiment  : {cfg.min_sentiment}")
    print(f"  min_mentions   : {cfg.min_mentions}")
    print(f"  dry_run        : {cfg.dry_run}")

    df = load_candidates(cfg)
    picks = pick_trades(df, cfg)
    place_trades(picks, cfg)


if __name__ == "__main__":
    main()

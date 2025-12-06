"""
trader_config.py

Configuration for the screener -> trading bridge.
This is educational only, NOT financial advice.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TraderConfig:
    # Path to the CSV produced by the screener
    candidates_csv: Path = Path("penny_candidates.csv")

    # Risk / sizing parameters (edit for your account)
    account_equity: float = 10_000.0   # total equity to model
    risk_per_trade: float = 0.02       # 2% of equity per position
    max_positions: int = 10            # cap number of open positions

    # Filters on the screener output
    min_sentiment: float = 0.10        # minimum avg_sentiment
    min_mentions: int = 3              # minimum Reddit mentions

    # Broker + safety
    dry_run: bool = True               # True = don't send real orders
    broker_name: str = "alpaca"        # currently only 'alpaca' implemented

    # Alpaca env var names (paper or live, depending on base_url)
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    alpaca_key_env: str = "ALPACA_API_KEY"
    alpaca_secret_env: str = "ALPACA_API_SECRET"

    def dollars_per_trade(self) -> float:
        return self.account_equity * self.risk_per_trade

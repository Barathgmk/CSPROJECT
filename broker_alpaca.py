"""
broker_alpaca.py

Thin wrapper around Alpaca for placing equity orders.

Install:
    pip install alpaca-trade-api

This is NOT production-hardened. Use at your own risk and always
start with paper trading.
"""

import os
from dataclasses import dataclass
from typing import Optional

from alpaca_trade_api import REST, TimeFrame  # type: ignore


@dataclass
class AlpacaCredentials:
    api_key: str
    api_secret: str
    base_url: str


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
    def from_env(cls, key_env: str, secret_env: str, base_url: str) -> "AlpacaBroker":
        key = os.getenv(key_env, "").strip()
        secret = os.getenv(secret_env, "").strip()
        if not key or not secret:
            raise RuntimeError(
                f"Missing Alpaca credentials in {key_env}/{secret_env}. "
                "Set them in your environment or .env file."
            )
        return cls(AlpacaCredentials(api_key=key, api_secret=secret, base_url=base_url))

    # --- basic helpers -------------------------------------------------

    def get_account_equity(self) -> float:
        acct = self.api.get_account()
        return float(acct.equity)

    def can_trade(self, symbol: str) -> bool:
        try:
            asset = self.api.get_asset(symbol)
            return bool(asset.tradable)
        except Exception:
            return False

    def latest_price(self, symbol: str) -> Optional[float]:
        try:
            barset = self.api.get_bars(symbol, TimeFrame.Minute, limit=1)
            if not barset:
                return None
            return float(barset[-1].c)
        except Exception:
            return None

    def submit_market_order(self, symbol: str, qty: int, side: str, dry_run: bool = True):
        side = side.lower()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")

        if qty <= 0:
            raise ValueError("qty must be positive")

        if dry_run:
            print(f"[DRY-RUN] {side.upper()} {qty} {symbol}")
            return None

        print(f"Submitting order: {side.upper()} {qty} {symbol}")
        order = self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type="market",
            time_in_force="day",
        )
        return order

"""
Live market data client using Yahoo Finance.
"""

from datetime import datetime
import yfinance as yf
from pathlib import Path
import csv


class TickerResolver:
    """
    Resolves company names to stock tickers using predefined datasets.
    """

    def __init__(self):
        self.company_to_ticker = {}
        self._load_all()

    def _load_all(self):
        base_dir = Path(__file__).resolve().parents[3]
        data_dir = base_dir / "data" / "processed"

        for file in ["nasdaq_100.csv", "nse_100.csv", "europe_100.csv"]:
            path = data_dir / file
            if path.exists():
                self._load_csv(path)

    def _load_csv(self, path: Path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["company"].lower()
                ticker = row["ticker"]
                self.company_to_ticker[name] = ticker

    def resolve(self, question: str) -> str | None:
        q = question.lower()
        for company, ticker in self.company_to_ticker.items():
            if company in q:
                return ticker
        return None


class MarketDataClient:
    """
    Fetches live market data for equities.
    """

    def get_stock_price(self, ticker: str) -> dict:
        """
        Get the latest stock price for a given ticker.

        Args:
            ticker (str): Stock ticker symbol (e.g., AAPL)

        Returns:
            dict: price info with timestamp
        """
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        latest = data.iloc[-1]

        return {
            "ticker": ticker,
            "price": round(float(latest["Close"]), 2),
            "currency": "USD",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

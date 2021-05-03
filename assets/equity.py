import yfinance

from assets.asset import Asset
from position import Date


class EquityYFinance(Asset):
    def __init__(self, ticker):
        self.ticker = ticker
        self.y = yfinance.Ticker(ticker)
        self.h = self.y.history(period="max")

    def price(self, t: Date) -> float:
        return self.h.Close[t]

    def coupon(self, t: Date) -> float:
        return self.h.Dividends[t]

    def name(self) -> str:
        return self.ticker
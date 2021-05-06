import pandas
import yfinance

from assets.asset import Asset
from common import Date


class EquityYFinance(Asset):
    def __init__(self, ticker):
        super().__init__(ticker)
        self.y = yfinance.Ticker(ticker)
        self.h = self.y.history(period="max")

    def price(self, t: Date) -> float:
        return self.h.Close[t]

    def coupon(self, t: Date) -> float:
        return self.h.Dividends[t]


class IndexPandasSeries(Asset):
    def __init__(self, series: pandas.Series, name: str):
        super().__init__(name)
        self.series = series

    def price(self, t: Date) -> float:
        return self.series[t]

    def coupon(self, t: Date) -> float:
        return 0.0

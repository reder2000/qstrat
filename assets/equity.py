import pandas

from assets.asset import Asset
from common import Date


class EquityYFinance(Asset):
    def __init__(self, ticker):
        from yfinance import Ticker
        super().__init__(ticker, None)
        self.y = Ticker(ticker)
        self.h = self.y.history(period="max")

    def price(self, t: Date) -> float:
        return self.h.Close[t]

    def coupon(self, t: Date) -> float:
        return self.h.Dividends[t]


class IndexPandasSeries(Asset):
    def __init__(self, series: pandas.Series, name: str):
        super().__init__(name, series.index[-1])
        self.series = series

    def price(self, t: Date) -> float:
        return self.series[t]

    def coupon(self, t: Date) -> float:
        return 0.0

    @property
    def index(self):
        return self.series.index

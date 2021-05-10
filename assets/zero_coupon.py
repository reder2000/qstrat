import math

from pandas import Timedelta

from assets.asset import Asset
from common import Date


class ZeroCouponFake(Asset):
    def __init__(self, rate: float, maturity: Date, zname=""):
        super().__init__(zname, maturity)
        self.rate = rate

    def price(self, t: Date) -> float:
        if t >= self.maturity:
            return 0
        dt = (self.maturity - t) / Timedelta(365.25, "D")
        return math.exp(-self.rate * dt)

    def coupon(self, t: Date) -> float:
        if t != self.maturity:
            return 0
        dt = (self.maturity - t) / Timedelta(365.25, "D")
        return math.exp(-self.rate * dt)

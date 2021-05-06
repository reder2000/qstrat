import math

from pandas import Timedelta

from assets.asset import Asset
from common import Date


class ZeroCouponFake(Asset):
    def __init__(self, rate: float, maturity: Date, zname=""):
        self.rate = rate
        self.maturity = maturity
        self.zname = zname

    def name(self):
        return self.zname

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

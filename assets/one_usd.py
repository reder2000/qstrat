from assets.asset import Asset
from common import Date


class OneUsd(Asset):
    def __init__(self):
        super().__init__("ONE_USD", None)

    def price(self, t: Date) -> float:
        return 1.0

    def coupon(self, t: Date) -> float:
        return 0

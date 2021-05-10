from assets.asset import Asset
from common import Date


class ConstantAsset(Asset):
    def __init__(self, value: float, name=None):
        super().__init__(None, None)
        self.value = value

    def price(self, t: Date) -> float:
        return self.value

    def coupon(self, t: Date) -> float:
        return 0

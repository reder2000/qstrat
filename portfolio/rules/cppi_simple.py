# example rule : CPPI with guarantee


from typing import Tuple

from assets.asset import Asset
from common import Date
from portfolio.position import Position
from portfolio.rule import Rule


class CPPI_simple(Rule):
    def __init__(
        self,
        risky_asset: Asset,
        zero_coupon: Asset,
        maturity: Date,
        multiplier: float,
        guarantee: float,
    ):
        self.risky_asset = risky_asset
        self.zero_coupon = zero_coupon
        self.assets = [risky_asset, zero_coupon]
        self.maturity = maturity
        self.multiplier = multiplier
        self.guarantee = guarantee
        # check ZC
        assert zero_coupon.full_price(maturity) == 1.0

    def new_position(
        self, at_date: Date, pv: float, previous_position: Position
    ) -> Tuple[Position, float, float]:
        # compute cushion
        cushion = pv - self.guarantee * self.zero_coupon.full_price(at_date)
        if cushion < 0:
            # bank pays guarantee
            res = Position(self.assets, [0.0, self.guarantee]), None, cushion
        else:
            res = (
                Position(
                    self.assets,
                    [
                        cushion * self.multiplier / self.risky_asset.price(at_date),
                        self.guarantee,
                    ],
                ),
                None,
                None,
            )
        return res

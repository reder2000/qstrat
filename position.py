from copy import copy
from typing import List

from assets.asset import Asset
from common import Date


class Position:
    def __init__(self, assets: List[Asset] = None, shares: List[float] = None):
        self.assets = [] if assets is None else assets
        self.shares = [] if shares is None else copy(shares)

    def add_assets(self, new_assets: List[Asset]):
        self.assets += new_assets
        self.shares += [0.0] * len(new_assets)

    def full_value(self, at_date: Date) -> float:
        """
        value with coupon
        :param at_date:
        :return:
        """
        res = 0.0
        if self.assets:
            for a, s in zip(self.assets, self.shares):
                res += a.full_price(at_date) * s
        return res

    def net_value(self, at_date: Date) -> float:
        """
        value after coupon
        :param at_date:
        :return:
        """
        res = 0.0
        if self.assets:
            for a, s in zip(self.assets, self.shares):
                res += a.price(at_date) * s
        return res

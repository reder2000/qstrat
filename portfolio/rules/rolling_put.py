import math
from copy import copy
from typing import Tuple

from assets.asset import Asset
from common import Date, indexing_dict
from portfolio.position import Position
from portfolio.rule import Rule
from pricer.option_cube import cboe_calendar_daycount


class RollingPut(Rule):
    def __init__(self, udl: Asset, option_cube):
        self.udl = udl
        # date X expiries X strikes options dataframe
        self.option_cube = option_cube
        self.assets_dict = indexing_dict()
        self.assets = []

    def new_position(
        self, at_date: Date, pv: float, previous_position: Position
    ) -> Tuple[Position, float, float]:
        # cut strat at < 20
        if pv < 20:
            shares = [0.0] * len(previous_position.shares)
            return Position(self.assets, shares), 0.0, 0.0
        oc = self.option_cube[at_date]
        # find back spot
        spot = self.udl.price(at_date)
        # number of days
        nb_days = cboe_calendar_daycount(oc.index[0], oc.index[1])
        # notional
        put_notional = pv / (3.5 * nb_days * spot)
        # find put with strike closest to 90%
        oe = oc.iloc[4]
        target_strike = 0.9 * spot
        i_s = oe.index.get_loc(target_strike, "nearest")
        if i_s > 0 and oe.index[i_s] > target_strike:
            # tie ?
            d1 = target_strike - oe.index[i_s - 1]
            d2 = oe.index[i_s] - target_strike
            if math.fabs(d1 - d2) < 1e-8:  # take smaller
                i_s = i_s - 1
        put = oe.iloc[i_s]
        # return results, adding put if necessary
        shares = copy(previous_position.shares)
        if not put.name in self.assets_dict:
            self.assets.append(put)
            shares.append(0.0)
        put_index = self.assets_dict[put.name]
        shares[put_index] += put_notional
        return Position(self.assets, shares), 0.0, 0.0

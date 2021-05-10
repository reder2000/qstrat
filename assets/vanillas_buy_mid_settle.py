# vanilla option worth
# BS price on inception
# mid price when available, intrinsic value else
# exercice price for settlement udl
import math
from math import isnan

import pandas
from pandas import Timedelta

from assets.asset import Asset
from common import Date
from pricer.black_scholes import BlsPriceP, BlsPriceC


def vanilla_put_buy_mid_impl_option_name(
    call_or_put: str, udl_name: str, maturity: Date, strike: float, inception: Date
) -> str:
    """ bbg like name """
    d_str = lambda d: d.strftime("%m/%d/%y")
    res = f"{udl_name} {d_str(maturity)} {call_or_put}{strike} {d_str(inception)}"
    return res


class VanillaOptionBuyMidImpl(Asset):
    def __init__(
        self,
        option_type: str,
        mid_price: Asset,
        udl: Asset,
        initial_vol: float,
        initial_forward: float,
        inception: Date,
        maturity: Date,
        strike: float,
        calendar: pandas.Index,
        udl_for_exercice=None,
    ):
        assert option_type == "P" or option_type == "C"
        name = vanilla_put_buy_mid_impl_option_name(
            option_type, udl.name, maturity, strike, inception
        )
        super().__init__(name, maturity)
        self.option_type = option_type
        self.mid_price = mid_price
        self.udl = udl
        self.initial_vol = initial_vol
        self.initial_forward = initial_forward
        self.inception = inception
        self.strike = strike
        self.calendar = calendar
        self.udl_for_exercice = udl if udl_for_exercice is None else udl_for_exercice
        if option_type == "P":
            self.bs_function = BlsPriceP
            self.intrinsic_value = lambda x: max(0, self.strike - x)
        else:
            self.bs_function = BlsPriceC
            self.intrinsic_value = lambda x: max(0, x - self.strike)

    def price(self, t: Date) -> float:
        if t >= self.maturity:
            return 0
        elif t == self.inception:
            # TODO calendar
            dt = (self.maturity - t) / Timedelta(365, "D")
            return self.bs_function(
                self.initial_forward, self.strike, 0.0, dt, self.initial_vol, 0.0
            )
        else:
            if t in self.mid_price.index:
                p = self.mid_price.price(t)
                if not isnan(p):
                    return p
                else:
                    S = self.udl.price(t)
                    return self.intrinsic_value(S)

    def coupon(self, t: Date) -> float:
        if t != self.maturity:
            return 0
        S = self.udl_for_exercice.price(t)
        return self.intrinsic_value(S)


if __name__ == "__main__":

    def sest():
        from assets.one_usd import OneUsd
        from assets.equity import IndexPandasSeries
        from assets.constant import ConstantAsset
        import pandas

        udl = ConstantAsset(0.9)
        mid_prices = IndexPandasSeries(
            pandas.Series(
                [0.15, math.nan, 0.075],
                [Date(2019, 1, 1), Date(2019, 2, 1), Date(2019, 3, 1)],
            ),
            "mid",
        )
        udl_for_exercice = ConstantAsset(0.95)
        calendar = None
        inception = Date(2018, 12, 31)
        maturity = Date(2019, 4, 1)
        vp = VanillaOptionBuyMidImpl(
            "P",
            mid_prices,
            udl,
            0.2,
            1.0,
            inception,
            maturity,
            1.0,
            calendar,
            udl_for_exercice,
        )
        print(vp.price(inception))
        print(vp.price(mid_prices.index[0]))
        print(vp.price(mid_prices.index[1]))
        print(vp.price(mid_prices.index[2]))
        print(vp[maturity])

    sest()

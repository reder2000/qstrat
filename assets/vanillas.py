from abc import ABC, abstractmethod

from pandas import Timedelta

from assets.asset import Asset
from common import Date
from pricer.black_scholes import BlsPriceP, BlsPriceC


class ImpliedVol(ABC):
    @abstractmethod
    def __call__(self, at_date, K: float, T: Date):
        raise NotImplementedError


# example vol impl = constant
class ImpliedVolConstant(ABC):
    def __init__(self, s):
        self.s = s

    def __call__(self, at_date, K: float, T: Date):
        return self.s


def vanilla_option_name(
    call_or_put: str, udl_name: str, maturity: Date, strike: float
) -> str:
    """ bbg like name """
    d_str = maturity.strftime("%m/%d/%y")
    res = f"{udl_name} {d_str} {call_or_put}{strike} Index"
    return res


class VanillaOption(Asset):
    def __init__(
        self,
        udl: Asset,
        ivol: ImpliedVol,
        maturity: Date,
        strike: float,
        udl_for_exercice=None,
        name=None,
    ):
        super().__init__(name, maturity)
        self.udl = udl
        self.ivol = ivol
        self.strike = strike
        self.udl_for_exercice = udl if udl_for_exercice is None else udl_for_exercice


class VanillaPut(VanillaOption):
    def __init__(
        self,
        udl: Asset,
        ivol: ImpliedVol,
        maturity: Date,
        strike: float,
        udl_for_exercice=None,
        name=None,
    ):
        if name is None:
            name = vanilla_option_name("P", udl.name, maturity, strike)
        super().__init__(udl, ivol, maturity, strike, udl_for_exercice, name)

    def price(self, t: Date) -> float:
        if t >= self.maturity:
            return 0
        else:
            S = self.udl.price(t)
            sig = self.ivol(t, self.strike, self.maturity)
            dt = (self.maturity - t) / Timedelta(365, "D")
            return BlsPriceP(S, self.strike, 0.0, dt, sig, 0.0)

    def coupon(self, t: Date) -> float:
        if t != self.maturity:
            return 0
        S = self.udl_for_exercice.price(t)
        return max(0, self.strike - S)


class VanillaCall(VanillaOption):
    def __init__(
        self,
        udl: Asset,
        ivol: ImpliedVol,
        maturity: Date,
        strike: float,
        udl_for_exercice=None,
        name=None,
    ):
        if name is None:
            name = vanilla_option_name("P", udl.name, maturity, strike)
        super().__init__(udl, ivol, maturity, strike, udl_for_exercice, name)

    def price(self, t: Date) -> float:
        if t >= self.maturity:
            return 0
        else:
            S = self.udl.price(t)
            sig = self.ivol(t, self.strike, self.maturity)
            dt = (self.maturity - t) / Timedelta(365, "D")
            return BlsPriceC(S, self.strike, 0.0, dt, sig, 0.0)

    def coupon(self, t: Date) -> float:
        if t != self.maturity:
            return 0
        S = self.udl_for_exercice.price(t)
        return max(0, -self.strike + S)


if __name__ == "__main__":

    def test():
        from assets.one_usd import OneUsd

        fake_asset = OneUsd()
        vp = VanillaPut(fake_asset, ImpliedVolConstant(0.2), Date(2019, 12, 31), 1.0)
        print(vp.price(Date(2018, 12, 31)))

from copy import copy
from typing import Tuple, List

from pandas import DataFrame

from assets.asset import Asset
from assets.equity import EquityYFinance
from assets.zero_coupon import ZeroCouponFake
from position import Date, Position
from rule import Rule, CPPI_simple

to_float = lambda x: 0.0 if x is None else x


class PortfolioTrack:
    def __init__(self, cash_asset: Asset):
        self.cash_asset_name = cash_asset.name()
        self.dates = []
        self.pv = []
        self.inflows = []
        self.outflows = []
        self.cash_values = []
        self.position_values = []
        self.positions = []
        self.last_position: Position = None

    def add(
        self, at_date: Date, pv, new_position: Position, inflow, outflow, cash_value
    ):
        self.dates.append(at_date)
        self.pv.append(pv)
        self.inflows.append(inflow)
        self.outflows.append(outflow)
        self.cash_values.append(cash_value)
        pvs = [
            s * a.price(at_date)
            for s, a in zip(new_position.shares, new_position.assets)
        ]
        self.position_values.append(pvs)
        self.positions.append(copy(new_position.shares))
        self.last_position = new_position

    def get(self) -> DataFrame:
        index = self.dates
        names = [a.name() for a in self.last_position.assets]
        columns = ["pv", "in", "out", "cash"] + [n + "_v" for n in names] + names
        a = []
        n = len(names)
        for i in range(len(index)):
            t = [self.pv[i], self.inflows[i], self.outflows[i], self.cash_values[i]]
            t += self.position_values[i] + [None] * (n - len(self.position_values[i]))
            t += self.positions[i] + [None] * (n - len(self.positions[i]))
            a.append(t)
        res = DataFrame(a, index, columns)
        return res


class Portfolio:
    def __init__(
        self,
        rule: Rule,
        cash_asset: Asset,
        start_value,
        start_date,
        start_position: Position = None,
    ):
        self.rule = rule
        self.cash_asset = cash_asset
        self.start_value = start_value
        self.start_date = start_date
        self.current_position = Position() if start_position is None else start_position
        self.portfolio_track = PortfolioTrack(cash_asset)

    def full_cash_value(self, at_date):
        return self.cash_position * self.cash_asset.full_price(at_date)

    def cash_value(self, at_date):
        return self.cash_position * self.cash_asset.price(at_date)

    def advance_to(self, at_date: Date):
        # compute current value of portfolio
        position_pv_start = self.current_position.full_value(at_date)
        pv_start = self.full_cash_value(at_date) + position_pv_start
        # get new position, inflows & outflows
        new_position, inflow, outflow = self.rule.new_position(
            at_date, pv_start, self.current_position
        )
        # set new position
        new_position_pv = new_position.net_value(at_date)
        new_pv_unadjusted_cash = new_position_pv + self.cash_value(at_date)
        delta_cash = (
            pv_start - new_pv_unadjusted_cash + to_float(inflow) - to_float(outflow)
        )
        new_cash = self.full_cash_value(at_date) + delta_cash
        self.cash_position = new_cash / self.cash_asset.price(at_date)
        new_pv = new_position_pv + new_cash

        self.current_position = new_position
        self.portfolio_track.add(
            at_date, new_pv, new_position, inflow, outflow, new_cash
        )

        return new_pv

    def compute(self, dates: List[Date]):
        assert dates[0] == self.start_date
        cash_value = self.start_value - self.current_position.net_value(dates[0])
        self.cash_position = cash_value / self.cash_asset.price(dates[0])
        self.portfolio_track.add(
            dates[0],
            self.start_value,
            self.current_position,
            self.start_value,
            0,
            cash_value,
        )
        for d in dates[1:]:
            pv = self.advance_to(d)

    def report(self) -> DataFrame:
        return self.portfolio_track.get()


# GLE CCPI
risky_asset = EquityYFinance("GLE.PA")
maturity = Date(2025, 1, 5)
zero_coupon = ZeroCouponFake(0.01, maturity, "long_rate_1")
rule = CPPI_simple(risky_asset, zero_coupon, maturity, 25, 80.0)
cash_asset = ZeroCouponFake(0.001, Date(2100, 1, 1), "cash_10_bp")
start_date = Date(2021, 1, 4)
portfolio = Portfolio(rule, cash_asset, 100.0, start_date)
dates = risky_asset.h.index[risky_asset.h.index >= start_date]
portfolio.compute(dates)
portfolio.report().to_clipboard()

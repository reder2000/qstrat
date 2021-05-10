from assets.one_usd import OneUsd
from common import Date
from portfolio.portfolio import Portfolio
from portfolio.rules.rolling_put import RollingPut
from pricer.option_cube import generate_cube


def example_rolling():
    start_date = Date(2019, 1, 3)
    oc = generate_cube(start_date, 0.88, 0.92)
    udl = oc.iloc[0].iloc[1].iloc[0].udl
    udls = udl.series
    dates = udls.index[udls.index.get_loc(Date(2019, 1, 3)) : :]
    cash_asset = OneUsd()
    rule = RollingPut(udl, oc)
    portfolio = Portfolio(rule, cash_asset, 100.0, start_date)
    portfolio.compute(dates)
    portfolio.report().to_clipboard()
    print(portfolio.report().head())


if __name__ == "__main__":
    example_rolling()

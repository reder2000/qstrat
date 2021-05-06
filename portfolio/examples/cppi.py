from assets.equity import EquityYFinance
from assets.zero_coupon import ZeroCouponFake
from common import Date
from portfolio.portfolio import Portfolio
from portfolio.rules.cppi_simple import CPPI_simple


def gle_cppi():
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
    print(portfolio.report().head())


if __name__ == "__main__":
    gle_cppi()

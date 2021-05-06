# date X expiries X strikes options dataframe
import math
import warnings
from typing import Dict

import pandas
import trading_calendars
from pandas import Timedelta
from trading_calendars.exchange_calendar_xcbf import XCBFExchangeCalendar
from xbbg import blp

from assets.vanillas import (
    VanillaOption,
    vanilla_option_name,
    VanillaPut,
    ImpliedVolConstant,
)
from assets.equity import IndexPandasSeries
from common import Date


warnings.simplefilter("ignore")


def cboe_calendar_is_session(a_date):
    assert a_date.date() < cboe_calendar_is_session.calendar.schedule.index[-1].date()
    return cboe_calendar_is_session.calendar.is_session(a_date)


cboe_calendar_is_session.calendar = XCBFExchangeCalendar(
    end=trading_calendars.trading_calendar.end_base + pandas.Timedelta(days=3 * 365)
)


def cboe_calendar_daycount(start_date, end_date, include_end_date=False):
    i_s = cboe_calendar_is_session.calendar.schedule.index.get_loc(start_date)
    i_e = cboe_calendar_is_session.calendar.schedule.index.get_loc(end_date)
    return i_e - i_s + (1 if include_end_date else 0)


def next_spx_expiry(a_date: Date):
    # 3d friday of each month
    y = a_date.year
    m = a_date.month
    # The day of the week with Monday=0, Sunday=6. (Friday=4)
    dow = Date(a_date.year, m, 1).dayofweek
    if dow > 4:
        d = 1 + 3 * 7 + (4 - dow)
    else:
        d = 1 + 2 * 7 + (4 - dow)
    while not cboe_calendar_is_session(Date(y, m, d)):
        d += 1
    res = Date(y, m, d)
    if res < a_date:
        return next_spx_expiry(Date(y, m + 1, 1))
    return res


def generate_n_spx_expiries(month: int, year: int, n: int, freq="Q"):
    res = []
    d = Date(year, month, 1)
    if freq == "Q":
        dt = 3
    elif freq == "M":
        dt = 1
    else:
        assert False
    for i in range(n):
        res.append(next_spx_expiry(d))
        year += (month + dt - 1) // 12
        month = (month + dt - 1) % 12 + 1
        d = Date(year, month, 1)
    return res


# populate an option cube with flat vol expiries and strikes
def generate_cube(start_date: Date, low_pct_range=0.85, up_pct_range=1.15):
    all_options: Dict[str, VanillaOption] = {}
    all_expiries = pandas.DatetimeIndex(generate_n_spx_expiries(3, 2000, 23 * 4))
    if 0:
        spx_series = blp.bdh("SPX Index", ["PX_LAST"], pandas.Timestamp(2000, 1, 1))[
            "SPX Index"
        ]["PX_LAST"]
    else:
        spx_series = pandas.read_csv("c:/tmp/spx.csv", index_col=0, parse_dates=True)[
            "PX_LAST"
        ]
    spx_udl = IndexPandasSeries(spx_series, "SPX US")
    i0 = spx_series.index.get_loc(start_date, "bfill")
    dates_exp_puts = []
    dates = spx_series.index[i0::]
    for d in dates:
        # get 6 expiries : [previous,next,...]
        i_e = all_expiries.get_loc(d, "ffill")
        expiries = [e for e in all_expiries[i_e : i_e + 6]]
        # range of strikes
        atm = spx_series[d]
        atm = round(atm / 5) * 5
        lower_atm = math.floor(atm * low_pct_range / 5) * 5
        upper_atm = math.ceil(atm * up_pct_range / 5) * 5
        i_s, i_e = (lower_atm - atm) // 5, (upper_atm - atm) // 5 + 1
        strikes = [atm + 5 * i for i in range(i_s, i_e)]
        exp_puts = [None]  # empty 1st expiry = previous
        for e in expiries[1:]:
            puts = []
            for s in strikes:
                name = vanilla_option_name("P", "SPX US", e, s)
                if not name in all_options:
                    all_options[name] = VanillaPut(
                        spx_udl, ImpliedVolConstant(0.2), e, s, spx_udl, None
                    )
                puts.append(all_options[name])
            exp_puts.append(pandas.Series(puts, strikes))
        dates_exp_puts.append(pandas.Series(exp_puts, expiries))
    res = pandas.Series(dates_exp_puts, dates)
    return res


if __name__ == "__main__":
    next_spx_expiry(Date(2022, 5, 5))
    next_spx_expiry(Date(2021, 5, 25))
    generate_n_spx_expiries(1, 2021, 10)
    generate_cube(Date(2021, 4, 1), 0.85, 0.95)

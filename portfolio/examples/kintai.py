# option list expiration = friday modified preceding (w)

# pack expi = next expi >= t + 3 bd

# pack select = price > 0.2

# price = settlement price

# selection :
# (hidden 0. : no implied BS vol)
#   1. order ( | opt delta - 5% | , strike )
#   2.  take 3 strikes or all options if less

# quantity = -1 / (spot * #options)
# spot = SX5E spot

# opt delta  :
#    BSDelta with
#       spot = DhObs
#       vol = implied BS

# implied BS:
# such as BS = OptionMid
# if no implied_bs (but in context of P&L : previous implied BS)

# BS Formula
# spot = Forward
# Time = business days / 252

# Forward :
# find center strike K such as |Cmid(K)-Pmid(K)| = min (and K = min)
# fd = K + Compound(Calendar Days) * (Cmid(K)-Pmid(K))

# option price for P&L
# if roll : BS price (forward) +/- bump
# if < expi : option mid, else intrisinc value
# if = expi : intrinsic value(UsedExpirySpot)

# UsedExpirySpot = SettlementSpot

# DhObs (forward used for delta) :
# roll : Forward
# else : Forward(t-1) TWAP / FutSettle(t-1)

# quantity mult  (for weeklys) = 2/5 * NAV_index_roll_day-1
import heapq
from dataclasses import dataclass
from math import fabs

import pandas

from common import Date

# options in hypercube
# - delta from BSImplied
# mid prices
#    - needs forward => needs Put+Call
from pricer.option_cube import CallPutOptionHyperCube, T

class  fake_option:
    @property
    def mid_price(self) -> float:
        pass
    def set_forward(self,at_date,value):
        pass
    def delta(self) -> float:
        # delta = None if no implied vol
        pass

# forward for given date/expiry
def forward_from_cube(iat_date: int, expiry_number:int, option_cube:CallPutOptionHyperCube[fake_option],rate_compound):
    puts = option_cube.puts.iloc[iat_date].iloc[expiry_number]
    calls = option_cube.calls.iloc[iat_date].iloc[expiry_number]
    # keeping common strikes
    common_strikes = set(puts.index) & set(calls.index)
    assert len(common_strikes)
    # mid price distance
    c_p  = lambda i : calls.iloc[i].mid_price , puts.iloc[i].mid_price
    c , p = c_p(0)
    K , M = common_strikes[0] , fabs(c-p)
    # find least mid price distance and lowest strike
    for i in range(1,len(common_strikes)):
        k , cc , pp = common_strikes[i] , *c_p(i)
        d = fabs(c-p)
        if d<M or (d<=M and k<K):
            K,M,c,p = k,d,cc,pp
    res = K + rate_compound * (c-p)
    return res


def selection(iat_date: int, expiry_number:int, option_cube:CallPutOptionHyperCube[fake_option], retain:int
              , target_delta:float):
    fwd = forward_from_cube(iat_date,expiry_number,option_cube)
    puts = option_cube.puts.iloc[iat_date].iloc[expiry_number]
    l = []
    N = len(puts.index)
    n = min(N,retain)
    for i in range(N):
        delta = puts.iloc[i].delta()
        if delta is not None:
            heapq.heappush(l, (fabs(delta - target_delta), puts.index[i]))
        if len(l) > retain:
            heapq.heappop()





#
# class KintaiPutW(Rule):
#     def __init__(self, udl: Asset, option_cube):
#         self.udl = udl
#         # date X expiries X strikes options dataframe
#         self.option_cube = option_cube
#         self.assets_dict = indexing_dict()
#         self.assets = []
#
#     def new_position(
#         self, at_date: Date, pv: float, previous_position: Position
#     ) -> Tuple[Position, float, float]:
#         # cut strat at < 20
#         if pv < 20:
#             shares = [0.0] * len(previous_position.shares)
#             return Position(self.assets, shares), 0.0, 0.0

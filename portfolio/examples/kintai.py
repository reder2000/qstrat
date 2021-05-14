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
from common import Date


def selection_weeklies(at_date: Date, option_cube, calendar):
    oc = option_cube[at_date]
    expiry = oc.iloc[0]


class KintaiPutW(Rule):
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

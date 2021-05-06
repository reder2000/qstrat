from math import log, sqrt, fabs, exp
from statistics import NormalDist


def NormCdf(x):
    return NormalDist().cdf(x)


def BlsD1(S0, X, R, T, sig, Q):
    return (log(S0 / X) + (R - Q + sig * sig / 2) * T) / (sig * sqrt(T))


def BlsD2(S0, X, R, T, sig, Q):
    if S0 == 0:
        if X == 0:
            return 20
        else:
            return -20
    if X == 0:
        return 20

    return (log(S0 / X) + (R - Q - sig * sig / 2) * T) / (sig * sqrt(T))


def quick_BlsD2(d1, T, sig):
    return d1 - (sig * sqrt(T))


def BlsCheckParams(S0, X, R, T, sig, Q):
    assert not ((S0 < 0) or (X < 0) or (R < 0) or (T < 0) or (sig < 0))


def BlsPriceP(S0, X, R, T, sig, Q):
    BlsCheckParams(S0, X, R, T, sig, Q)
    if fabs(T) < 1e-8:
        return max(X - S0, 0)
    d1 = BlsD1(S0, X, R, T, sig, Q)
    d2 = quick_BlsD2(d1, T, sig)
    put = X * exp(-R * T) * NormCdf(-d2) - S0 * exp(-Q * T) * NormCdf(-d1)
    return put


def BlsPriceC(S0, X, R, T, sig, Q):
    BlsCheckParams(S0, X, R, T, sig, Q)
    if fabs(T) < 1e-8:
        return max(S0 - X, 0)
    if X > 0:
        d1 = BlsD1(S0, X, R, T, sig, Q)
        d2 = quick_BlsD2(d1, T, sig)
    else:
        d1 = 20
        d2 = 20
    res = S0 * exp(-Q * T) * NormCdf(d1) - X * (exp(-R * T) * NormCdf(d2))
    return res

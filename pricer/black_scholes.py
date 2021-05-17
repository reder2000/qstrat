from math import log, sqrt, fabs, exp
from statistics import NormalDist

from scipy.optimize import brentq


def NormCdf(x):
    return NormalDist().cdf(x)


def BlsD1(S0, X, R, T, sig, Q):
    if S0 == 0:
        if X == 0:
            return 20
        else:
            return -20
    if X == 0:
        return 20
    if sig == 0:
        sig = 1e-9

    return (log(S0 / X) + (R - Q + sig * sig / 2) * T) / (sig * sqrt(T))


def BlsD2(S0, X, R, T, sig, Q):
    if S0 == 0:
        if X == 0:
            return 20
        else:
            return -20
    if X == 0:
        return 20
    if sig == 0:
        sig = 1e-9

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

def BlsImpliedVol(CallOrPut:str,S0,X,R,T,Q,price):
    # return None = not found
    BlsCheckParams(S0, X, R, T, 0.2, Q)
    assert CallOrPut == "P" or  CallOrPut == "C"
    fn = BlsPriceC if CallOrPut == "C" else BlsPriceP
    f = lambda s : fn(S0,X,R,T,s,Q) - price
    # scipy raises anyway in this case. What's the use of disp then ?
    if f(0.)*f(10.) > 0:
        return None
    root,r = brentq(f,0.,10.,full_output=True,disp=False)
    return root if r.converged else None

if __name__ == "__main__":

    def  te_ImpliedVol():
        pr = BlsPriceC(1.,1.,0.,1.,0.2,0.)
        print(BlsImpliedVol("C",1.,1.,0.,1.,0.,pr))
        print(BlsImpliedVol("C", 1., 1., 0., 1., 0., 1000))

    te_ImpliedVol()
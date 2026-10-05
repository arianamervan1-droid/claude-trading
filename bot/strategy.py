"""Long-only SMA crossover with a trend filter. Returns 'buy', 'sell' or 'hold'."""


def sma(values, n):
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def signal(closes, fast=20, slow=50):
    f, s = sma(closes, fast), sma(closes, slow)
    pf, ps = sma(closes[:-1], fast), sma(closes[:-1], slow)
    if None in (f, s, pf, ps):
        return "hold"
    if pf <= ps and f > s:
        return "buy"
    if pf >= ps and f < s:
        return "sell"
    return "hold"


def in_uptrend(closes, fast=20, slow=50):
    f, s = sma(closes, fast), sma(closes, slow)
    return f is not None and s is not None and f > s

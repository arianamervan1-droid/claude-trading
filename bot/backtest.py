"""Replay the strategy + risk rules over historical closes (dict sym -> list of closes)."""
from .broker import PaperBroker
from .engine import run_once
from .risk import RiskManager


def backtest(cfg, data, warmup=None):
    warmup = warmup or cfg.slow + 1
    n = min(len(v) for v in data.values())
    t = {"i": warmup}
    b = PaperBroker(cfg.paper_start_cash,
                    lambda s: data[s][t["i"] - 1],
                    lambda s: data[s][: t["i"]])
    risk = RiskManager(cfg)
    curve = []
    for i in range(warmup, n + 1):
        t["i"] = i
        risk.new_day(b.equity())  # one pass per bar == one day
        run_once(cfg, b, risk)
        curve.append(b.equity())
    start, end = cfg.paper_start_cash, curve[-1]
    peak, mdd = curve[0], 0.0
    for e in curve:
        peak = max(peak, e); mdd = max(mdd, (peak - e) / peak)
    return {"start": start, "end": end, "return_pct": (end / start - 1) * 100,
            "max_drawdown_pct": mdd * 100, "days": len(curve)}

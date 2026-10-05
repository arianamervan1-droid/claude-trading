import random
from bot.config import Config
from bot.risk import RiskManager
from bot.strategy import signal
from bot.backtest import backtest


def test_signal_cross_up_and_down():
    up = [10] * 50 + [20]
    assert signal(up, 5, 20) == "buy"
    down = [20] * 50 + [10]
    assert signal(down, 5, 20) == "sell"


def test_risk_caps():
    c = Config(); r = RiskManager(c)
    assert r.buy_amount(10_000, 10_000, 0, 0) == 2000.0
    assert r.buy_amount(10_000, 10_000, 0, 7_900) == 100.0
    assert r.buy_amount(10_000, 3, 0, 0) == 0.0


def test_kill_switch_and_stop():
    c = Config(); r = RiskManager(c); r.new_day(10_000)
    assert not r.check_daily_loss(9_800)
    assert r.check_daily_loss(9_600)
    assert r.stop_hit(100, 94) and not r.stop_hit(100, 96)


def test_backtest_runs():
    random.seed(1)
    px, d = 100, []
    for _ in range(400):
        px *= 1 + random.gauss(0.0004, 0.01); d.append(px)
    res = backtest(Config(symbols=["X"]), {"X": d})
    assert res["days"] > 0 and res["max_drawdown_pct"] >= 0

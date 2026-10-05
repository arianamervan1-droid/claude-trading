import logging
from .strategy import signal, in_uptrend
from .risk import RiskManager

log = logging.getLogger("bot")


def run_once(cfg, broker, risk: RiskManager):
    """One pass over all symbols: stops first, then signals. Returns list of actions taken."""
    actions = []
    equity = broker.equity()
    if risk.day_start_equity is None:
        risk.new_day(equity)
    if risk.check_daily_loss(equity):
        log.warning("Daily loss limit hit (equity %.2f); flattening and halting.", equity)
        for s in list(broker.holdings()):
            broker.sell_all(s)
            actions.append(("sell", s, "daily_loss_limit"))
        return actions

    holdings = broker.holdings()
    for sym in cfg.symbols:
        closes = broker.history(sym)
        px = broker.price(sym)
        pos = holdings.get(sym)
        if pos and risk.stop_hit(pos["entry"], px):
            broker.sell_all(sym); actions.append(("sell", sym, "stop")); continue
        sig = signal(closes, cfg.fast, cfg.slow)
        if sig == "sell" and pos:
            broker.sell_all(sym); actions.append(("sell", sym, "signal"))
        elif sig == "buy" and not pos:
            holdings = broker.holdings()
            invested = sum(p["qty"] * broker.price(s) for s, p in holdings.items())
            amt = risk.buy_amount(equity, broker.cash, 0.0, invested)
            if amt:
                broker.buy(sym, amt); actions.append(("buy", sym, amt))
    return actions

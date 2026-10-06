import logging, sys, time
from datetime import date, datetime
from zoneinfo import ZoneInfo
from .config import Config
from .broker import PaperBroker, RobinhoodBroker
from .control import read_control, update_control, write_status
from .engine import run_once
from .risk import RiskManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")


def market_open() -> bool:
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.weekday() < 5 and (9, 30) <= (now.hour, now.minute) < (16, 0)


def build_broker(cfg):
    if cfg.live:
        log.warning("LIVE MODE: real orders will be placed.")
        return RobinhoodBroker()
    try:
        real = RobinhoodBroker()  # login is only used for market data
    except Exception as e:
        sys.exit(f"Paper mode needs Robinhood login for market data: {e}")
    log.info("PAPER MODE: no real orders.")
    return PaperBroker(cfg.paper_start_cash, real.price, real.history)


def main():
    cfg = Config()
    if cfg.mode == "live" and not cfg.live:
        sys.exit("Refusing live mode: set LIVE_CONFIRM=YES_I_UNDERSTAND_THE_RISK")
    broker, risk = build_broker(cfg), RiskManager(cfg)
    update_control(stop=False)  # clear a stale stop from last run
    today, last_run, last_actions = None, 0.0, []
    log.info("Running. Control it with: python -m bot.ctl status|pause|resume|flatten|stop")
    while True:
        ctl = read_control()
        if ctl["stop"]:
            log.info("Stop requested. Positions are left open."); break
        if ctl["flatten"]:
            for s in list(broker.holdings()):
                broker.sell_all(s); last_actions.append(("sell", s, "manual_flatten"))
            update_control(flatten=False, paused=True)
            log.warning("Flattened all positions; bot paused.")
        elif not ctl["paused"] and market_open() and time.time() - last_run >= cfg.poll_seconds:
            if today != date.today():
                today = date.today(); risk.new_day(broker.equity())
            if not risk.halted:
                last_actions = (run_once(cfg, broker, risk) or last_actions)[-10:]
                for a in last_actions: log.info("action: %s", a)
            last_run = time.time()
        write_status(mode="live" if cfg.live else "paper", paused=ctl["paused"], halted=risk.halted,
                     market_open=market_open(), equity=round(broker.equity(), 2),
                     positions=broker.holdings(), last_actions=last_actions,
                     updated=datetime.now().isoformat(timespec="seconds"))
        time.sleep(5)


if __name__ == "__main__":
    main()

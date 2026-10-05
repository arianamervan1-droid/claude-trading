import logging, sys, time
from datetime import date
from .config import Config
from .broker import PaperBroker, RobinhoodBroker
from .engine import run_once
from .risk import RiskManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")


def market_open() -> bool:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.weekday() < 5 and (9, 30) <= (now.hour, now.minute) < (16, 0)


def main():
    cfg = Config()
    if cfg.mode == "live" and not cfg.live:
        sys.exit("Refusing live mode: set LIVE_CONFIRM=YES_I_UNDERSTAND_THE_RISK")
    if cfg.live:
        broker = RobinhoodBroker()
        log.warning("LIVE MODE: real orders will be placed.")
    else:
        try:
            real = RobinhoodBroker()
            broker = PaperBroker(cfg.paper_start_cash, real.price, real.history)
        except Exception as e:
            sys.exit(f"Paper mode needs Robinhood login for market data: {e}")
        log.info("PAPER MODE: no real orders.")
    risk, today = RiskManager(cfg), None
    while True:
        if market_open():
            if today != date.today():
                today = date.today(); risk.new_day(broker.equity())
            if not risk.halted:
                for a in run_once(cfg, broker, risk):
                    log.info("action: %s", a)
        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    main()

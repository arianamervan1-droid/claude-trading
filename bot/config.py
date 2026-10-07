import os
from dataclasses import dataclass, field


@dataclass
class Config:
    symbols: list = field(default_factory=lambda: os.getenv("SYMBOLS", "SPY,QQQ,MSFT").split(","))
    mode: str = os.getenv("MODE", "paper")
    live_confirm: str = os.getenv("LIVE_CONFIRM", "")
    fast: int = 20
    slow: int = 50
    max_position_pct: float = 0.20      # max share of equity in one symbol
    max_total_exposure_pct: float = 0.80
    stop_loss_pct: float = 0.05         # exit if price falls 5% below entry
    daily_loss_limit_pct: float = 0.03  # halt trading for the day at -3% equity
    min_order_usd: float = 1.0       # Robinhood fractional-share minimum
    poll_seconds: int = 300
    paper_start_cash: float = 40.0

    @property
    def live(self) -> bool:
        return self.mode == "live" and self.live_confirm == "YES_I_UNDERSTAND_THE_RISK"

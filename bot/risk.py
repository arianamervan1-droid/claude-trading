class RiskManager:
    """Pure logic: sizing, stops and a daily kill switch. No I/O."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.day_start_equity = None
        self.halted = False

    def new_day(self, equity):
        self.day_start_equity = equity
        self.halted = False

    def check_daily_loss(self, equity):
        if self.day_start_equity and equity <= self.day_start_equity * (1 - self.cfg.daily_loss_limit_pct):
            self.halted = True
        return self.halted

    def buy_amount(self, equity, cash, symbol_value, total_invested):
        """Dollars to buy, respecting per-symbol and total exposure caps."""
        room_symbol = equity * self.cfg.max_position_pct - symbol_value
        room_total = equity * self.cfg.max_total_exposure_pct - total_invested
        amt = max(0.0, min(room_symbol, room_total, cash))
        return round(amt, 2) if amt >= self.cfg.min_order_usd else 0.0

    def stop_hit(self, entry_price, price):
        return price <= entry_price * (1 - self.cfg.stop_loss_pct)

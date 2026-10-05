import os


class PaperBroker:
    """Simulated account. Prices come from a callable so it works live or in backtests."""

    def __init__(self, cash, price_fn, history_fn):
        self.cash, self._price, self._history = cash, price_fn, history_fn
        self.positions = {}  # sym -> {"qty", "entry"}

    def price(self, sym): return self._price(sym)
    def history(self, sym): return self._history(sym)

    def holdings(self):
        return {s: dict(p) for s, p in self.positions.items() if p["qty"] > 0}

    def equity(self):
        return self.cash + sum(p["qty"] * self.price(s) for s, p in self.positions.items())

    def buy(self, sym, usd):
        px = self.price(sym)
        usd = min(usd, self.cash)
        qty = usd / px
        p = self.positions.setdefault(sym, {"qty": 0.0, "entry": px})
        p["entry"] = (p["entry"] * p["qty"] + px * qty) / (p["qty"] + qty)
        p["qty"] += qty
        self.cash -= usd

    def sell_all(self, sym):
        p = self.positions.get(sym)
        if p and p["qty"] > 0:
            self.cash += p["qty"] * self.price(sym)
            p["qty"] = 0.0


class RobinhoodBroker:
    """Real orders via the unofficial robin_stocks library. Only built when live is confirmed."""

    def __init__(self):
        import pyotp
        import robin_stocks.robinhood as rh
        self.rh = rh
        mfa = os.getenv("RH_MFA_SECRET")
        rh.login(os.environ["RH_USERNAME"], os.environ["RH_PASSWORD"],
                 mfa_code=pyotp.TOTP(mfa).now() if mfa else None, store_session=True)
        self.entries = {}  # sym -> entry price; falls back to Robinhood's average_buy_price

    def price(self, sym): return float(self.rh.stocks.get_latest_price(sym)[0])

    def history(self, sym):
        h = self.rh.stocks.get_stock_historicals(sym, interval="day", span="year", bound="regular")
        return [float(x["close_price"]) for x in h]

    def holdings(self):
        out = {}
        for s, d in self.rh.account.build_holdings().items():
            out[s] = {"qty": float(d["quantity"]), "entry": float(d["average_buy_price"])}
        return out

    def equity(self):
        return float(self.rh.profiles.load_portfolio_profile()["equity"])

    @property
    def cash(self):
        return float(self.rh.profiles.load_account_profile()["buying_power"])

    def buy(self, sym, usd):
        return self.rh.orders.order_buy_fractional_by_price(sym, usd, timeInForce="gfd")

    def sell_all(self, sym):
        qty = self.holdings().get(sym, {}).get("qty", 0)
        if qty > 0:
            return self.rh.orders.order_sell_fractional_by_quantity(sym, qty, timeInForce="gfd")

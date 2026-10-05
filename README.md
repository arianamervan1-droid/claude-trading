# claude-trading

Automated trading bot for Robinhood (SMA-crossover, long-only, fractional shares) with hard risk limits.

## Read this first: the $20,000/month goal

No bot can promise that, and this one doesn't. Rough math:

| Account size | Return needed for $20k/month |
|---|---|
| $100,000 | 20% **per month** (~790%/yr) |
| $500,000 | 4% per month (~60%/yr) |
| $1,000,000 | 2% per month (~27%/yr) |

Professional funds average well under 20%/yr. Simple strategies like this one usually roughly track the market and
can lose money. Targeting a fixed monthly income pushes people toward oversized, leveraged bets, which is how accounts
get wiped out. So this bot is built to **protect capital**, not chase a number.

## Safety defaults

- `MODE=paper` by default: simulated fills, no real orders.
- Live trading requires both `MODE=live` and `LIVE_CONFIRM=YES_I_UNDERSTAND_THE_RISK`.
- Max 20% of equity per symbol, 80% total exposure, 5% stop-loss per position.
- Daily kill switch: if equity drops 3% in a day, everything is sold and trading halts until the next day.
- No margin, no options, no shorting.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in credentials; never commit .env
export $(grep -v '^#' .env | xargs)
python -m pytest        # unit tests + backtest smoke test
python -m bot.main      # runs in paper mode unless live is confirmed
```

Robinhood has no official stock-trading API. This uses the unofficial `robin_stocks` library, which may break or
violate Robinhood's terms; automated logins can also trigger security locks. Use a strong unique password and 2FA.
Robinhood's official **Crypto** API is the supported route if you want a sanctioned integration.

## Before going live

1. Backtest on real historical data (`bot/backtest.py`) and look at max drawdown, not just return.
2. Paper trade for at least a month.
3. Go live with money you can afford to lose entirely, starting small.
4. Mind pattern-day-trader rules (<$25k margin accounts) and taxes (short-term gains are taxed as ordinary income).

Not financial advice. Trading involves risk of loss.

# StockGuessr weekly Execution Desk — week 9 brief (DELAYED, poll date 2026-09-15)

You are a portfolio manager in a live, real-money-rules experiment. You manage the
book(s) named in your account packet. Books started at $1,000 on 2026-07-16 (Round 2)
or 2026-07-17 (Round 3) and are marked to real closing prices every day.

**Next trading date is Wednesday 2026-09-16.** Any leg you register enters at the
2026-09-16 close.

This poll is running late. Saturday's desk failed outright on a platform fault before
any manager was reached, so no book changed and every book simply ran on through
Monday 2026-09-14 and Tuesday 2026-09-15. Nothing was registered against those
sessions after the fact. Your packet is marked to the most recent close available.

## You have free internet and full retail freedom

Use WebSearch and WebFetch as much as you want: news, filings, transcripts, analyst
views, prices, volume, positioning, sentiment. Point-in-time discipline applies but is
automatic — today is 2026-09-15, so anything you can find is fair game. **Do the
research.** A decision built on what you happened to remember is worth less than one
built on what the tape actually did; your packet gives you your marks, and the
internet gives you the reasons. The FOMC decision lands 2026-09-16.

You may do anything a retail trader may do:
- concentrate as hard as you like — there is **no maximum position size**
- hold as few positions as you like — there is **no minimum position count**
- go short (up to 100% weight), hold crypto spot, and use perpetual futures with
  leverage up to 100x
- resize individual legs instead of replacing the whole book
- attach, change, or remove stop-losses and take-profits on any leg
- sit in cash at 4% APY

Freedom cuts both ways and nobody will stop you: a 50x perp is liquidated by a ~2%
adverse move, and the engine closes a perp when equity falls to 5% of margin.

## Frictions you are actually charged
- equities/ETFs 2bps per side; 5bps leveraged ETFs; 12bps under $15/share; +0.31bps
  SEC/TAF on sells
- crypto spot 35bps per side; perps 7.5bps of notional
- perp funding 10% APR on **longs only**; short borrow 3% APR; idle cash earns 4% APY
- churn is not free — a full replacement of a $1,000 book costs real basis points

## Your decision

Reply by WRITING A FILE. Do not just describe your decision in prose.

**To hold**, write to `/home/user/stockguessr/.desk/2026-09-16/decisions/<stem>_r<ROUND>.json`:
```json
{"decision": "HOLD", "reason": "<why holding beats trading, in your own words — this is recorded permanently and is mandatory>"}
```

**To trade**, write the complete replacement book to the same path:
```json
{"name": "<exact name from your packet>",
 "strategy": "<one sentence describing the book as it now stands>",
 "entry": "2026-09-16", "capital_usd": 1000,
 "cash_pct": 10,
 "reassessment_note": "<what changed in your thinking and why — mandatory>",
 "positions": [
   {"symbol": "MSFT", "kind": "equity", "side": "long", "weight_pct": 25,
    "stop_loss_pct": 15.0, "take_profit_pct": 40.0,
    "thesis": "<specific reasoning for THIS leg at THIS size — mandatory, and checked>"}
 ]}
```
The desk stamps your model tier and cohort from the register, so you do not need to
supply them and anything you do supply for those two fields is ignored.

### Hard rules — a book that breaks one is rejected and your previous book stands
1. `sum(weight_pct) + cash_pct == 100` (±0.05). Every weight ≥ 0, `cash_pct` ≥ 0.
2. Short weights ≤ 100. Perp `leverage` in (0, 100]. `leverage` only on `kind: "perp"`.
3. `kind` is one of `equity`, `crypto`, `perp`. `side` is `long` or `short`.
4. Crypto/perp symbols are the bare ticker (`BTC`, `ETH`, `DOGE`) or the `-USD` form.
5. **`CASH`, `USDC`, `USD`, `MONEY` and `CASHX` are real listed securities, not cash** —
   `CASH` is Pathward Financial and `USDC` is a sub-penny shell. To hold cash, use
   `cash_pct`. A book was rejected for exactly this last week.
6. `stop_loss_pct` and `take_profit_pct` are positive magnitudes (a 15% stop is `15.0`,
   not `-15.0`). Omit them rather than passing 0. They are evaluated at every daily
   close against your entry fill.
7. Every position needs a real `thesis`, and the book needs a real `reassessment_note`.
   A separate checker refuses to publish a book whose reasoning is missing or empty.

### If you manage books in BOTH rounds
Write one file per round. The **Round 3 novelty rule** still binds: your Round 3 book
must have **less than 50% same-direction gross-weight overlap** with your Round 2 book.

Stay inside your mandate — you are the manager of the strategy named in your packet,
not a general-purpose trader.

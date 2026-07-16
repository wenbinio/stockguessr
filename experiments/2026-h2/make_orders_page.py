"""Render orders/*.json into orders.html — the H2-2026 forward-test order blotter.

Sections:
  1. Consensus flows — most-bought / most-sold tickers across all 28 agents
  2. Per-agent order sheets grouped by model tier (Fable, Opus, Sonnet, Haiku),
     each with SELL/BUY orders + reasons, holds, resulting book with marks,
     and the agent's H2 outlook.
"""

import html
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
TIER_ORDER = ["fable", "opus", "sonnet", "haiku"]
TIER_LABEL = {"fable": "Fable tier", "opus": "Opus tier", "sonnet": "Sonnet fleet", "haiku": "Haiku fleet"}
# Validated categorical palette slots 1-4 (all-pairs safe in both modes)
TIER_SLOT = {"fable": 1, "opus": 2, "sonnet": 3, "haiku": 4}

HEAD = """<title>StockGuessr H2 2026 — Forward Order Blotter</title>
<style>
  html, body { margin: 0; padding: 0; }
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb; --page: #f9f9f7;
    --ink-1: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
    --grid: #e1e0d9; --baseline: #c3c2b7; --border: rgba(11,11,11,0.10);
    --s1: #2a78d6; --s2: #008300; --s3: #e87ba4; --s4: #eda100;
    --up: #006300; --down: #d03b3b; --bench: #52514e;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19; --page: #0d0d0d;
      --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
      --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
      --s1: #3987e5; --s2: #008300; --s3: #d55181; --s4: #c98500;
      --up: #0ca30c; --down: #e66767; --bench: #c3c2b7;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
    --s1: #3987e5; --s2: #008300; --s3: #d55181; --s4: #c98500;
    --up: #0ca30c; --down: #e66767; --bench: #c3c2b7;
  }
  .viz-root { background: var(--page); color: var(--ink-1);
    font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 24px; min-height: 100vh; box-sizing: border-box; }
  .viz-root * { box-sizing: border-box; }
  .wrap { max-width: 980px; margin: 0 auto; display: grid; gap: 18px; }
  h1 { font-size: 21px; margin: 0; }
  h2 { font-size: 16px; margin: 14px 0 0; }
  .sub { color: var(--ink-2); margin: 4px 0 0; font-size: 13.5px; }
  .card { background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 20px; }
  .card h3 { font-size: 14.5px; margin: 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .chip { width: 10px; height: 10px; border-radius: 3px; display: inline-block; flex: none; }
  .badge { font-size: 11.5px; font-weight: 600; padding: 1px 8px; border-radius: 99px;
    border: 1px solid var(--border); color: var(--ink-2); }
  .strat { color: var(--ink-muted); font-size: 12.5px; margin: 2px 0 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px;
    color: var(--ink-1); font-family: inherit; }
  th { text-align: left; color: var(--ink-muted); font-weight: 600;
    border-bottom: 1px solid var(--baseline); padding: 5px 8px; white-space: nowrap; }
  td { padding: 5px 8px; border-bottom: 1px solid var(--grid); vertical-align: top; }
  td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .act { font-weight: 700; white-space: nowrap; }
  .act.buy { color: var(--up); } .act.sell { color: var(--down); }
  .tk { font-weight: 600; white-space: nowrap; }
  .holds, .book { font-size: 12.5px; color: var(--ink-2); margin: 8px 0 0; }
  .holds b, .book b { color: var(--ink-1); }
  .outlook { font-size: 12.5px; color: var(--ink-2); margin: 8px 0 0; padding: 8px 10px;
    border-left: 3px solid var(--grid); }
  .flows { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  @media (max-width: 640px) { .flows { grid-template-columns: 1fr; } }
  .bar-row { display: grid; grid-template-columns: 64px 1fr 30px; gap: 8px; align-items: center;
    font-size: 12.5px; margin: 3px 0; }
  .bar-row .tk { text-align: right; }
  .bar { height: 14px; border-radius: 4px; }
  .bar.buy { background: var(--up); opacity: .85; } .bar.sell { background: var(--down); opacity: .85; }
  .bar-row .ct { color: var(--ink-2); font-variant-numeric: tabular-nums; }
  .foot { color: var(--ink-muted); font-size: 12px; }
  .tierhead { display: flex; align-items: center; gap: 8px; }
</style>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def main() -> None:
    sheets = [json.loads(p.read_text()) for p in sorted((HERE / "orders").glob("*.json"))]
    marks = json.loads((HERE / "marks.json").read_text())
    perf = json.loads((HERE / "h1_performance.json").read_text())
    h1_by_name = {v["name"]: v for k, v in perf.items() if k != "_market"}

    h1_results = json.loads((HERE.parent / "2026-h1" / "results.json").read_text())
    h1_return = {r["name"]: r["total_return_pct"] for r in h1_results["summary"]}

    buys, sells = Counter(), Counter()
    for s in sheets:
        for o in s["orders"]:
            (buys if o["action"] == "BUY" else sells)[o["ticker"]] += 1

    def flow_col(counter, cls, title):
        top = counter.most_common(12)
        mx = top[0][1]
        rows = "".join(
            f'<div class="bar-row"><span class="tk">{esc(t)}</span>'
            f'<div><div class="bar {cls}" style="width:{max(6, c / mx * 100):.0f}%"></div></div>'
            f'<span class="ct">{c}</span></div>' for t, c in top)
        return f'<div><h2 style="margin-top:0">{title}</h2>{rows}</div>'

    total_orders = sum(len(s["orders"]) for s in sheets)
    parts = [HEAD, '<div class="viz-root"><div class="wrap">',
        f'''<header><h1>H2 2026 forward test — the order blotter</h1>
        <p class="sub">All 28 agents (1 Fable orchestrator, 2 Fable + 5 Opus flagships, 10 Sonnet + 10 Haiku fleet)
        reviewed their H1 books and issued {total_orders} orders on 2026-07-16, marked at the 2026-07-15 close and
        pre-registered in git. Scored on real prices through 2026-12-31. Because these predictions precede the
        outcomes, training-data leakage is impossible for this leg — whatever alpha shows up here is real
        (or luck), not memory.</p></header>''',
        '<section class="card"><h2 style="margin-top:0">Consensus flows — what the swarm is buying and selling</h2>',
        '<p class="strat">Number of agents (of 28) placing an order in each ticker</p>',
        '<div class="flows">',
        flow_col(buys, "buy", "Top buys"),
        flow_col(sells, "sell", "Top sells"),
        '</div></section>']

    for tier in TIER_ORDER:
        tier_sheets = [s for s in sheets if s["model"] == tier]
        if not tier_sheets:
            continue
        tier_sheets.sort(key=lambda s: h1_return.get(s["name"], 0), reverse=True)
        parts.append(f'<div class="tierhead"><span class="chip" style="background:var(--s{TIER_SLOT[tier]})"></span>'
                     f'<h2>{TIER_LABEL[tier]}</h2></div>')
        for s in tier_sheets:
            h1r = h1_return.get(s["name"])
            badge = "" if h1r is None else f'<span class="badge">H1 {"+" if h1r >= 0 else ""}{h1r:.1f}%</span>'
            rows = []
            pf_perf = h1_by_name.get(s["name"], {}).get("performance", {})
            for o in sorted(s["orders"], key=lambda o: (o["action"] != "SELL",)):
                t = o["ticker"]
                if o["action"] == "SELL":
                    p = pf_perf.get(t, {})
                    mark = "—" if p.get("h1_return_pct") is None else f'{p["h1_return_pct"]:+.1f}% held'
                else:
                    mark = f'${marks[t]:,.2f}' if t in marks else "—"
                rows.append(f'<tr><td class="act {o["action"].lower()}">{o["action"]}</td>'
                            f'<td class="tk">{esc(t)}</td><td>{esc(o["reason"])}</td>'
                            f'<td class="n">{mark}</td></tr>')
            book = ", ".join(f'{esc(t)} (${marks[t]:,.2f})' if t in marks else esc(t)
                             for t in s["resulting_portfolio"])
            parts.append(f'''<section class="card">
              <h3><span class="chip" style="background:var(--s{TIER_SLOT[tier]})"></span>{esc(s["name"])} {badge}</h3>
              <p class="strat">{esc(s["strategy"])}</p>
              <table><thead><tr><th>Order</th><th>Ticker</th><th>Reason</th><th class="n">Mark / H1 result</th></tr></thead>
              <tbody>{"".join(rows) if rows else '<tr><td colspan="4" style="color:var(--ink-muted)">No changes — full hold</td></tr>'}</tbody></table>
              <p class="holds"><b>Holds:</b> {", ".join(map(esc, s["holds"]))}</p>
              <p class="book"><b>Resulting book</b> (equal weight at 2026-07-15 close): {book}</p>
              <p class="outlook">{esc(s["outlook"])}</p>
            </section>''')

    parts.append('''<p class="foot">Marks are 2026-07-15 closing prices (Yahoo Finance). Scoring: each resulting
    book is equal-weighted at those marks and held to 2026-12-31; same friction model as H1 available at scoring
    time. SELL rows show the position's H1 result at exit. Fleet agents issued orders from knowledge + their own
    book's H1 results only (no tools); flagship agents could fetch market data through 2026-07-15.
    Research/educational demo — not investment advice.</p></div></div>''')

    (HERE / "orders.html").write_text("\n".join(parts))
    print(f"Wrote orders.html: {len(sheets)} agents, {total_orders} orders, "
          f"{sum(len(s['resulting_portfolio']) for s in sheets)} resulting positions")


if __name__ == "__main__":
    main()

"""Compile every pre-registration backtest from Round 1 and Round 2 into one
static, self-contained page: docs/backtests.html.

Backtests are immutable pre-registration artifacts, so this page is rebuilt on
demand (not by the CI cron). Data comes verbatim from:
  experiments/2026-h1/portfolios/*.json  (Round 1 flagship "backtest" blocks)
  experiments/round2/allocations/*.json  (Round 2 flagship "backtest" blocks)
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R1_ORDER = ["claude_fable", "fable_unconstrained", "fable_barbell", "opus_momentum",
            "opus_value", "opus_quality_defensive", "opus_picks_and_shovels", "opus_broadening"]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StockGuessr — Backtest Compendium (Rounds 1 & 2)</title>
<style>
  html, body { margin: 0; padding: 0; }
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb; --page: #f9f9f7;
    --ink-1: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
    --grid: #e1e0d9; --baseline: #c3c2b7; --border: rgba(11,11,11,0.10);
    --s1: #2a78d6; --s2: #008300; --s3: #e87ba4; --s4: #eda100;
    --up: #006300; --down: #d03b3b;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19; --page: #0d0d0d;
      --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
      --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
      --s1: #3987e5; --s2: #008300; --s3: #d55181; --s4: #c98500;
      --up: #0ca30c; --down: #e66767;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
    --s1: #3987e5; --s2: #008300; --s3: #d55181; --s4: #c98500;
    --up: #0ca30c; --down: #e66767;
  }
  .viz-root { background: var(--page); color: var(--ink-1);
    font: 14px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 24px; min-height: 100vh; box-sizing: border-box; }
  .viz-root * { box-sizing: border-box; }
  .wrap { max-width: 940px; margin: 0 auto; display: grid; gap: 16px; }
  h1 { font-size: 21px; margin: 0; }
  h2 { font-size: 17px; margin: 12px 0 0; }
  .sub { color: var(--ink-2); margin: 4px 0 0; font-size: 13.5px; }
  .sub a { color: inherit; }
  .card { background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 20px; }
  .card h3 { font-size: 14.5px; margin: 0; }
  .meta { color: var(--ink-muted); font-size: 12.5px; margin: 2px 0 10px; }
  .chip { width: 10px; height: 10px; border-radius: 3px; display: inline-block;
    margin-right: 7px; vertical-align: -1px; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px;
    color: var(--ink-1); font-family: inherit; margin: 4px 0 10px; }
  th { text-align: left; color: var(--ink-muted); font-weight: 600;
    border-bottom: 1px solid var(--baseline); padding: 4px 8px; }
  th.n, td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  td { padding: 4px 8px; border-bottom: 1px solid var(--grid); }
  .pos { color: var(--up); } .neg { color: var(--down); }
  .notes { font-size: 12.5px; color: var(--ink-2); border-left: 3px solid var(--grid);
    padding: 6px 10px; margin: 0; }
  .foot { color: var(--ink-muted); font-size: 12px; }
</style>
</head>
<body>
<div class="viz-root"><div class="wrap">
  <header>
    <h1>Backtest compendium — everything tested before it was traded</h1>
    <p class="sub">Every pre-registration backtest from both rounds, extracted verbatim from the
    registered portfolio/allocation files (pre-entry timestamps in git history). Round-1 backtests
    validated strategies on pre-cutoff data (2024/2025) before the 2026-01-02 entry; Round-2 backtests
    validated full-toolkit constructions (leverage, shorts, crypto, perps) with engine costs before the
    2026-07-16 entry. Fleet (Sonnet/Haiku) agents run tools-disabled by design and carry no backtests.
    <a href="index.html">&larr; live tracker</a></p>
  </header>
"""

TIER_SLOT = {"fable": 1, "opus": 2, "sonnet": 3, "haiku": 4}


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):+.1f}%"
    except (TypeError, ValueError):
        return esc(v)


def card(d, round_label, extra_meta=""):
    bt = d.get("backtest")
    chip = f'<span class="chip" style="background:var(--s{TIER_SLOT[d["model"]]})"></span>'
    out = [f'<section class="card"><h3>{chip}{esc(d["name"])} <span class="meta" '
           f'style="display:inline">· {esc(d["model"])} · {round_label}</span></h3>',
           f'<p class="meta">{esc(d["strategy"])}{extra_meta}</p>']
    if not bt:
        out.append('<p class="notes">No backtest block registered'
                   + (' — the orchestrator pre-registered Round-1 picks directly from '
                      'cutoff knowledge (git commit precedes any data fetch), without a '
                      'strategy backtest. That gap was closed in Round 2.' if "orchestrator" in d["name"]
                      else '.') + '</p></section>')
        return "\n".join(out)
    sr = bt.get("strategy_return_pct", {})
    br = bt.get("benchmark_return_pct", bt.get("spy_return_pct", {}))
    bkeys = list(br.keys())
    rows = []
    for i, (k, v) in enumerate(sr.items()):
        bench = br.get(k, br[bkeys[i]] if i < len(bkeys) else None)
        c = ""
        try:
            c = "pos" if float(v) >= float(bench) else "neg"
        except (TypeError, ValueError):
            pass
        rows.append(f'<tr><td>{esc(k)}</td><td class="n"><span class="{c}">{fmt(v)}</span></td>'
                    f'<td class="n">{fmt(bench)}</td></tr>')
    out.append('<table><thead><tr><th>Window</th><th class="n">Strategy</th>'
               '<th class="n">Benchmark (SPY)</th></tr></thead><tbody>'
               + "".join(rows) + '</tbody></table>')
    for key in ("max_drawdown_pct", "drawdown_defense"):
        if key in bt:
            v = bt[key]
            v = ", ".join(f"{k} {x}%" for k, x in v.items()) if isinstance(v, dict) else v
            out.append(f'<p class="meta"><b>Drawdown:</b> {esc(v)}</p>')
    out.append(f'<p class="notes">{esc(bt.get("notes", ""))}</p></section>')
    return "\n".join(out)


def main():
    parts = [HEAD, '<h2>Round 1 — pre-cutoff strategy validation (entered 2026-01-02)</h2>',
             '<p class="sub">Flagship agents fetched only pre-cutoff data (hard bound '
             'period2 &le; 2026-01-02, verified by the independent audit in '
             '<code>experiments/2026-h1/AUDIT.md</code>) and tested their rule on 2024/2025 windows.</p>']
    for stem in R1_ORDER:
        f = ROOT / "experiments" / "2026-h1" / "portfolios" / f"{stem}.json"
        if f.exists():
            parts.append(card(json.loads(f.read_text()), "Round 1"))

    parts.append('<h2>Round 2 — full-toolkit construction tests (entered 2026-07-16)</h2>'
                 '<p class="sub">Same agents, now testing leverage decay, short carry, perp '
                 'funding/liquidation, and crypto legs with the live engine\'s cost model. The '
                 'orchestrator\'s test ran through <code>tracker/round2.py --backtest</code> itself, '
                 'validating the engine.</p>')
    for stem in R1_ORDER:
        f = ROOT / "experiments" / "round2" / "allocations" / f"{stem}.json"
        if f.exists():
            d = json.loads(f.read_text())
            gross = sum(p["weight_pct"] * p.get("leverage", 1) for p in d["positions"])
            shorts = sum(p["weight_pct"] for p in d["positions"] if p["side"] == "short")
            extra = (f' · book: {len(d["positions"])} positions, {gross:.0f}% gross, '
                     f'{shorts:.0f}% short, {d["cash_pct"]}% cash')
            parts.append(card(d, "Round 2", extra))

    parts.append("""<section class="card"><h3>How to read these honestly</h3>
    <p class="notes" style="margin-top:8px">
    1) Windows ending near an entry date are partly in-sample — a book chosen knowing that window's
    winners will flatter itself; the stress windows (2024H2, the 2025 tariff crash, the April 2026
    drawdown) are the meaningful evidence.
    2) The rejections are the strongest signal the process worked: Round 2's backtests killed a SOXL
    sleeve (-50.7% in stress), a 2x ETH perp short (adverse move = 202% of margin = liquidation), an
    oversized momentum short ("catastrophic"), and inverse leveraged ETFs (SOXS -98% through a recovery)
    before a dollar was virtually deployed.
    3) Several agents report backtests that LOSE to the benchmark in some windows and say so — a
    strategy honestly described as regime-dependent beats one curve-fit to always win.
    4) A backtest is a hypothesis. The forward legs — Round 1's pre-registered July orders and Round 2's
    weekly-rebalanced accounts — are the experiment.</p></section>
    <p class="foot">Generated by <code>tracker/make_backtests_page.py</code> from the registered files.
    Research/educational demo — not investment advice.</p>
    </div></div></body></html>""")

    out = ROOT / "docs" / "backtests.html"
    out.write_text("\n".join(parts))
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

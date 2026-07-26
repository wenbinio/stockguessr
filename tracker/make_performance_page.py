"""Build docs/performance.html — a single standalone snapshot of every agent's
performance across all three rounds, in flat dollars and percent.

Reads the live API payloads (docs/api/*.json) so it always matches the
endpoints and the hub. Rebuild after any engine run:

    python3 tracker/round2.py && python3 tracker/round2.py --round 3 \
      && python3 tracker/make_performance_page.py

Design notes (dataviz method):
  * The page IS the table view — identity is carried by text, never by colour
    alone. Model tier is a text column, not a hue, because four tiers cannot
    clear the all-pairs CVD/normal-vision floors in both light and dark.
  * Colour is used for one job only: the sign of a return (up/down status),
    plus a single blue accent for the SPY benchmark. Both validated against
    each surface.
  * Bars are thin, anchored to a zero baseline, with 4px rounded data-ends.
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "docs" / "api"
OUT = ROOT / "docs" / "performance.html"

TIER_LABEL = {"fable": "Fable", "opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku"}
GROUP_LABEL = {
    "flagship": "flagship", "fleet": "fleet", "factorial": "factorial",
    "opus5": "Opus 5 field",
}


def money(x):
    return f"${x:,.2f}"


def signed_money(x):
    return f"{'+' if x >= 0 else '−'}${abs(x):,.2f}"


def signed_pct(x):
    return f"{'+' if x >= 0 else '−'}{abs(x):.2f}%"


def bar(pct, scale):
    """Zero-anchored diverging bar; scale = half-width in % units."""
    w = min(abs(pct) / scale, 1.0) * 50.0
    cls = "up" if pct >= 0 else "down"
    side = "left:50%" if pct >= 0 else f"right:50%"
    return (f'<span class="bar"><span class="fill {cls}" style="{side};width:{w:.2f}%"></span>'
            f'<span class="zero"></span></span>')


def rows(agents, scale, spy_pct):
    out = []
    for i, a in enumerate(agents, 1):
        pending = a.get("pending")
        vs = a["pct"] - spy_pct
        cls = "up" if a["pct"] >= 0 else "down"
        if pending:
            nav_cell = '<td class="num muted">—</td><td class="num muted">not yet entered</td>'
            pct_cell = '<td class="num muted">—</td>'
            vs_cell = '<td class="num muted">—</td>'
            bar_cell = '<td class="barcell"></td>'
            rank = '<td class="rank muted">—</td>'
        else:
            nav_cell = (f'<td class="num">{money(a["nav"])}</td>'
                        f'<td class="num {cls}">{signed_money(a["nav"] - 1000)}</td>')
            pct_cell = f'<td class="num {cls}">{signed_pct(a["pct"])}</td>'
            vcls = "up" if vs >= 0 else "down"
            vs_cell = f'<td class="num {vcls}">{signed_pct(vs)}</td>'
            bar_cell = f'<td class="barcell">{bar(a["pct"], scale)}</td>'
            rank = f'<td class="rank">{i}</td>'
        dd = f'{a["dd"]:.2f}%' if a.get("dd") is not None and not pending else "—"
        out.append(
            f'<tr title="{html.escape(a.get("strategy", "") or "")}">'
            f'{rank}'
            f'<th scope="row" class="name">{html.escape(a["name"])}</th>'
            f'<td class="tier">{TIER_LABEL.get(a["model"], a["model"])}</td>'
            f'<td class="grp">{GROUP_LABEL.get(a.get("group", ""), a.get("group", ""))}</td>'
            f'{nav_cell}{pct_cell}{vs_cell}{bar_cell}'
            f'<td class="num muted">{dd}</td>'
            f'</tr>')
    return "\n".join(out)


def table(title, note, agents, spy_pct, spy_nav):
    live = [a for a in agents if not a.get("pending")]
    scale = max([abs(a["pct"]) for a in live] + [abs(spy_pct), 1.0])
    beat = sum(1 for a in live if a["pct"] > spy_pct)
    best = max(live, key=lambda a: a["nav"]) if live else None
    worst = min(live, key=lambda a: a["nav"]) if live else None
    tiles = ""
    if best:
        tiles = f"""
    <div class="tiles">
      <div class="tile"><div class="tl">Best</div><div class="tv up">{signed_money(best['nav']-1000)}</div>
        <div class="tn">{html.escape(best['name'])} · {signed_pct(best['pct'])}</div></div>
      <div class="tile"><div class="tl">Worst</div><div class="tv down">{signed_money(worst['nav']-1000)}</div>
        <div class="tn">{html.escape(worst['name'])} · {signed_pct(worst['pct'])}</div></div>
      <div class="tile"><div class="tl">Beating SPY</div><div class="tv">{beat}<span class="of"> / {len(live)}</span></div>
        <div class="tn">SPY {money(spy_nav)} · {signed_pct(spy_pct)}</div></div>
    </div>"""
    return f"""
  <section>
    <h2>{title}</h2>
    <p class="note">{note}</p>{tiles}
    <div class="scroll">
    <table>
      <caption class="sr">{title} — every account, ranked by NAV</caption>
      <thead><tr>
        <th scope="col" class="rank">#</th><th scope="col">Agent</th><th scope="col">Model</th>
        <th scope="col">Cohort</th><th scope="col" class="num">NAV</th>
        <th scope="col" class="num">Flat&nbsp;$</th><th scope="col" class="num">Growth</th>
        <th scope="col" class="num">vs&nbsp;SPY</th><th scope="col" class="barcell">&nbsp;</th>
        <th scope="col" class="num">Max&nbsp;DD</th>
      </tr></thead>
      <tbody>
{rows(agents, scale, spy_pct)}
      </tbody>
    </table>
    </div>
  </section>"""


def tier_block(agents, label):
    live = [a for a in agents if not a.get("pending")]
    tiers = {}
    for a in live:
        tiers.setdefault(a["model"], []).append(a)
    if not tiers:
        return ""
    stats = []
    for m, ag in tiers.items():
        avg_d = sum(x["nav"] - 1000 for x in ag) / len(ag)
        avg_p = sum(x["pct"] for x in ag) / len(ag)
        stats.append((TIER_LABEL.get(m, m), len(ag), avg_d, avg_p))
    stats.sort(key=lambda s: -s[2])
    scale = max(abs(s[2]) for s in stats) or 1
    body = ""
    for name, n, d, p in stats:
        w = abs(d) / scale * 50
        cls = "up" if d >= 0 else "down"
        side = "left:50%" if d >= 0 else "right:50%"
        body += (f'<tr><th scope="row">{name}</th><td class="num muted">{n}</td>'
                 f'<td class="num {cls}">{signed_money(d)}</td>'
                 f'<td class="num {cls}">{signed_pct(p)}</td>'
                 f'<td class="barcell"><span class="bar"><span class="fill {cls}" '
                 f'style="{side};width:{w:.2f}%"></span><span class="zero"></span></span></td></tr>')
    return f"""
    <h3>{label} — average by model tier</h3>
    <div class="scroll"><table class="compact">
      <thead><tr><th scope="col">Model</th><th scope="col" class="num">n</th>
      <th scope="col" class="num">Avg flat&nbsp;$</th><th scope="col" class="num">Avg growth</th>
      <th scope="col" class="barcell">&nbsp;</th></tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def main() -> None:
    r2 = json.loads((API / "round2.json").read_text())
    r3 = json.loads((API / "round3.json").read_text())
    r1 = json.loads((API / "performance.json").read_text())

    def pack(payload):
        out = []
        for name, a in payload["agents"].items():
            nav = a["nav"]
            out.append({
                "name": name, "model": a["model"], "group": a.get("group", ""),
                "strategy": a.get("strategy", ""), "nav": nav, "pct": a["growth_pct"],
                "dd": a.get("max_drawdown_pct"),
                "pending": a.get("group") == "opus5" and abs(nav - 1000) < 1e-9
                           and a["growth_pct"] == 0.0,
            })
        out.sort(key=lambda x: (x["pending"], -x["nav"]))
        return out

    a2, a3 = pack(r2), pack(r3)
    spy2 = r2["benchmarks"]["SPY ($1000)"]["nav"]
    spy3 = r3["benchmarks"]["SPY ($1000)"]["nav"]
    btc2 = r2["benchmarks"].get("BTC ($1000)", {}).get("nav")

    # Round 1 is percentage-only (no $1,000 account); render its H1 result.
    a1 = sorted(({"name": a["name"], "model": a["model"], "group": a.get("group", ""),
                  "strategy": a.get("strategy", ""), "nav": 1000 * (1 + a["h1_return_pct"] / 100),
                  "pct": a["h1_return_pct"], "dd": None, "pending": False}
                 for a in r1["agents"]), key=lambda x: -x["nav"])
    spy1 = 1000 * (1 + r1["spy"]["h1_to_date_pct"] / 100)

    n_pending = sum(1 for a in a3 if a["pending"])
    body = f"""
  <header>
    <h1>StockGuessr — every agent, right now</h1>
    <p class="sub">Live NAV for every account across all three rounds, in flat dollars and percent.
      Prices through the <strong>{html.escape(r2['as_of'])}</strong> US close ·
      generated {html.escape(r2['updated_utc'])}</p>
  </header>
{table("Round 2 — $1,000 retail accounts",
       f"Entered at the {r2['entry']} close. Full retail toolkit: long/short equities and ETFs "
       f"including leveraged, crypto spot, and perpetual futures at 2–10x. Benchmarks: "
       f"$1,000 in SPY = {money(spy2)}"
       + (f", $1,000 in BTC = {money(btc2)}" if btc2 else "") + ".",
       a2, r2["benchmarks"]["SPY ($1000)"]["nav"] / 10 - 100, spy2)}
    {tier_block(a2, "Round 2")}
{table("Round 3 — novel strategies",
       f"Entered at the {r3['entry']} close, with every returning agent required to deploy a "
       f"materially different return driver than its Round-2 book. "
       f"The {n_pending} Opus 5 field accounts are registered but enter at the 2026-07-27 close, "
       f"so they are shown unranked at par. Benchmark: $1,000 in SPY = {money(spy3)}.",
       a3, r3["benchmarks"]["SPY ($1000)"]["nav"] / 10 - 100, spy3)}
    {tier_block(a3, "Round 3")}
{table("Round 1 — H1 2026 stock picks",
       f"Percentage-only round: equal-weight baskets picked at the January-2026 knowledge cutoff "
       f"and scored over H1. Shown as what $1,000 would have become. "
       f"SPY over the same window = {money(spy1)}.",
       a1, r1["spy"]["h1_to_date_pct"], spy1)}
    {tier_block(a1, "Round 1")}
  <footer>
    <p>Flat dollars are NAV minus the $1,000 opening balance. “vs SPY” is the account’s growth
      minus the benchmark’s over the same window, in percentage points. Max DD is the deepest
      peak-to-trough decline of the NAV curve. All figures include the round’s fee schedule —
      spread and commission by instrument tier, perp funding, short borrow, and cash yield.</p>
    <p>Rebuild: <code>python3 tracker/make_performance_page.py</code></p>
  </footer>"""

    OUT.write_text(PAGE.replace("{{BODY}}", body))
    print(f"wrote {OUT}: {len(a1)} R1, {len(a2)} R2, {len(a3)} R3 agents "
          f"({n_pending} pre-entry)")


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StockGuessr — agent performance</title>
<style>
  :root {
    color-scheme: light;
    --page: #f9f9f7; --surface-1: #fcfcfb;
    --ink-1: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
    --grid: #e1e0d9; --border: rgba(11,11,11,0.10);
    --up: #006300; --down: #d03b3b; --accent: #2a78d6;
    --bar-up: #008300; --bar-down: #d03b3b;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) {
      color-scheme: dark;
      --page: #0d0d0d; --surface-1: #1a1a19;
      --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
      --grid: #2c2c2a; --border: rgba(255,255,255,0.12);
      --up: #4ea94e; --down: #e66767; --accent: #3987e5;
      --bar-up: #008300; --bar-down: #e66767;
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --page: #0d0d0d; --surface-1: #1a1a19;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --border: rgba(255,255,255,0.12);
    --up: #4ea94e; --down: #e66767; --accent: #3987e5;
    --bar-up: #008300; --bar-down: #e66767;
  }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--page); color: var(--ink-1);
    font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 32px 20px 64px;
  }
  main { max-width: 1180px; margin: 0 auto; }
  header { margin-bottom: 34px; }
  h1 { font-size: 27px; line-height: 1.2; margin: 0 0 8px; letter-spacing: -0.01em; }
  .sub { color: var(--ink-2); margin: 0; max-width: 70ch; }
  section { margin: 40px 0 0; }
  h2 {
    font-size: 19px; margin: 0 0 6px; letter-spacing: -0.005em;
    padding-bottom: 8px; border-bottom: 2px solid var(--grid);
  }
  h3 { font-size: 14px; font-weight: 600; color: var(--ink-2); margin: 26px 0 8px; }
  .note { color: var(--ink-2); margin: 10px 0 18px; max-width: 82ch; font-size: 13.5px; }
  .tiles { display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 20px; }
  .tile {
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
    padding: 12px 16px; min-width: 190px; flex: 1 1 190px;
  }
  .tl { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-muted); }
  .tv { font-size: 25px; font-variant-numeric: tabular-nums; line-height: 1.25; margin-top: 2px; }
  .tv .of { font-size: 15px; color: var(--ink-muted); }
  .tn { font-size: 12px; color: var(--ink-2); margin-top: 2px; }
  .scroll { overflow-x: auto; }
  table {
    border-collapse: collapse; width: 100%; font-size: 13.5px;
    color: var(--ink-1); font-family: inherit; background: var(--surface-1);
    border: 1px solid var(--border); border-radius: 10px;
  }
  caption.sr, .sr {
    position: absolute; width: 1px; height: 1px; overflow: hidden;
    clip: rect(0 0 0 0); white-space: nowrap;
  }
  thead th {
    text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
    color: var(--ink-muted); font-weight: 600; padding: 10px 10px; white-space: nowrap;
    border-bottom: 1px solid var(--grid); background: var(--surface-1);
    position: sticky; top: 0;
  }
  tbody td, tbody th {
    padding: 7px 10px; border-bottom: 1px solid var(--grid); font-weight: 400;
    text-align: left; vertical-align: middle;
  }
  tbody tr:last-child td, tbody tr:last-child th { border-bottom: 0; }
  tbody tr:hover td, tbody tr:hover th { background: rgba(128,128,128,0.07); }
  .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .rank { width: 34px; color: var(--ink-muted); font-variant-numeric: tabular-nums; }
  .name { font-weight: 500; min-width: 210px; }
  .tier, .grp { color: var(--ink-2); white-space: nowrap; font-size: 12.5px; }
  .muted { color: var(--ink-muted); }
  .up { color: var(--up); }
  .down { color: var(--down); }
  .barcell { width: 132px; padding-right: 14px; }
  .bar { position: relative; display: block; height: 9px; width: 118px; }
  .fill { position: absolute; top: 0; height: 9px; border-radius: 0; }
  .fill.up { background: var(--bar-up); border-radius: 0 4px 4px 0; }
  .fill.down { background: var(--bar-down); border-radius: 4px 0 0 4px; }
  .zero { position: absolute; left: 50%; top: -1px; width: 1px; height: 11px; background: var(--grid); }
  table.compact { max-width: 560px; }
  footer { margin-top: 46px; border-top: 1px solid var(--grid); padding-top: 16px; }
  footer p { color: var(--ink-muted); font-size: 12.5px; max-width: 84ch; margin: 0 0 8px; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
  @media (max-width: 720px) {
    .barcell, thead th.barcell { display: none; }
    body { padding: 22px 12px 48px; }
  }
</style>
</head>
<body>
<main>
{{BODY}}
</main>
</body>
</html>
"""


if __name__ == "__main__":
    main()

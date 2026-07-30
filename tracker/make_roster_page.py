#!/usr/bin/env python3
"""Build docs/roster.html — the full StockGuessr agent roster dossier.

Every number on the page is read out of the committed data files; nothing is
recomputed here except (a) flat P&L = NAV - capital and (b) the window-matched
SPY comparison, both derived straight from the API's own figures.

Sources
  docs/api/round2.json, docs/api/round3.json  live NAV / positions / series
  docs/api/performance.json                   Round 1 (percentage-only)
  experiments/round{2,3}/allocations/*.json   opening books
  experiments/round{2,3}/weeks/<date>/*.json  reassessment books
  experiments/desk/*.json                     desk logs (HOLDs live here)
  experiments/round{2,3}/fills.jsonl          standing-order executions

Run:  python3 tracker/make_roster_page.py
"""

import html
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
EXP = ROOT / "experiments"
OUT = DOCS / "roster.html"

CAPITAL = 1000.0

TIER = {"fable": "Fable", "opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku"}
COHORT = {"flagship": "Flagship", "fleet": "Fleet",
          "factorial": "Factorial", "opus5": "Opus 5 field"}
COHORT_ORDER = ["flagship", "factorial", "opus5", "fleet"]
COHORT_BLURB = {
    "flagship": "Fable orchestrator, two Fable flagships and five Opus flagships. "
                "Tool access and a mandatory pre-registration backtest.",
    "factorial": "The 2x5 factorial: five mandates run by Opus and by Sonnet+tools, "
                 "so model tier and treatment can be separated. Round 3 only.",
    "opus5": "Nine single-edge Opus 5 books that entered on 2026-07-27, seven sessions "
             "after the rest of Round 3. Round 3 only.",
    "fleet": "Ten mandates run by Sonnet and the same ten by Haiku — the tier "
             "comparison at fixed strategy.",
}

DESKS = [
    ("week1_2026-07-18.json", "2026-07-20", "Week 1 reassessment"),
    ("week2_2026-07-25.json", "2026-07-27", "Week 2 reassessment (drip-info protocol v2)"),
    ("unrestricted_resize_2026-07-30.json", "2026-07-31",
     "Unrestricted-retail resize (position caps lifted, free-internet research poll)"),
]


# ---------------------------------------------------------------- loading

def jload(p):
    return json.loads(Path(p).read_text())


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def load_books(rnd):
    """name -> [{entry, path, data}] sorted by entry date."""
    out = defaultdict(list)
    base = EXP / f"round{rnd}"
    files = sorted((base / "allocations").glob("*.json"))
    for wk in sorted(base.glob("weeks/*/")):
        files += sorted(wk.glob("*.json"))
    for f in files:
        d = jload(f)
        out[d["name"]].append({"entry": d["entry"], "path": rel(f), "data": d})
    for v in out.values():
        v.sort(key=lambda b: b["entry"])
    return out


def load_fills(rnd):
    out = defaultdict(list)
    p = EXP / f"round{rnd}" / "fills.jsonl"
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        f = json.loads(line)
        if f["action"] != "OPEN":
            out[f["agent"]].append(f)
    for v in out.values():
        v.sort(key=lambda f: f["ts"])
    return out


API = {2: jload(DOCS / "api" / "round2.json"), 3: jload(DOCS / "api" / "round3.json")}
PERF = jload(DOCS / "api" / "performance.json")
BOOKS = {2: load_books(2), 3: load_books(3)}
FILLS = {2: load_fills(2), 3: load_fills(3)}
DESK_LOGS = [(jload(EXP / "desk" / fn), eff, label) for fn, eff, label in DESKS]
DESK_PATHS = {eff: f"experiments/desk/{fn}" for fn, eff, _ in DESKS}

AS_OF = API[2]["as_of"]
assert API[3]["as_of"] == AS_OF, "rounds priced to different dates"


# ------------------------------------------------------- decision timeline

def build_decisions():
    """(agent, round) -> [event dicts], each with date / action / reason."""
    ev = defaultdict(list)
    for log, eff, label in DESK_LOGS:
        src = DESK_PATHS[eff]
        for mgr in log["decisions"]:
            for dec in mgr["decisions"]:
                ev[(mgr["name"], dec["round"])].append({
                    "date": eff, "poll": log.get("desk_run_utc", ""), "label": label,
                    "action": dec["action"], "reason": dec["reason"], "source": src,
                })
        orch = log.get("orchestrator") or {}
        for rnd in (2, 3):
            raw = orch.get(f"round{rnd}")
            if not raw:
                continue
            action = "REBALANCE" if str(raw).upper().startswith("REBALANCE") else "HOLD"
            note = ("Orchestrator decision, logged under the desk log's `orchestrator` key "
                    f"as “{raw}”.")
            if not orch.get("reason"):
                note += (" That log records only the action for the orchestrator — no reason "
                         "text is stored for this round, so none is shown.")
            ev[("Claude Fable (orchestrator)", rnd)].append({
                "date": eff, "poll": log.get("desk_run_utc", ""), "label": label,
                "action": action, "reason": orch.get("reason"), "source": src,
                "note": note,
            })
        for name in log.get("failed_default_hold", []):
            for rnd in (2, 3):
                if name in API[rnd]["agents"]:
                    ev[(name, rnd)].append({
                        "date": eff, "poll": log.get("desk_run_utc", ""), "label": label,
                        "action": "DEFAULT HOLD", "source": src,
                        "reason": "No response was recorded from this manager at the desk "
                                  "poll; the desk defaulted the book to HOLD. Listed in the "
                                  "desk log's `failed_default_hold` array — there is no "
                                  "stated reason in the data.",
                    })
    return ev


DECISIONS = build_decisions()


# ------------------------------------------------------------------ format

def esc(s):
    return html.escape(str(s), quote=True)


def paras(text):
    """Verbatim text -> paragraphs, preserving the author's blank-line breaks."""
    chunks = [c.strip() for c in str(text).split("\n\n") if c.strip()]
    if not chunks:
        chunks = [str(text).strip()]
    return "".join(f"<p>{esc(c).replace(chr(10), '<br>')}</p>" for c in chunks)


def money(v, sign=False):
    s = f"{abs(v):,.2f}"
    if sign:
        return ("+$" if v >= 0 else "−$") + s
    return "$" + s


def pct(v, dp=2):
    return ("+" if v >= 0 else "−") + f"{abs(v):.{dp}f}%"


def cls(v):
    return "up" if v >= 0 else "down"


def arrow(v):
    return "▲" if v >= 0 else "▼"


def signed(v, fmt="pct", dp=2):
    body = pct(v, dp) if fmt == "pct" else money(v, sign=True)
    return f'<span class="num {cls(v)}"><span class="gly">{arrow(v)}</span>{body}</span>'


def num(v, dp=2, suffix=""):
    return f'<span class="num">{v:,.{dp}f}{suffix}</span>'


def slug(name, rnd=None):
    s = "".join(ch.lower() if ch.isalnum() else "-" for ch in name)
    while "--" in s:
        s = s.replace("--", "-")
    s = "agent-" + s.strip("-")
    return f"{s}-r{rnd}" if rnd else s


# ------------------------------------------------------------- sparkline

def spy_window(rnd, d0, d1):
    """SPY $1,000 return between two dates, from the API's own benchmark series."""
    s = API[rnd]["benchmarks"]["SPY ($1000)"]["series"]
    if d0 not in s or d1 not in s:
        return None
    return (s[d1] / s[d0] - 1) * 100


def sparkline(rnd, series):
    """One NAV line + a muted dashed SPY reference. Colour = sign of the return."""
    dates = sorted(series)
    if len(dates) < 2:
        return '<p class="tiny muted">Not enough daily marks to plot.</p>'
    spy_all = API[rnd]["benchmarks"]["SPY ($1000)"]["series"]
    nav = [series[d] for d in dates]
    base_spy = spy_all.get(dates[0])
    spy = [spy_all[d] / base_spy * CAPITAL for d in dates] if base_spy else []

    W, H = 620, 132
    L, R, T, B = 46, 74, 14, 24
    vals = nav + spy + [CAPITAL]
    lo, hi = min(vals), max(vals)
    pad = max((hi - lo) * 0.10, 0.6)
    lo, hi = lo - pad, hi + pad

    def X(i):
        return L + i * (W - L - R) / (len(dates) - 1)

    def Y(v):
        return T + (hi - v) / (hi - lo) * (H - T - B)

    def path(vs):
        return " ".join(("M" if i == 0 else "L") + f"{X(i):.1f} {Y(v):.1f}"
                        for i, v in enumerate(vs))

    sign = cls(nav[-1] - CAPITAL)
    y_par = Y(CAPITAL)
    parts = [
        f'<svg class="spark" viewBox="0 0 {W} {H}" role="img" preserveAspectRatio="xMidYMid meet" '
        f'aria-label="Daily NAV from {dates[0]} to {dates[-1]}, ending {money(nav[-1])}">',
        f'<line class="par" x1="{L}" y1="{y_par:.1f}" x2="{W-R}" y2="{y_par:.1f}"/>',
        f'<text class="axlbl" x="{L-6}" y="{y_par+3.5:.1f}" text-anchor="end">$1,000</text>',
    ]
    if spy:
        parts.append(f'<path class="spy" d="{path(spy)}"/>')
    parts += [
        f'<path class="nav {sign}" d="{path(nav)}"/>',
        f'<circle class="end {sign}" cx="{X(len(nav)-1):.1f}" cy="{Y(nav[-1]):.1f}" r="4.5"/>',
        f'<text class="endlbl" x="{X(len(nav)-1)+9:.1f}" y="{Y(nav[-1])+4:.1f}">{money(nav[-1])}</text>',
        f'<text class="axlbl" x="{L}" y="{H-6}" text-anchor="start">{dates[0]}</text>',
        f'<text class="axlbl" x="{W-R}" y="{H-6}" text-anchor="end">{dates[-1]}</text>',
        f'<line class="cross" x1="0" y1="{T}" x2="0" y2="{H-B}" style="display:none"/>',
        f'<circle class="focus {sign}" cx="0" cy="0" r="4.5" style="display:none"/>',
        "</svg>",
    ]
    payload = {"d": dates, "n": [round(v, 2) for v in nav],
               "s": [round(v, 2) for v in spy], "L": L, "R": R, "W": W}
    return ('<figure class="chartbox">'
            '<figcaption class="tiny muted">Daily NAV (solid) against $1,000 in SPY over the '
            'same window (dashed grey). Hover for values.</figcaption>'
            f'<div class="sparkwrap" data-series="{esc(json.dumps(payload, separators=(",", ":")))}">'
            + "".join(parts) + '<div class="tip" hidden></div></div></figure>')


# ------------------------------------------------------------ book render

DASH = '<span class="muted">—</span>'
NONE_C = '<span class="muted">none</span>'


def position_rows(book, closed_map):
    rows = []
    for p in book["positions"]:
        lev = p.get("leverage")
        sl = p.get("stop_loss_pct")
        tp = p.get("take_profit_pct")
        fill = closed_map.get(p["symbol"].upper())
        flag = ""
        if fill:
            d = fill["ts"][:10]
            act = "stopped out" if fill["action"] == "STOP_LOSS" else "taken profit"
            flag = f'<span class="badge closed">CLOSED — {act} {d}</span>'
        lev_c = num(float(lev), 1, "×") if lev else DASH
        sl_c = ("−" + f"{abs(float(sl)):g}%") if sl is not None else NONE_C
        tp_c = ("+" + f"{abs(float(tp)):g}%") if tp is not None else NONE_C
        rows.append(
            "<tr>"
            f'<th scope="row" class="sym">{esc(p["symbol"])}{flag}</th>'
            f'<td>{esc(p["kind"])}</td>'
            f'<td>{esc(p["side"])}</td>'
            f'<td class="r">{num(p["weight_pct"], 1, "%")}</td>'
            f'<td class="r">{lev_c}</td>'
            f'<td class="r">{sl_c}</td>'
            f'<td class="r">{tp_c}</td>'
            f'<td class="thesis">{esc(p.get("thesis", ""))}</td>'
            "</tr>")
    return "".join(rows)


def book_table(book, closed_map=None):
    return (
        '<div class="scroller"><table class="pos">'
        "<thead><tr><th>Symbol</th><th>Kind</th><th>Side</th>"
        '<th class="r">Weight</th><th class="r">Leverage</th><th class="r">Stop-loss</th>'
        '<th class="r">Take-profit</th><th>Recorded thesis</th></tr></thead>'
        f"<tbody>{position_rows(book, closed_map or {})}</tbody></table></div>")


def book_meta(book):
    """The extra fields a book may carry, rendered under it."""
    out = []
    if book.get("registration_note"):
        out.append('<div class="repair"><span class="badge repair-b">DESK REPAIR</span>'
                   f'{paras(book["registration_note"])}</div>')
    if book.get("r2_overlap_pct") is not None:
        out.append(f'<p class="tiny muted">Round-2 overlap check at registration: '
                   f'<strong>{book["r2_overlap_pct"]}%</strong> of gross weight shared with '
                   f'this agent’s same-direction Round-2 positions.</p>')
    if book.get("rules_epoch"):
        out.append(f'<p class="tiny muted">Rules epoch: <code>{esc(book["rules_epoch"])}</code></p>')
    return "".join(out)


def backtest_block(bt):
    if not bt:
        return ""
    rows = []
    for k in ("windows_tested", "strategy_return_pct", "benchmark_return_pct",
              "max_drawdown_pct"):
        if k not in bt:
            continue
        v = bt[k]
        if isinstance(v, dict):
            txt = "; ".join(f"{kk} {vv:+g}%" if isinstance(vv, (int, float)) else f"{kk} {vv}"
                            for kk, vv in v.items())
        elif isinstance(v, list):
            txt = "; ".join(str(x) for x in v)
        else:
            txt = str(v)
        rows.append(f'<tr><th scope="row">{esc(k.replace("_", " "))}</th><td>{esc(txt)}</td></tr>')
    notes = f'<p class="tiny">{esc(bt["notes"])}</p>' if bt.get("notes") else ""
    return ('<details class="sub"><summary>Pre-registration backtest</summary>'
            f'<table class="kv">{"".join(rows)}</table>{notes}</details>')


# ---------------------------------------------------------------- an agent

def agent_registry():
    reg = {}
    for rnd in (3, 2):
        for name, a in API[rnd]["agents"].items():
            e = reg.setdefault(name, {"name": name, "model": a["model"],
                                      "group": a["group"], "rounds": set()})
            e["rounds"].add(rnd)
            e["model"], e["group"] = a["model"], a["group"]
    perf_by_name = {a["name"]: a for a in PERF["agents"]}
    for name, e in reg.items():
        e["r1"] = perf_by_name.get(name)
        if e["r1"]:
            e["rounds"].add(1)
    return reg


REG = agent_registry()


def round_block(name, rnd, ent):
    a = API[rnd]["agents"][name]
    books = BOOKS[rnd][name]
    live = [b for b in books if b["entry"] <= AS_OF][-1]
    pending = [b for b in books if b["entry"] > AS_OF]
    fills = [f for f in FILLS[rnd].get(name, [])]
    closed = {f["symbol"].upper(): f for f in fills if f["ts"][:10] >= live["entry"]}

    pnl = a["nav"] - CAPITAL
    dates = sorted(a["series"])
    vs = spy_window(rnd, dates[0], dates[-1]) if len(dates) >= 2 else None
    late = dates and dates[0] > API[rnd]["entry"]

    tiles = [
        ("NAV", f'<span class="num">{money(a["nav"])}</span>', f'from {money(CAPITAL)} at entry'),
        ("P&amp;L, flat", signed(pnl, "usd"), "dollars earned or lost"),
        ("Growth", signed(a["growth_pct"]), "API <code>growth_pct</code>"),
        ("vs SPY", (signed(a["growth_pct"] - vs) + " pp") if vs is not None
         else '<span class="muted">n/a</span>',
         f'SPY {pct(vs)} over the same window' if vs is not None else ""),
        ("Max drawdown", f'<span class="num down">{pct(a["max_drawdown_pct"])}</span>',
         "peak-to-trough on daily NAV"),
        ("Gross exposure", num(a["gross_exposure_pct"], 1, "%"),
         "weight × leverage, registered book"),
        ("Cash", num(a["cash_pct"], 1, "%"), "earning 4% APY"),
        ("Positions", num(a["n_positions"], 0), "in the live book"),
    ]
    tile_html = "".join(
        f'<div class="tile"><div class="tl">{t}</div><div class="tv">{v}</div>'
        f'<div class="tn">{n}</div></div>' for t, v, n in tiles)

    entry_label = API[rnd]["entry"]
    head = (f'<div class="rndhead"><h4 id="{slug(name, rnd)}">Round {rnd} '
            f'<span class="tiny muted">· opened {entry_label} · priced through {AS_OF}</span></h4></div>')

    warn = ""
    if late:
        warn = ('<p class="callout">This book entered at the <strong>' + dates[0] +
                "</strong> close, after the Round-3 opening on " + entry_label +
                ". Its NAV covers a shorter window than the rest of the round and is "
                "<strong>not directly comparable</strong>; the “vs SPY” tile above is "
                "matched to this book’s own window.</p>")

    # mandate
    mand = [f'<p class="mandate"><span class="lab">Strategy</span>{esc(a["strategy"])}</p>']
    lb = live["data"]
    if lb.get("novelty"):
        mand.append(f'<p class="mandate"><span class="lab">Novelty statement</span>{esc(lb["novelty"])}</p>')
    if lb.get("treatment"):
        mand.append(f'<p class="mandate"><span class="lab">Treatment</span>{esc(lb["treatment"])}</p>')
    if lb.get("outlook"):
        mand.append(f'<p class="mandate"><span class="lab">Outlook</span>{esc(lb["outlook"])}</p>')
    if lb.get("why_no_leverage"):
        mand.append(f'<p class="mandate"><span class="lab">Why no leverage</span>{esc(lb["why_no_leverage"])}</p>')

    # live portfolio
    livehtml = (
        f'<h5>Live portfolio <span class="badge live">LIVE</span></h5>'
        f'<p class="tiny muted">Registered book effective at the <strong>{live["entry"]}</strong> '
        f'close — <code>{esc(live["path"])}</code>. This is what the account holds right now.</p>'
        + book_table(lb, closed) + book_meta(lb))

    # pending
    pend = ""
    for b in pending:
        pb = b["data"]
        pend += (
            f'<div class="pending"><h5>Registered, NOT yet filled '
            f'<span class="badge pend">PENDING — fills at the {b["entry"]} close</span></h5>'
            f'<p class="tiny">Price data runs through <strong>{AS_OF}</strong>. This book is '
            f'registered in git but has <strong>not</strong> been executed, contributes nothing to '
            f'the NAV above, and is <strong>not</strong> the current holding — '
            f'<code>{esc(b["path"])}</code>.</p>')
        if pb.get("strategy") and pb["strategy"] != a["strategy"]:
            pend += f'<p class="mandate"><span class="lab">Revised strategy</span>{esc(pb["strategy"])}</p>'
        if pb.get("novelty"):
            pend += f'<p class="mandate"><span class="lab">Novelty statement</span>{esc(pb["novelty"])}</p>'
        pend += (f'<p class="tiny muted">Declared cash: <strong>{pb["cash_pct"]}%</strong></p>'
                 + book_table(pb) + book_meta(pb) + "</div>")

    # decisions
    events = []
    b0 = books[0]
    open_bits = []
    if b0["data"].get("outlook"):
        open_bits.append(f'<p><span class="lab">Outlook at registration</span>{esc(b0["data"]["outlook"])}</p>')
    open_bits.append(backtest_block(b0["data"].get("backtest")))
    events.append({
        "date": b0["entry"], "action": "OPENED", "label": "Opening book registered",
        "source": b0["path"], "reason": None, "extra": "".join(open_bits) + book_meta(b0["data"]),
    })
    by_date = {b["entry"]: b for b in books[1:]}
    for e in sorted(DECISIONS.get((name, rnd), []), key=lambda x: x["date"]):
        e = dict(e)
        bk = by_date.get(e["date"])
        if bk:
            e["book"] = bk
        events.append(e)
    # any registered book with no matching desk decision still gets an event
    covered = {e["date"] for e in events}
    for d, bk in by_date.items():
        if d not in covered:
            events.append({"date": d, "action": "REBALANCE", "label": "Registered rebalance",
                           "source": bk["path"], "reason": None, "book": bk})
    events.sort(key=lambda x: (x["date"], x["action"]))

    dec_html = []
    for e in events:
        act = e["action"]
        akey = act.lower().replace(" ", "-")
        blocks = ""
        if e.get("reason"):
            blocks += (f'<div class="quote"><span class="lab">Stated reason (desk log)</span>'
                       f"{paras(e['reason'])}</div>")
        bk = e.get("book")
        if bk:
            rn = bk["data"].get("reassessment_note")
            if rn and rn != e.get("reason"):
                blocks += (f'<div class="quote"><span class="lab">Registered book note '
                           f'— <code>{esc(bk["path"])}</code></span>{paras(rn)}</div>')
            elif rn:
                blocks += ('<p class="tiny muted">The registered book carries the identical '
                           f'<code>reassessment_note</code> (<code>{esc(bk["path"])}</code>).</p>')
            blocks += book_meta(bk["data"])
        if e.get("note"):
            blocks += f'<p class="tiny muted">{esc(e["note"])}</p>'
        if e.get("extra"):
            blocks += e["extra"]
        if not blocks:
            blocks = '<p class="tiny muted">No reason text recorded in the data for this event.</p>'
        dec_html.append(
            f'<li class="ev"><div class="evhead"><span class="evdate">{e["date"]}</span>'
            f'<span class="badge act-{akey}">{esc(act)}</span>'
            f'<span class="tiny muted">{esc(e.get("label", ""))} · '
            f'<code>{esc(e["source"])}</code></span></div>{blocks}</li>')

    dec = (f'<details class="sub" open><summary>Decision history — {len(events)} recorded '
           f'event{"s" if len(events) != 1 else ""}</summary>'
           f'<ol class="timeline">{"".join(dec_html)}</ol></details>')

    # orders fired
    if fills:
        rows = "".join(
            "<tr>"
            f'<td>{f["ts"][:10]}</td>'
            f'<td><span class="badge act-{f["action"].lower()}">{esc(f["action"].replace("_", " "))}</span></td>'
            f'<th scope="row" class="sym">{esc(f["symbol"])}</th>'
            f'<td>{esc(f["kind"])}</td><td>{esc(f["side"])}</td>'
            f'<td class="r">{num(f["fill_price"], 4)}</td>'
            f'<td class="r">{money(f["proceeds_usd"])}</td>'
            f'<td class="r">{money(f["exit_cost_usd"])}</td></tr>' for f in fills)
        orders = ('<h5>Standing orders that fired</h5><div class="scroller">'
                  '<table class="pos"><thead><tr><th>Date</th><th>Action</th><th>Symbol</th>'
                  '<th>Kind</th><th>Side</th><th class="r">Fill price</th>'
                  '<th class="r">Proceeds</th><th class="r">Exit cost</th></tr></thead>'
                  f'<tbody>{rows}</tbody></table></div>'
                  '<p class="tiny muted">Proceeds move to cash at that close and earn 4% APY '
                  f'from that date. Source: <code>experiments/round{rnd}/fills.jsonl</code>.</p>')
    else:
        orders = ('<h5>Standing orders that fired</h5><p class="tiny muted">None — no '
                  'STOP_LOSS or TAKE_PROFIT executed for this book.</p>')

    return (f'<section class="rnd">{head}{warn}<div class="tiles">{tile_html}</div>'
            f'{sparkline(rnd, a["series"])}<div class="mand">{"".join(mand)}</div>'
            f"{livehtml}{pend}{orders}{dec}</section>")


def round1_block(r1):
    return (
        '<section class="rnd"><div class="rndhead"><h4>Round 1 '
        f'<span class="tiny muted">· percentage-only, no $1,000 account</span></h4></div>'
        '<p class="callout">Round 1 was scored in <strong>percent return only</strong> — it '
        'never had a $1,000 account, so there is no NAV, no flat-dollar P&amp;L and no drawdown '
        'series for it. The figures below are returns as published in '
        '<code>docs/api/performance.json</code>; reading them as dollars would only ever be a '
        '$1,000-equivalent illustration, not something the experiment traded.</p>'
        '<div class="tiles">'
        f'<div class="tile"><div class="tl">H1 2026 return</div><div class="tv">{signed(r1["h1_return_pct"])}</div>'
        f'<div class="tn">2026-01-02 → close; SPY {pct(PERF["spy"]["h1_to_date_pct"])}</div></div>'
        f'<div class="tile"><div class="tl">H2 to date</div><div class="tv">{signed(r1["h2_return_pct"])}</div>'
        f'<div class="tn">from {PERF["h2_entry"]}; SPY {pct(PERF["spy"]["h2_to_date_pct"])}</div></div>'
        f'<div class="tile"><div class="tl">H2 hold counterfactual</div>'
        f'<div class="tv">{signed(r1["h2_hold_counterfactual_pct"])}</div>'
        f'<div class="tn">had the H1 book simply been held</div></div>'
        "</div>"
        f'<p class="mandate"><span class="lab">Round-1 mandate</span>{esc(r1["strategy"])}</p>'
        "</section>")


def agent_card(e):
    name = e["name"]
    rounds = sorted(e["rounds"])
    tags = "".join(f'<span class="badge rnd-b">R{r}</span>' for r in rounds)
    idx = " ".join([name, e["model"], e["group"]])
    syms = set()
    for r in (2, 3):
        if r in e["rounds"]:
            for p in API[r]["agents"][name]["positions"]:
                syms.add(p["symbol"])
        for b in BOOKS[r].get(name, []):
            idx += " " + b["data"].get("strategy", "")
    idx += " " + " ".join(sorted(syms))

    research = None
    for log, eff, _ in DESK_LOGS:
        for mgr in log["decisions"]:
            if mgr["name"] == name and mgr.get("research_notes"):
                research = (eff, log.get("desk_run_utc", ""), mgr["research_notes"])
    rn_html = ""
    if research:
        rn_html = ('<details class="sub"><summary>Research notes — free-internet poll, '
                   f'desk run {esc(research[1])}</summary>'
                   f'<div class="quote">{paras(research[2])}</div>'
                   '<p class="tiny muted">Recorded once per manager in '
                   '<code>experiments/desk/unrestricted_resize_2026-07-30.json</code> and copied '
                   'verbatim into that manager’s 2026-07-31 books.</p></details>')

    body = ""
    if e.get("r1"):
        body += round1_block(e["r1"])
    for r in (2, 3):
        if r in e["rounds"]:
            body += round_block(name, r, e)

    return (
        f'<article class="card" id="{slug(name)}" data-idx="{esc(idx.lower())}">'
        f'<header class="cardhead"><h3>{esc(name)}<a class="anchor" href="#{slug(name)}" '
        f'aria-label="Link to {esc(name)}">#</a></h3>'
        f'<div class="idline"><span><span class="lab2">Model tier</span> '
        f'<strong>{TIER.get(e["model"], e["model"])}</strong></span>'
        f'<span><span class="lab2">Cohort</span> <strong>{COHORT.get(e["group"], e["group"])}</strong></span>'
        f'<span><span class="lab2">Manages</span> {tags}</span></div></header>'
        f"{rn_html}{body}</article>")


# ------------------------------------------------------------ summary rows

def summary_rows():
    rows = []
    for name, e in REG.items():
        for rnd in (2, 3):
            if rnd not in e["rounds"]:
                continue
            a = API[rnd]["agents"][name]
            books = BOOKS[rnd][name]
            live = [b for b in books if b["entry"] <= AS_OF][-1]
            dates = sorted(a["series"])
            vs = spy_window(rnd, dates[0], dates[-1]) if len(dates) >= 2 else None
            pnl = a["nav"] - CAPITAL
            late = "" if not (dates and dates[0] > API[rnd]["entry"]) else \
                ' <span class="badge late">late entry</span>'
            vs_v = (a["growth_pct"] - vs) if vs is not None else None
            vs_c = (signed(vs_v) + " pp") if vs_v is not None else DASH
            rows.append({
                "sort": (-a["nav"], name), "name": name, "rnd": rnd,
                "html": "<tr>"
                f'<th scope="row"><a href="#{slug(name, rnd)}">{esc(name)}</a>{late}</th>'
                f'<td>{TIER.get(e["model"], e["model"])}</td>'
                f'<td>{COHORT.get(e["group"], e["group"])}</td>'
                f'<td class="r">{rnd}</td>'
                f'<td class="r">{live["entry"]}</td>'
                f'<td class="r" data-v="{a["nav"]}"><span class="num">{money(a["nav"])}</span></td>'
                f'<td class="r" data-v="{pnl}">{signed(pnl, "usd")}</td>'
                f'<td class="r" data-v="{a["growth_pct"]}">{signed(a["growth_pct"])}</td>'
                f'<td class="r" data-v="{vs_v if vs_v is not None else -999}">{vs_c}</td>'
                f'<td class="r" data-v="{a["max_drawdown_pct"]}"><span class="num down">{pct(a["max_drawdown_pct"])}</span></td>'
                f'<td class="r" data-v="{a["gross_exposure_pct"]}">{num(a["gross_exposure_pct"], 1, "%")}</td>'
                f'<td class="r" data-v="{a["cash_pct"]}">{num(a["cash_pct"], 1, "%")}</td>'
                f'<td class="r" data-v="{a["n_positions"]}">{num(a["n_positions"], 0)}</td>'
                "</tr>"})
    rows.sort(key=lambda r: r["sort"])
    return rows


def round1_table():
    rows = []
    for a in sorted(PERF["agents"], key=lambda x: -x["h2_return_pct"]):
        e = REG.get(a["name"], {})
        rows.append(
            "<tr>"
            f'<th scope="row"><a href="#{slug(a["name"])}">{esc(a["name"])}</a></th>'
            f'<td>{TIER.get(a["model"], a["model"])}</td>'
            f'<td>{COHORT.get(a["group"], a["group"])}</td>'
            f'<td class="r" data-v="{a["h1_return_pct"]}">{signed(a["h1_return_pct"])}</td>'
            f'<td class="r" data-v="{a["h2_return_pct"]}">{signed(a["h2_return_pct"])}</td>'
            f'<td class="r" data-v="{a["h2_hold_counterfactual_pct"]}">{signed(a["h2_hold_counterfactual_pct"])}</td>'
            "</tr>")
    return "".join(rows)


def repairs_table():
    rows = []
    for rnd in (2, 3):
        for name, books in sorted(BOOKS[rnd].items()):
            for b in books:
                note = b["data"].get("registration_note")
                if not note:
                    continue
                rows.append((b["entry"], rnd, name,
                             "<tr>"
                             f'<td class="r">{b["entry"]}</td><td class="r">{rnd}</td>'
                             f'<th scope="row"><a href="#{slug(name, rnd)}">{esc(name)}</a></th>'
                             f'<td>{esc(note)}</td>'
                             f'<td><code>{esc(b["path"])}</code></td></tr>'))
    rows.sort()
    return "".join(r[3] for r in rows), len(rows)


def fills_table():
    rows = []
    for rnd in (2, 3):
        for name, fs in FILLS[rnd].items():
            for f in fs:
                rows.append((f["ts"], "<tr>"
                             f'<td class="r">{f["ts"][:10]}</td><td class="r">{rnd}</td>'
                             f'<th scope="row"><a href="#{slug(name, rnd)}">{esc(name)}</a></th>'
                             f'<td><span class="badge act-{f["action"].lower()}">'
                             f'{esc(f["action"].replace("_", " "))}</span></td>'
                             f'<td class="sym">{esc(f["symbol"])}</td><td>{esc(f["side"])}</td>'
                             f'<td class="r">{num(f["fill_price"], 4)}</td>'
                             f'<td class="r">{money(f["proceeds_usd"])}</td></tr>'))
    rows.sort()
    return "".join(r[1] for r in rows), len(rows)


# ------------------------------------------------------------------- page

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  color-scheme:light;
  --page:#f9f9f7; --surface:#fcfcfb; --surface-2:#f3f2ee;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,0.10);
  --up:#256abf; --down:#b52a26;
  --chip:#eceae4;
}
@media (prefers-color-scheme:dark){
  :root:where(:not([data-theme="light"])){
    color-scheme:dark;
    --page:#0d0d0d; --surface:#1a1a19; --surface-2:#121211;
    --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,0.10);
    --up:#3987e5; --down:#e66767;
    --chip:#262624;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --page:#0d0d0d; --surface:#1a1a19; --surface-2:#121211;
  --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,0.10);
  --up:#3987e5; --down:#e66767;
  --chip:#262624;
}
body{margin:0;background:var(--page);color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;
  overflow-x:hidden;-webkit-text-size-adjust:100%}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px 96px}
h1{font-size:26px;line-height:1.2;margin:0 0 6px}
h2{font-size:19px;margin:44px 0 10px;padding-top:14px;border-top:1px solid var(--border)}
h3{font-size:18px;margin:0}
h4{font-size:15px;margin:0}
h5{font-size:13px;margin:20px 0 6px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2)}
p{margin:8px 0}
code{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  background:var(--chip);padding:1px 4px;border-radius:3px;word-break:break-all}
a{color:inherit}
.num{font-variant-numeric:tabular-nums}
.up{color:var(--up)} .down{color:var(--down)}
.gly{font-size:.78em;margin-right:.25em;vertical-align:.05em}
.muted{color:var(--muted)}
.tiny{font-size:12px;line-height:1.5}
.r{text-align:right}
.lab,.lab2{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin-bottom:2px}
.lab code{text-transform:none;letter-spacing:0}
.lab2{display:inline;text-transform:uppercase;font-size:11px;margin-right:2px}

/* header */
.top{position:sticky;top:0;z-index:20;background:var(--surface);
  border-bottom:1px solid var(--border);padding:8px 20px;
  display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.top .brand{font-weight:600;font-size:13px;margin-right:auto}
.top input{flex:1 1 200px;min-width:140px;max-width:340px;font:inherit;font-size:13px;
  padding:5px 9px;border:1px solid var(--axis);border-radius:6px;
  background:var(--surface-2);color:var(--ink)}
.btn{font:inherit;font-size:12px;padding:5px 10px;border:1px solid var(--axis);
  border-radius:6px;background:var(--surface-2);color:var(--ink);cursor:pointer}
.btn:hover{background:var(--chip)}
.hero{padding:28px 0 4px}
.sub-l{color:var(--ink-2);font-size:14px;margin:0 0 14px;max-width:74ch}

/* callouts */
.callout{background:var(--surface-2);border:1px solid var(--border);
  border-left:3px solid var(--axis);border-radius:0 6px 6px 0;padding:10px 14px;
  font-size:13px;line-height:1.55}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--ink-2);
  margin:10px 0 0;align-items:center}
.legend .k{display:inline-flex;align-items:center;gap:6px}
.swatch{width:22px;height:3px;border-radius:2px;display:inline-block}

/* index */
.idxgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.idxcol h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2);
  margin:0 0 4px}
.idxcol ul{list-style:none;margin:0;padding:0}
.idxcol li{margin:0}
.idxcol a{display:block;padding:2px 0;font-size:13px;text-decoration:none;color:var(--ink-2);
  border-bottom:1px solid transparent}
.idxcol a:hover{color:var(--ink);border-bottom-color:var(--axis)}

/* tables */
.scroller{overflow-x:auto;max-width:100%;border:1px solid var(--border);border-radius:8px;
  background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:7px 10px;text-align:left;vertical-align:top;
  border-bottom:1px solid var(--grid);white-space:nowrap}
thead th{position:sticky;top:0;background:var(--surface-2);z-index:2;
  font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-2);
  border-bottom:1px solid var(--axis)}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:none}
tbody tr:hover td,tbody tr:hover th{background:var(--surface-2)}
table.sortable thead th{cursor:pointer;user-select:none}
table.sortable thead th::after{content:"";opacity:.45;font-size:9px;margin-left:4px}
table.sortable thead th[data-dir="asc"]::after{content:"\\25b2"}
table.sortable thead th[data-dir="desc"]::after{content:"\\25bc"}
td.thesis,td.note{white-space:normal;min-width:280px;max-width:560px;color:var(--ink-2);
  font-size:12.5px;line-height:1.5}
.sym{font-weight:600;font-variant-numeric:tabular-nums}
table.kv th{width:190px;color:var(--ink-2);font-weight:500;white-space:normal}
table.kv td{white-space:normal}
table.summary th,table.summary td{padding:6px 8px}
table.summary tbody th{white-space:normal;min-width:150px;max-width:230px;font-weight:600}
table.summary tbody th a{text-decoration:none;border-bottom:1px solid var(--axis)}
table.summary tbody th a:hover{border-bottom-color:var(--ink)}

/* cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:18px 20px 8px;margin:16px 0;scroll-margin-top:64px;
  content-visibility:auto;contain-intrinsic-size:auto 1400px}
.cardhead{border-bottom:1px solid var(--grid);padding-bottom:10px;margin-bottom:4px}
.cardhead h3{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.anchor{text-decoration:none;color:var(--muted);font-size:14px;opacity:.6}
.anchor:hover{opacity:1}
.idline{display:flex;gap:20px;flex-wrap:wrap;margin-top:6px;font-size:13px;color:var(--ink-2)}
.rnd{padding:14px 0 4px;border-top:1px solid var(--grid);margin-top:12px}
.rnd:first-of-type{border-top:none}
.rndhead{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}
.rndhead h4{scroll-margin-top:64px}

/* tiles */
.tiles{display:grid;gap:1px;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));
  background:var(--surface);border:1px solid var(--grid);border-radius:8px;overflow:hidden;
  margin:10px 0 14px}
.tile{background:var(--surface);padding:9px 11px;
  box-shadow:1px 0 0 var(--grid),0 1px 0 var(--grid),1px 1px 0 var(--grid)}
.tl{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.tv{font-size:17px;line-height:1.3;margin:2px 0 1px}
.tn{font-size:11px;color:var(--muted);line-height:1.35}

/* chart */
.chartbox{margin:0 0 14px;padding:0}
.chartbox figcaption{margin-bottom:2px}
.sparkwrap{position:relative;background:var(--surface);border:1px solid var(--border);
  border-radius:8px;padding:4px 6px}
svg.spark{display:block;width:100%;height:auto;max-height:150px}
svg.spark .par{stroke:var(--grid);stroke-width:1;stroke-dasharray:3 3}
svg.spark .spy{fill:none;stroke:var(--muted);stroke-width:2;stroke-dasharray:5 4}
svg.spark .nav{fill:none;stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}
svg.spark .nav.up,svg.spark .end.up,svg.spark .focus.up{stroke:var(--up)}
svg.spark .nav.down,svg.spark .end.down,svg.spark .focus.down{stroke:var(--down)}
svg.spark .end.up{fill:var(--up)} svg.spark .end.down{fill:var(--down)}
svg.spark .focus{fill:var(--surface);stroke-width:2.5}
svg.spark .cross{stroke:var(--axis);stroke-width:1}
svg.spark .axlbl{fill:var(--muted);font:11px system-ui,sans-serif}
svg.spark .endlbl{fill:var(--ink);font:11px system-ui,sans-serif;font-variant-numeric:tabular-nums}
.tip{position:absolute;pointer-events:none;background:var(--surface);color:var(--ink);
  border:1px solid var(--axis);border-radius:6px;padding:5px 8px;font-size:12px;
  box-shadow:0 2px 8px rgba(0,0,0,.14);white-space:nowrap;z-index:5;
  font-variant-numeric:tabular-nums}

/* prose blocks */
.mand{margin:4px 0 10px}
.mandate{background:var(--surface-2);border:1px solid var(--border);border-radius:8px;
  padding:9px 12px;margin:6px 0;font-size:13.5px;line-height:1.55}
.quote{border-left:3px solid var(--axis);padding:2px 0 2px 12px;margin:8px 0;
  font-size:13px;line-height:1.6;color:var(--ink-2)}
.quote p{margin:6px 0}
.repair{border:1px dashed var(--axis);border-radius:8px;padding:8px 12px;margin:8px 0;
  font-size:12.5px;background:var(--surface-2)}
.pending{border:2px dashed var(--axis);border-radius:10px;padding:12px 14px;margin:16px 0;
  background:var(--surface-2)}
.pending h5{margin-top:0}

/* badges */
.badge{display:inline-block;font-size:10px;font-weight:700;letter-spacing:.07em;
  text-transform:uppercase;padding:2px 6px;border-radius:4px;border:1px solid var(--axis);
  color:var(--ink-2);background:var(--surface);white-space:nowrap;vertical-align:middle}
.badge.live{border-color:var(--ink-2);color:var(--ink)}
.badge.pend{border-style:dashed;border-width:2px;color:var(--ink);font-weight:700}
.badge.closed{margin-left:6px;font-size:9px;border-style:dashed}
.badge.rnd-b{margin-right:3px}
.badge.late{font-weight:600}
.badge.act-hold{border-style:dotted}
.badge.act-rebalance,.badge.act-opened{border-color:var(--ink-2);color:var(--ink)}
.badge.act-default-hold{border-style:dotted;font-style:italic}
.badge.act-stop_loss,.badge.act-take_profit{border-color:var(--ink-2);color:var(--ink)}
.badge.repair-b{margin-right:8px}

/* timeline */
details.sub{border-top:1px solid var(--grid);margin-top:14px;padding-top:2px}
details.sub>summary{cursor:pointer;font-size:13px;font-weight:600;padding:8px 0;
  color:var(--ink-2);list-style-position:outside}
details.sub>summary:hover{color:var(--ink)}
.timeline{list-style:none;margin:4px 0 12px;padding:0 0 0 14px;border-left:1px solid var(--grid)}
.ev{position:relative;padding:0 0 16px 14px}
.ev::before{content:"";position:absolute;left:-19px;top:7px;width:9px;height:9px;
  border-radius:50%;background:var(--surface);border:2px solid var(--axis)}
.evhead{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:2px}
.evdate{font-weight:600;font-size:13px;font-variant-numeric:tabular-nums}

.tofoot{position:fixed;right:16px;bottom:16px;z-index:30;text-decoration:none;
  background:var(--surface);border:1px solid var(--axis);border-radius:20px;
  padding:7px 13px;font-size:12px;box-shadow:0 2px 8px rgba(0,0,0,.14)}
.hidden{display:none !important}
@media (max-width:620px){
  .wrap{padding:0 12px 80px}
  .card{padding:14px 12px 6px;scroll-margin-top:150px}
  .rndhead h4{scroll-margin-top:150px}
  h1{font-size:22px}
}
"""

JS = r"""
(function(){
  // ---- sparkline hover -------------------------------------------------
  document.querySelectorAll('.sparkwrap').forEach(function(wrap){
    var data; try{ data = JSON.parse(wrap.dataset.series); }catch(e){ return; }
    var svg = wrap.querySelector('svg'), tip = wrap.querySelector('.tip');
    var cross = svg.querySelector('.cross'), focus = svg.querySelector('.focus');
    var n = data.d.length;
    function step(i){ return data.L + i*(data.W-data.L-data.R)/(n-1); }
    function move(ev){
      var r = svg.getBoundingClientRect();
      var vx = (ev.clientX - r.left) / r.width * data.W;
      var i = Math.round((vx - data.L) / ((data.W-data.L-data.R)/(n-1)));
      i = Math.max(0, Math.min(n-1, i));
      var x = step(i);
      cross.setAttribute('x1', x); cross.setAttribute('x2', x);
      cross.style.display = '';
      var pts = svg.querySelector('.nav').getAttribute('d').split('L');
      var yy = (i===0 ? pts[0].slice(1) : pts[i]).trim().split(' ')[1];
      focus.setAttribute('cx', x); focus.setAttribute('cy', yy); focus.style.display = '';
      var spy = data.s.length ? '<br>SPY $1,000 &middot; $' + data.s[i].toLocaleString(undefined,
                {minimumFractionDigits:2, maximumFractionDigits:2}) : '';
      tip.innerHTML = '<strong>' + data.d[i] + '</strong><br>NAV &middot; $' +
        data.n[i].toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}) + spy;
      tip.hidden = false;
      var px = x / data.W * r.width;
      tip.style.left = Math.max(2, Math.min(r.width - tip.offsetWidth - 2, px - tip.offsetWidth/2)) + 'px';
      tip.style.top = '2px';
    }
    function leave(){ tip.hidden = true; cross.style.display='none'; focus.style.display='none'; }
    wrap.addEventListener('mousemove', move);
    wrap.addEventListener('mouseleave', leave);
    wrap.addEventListener('touchmove', function(e){ if(e.touches[0]) move(e.touches[0]); });
    wrap.addEventListener('touchend', leave);
  });

  // ---- sortable tables --------------------------------------------------
  document.querySelectorAll('table.sortable').forEach(function(tbl){
    tbl.querySelectorAll('thead th').forEach(function(th, idx){
      th.addEventListener('click', function(){
        var dir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
        tbl.querySelectorAll('thead th').forEach(function(o){ delete o.dataset.dir; });
        th.dataset.dir = dir;
        var body = tbl.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function(a,b){
          var ca = a.cells[idx], cb = b.cells[idx];
          var va = ca.dataset.v, vb = cb.dataset.v;
          if(va !== undefined && vb !== undefined){
            return (dir==='asc'?1:-1) * (parseFloat(va) - parseFloat(vb));
          }
          return (dir==='asc'?1:-1) *
            ca.textContent.trim().localeCompare(cb.textContent.trim(), undefined, {numeric:true});
        });
        rows.forEach(function(r){ body.appendChild(r); });
      });
    });
  });

  // ---- search filter ----------------------------------------------------
  var box = document.getElementById('q');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var links = Array.prototype.slice.call(document.querySelectorAll('.idxcol li'));
  var count = document.getElementById('qcount');
  if(box){
    box.addEventListener('input', function(){
      var q = box.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function(c){
        var hit = !q || c.dataset.idx.indexOf(q) > -1;
        c.classList.toggle('hidden', !hit); if(hit) shown++;
      });
      links.forEach(function(li){
        var a = li.querySelector('a'), id = a.getAttribute('href').slice(1);
        var c = document.getElementById(id);
        li.classList.toggle('hidden', !!c && c.classList.contains('hidden'));
      });
      document.querySelectorAll('.cohort-sec').forEach(function(s){
        var any = s.querySelectorAll('.card:not(.hidden)').length;
        s.classList.toggle('hidden', any === 0);
      });
      count.textContent = q ? shown + ' of ' + cards.length + ' agents' : '';
    });
  }

  // ---- expand / collapse ------------------------------------------------
  function setAll(open){
    document.querySelectorAll('details.sub').forEach(function(d){ d.open = open; });
  }
  var eb = document.getElementById('expand'), cb = document.getElementById('collapse');
  if(eb) eb.addEventListener('click', function(){ setAll(true); });
  if(cb) cb.addEventListener('click', function(){ setAll(false); });

  // ---- theme toggle -----------------------------------------------------
  var tb = document.getElementById('theme');
  if(tb) tb.addEventListener('click', function(){
    var cur = document.documentElement.getAttribute('data-theme');
    if(!cur){
      cur = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
  });
})();
"""


def build():
    rows = summary_rows()
    repairs_html, n_repairs = repairs_table()
    fills_html, n_fills = fills_table()

    n_decisions = sum(len(v) for v in DECISIONS.values())
    n_books = sum(len(b) for r in (2, 3) for b in BOOKS[r].values())
    n_pending = sum(1 for r in (2, 3) for bl in BOOKS[r].values()
                    for b in bl if b["entry"] > AS_OF)
    n_live = sum(len(API[r]["agents"]) for r in (2, 3))

    # index
    idx = []
    for g in COHORT_ORDER:
        names = sorted(n for n, e in REG.items() if e["group"] == g)
        if not names:
            continue
        lis = "".join(f'<li><a href="#{slug(n)}">{esc(n)}</a></li>' for n in names)
        idx.append(f'<div class="idxcol"><h3>{COHORT[g]} <span class="muted">({len(names)})</span></h3>'
                   f"<ul>{lis}</ul></div>")

    # cards by cohort
    sections = []
    for g in COHORT_ORDER:
        members = sorted((e for e in REG.values() if e["group"] == g),
                         key=lambda e: (list(TIER).index(e["model"]), e["name"]))
        if not members:
            continue
        cards = "".join(agent_card(e) for e in members)
        sections.append(
            f'<section class="cohort-sec"><h2 id="cohort-{g}">{COHORT[g]} '
            f'<span class="muted" style="font-weight:400">· {len(members)} agents</span></h2>'
            f'<p class="sub-l">{COHORT_BLURB[g]}</p>{cards}</section>')

    b2 = API[2]["benchmarks"]
    b3 = API[3]["benchmarks"]

    head_stats = "".join(
        f'<div class="tile"><div class="tl">{t}</div><div class="tv">{v}</div>'
        f'<div class="tn">{n}</div></div>' for t, v, n in [
            ("Agents", num(len(REG), 0), f"{len(API[2]['agents'])} Round-2 books, "
                                         f"{len(API[3]['agents'])} Round-3 books"),
            ("Books registered", num(n_books, 0),
             f"{n_live} live now, {n_pending} pending, {n_books - n_live - n_pending} superseded"),
            ("Decision events", num(n_decisions, 0), "desk-log entries, HOLDs included"),
            ("Standing orders fired", num(n_fills, 0), "STOP_LOSS / TAKE_PROFIT"),
            ("SPY $1,000 · R2", f'<span class="num">{money(b2["SPY ($1000)"]["nav"])}</span>',
             f'{pct(b2["SPY ($1000)"]["nav"]/CAPITAL*100-100)} since {API[2]["entry"]}'),
            ("BTC $1,000 · R2", f'<span class="num">{money(b2["BTC ($1000)"]["nav"])}</span>',
             f'{pct(b2["BTC ($1000)"]["nav"]/CAPITAL*100-100)} since {API[2]["entry"]}'),
            ("SPY $1,000 · R3", f'<span class="num">{money(b3["SPY ($1000)"]["nav"])}</span>',
             f'{pct(b3["SPY ($1000)"]["nav"]/CAPITAL*100-100)} since {API[3]["entry"]}'),
            ("BTC $1,000 · R3", f'<span class="num">{money(b3["BTC ($1000)"]["nav"])}</span>',
             f'{pct(b3["BTC ($1000)"]["nav"]/CAPITAL*100-100)} since {API[3]["entry"]}'),
        ])

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StockGuessr — agent roster dossier</title>
<style>{CSS}</style>
</head>
<body>
<div class="top">
  <span class="brand">StockGuessr roster · priced through {AS_OF}</span>
  <input id="q" type="search" placeholder="Filter agents — name, mandate, ticker…"
         aria-label="Filter agents">
  <span id="qcount" class="tiny muted"></span>
  <button class="btn" id="expand" type="button">Expand all</button>
  <button class="btn" id="collapse" type="button">Collapse all</button>
  <button class="btn" id="theme" type="button">Light / dark</button>
</div>
<div class="wrap">

<header class="hero">
  <h1>Agent roster dossier</h1>
  <p class="sub-l">Every agent in the StockGuessr experiment: identity, mandate, live
  portfolio, decision history with the reasons each manager stated, and performance as of
  the <strong>{AS_OF}</strong> close. Round-2 and Round-3 books are priced by
  <code>tracker/round2.py</code>; this page is generated from the committed data files by
  <code>tracker/make_roster_page.py</code> and states no figure the files do not.</p>
  <div class="tiles">{head_stats}</div>
  <p class="callout"><strong>Live vs pending.</strong> Price data runs through the
  <strong>{AS_OF}</strong> close. An agent&rsquo;s live portfolio is its most recent book whose
  <code>entry</code> is on or before that date. The books dated
  <code>weeks/2026-07-31/</code> are <strong>registered but not yet filled</strong> — they
  execute at the 2026-07-31 close. They appear on every card in a separate dashed
  <em>pending</em> block and are never counted in the NAV, exposure or cash figures above them.</p>
  <p class="callout"><strong>Three things not to misread.</strong>
  (1) <strong>Round 1 is percentage-only</strong> — it never had a $1,000 account; its H1/H2
  numbers are returns, and any dollar reading of them is a $1,000-equivalent illustration.
  (2) The <strong>Opus 5 field entered on 2026-07-27</strong>, seven sessions after the rest of
  Round 3, so its NAV is <strong>not directly comparable</strong> with the rest of the round;
  each of those cards carries the warning and its &ldquo;vs SPY&rdquo; figure is matched to its own
  shorter window. (3) A position can still be listed in a live book after a standing order
  closed it — those are flagged <em>CLOSED</em> in the portfolio table, and the API&rsquo;s
  gross-exposure figure reflects the registered book, not the post-stop book.</p>
  <div class="legend">
    <span class="k"><span class="swatch" style="background:var(--up)"></span>
      <span class="up">▲ gain</span></span>
    <span class="k"><span class="swatch" style="background:var(--down)"></span>
      <span class="down">▼ loss</span></span>
    <span class="k">Colour marks the sign of a return and nothing else — model tier and cohort
    are written out in text. Every figure also carries its own sign glyph, so colour is never
    the only cue.</span>
  </div>
</header>

<h2 id="summary">Summary — all books, current standing</h2>
<p class="sub-l">One row per agent-round book, {len(rows)} in total ({len(API[2]['agents'])}
Round-2 + {len(API[3]['agents'])} Round-3). NAV, growth, drawdown, exposure and cash are read
verbatim from <code>docs/api/round2.json</code> and <code>docs/api/round3.json</code>; flat P&amp;L
is NAV minus the $1,000 opening capital, and &ldquo;vs SPY&rdquo; is this book&rsquo;s growth minus
$1,000-in-SPY over the same dates. Click a header to sort.</p>
<div class="scroller"><table class="sortable summary">
<thead><tr><th>Agent</th><th>Tier</th><th>Cohort</th><th class="r">Round</th>
<th class="r">Live book</th><th class="r">NAV</th><th class="r">P&amp;L $</th>
<th class="r">Growth</th><th class="r">vs SPY</th><th class="r">Max DD</th>
<th class="r">Gross</th><th class="r">Cash</th><th class="r">Pos</th></tr></thead>
<tbody>{"".join(r["html"] for r in rows)}</tbody></table></div>

<h2 id="round1">Round 1 — percentage-only</h2>
<p class="sub-l">The original round, from <code>docs/api/performance.json</code>, as of the
{PERF['as_of_close']} close. <strong>No $1,000 account existed</strong>: these are percentage
returns, not dollars. SPY over the same windows: H1 {pct(PERF['spy']['h1_to_date_pct'])},
H2 {pct(PERF['spy']['h2_to_date_pct'])}. The counterfactual column is what the H1 book would
have returned in H2 had it simply been held.</p>
<div class="scroller"><table class="sortable summary">
<thead><tr><th>Agent</th><th>Tier</th><th>Cohort</th><th class="r">H1 2026</th>
<th class="r">H2 to date</th><th class="r">H2 hold counterfactual</th></tr></thead>
<tbody>{round1_table()}</tbody></table></div>

<h2 id="orders">Standing orders that fired</h2>
<p class="sub-l">Every non-opening execution in
<code>experiments/round2/fills.jsonl</code> and <code>experiments/round3/fills.jsonl</code> —
{n_fills} in total. Proceeds move to cash at that close and earn 4% APY from that date.</p>
<div class="scroller"><table>
<thead><tr><th class="r">Date</th><th class="r">Round</th><th>Agent</th><th>Action</th>
<th>Symbol</th><th>Side</th><th class="r">Fill price</th><th class="r">Proceeds</th></tr></thead>
<tbody>{fills_html}</tbody></table></div>

<h2 id="repairs">Desk repairs at registration</h2>
<p class="sub-l">{n_repairs} books carry a <code>registration_note</code> disclosing that the
execution desk repaired the arithmetic of a submitted book. These are shown here and again on
each agent&rsquo;s card; they are not hidden. The 2026-07-30 desk log records
<strong>{DESK_LOGS[2][0]['arithmetic_repairs']}</strong> repairs for the resize event.</p>
<div class="scroller"><table>
<thead><tr><th class="r">Effective</th><th class="r">Round</th><th>Agent</th>
<th>Repair recorded by the desk</th><th>File</th></tr></thead>
<tbody>{repairs_html}</tbody></table></div>

<h2 id="index">Index — {len(REG)} agents</h2>
<div class="idxgrid">{"".join(idx)}</div>

{"".join(sections)}

<h2 id="notes">Notes on the data</h2>
<ul class="tiny" style="color:var(--ink-2);line-height:1.7;max-width:78ch">
<li>Agent counts: <strong>{len(API[2]['agents'])}</strong> Round-2 books,
<strong>{len(API[3]['agents'])}</strong> Round-3 books,
<strong>{len(REG)}</strong> distinct agents. The 2026-07-30 desk log polled
<strong>{DESK_LOGS[2][0]['managers_polled']}</strong> managers — that is the roster minus the
orchestrator, whose own decisions are logged separately under each desk log&rsquo;s
<code>orchestrator</code> key rather than in its <code>decisions</code> array. That is why the
orchestrator&rsquo;s events cite the log&rsquo;s orchestrator field.</li>
<li>Two managers — Sonnet quality compounders and Sonnet small/mid-cap growth — did
not respond to the week-1 poll and are listed in that log&rsquo;s
<code>failed_default_hold</code>. Their 2026-07-20 events are shown as
<strong>DEFAULT HOLD</strong> with no stated reason, because the data contains none.</li>
<li>The 2026-07-18 desk log stores only an action for the orchestrator
(<code>round2: &ldquo;REBALANCE (deployed 9pts cash into MU/AMD/NVDA)&rdquo;</code>,
<code>round3: &ldquo;HOLD&rdquo;</code>) and no reason field. Its Round-2 reason survives in the
registered book&rsquo;s <code>reassessment_note</code>; its Round-3 HOLD has <strong>no recorded
reason anywhere in the data</strong> and is shown as such.</li>
<li>The Opus 5 field&rsquo;s nine books open on 2026-07-27 and therefore have three daily
marks, not thirteen. They took part in the 2026-07-30 resize only.</li>
<li>Research notes were collected once per manager at the 2026-07-30 free-internet poll and
copied verbatim into that manager&rsquo;s 2026-07-31 books; the page shows them once per agent.</li>
<li>Rules epochs: books registered before 2026-07-30 were built under the old concentration
caps (max 40% single position, shorts ≤ 50%, minimum 5 positions); books tagged
<code>unrestricted-retail-2026-07-30</code> were built with those caps lifted. See
<code>experiments/round2/RULES.md</code> and <code>experiments/round3/RULES.md</code>.</li>
</ul>

<p class="tiny muted" style="margin-top:28px">Generated {generated} by
<code>tracker/make_roster_page.py</code>. Round-2 API updated {API[2]['updated_utc']};
Round-3 API updated {API[3]['updated_utc']}; Round-1 performance updated
{PERF['updated_utc']}.</p>

</div>
<a class="tofoot" href="#summary">↑ Top</a>
<script>{JS}</script>
</body>
</html>
"""


def main():
    OUT.write_text(build())
    n_dec = sum(len(v) for v in DECISIONS.values())
    n_fills = sum(len(v) for r in (2, 3) for v in FILLS[r].values())
    print(f"wrote {rel(OUT)}  ({OUT.stat().st_size/1024:.0f} KB)")
    print(f"  agents: {len(REG)}  |  R2 books: {len(API[2]['agents'])}  "
          f"R3 books: {len(API[3]['agents'])}")
    print(f"  decision events: {n_dec}  |  standing-order fills: {n_fills}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Assemble one account packet per manager for a weekly Execution Desk poll.

Lives in the repo on purpose. The first eight weeks of this were run from a
throwaway script in the session scratchpad, and when the container was rebuilt
on 2026-09-15 the whole desk toolchain vanished with it, mid-week, while the
poll was already overdue. The packets are the managers' only view of their own
accounts; the thing that builds them belongs under version control.

    python3 tracker/desk_packets.py --entry 2026-09-16 --last-poll 2026-09-08 \
        [--out DIR]
"""
import argparse, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    argv, sys.argv = sys.argv, ["round2.py"]
    spec = importlib.util.spec_from_file_location("r2", ROOT / "tracker/round2.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    sys.argv = argv
    return m


def legs_for(rnd, stem):
    base = ROOT / "experiments" / f"round{rnd}"
    out = [json.loads((base / "allocations" / f"{stem}.json").read_text())]
    for wk in sorted((base / "weeks").glob("*/")):
        f = wk / f"{stem}.json"
        if f.exists():
            out.append(json.loads(f.read_text()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True, help="next trading date, YYYY-MM-DD")
    ap.add_argument("--last-poll", required=True, help="entry date of the previous desk leg")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out_dir = Path(a.out) if a.out else ROOT / ".desk" / a.entry / "packets"
    out_dir.mkdir(parents=True, exist_ok=True)

    r2 = load_engine()
    AS_OF = json.loads((ROOT / "docs/api/round2.json").read_text())["as_of"]

    def collect(rnd):
        base = ROOT / "experiments" / f"round{rnd}"
        api = json.loads((ROOT / f"docs/api/round{rnd}.json").read_text())
        fills = [json.loads(l) for l in (base / "fills.jsonl").read_text().splitlines() if l.strip()]
        books = {}
        for f in sorted((base / "allocations").glob("*.json")):
            legs = legs_for(rnd, f.stem)
            live = [l for l in legs if l["entry"] <= AS_OF][-1]
            name = live["name"]
            books[name] = {
                "stem": f.stem, "round": rnd, "live": live, "n_legs": len(legs),
                "api": api["agents"].get(name),
                "fills": [x for x in fills if x["agent"] == name],
                "recent": [x for x in fills if x["ts"][:10] >= a.last_poll and x["agent"] == name],
            }
        return books, api

    r2books, r2api = collect(2)
    r3books, r3api = collect(3)

    syms = set()
    for bk in list(r2books.values()) + list(r3books.values()):
        for p in bk["live"]["positions"]:
            s = r2.normalize(p["symbol"])
            if p["kind"] in ("crypto", "perp") and not s.endswith("-USD"):
                s += "-USD"
            syms.add(s)
    px = {}
    for s in sorted(syms):
        ser = r2.fetch(s)
        if ser is not None and len(ser):
            px[s] = float(ser.iloc[-1])
    print(f"priced {len(px)}/{len(syms)} symbols", file=sys.stderr)

    def marked(bk):
        entry = bk["live"]["entry"]
        idx = {(f["symbol"], f.get("side", "long"), f.get("kind")): f
               for f in bk["fills"] if f["ts"][:10] == entry and f["action"] == "OPEN"}
        rows = []
        for p in bk["live"]["positions"]:
            s = r2.normalize(p["symbol"])
            key = s + ("-USD" if p["kind"] in ("crypto", "perp") and not s.endswith("-USD") else "")
            f = idx.get((p["symbol"], p.get("side", "long"), p.get("kind"))) or \
                idx.get((s, p.get("side", "long"), p.get("kind")))
            ep, cp = (f.get("fill_price") if f else None), px.get(key)
            ret = None
            if ep and cp:
                ret = (cp / ep - 1) * 100
                if p.get("side") == "short":
                    ret = -ret
                if p.get("leverage"):
                    ret *= float(p["leverage"])
            rows.append({**p, "entry_fill": ep, "mark": cp, "leg_return_pct": ret})
        return rows

    def render(name, entries):
        L = [f"# Account packet — {name}",
             f"as of the {AS_OF} close  |  next trading date: {a.entry}", ""]
        for bk in entries:
            rnd, api = bk["round"], bk["api"]
            L.append(f"## Round {rnd} book (`{bk['stem']}.json`)")
            if api:
                b = (r2api if rnd == 2 else r3api)["benchmarks"]
                L += [f"- NAV **${api['nav']:,.2f}** from $1,000 → **{api['growth_pct']:+.2f}%**"
                      f"  (SPY {b['SPY ($1000)']['nav']/10-100:+.2f}%, "
                      f"BTC {b['BTC ($1000)']['nav']/10-100:+.2f}%)",
                      f"- max drawdown {api['max_drawdown_pct']:+.2f}%  |  gross exposure "
                      f"{api['gross_exposure_pct']}%  |  cash {api['cash_pct']}%  |  "
                      f"{api['n_positions']} positions",
                      f"- strategy of record: {api['strategy']}"]
            L += [f"- current leg entered {bk['live']['entry']} "
                  f"(leg {bk['n_legs']} of this book's history)", "",
                  "| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for p in marked(bk):
                L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                    p["symbol"], p["kind"], p.get("side", "long"), p.get("leverage") or "",
                    p.get("weight_pct"),
                    f"{p['entry_fill']:.4f}" if p["entry_fill"] else "—",
                    f"{p['mark']:.4f}" if p["mark"] else "—",
                    f"{p['leg_return_pct']:+.2f}" if p["leg_return_pct"] is not None else "—",
                    f"-{p['stop_loss_pct']}%" if p.get("stop_loss_pct") else "—",
                    f"+{p['take_profit_pct']}%" if p.get("take_profit_pct") else "—"))
            L += ["", f"- cash: {bk['live'].get('cash_pct', 0)}%"]
            fired = [f for f in bk["recent"] if f["action"] != "OPEN"]
            if fired:
                L += ["", "**Standing orders that FIRED since the last poll:**"]
                for f in fired:
                    L.append(f"  - {f['ts'][:10]} {f['action']} {f['symbol']} "
                             f"({f.get('side','long')}) at {f.get('fill_price')}")
            hist = [f for f in bk["fills"]
                    if f["action"] in ("STOP_LOSS", "TAKE_PROFIT", "LIQUIDATION")]
            if hist:
                L += ["", f"- lifetime standing-order fills on this book: {len(hist)} "
                          f"({', '.join(sorted({f['symbol'] for f in hist}))})"]
            L.append("")
        return "\n".join(L)

    names = sorted(set(r2books) | set(r3books))
    manifest = []
    for name in names:
        entries = [b[name] for b in (r2books, r3books) if name in b]
        safe = name.replace("/", "-").replace(" ", "_")
        (out_dir / f"{safe}.md").write_text(render(name, entries))
        stems = {str(b["round"]): b["stem"] for b in entries}
        manifest.append({"name": name, "file": f"{safe}.md", "stems": stems,
                         "rounds": sorted(stems), "model": entries[0]["live"].get("model", "")})
    (out_dir / "_manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(names)} packets to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

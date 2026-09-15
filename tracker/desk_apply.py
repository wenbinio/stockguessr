#!/usr/bin/env python3
"""Validate a week's poll returns and write the accepted books.

Rejection is never silent and never partial: a book that breaks a hard rule is
refused whole and the manager's previous book stands, which is what the desk
protocol means by "a rejected book means the prior book stands".

    python3 tracker/desk_apply.py --entry 2026-09-16 [--decisions DIR] [--apply]

Without --apply it reports what it would do and writes nothing.
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


def live_book(r2, rnd, stem, before):
    base = ROOT / "experiments" / f"round{rnd}"
    legs = [json.loads((base / "allocations" / f"{stem}.json").read_text())]
    for wk in sorted((base / "weeks").glob("*/")):
        f = wk / f"{stem}.json"
        if f.exists() and wk.name < before:
            legs.append(json.loads(f.read_text()))
    return legs[-1]


def sanitize(d):
    notes = []
    for p in d.get("positions", []):
        for k in ("stop_loss_pct", "take_profit_pct"):
            if k in p and (p[k] is None or float(p[k]) <= 0):
                notes.append(f"dropped {k}={p[k]} on {p['symbol']}")
                p.pop(k)
            elif k in p:
                p[k] = abs(float(p[k]))
        if p.get("kind") != "perp" and p.get("leverage") is not None:
            notes.append(f"stripped leverage off non-perp {p['symbol']}")
            p.pop("leverage")
    return notes


def overlap_pct(r2, r3book, r2book):
    """Same-direction gross-weight overlap of an R3 book against the R2 book."""
    def gw(d):
        out = {}
        for p in d.get("positions", []):
            key = (r2.normalize(p["symbol"]), p.get("side", "long"))
            out[key] = out.get(key, 0.0) + abs(float(p.get("weight_pct", 0))) * \
                       float(p.get("leverage") or 1)
        return out
    a, b = gw(r3book), gw(r2book)
    if not a:
        return 0.0
    return sum(min(a[k], b.get(k, 0.0)) for k in a) / sum(a.values()) * 100


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True)
    ap.add_argument("--decisions", default=None)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    base = ROOT / ".desk" / a.entry
    dec_dir = Path(a.decisions) if a.decisions else base / "decisions"
    man = {m["name"]: m for m in json.loads((base / "packets/_manifest.json").read_text())}
    stem2name = {(r, s): m["name"] for m in man.values() for r, s in m["stems"].items()}

    r2 = load_engine()
    rows, accepted = [], {}
    for fp in sorted(dec_dir.glob("*.json")):
        stem, rnd = fp.stem.rsplit("_r", 1)
        name = stem2name.get((rnd, stem))
        try:
            d = json.loads(fp.read_text())
        except Exception as e:  # noqa: BLE001
            rows.append((name or stem, rnd, "REJECT", f"unparseable JSON: {e}")); continue
        if name is None:
            rows.append((stem, rnd, "REJECT", "no such book in the register")); continue
        if str(d.get("decision", "")).upper() == "HOLD":
            why = (d.get("reason") or "").strip()
            rows.append((name, rnd, "HOLD" if len(why) >= 25 else "HOLD*", why[:90]))
            accepted[(rnd, stem)] = None
            continue

        d["entry"] = d.get("entry") or a.entry
        d["name"], d["capital_usd"] = name, 1000
        # Tier and cohort are the experiment's independent variables: they come
        # from the register, never from the manager's return. In week 8, 22 of
        # 55 books came back with a free-text model field ("Sonnet", "opus-5",
        # "Fable 5.1"), which would have split single cohorts in any by-model
        # grouping.
        reg = json.loads((ROOT / "experiments" / f"round{rnd}" /
                          "allocations" / f"{stem}.json").read_text())
        d["model"], d["group"] = reg["model"], reg.get("group")

        notes = sanitize(d)
        if not r2.validate(d, f"{stem}_r{rnd}"):
            rows.append((name, rnd, "REJECT", "failed hard rules — prior book stands")); continue
        if rnd == "3" and "2" in man[name]["stems"]:
            ov = overlap_pct(r2, d, live_book(r2, "2", man[name]["stems"]["2"], a.entry))
            if ov >= 50:
                rows.append((name, rnd, "REJECT", f"novelty: {ov:.0f}% overlap with own R2 book"))
                continue
            notes.append(f"R3/R2 overlap {ov:.0f}%")
        thin = [p["symbol"] for p in d["positions"] if len((p.get("thesis") or "").strip()) < 25]
        if thin or len((d.get("reassessment_note") or "").strip()) < 25:
            rows.append((name, rnd, "REJECT",
                         f"reasoning missing on {thin or 'the book itself'}")); continue
        accepted[(rnd, stem)] = d
        rows.append((name, rnd, "TRADE", f"{len(d['positions'])} legs, cash {d.get('cash_pct',0)}%"
                     + (f" [{'; '.join(notes)}]" if notes else "")))

    if a.apply:
        n = 0
        for (rnd, stem), d in accepted.items():
            if d is None:
                continue
            out = ROOT / "experiments" / f"round{rnd}" / "weeks" / d["entry"]
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{stem}.json").write_text(json.dumps(d, indent=1) + "\n")
            n += 1
        print(f"WROTE {n} books\n")

    for name, rnd, verdict, why in sorted(rows, key=lambda r: (r[2], r[0])):
        print(f"{verdict:7s} R{rnd}  {name[:46]:46s} {why}")
    print(f"\n{len(rows)} returns: " + ", ".join(
        f"{v}={sum(1 for r in rows if r[2] == v)}" for v in sorted({r[2] for r in rows})))
    missing = [(m["name"], r) for m in man.values() for r in m["stems"]
               if (r, m["stems"][r]) not in accepted]
    print(f"still outstanding: {len(missing)}")
    for nm, r in sorted(missing):
        print(f"   R{r}  {nm}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

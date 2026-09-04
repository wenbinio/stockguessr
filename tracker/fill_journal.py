"""Append-only journal of executed fills, and a tripwire for rewritten history.

The engine recomputes every fill from live prices on each run, so `fills.jsonl`
is a *derived* artifact: if the data source restates a historical close, the
recomputation silently changes what "happened". On 2026-08-12 Yahoo revised
URNM's 2026-07-31 close from 48.57 to 49.45. That moved a short's mark from
-12.27% to -10.27% against a -12% stop, and a STOP_LOSS recorded as executed on
2026-08-07 — one the manager had already been shown, and had already reasoned
about at the 2026-08-08 desk — simply ceased to exist.

This module keeps `experiments/<round>/fills_journal.jsonl`, which is
APPEND-ONLY and never regenerated. Every run:

  * appends fills that are new,
  * reports fills that were previously journalled but have VANISHED from the
    recomputation, and records the vanishing as its own journal entry so the
    disappearance is itself part of the permanent record,
  * reports fills that had vanished and have since RETURNED. Not every
    disappearance is a restatement: on 2026-09-03 a rate-limited sweep failed
    to fetch CRWD and XOM, and 96 fills across three books "vanished" because
    of a network hiccup. Recording only the disappearance would leave the
    journal permanently accusing a restatement that never happened, so the
    resurrection is journalled too and the original entry is marked retracted.
  * reports fills whose price MOVED, which is the early warning that a
    restatement is in progress.

The journal does not "fix" the NAV — the engine still values books off current
data, which is the right behaviour for a live experiment. What it fixes is that
the experiment can no longer quietly disagree with its own past.

    python3 tracker/fill_journal.py [--round 2|3]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ident(f: dict) -> str:
    """Stable identity for a fill.

    A perp leg gets its kind and leverage appended, because a book may hold the
    same asset spot and levered at once: Opus Value opened BTC-USD twice on
    2026-07-16, 13% spot and 4% at 2x, and on the bare five-field key those
    collapse into one entry. The journal was therefore watching one of them and
    silently ignoring the other - and the ignored one was the leveraged leg,
    the only kind of position here that can be liquidated outright. The suffix
    is confined to perps so that every id already written for a spot or equity
    fill keeps its meaning and nothing appears to vanish.
    """
    base = f"{f['ts'][:10]}|{f['agent']}|{f['symbol']}|{f['action']}|{f.get('side', '')}"
    if f.get("kind") == "perp":
        base += f"|perp{f.get('leverage')}"
    return base


# A restatement is worth a human's attention only if it is not the routine
# re-basing of adjusted closes. When a holding goes ex-dividend, Yahoo rescales
# that symbol's ENTIRE adjclose history by one factor, so every journalled fill
# in it moves by the same ratio - benign, and on a busy dividend week it is
# hundreds of lines that bury the one that matters. A genuine data revision, by
# contrast, moves a single session: URNM's 2026-07-31 close went 48.57 -> 49.45
# while the rest of its history sat still, and that is the event that silently
# deleted an executed stop. Same ratio across the symbol => ROUTINE; anything
# else => ANOMALOUS. Two refinements keep the test from crying wolf and from
# going deaf. A rebase touches EVERY journalled fill in the symbol, so if some
# of them moved and others did not, one session was revised no matter how
# uniform the movers look. And a symbol with a single journalled fill supports
# neither verdict, so it is reported as UNDETERMINED rather than being counted
# as evidence of a revision it may well not be.
UNIFORM_TOL = 1e-3  # 0.1% spread in the ratio still counts as one factor

# What counts as a restatement at all. The test used to be an absolute 1e-9 on
# the price, which on a $100 quote is the last digit Yahoo prints: on 2026-09-04
# it flagged SHV at 109.7229 -> 109.7230 and TLT at 83.8596 -> 83.8595 across
# nine books, all of them rounding dust. Worse, that dust was classified
# ANOMALOUS, because only the fills that happened to cross the absolute
# threshold moved and a partial move is the signature of a real revision. The
# threshold is relative, and sits two orders of magnitude below the smallest
# move with any meaning - a monthly distribution on even a cash-like ETF is
# some 4e-3, and the URNM revision that started all this was 1.8e-2.
RESTATEMENT_EPS = 1e-5


def classify(moves: list[tuple[str, float, float]],
             journal: dict[str, dict]) -> dict[str, str]:
    total = {}
    for k in journal:
        sym = k.split("|")[2]
        total[sym] = total.get(sym, 0) + 1

    by_symbol: dict[str, list[tuple[str, float]]] = {}
    for k, was, isnow in moves:
        by_symbol.setdefault(k.split("|")[2], []).append((k, isnow / was))

    out = {}
    for sym, items in by_symbol.items():
        ratios = [r for _, r in items]
        if total.get(sym, 0) <= 1:
            verdict = "UNDETERMINED_SINGLE_FILL"
        elif len(items) < total[sym]:
            verdict = "ANOMALOUS"       # a rebase would have moved all of them
        elif (max(ratios) - min(ratios)) / min(ratios) < UNIFORM_TOL:
            verdict = "ROUTINE_ADJCLOSE_REBASE"
        else:
            verdict = "ANOMALOUS"
        for k, _ in items:
            out[k] = verdict
    return out


def run(rnd: str) -> int:
    base = ROOT / "experiments" / f"round{rnd}"
    live_p, jrn_p = base / "fills.jsonl", base / "fills_journal.jsonl"
    if not live_p.exists():
        return 0
    live = {}
    for line in live_p.read_text().splitlines():
        if line.strip():
            f = json.loads(line)
            live[ident(f)] = f

    journal = {}
    vanished_before = set()
    if jrn_p.exists():
        for line in jrn_p.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            ev = e.get("_event")
            if ev == "VANISHED":
                vanished_before.add(e["id"])
            elif ev == "RETURNED":
                vanished_before.discard(e["id"])
            elif ev == "FILL":
                journal[e["id"]] = e
            elif ev == "PRICE_RESTATED" and e["id"] in journal:
                # Advance the baseline to what was last seen. Without this a
                # restated fill is compared against its original price forever
                # and re-reported on every single run; the earlier code instead
                # let the restatement entry shadow the fill entry, which had no
                # fill_price at all and so quietly retired that fill from
                # monitoring after its first move. Both are wrong: a fill should
                # be reported once per restatement and watched thereafter.
                journal[e["id"]] = {**journal[e["id"]], "fill_price": e["now"]}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    appended, vanished, returned = [], [], []
    raw_moves = []
    for k, f in live.items():
        if k not in journal:
            continue
        was, isnow = journal[k].get("fill_price"), f.get("fill_price")
        if (was is not None and isnow is not None and was
                and abs(isnow / was - 1) > RESTATEMENT_EPS):
            raw_moves.append((k, was, isnow))
    classes = classify(raw_moves, journal)
    moved = [(k, was, isnow, classes[k]) for k, was, isnow in raw_moves]

    with jrn_p.open("a") as out:
        for k, f in live.items():
            if k in vanished_before:
                out.write(json.dumps({"_event": "RETURNED", "_seen_utc": now, "id": k,
                                      "note": "previously journalled as VANISHED; the "
                                              "recomputation produces it again, so that "
                                              "vanishing was not a restatement"}) + "\n")
                returned.append(k)
            if k not in journal:
                out.write(json.dumps({"_event": "FILL", "_first_seen_utc": now,
                                      "id": k, **f}) + "\n")
                appended.append(k)
        for k, was, isnow in raw_moves:
            out.write(json.dumps({"_event": "PRICE_RESTATED", "_seen_utc": now,
                                  "id": k, "was": was, "now": isnow,
                                  "_class": classes[k]}) + "\n")
        for k, e in journal.items():
            if k not in live and k not in vanished_before:
                out.write(json.dumps({"_event": "VANISHED", "_seen_utc": now, "id": k,
                                      "original": {kk: vv for kk, vv in e.items()
                                                   if not kk.startswith("_")}}) + "\n")
                vanished.append(k)

    print(f"round{rnd} journal: {len(live)} live fills, +{len(appended)} appended")
    if returned:
        print(f"  {len(returned)} previously-VANISHED fill(s) have RETURNED - those "
              f"disappearances were not restatements:")
        for k in returned[:10]:
            print(f"    {k}")
        if len(returned) > 10:
            print(f"    ... and {len(returned) - 10} more")
    if moved:
        odd = [m for m in moved if m[3] == "ANOMALOUS"]
        unk = [m for m in moved if m[3] == "UNDETERMINED_SINGLE_FILL"]
        routine = len(moved) - len(odd) - len(unk)
        print(f"  PRICE RESTATED on {len(moved)} previously-journalled fill(s) "
              f"({routine} routine adjusted-close re-basing, {len(odd)} anomalous, "
              f"{len(unk)} undetermined - only one journalled fill in the symbol)")
        if odd:
            print(f"  *** {len(odd)} restatement(s) do NOT look like an ex-dividend "
                  f"re-basing - a single session was revised:")
            for k, a, b, _ in odd[:15]:
                print(f"    {k}  {a} -> {b}  ({(b / a - 1) * 100:+.3f}%)")
            if len(odd) > 15:
                print(f"    ... and {len(odd) - 15} more")
    if vanished:
        print(f"  *** {len(vanished)} JOURNALLED FILL(S) NO LONGER EXIST in the recomputation.")
        print(f"  *** History was rewritten by a data restatement, not by a decision.")
        for k in vanished:
            print(f"    {k}")
    return len(vanished)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=None)
    args = ap.parse_args()
    rounds = [args.round] if args.round else ["2", "3"]
    return 0 if sum(run(r) for r in rounds) == 0 else 0  # report, never block the refresh


if __name__ == "__main__":
    sys.exit(main())

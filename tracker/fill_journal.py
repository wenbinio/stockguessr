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
    return f"{f['ts'][:10]}|{f['agent']}|{f['symbol']}|{f['action']}|{f.get('side', '')}"


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
            if e.get("_event") == "VANISHED":
                vanished_before.add(e["id"])
            else:
                journal[e["id"]] = e

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    appended, moved, vanished = [], [], []
    with jrn_p.open("a") as out:
        for k, f in live.items():
            if k not in journal:
                out.write(json.dumps({"_event": "FILL", "_first_seen_utc": now,
                                      "id": k, **f}) + "\n")
                appended.append(k)
            else:
                was, isnow = journal[k].get("fill_price"), f.get("fill_price")
                if was is not None and isnow is not None and abs(was - isnow) > 1e-9:
                    out.write(json.dumps({"_event": "PRICE_RESTATED", "_seen_utc": now,
                                          "id": k, "was": was, "now": isnow}) + "\n")
                    moved.append((k, was, isnow))
        for k, e in journal.items():
            if k not in live and k not in vanished_before:
                out.write(json.dumps({"_event": "VANISHED", "_seen_utc": now, "id": k,
                                      "original": {kk: vv for kk, vv in e.items()
                                                   if not kk.startswith("_")}}) + "\n")
                vanished.append(k)

    print(f"round{rnd} journal: {len(live)} live fills, +{len(appended)} appended")
    if moved:
        print(f"  PRICE RESTATED on {len(moved)} previously-journalled fill(s):")
        for k, a, b in moved[:10]:
            print(f"    {k}  {a} -> {b}")
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

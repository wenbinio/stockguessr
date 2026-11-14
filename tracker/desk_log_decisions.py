#!/usr/bin/env python3
"""Build the `decisions` list of a weekly desk log from a desk's returned files.

Lives in the repo for the same reason desk_packets.py does: the scratchpad copy of
this helper was lost when the container was rebuilt between weeks 17 and 18.

Each prompt names its book files as `- Round N: <path>.json`; the dispatch order
gives each manager's name and tier. Output entries have the shape
    {name, model, decisions: [{round, action, reason, book?}]}
where a HOLD carries its own `reason` and a REBALANCE carries the book's
`reassessment_note` as its reason plus the full book.

    from desk_log_decisions import build; build("2026-11-16")
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(entry: str) -> list:
    desk = ROOT / ".desk" / entry
    order = json.loads((desk / "dispatch_order.json").read_text())
    out = []
    for x in order:
        prompt = (desk / "prompts" / f"{x['seq'] - 1:02d}.md").read_text()
        decs = []
        for rnd, path in re.findall(r"- Round (\d): (\S+\.json)", prompt):
            p = desk / "decisions" / Path(path).parent.name / Path(path).name
            if not p.exists():
                decs.append({"round": int(rnd), "action": "HOLD",
                             "reason": "No decision file returned; the prior book stands by desk default.",
                             "reason_unavailable": True, "reason_source": "desk"})
                continue
            d = json.loads(p.read_text())
            if str(d.get("decision", "")).upper() == "HOLD":
                decs.append({"round": int(rnd), "action": "HOLD", "reason": d.get("reason", "")})
            else:
                decs.append({"round": int(rnd), "action": "REBALANCE",
                             "reason": d.get("reassessment_note", ""), "book": d})
        out.append({"name": x["name"], "model": x["model"], "decisions": decs})
    return out


if __name__ == "__main__":
    print(json.dumps(build(sys.argv[1]), indent=1)[:2000])

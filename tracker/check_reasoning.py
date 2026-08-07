"""Enforce the recorded-reasoning invariant across the whole experiment.

Every decision an agent makes must carry written reasoning. This script is the
mechanical check, so the rule cannot quietly decay into "we asked nicely in the
prompt". It fails loudly (exit 1) when reasoning is missing.

What must be recorded:

  1. Every registered book (allocations/ and weeks/<date>/) must state why it
     exists — an opening book via `strategy` (plus `novelty` where the round
     requires it), a reassessment via `reassessment_note`.
  2. Every position in every book must carry its own `thesis`.
  3. Every decision in every desk log must carry a non-trivial `reason`,
     including HOLDs.
  4. Where no agent reasoning exists — the agent failed to respond, or the
     record predates this rule — the gap must be declared explicitly with
     `reason_unavailable` (and `reason_source` naming who is speaking), never
     left blank and never filled with an action string dressed up as a reason.

Run standalone, or as part of the refresh:
    python3 tracker/check_reasoning.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_CHARS = 25  # a reason shorter than this is a label, not reasoning


def _thin(s) -> bool:
    return not isinstance(s, str) or len(s.strip()) < MIN_CHARS


def check_books(problems: list) -> int:
    n = 0
    for rnd in ("round2", "round3"):
        base = ROOT / "experiments" / rnd
        for kind, paths in (("opening", sorted((base / "allocations").glob("*.json"))),
                            ("reassessment", sorted(base.glob("weeks/*/*.json")))):
            for f in paths:
                d = json.loads(f.read_text())
                rel = f.relative_to(ROOT)
                n += 1
                if kind == "opening":
                    if _thin(d.get("strategy")):
                        problems.append(f"{rel}: opening book has no strategy rationale")
                    if rnd == "round3" and d.get("group") != "factorial" \
                            and _thin(d.get("novelty")) and not d.get("reason_unavailable"):
                        problems.append(f"{rel}: Round-3 book has no novelty statement")
                else:
                    if _thin(d.get("reassessment_note")) and not d.get("reason_unavailable"):
                        problems.append(f"{rel}: reassessment has no recorded reason")
                for i, p in enumerate(d.get("positions", [])):
                    if _thin(p.get("thesis")):
                        problems.append(
                            f"{rel}: position {i + 1} ({p.get('symbol')}) has no thesis")
    return n


def check_desk(problems: list) -> int:
    n = 0
    for f in sorted((ROOT / "experiments" / "desk").glob("*.json")):
        log = json.loads(f.read_text())
        rel = f.relative_to(ROOT)
        for entry in log.get("decisions", []):
            who = entry.get("name", "?")
            for dec in entry.get("decisions", []):
                n += 1
                if _thin(dec.get("reason")) and not dec.get("reason_unavailable"):
                    problems.append(
                        f"{rel}: {who} R{dec.get('round')} {dec.get('action')} has no reason")
        # a non-responding manager still produces a decision (the default HOLD);
        # the desk must record its own reasoning for it and say it is the desk speaking
        for fd in log.get("failed_default_hold", []):
            n += 1
            if isinstance(fd, str):
                problems.append(f"{rel}: default HOLD for {fd!r} recorded as a bare name "
                                f"with no reasoning or attribution")
                continue
            if _thin(fd.get("reason")):
                problems.append(f"{rel}: default HOLD for {fd.get('name')} has no reasoning")
            elif not fd.get("reason_source"):
                problems.append(f"{rel}: default HOLD for {fd.get('name')} does not say "
                                f"who authored the reasoning (reason_source)")

        # the orchestrator is a participant and is held to the same standard
        orc = log.get("orchestrator")
        if isinstance(orc, dict):
            for k in ("round2", "round3"):
                if k not in orc:
                    continue
                n += 1
                # per-round reason required: a single blended reason covering two
                # separate round decisions was accepted twice before 2026-08-07
                r = orc.get(f"{k}_reason")
                if _thin(r) and not orc.get(f"{k}_reason_unavailable"):
                    problems.append(
                        f"{rel}: orchestrator {k} decision has no reason "
                        f"(action string is not a reason)")
    return n


def main() -> int:
    problems: list[str] = []
    nb = check_books(problems)
    nd = check_desk(problems)
    print(f"checked {nb} registered books and {nd} desk decisions")
    if problems:
        print(f"\nMISSING REASONING ({len(problems)}):")
        for p in problems:
            print(f"  {p}")
        print("\nEvery decision must carry written reasoning. Where none exists, "
              "declare it with reason_unavailable + reason_source rather than "
              "leaving it blank.")
        return 1
    print("all decisions carry recorded reasoning")
    return 0


if __name__ == "__main__":
    sys.exit(main())

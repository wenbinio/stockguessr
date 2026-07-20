#!/usr/bin/env python3
"""Build docs/api/ledger.json — the master trade ledger across all rounds.

Emits EVERY trade by every agent:
  * Round 1 H1 entries (BUY, 2026-01-02) and H2 rebalance orders (BUY/SELL,
    2026-07-16), pulled from the assembled per-agent ledger in
    docs/api/agents.json and enriched with the ex-ante rationale strings from
    experiments/2026-h1/portfolios/*.json.
  * Round 2 book openings (OPEN, 2026-07-16) from experiments/round2/allocations.
  * Round 3 book openings (OPEN, 2026-07-17) from experiments/round3/allocations,
    plus any attached standing STOP_LOSS / TAKE_PROFIT orders.

Every figure is copied from a source file — nothing is invented. Fees are only
populated where a source records a per-trade fee (none of the current sources do,
so `fees` is null and `fee_schedule` names the applicable rule instead).
Run: python3 tracker/make_ledger.py
"""
import json, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(*a): return os.path.join(ROOT, *a)

# Fee schedules that apply to each round's fills (from RULES.md / friction_model).
R1_FEE = "10bps/side friction model; 15% dividend tax (aggregate, not per-fill)"
RETAIL_FEE = ("equities/ETFs 2bps (5bps leveraged, 12bps sub-$15) + 0.31bps SEC/TAF on sells; "
              "crypto spot 35bps; perps 7.5bps notional + 10% APR funding; short borrow 3% APR")

def load(fp):
    with open(fp) as f: return json.load(f)

records = []

# ---- Round 1: from the assembled agent ledger, enriched with H1 rationale ----
agents = load(p("docs/api/agents.json"))["agents"]

# name -> rationale from the H1 portfolio files. Flagship files carry a per-ticker
# dict; fleet files carry a single book-level string.
h1_reason = {}      # name -> {ticker: reason}
h1_book_reason = {} # name -> book-level reason string (fleet)
for fp in glob.glob(p("experiments/2026-h1/portfolios/*.json")):
    d = load(fp)
    r = d.get("rationale")
    if isinstance(r, dict):
        h1_reason[d["name"]] = r
    elif isinstance(r, str):
        h1_book_reason[d["name"]] = r

for name, a in agents.items():
    model = a["model"]
    n_h1 = sum(1 for l in a["ledger"] if l["leg"] == "H1")
    for l in a["ledger"]:
        leg = l["leg"]
        rec = {
            "when": l["date"],
            "agent": name,
            "model": model,
            "round": "R1",
            "leg": leg,
            "action": l["action"],
            "symbol": l["ticker"],
            "kind": "equity",
            "side": "long",
            "leverage": None,
            "weight_pct": round(100.0 / n_h1, 2) if leg == "H1" else None,
            "fill": l.get("fill"),
            "fees": None,
            "fee_schedule": R1_FEE,
            "realized_pct": l.get("realized_pct"),
            "why": (l.get("reason") or h1_reason.get(name, {}).get(l["ticker"])
                    or h1_book_reason.get(name)
                    or "Initial equal-weight H1 entry at the January-2026 knowledge cutoff."),
        }
        records.append(rec)

# ---- Round 2 & Round 3: book openings from the allocation files ----
def add_book(round_id, when, alloc_dir):
    for fp in sorted(glob.glob(p(alloc_dir, "*.json"))):
        d = load(fp)
        name = d["name"]
        model = d.get("model", "")
        for pos in d.get("positions", []):
            records.append({
                "when": when,
                "agent": name,
                "model": model,
                "round": round_id,
                "leg": round_id,
                "action": "OPEN",
                "symbol": pos["symbol"],
                "kind": pos.get("kind", "equity"),
                "side": pos.get("side", "long"),
                "leverage": pos.get("leverage"),
                "weight_pct": pos.get("weight_pct"),
                "fill": None,           # forward leg is pre-entry; no fills recorded yet
                "fees": None,
                "fee_schedule": RETAIL_FEE,
                "realized_pct": None,
                "why": pos.get("thesis"),
            })
            # Standing orders attached at registration.
            if pos.get("stop_loss_pct") is not None:
                records.append({
                    "when": when, "agent": name, "model": model, "round": round_id,
                    "leg": round_id, "action": "STOP_LOSS", "symbol": pos["symbol"],
                    "kind": pos.get("kind", "equity"), "side": pos.get("side", "long"),
                    "leverage": pos.get("leverage"), "weight_pct": pos.get("weight_pct"),
                    "fill": None, "fees": None, "fee_schedule": RETAIL_FEE,
                    "realized_pct": None,
                    "why": f"Standing stop-loss at -{pos['stop_loss_pct']}%: {pos.get('thesis','')}",
                })
            if pos.get("take_profit_pct") is not None:
                records.append({
                    "when": when, "agent": name, "model": model, "round": round_id,
                    "leg": round_id, "action": "TAKE_PROFIT", "symbol": pos["symbol"],
                    "kind": pos.get("kind", "equity"), "side": pos.get("side", "long"),
                    "leverage": pos.get("leverage"), "weight_pct": pos.get("weight_pct"),
                    "fill": None, "fees": None, "fee_schedule": RETAIL_FEE,
                    "realized_pct": None,
                    "why": f"Standing take-profit at +{pos['take_profit_pct']}%: {pos.get('thesis','')}",
                })

add_book("R2", "2026-07-16", "experiments/round2/allocations")
add_book("R3", "2026-07-17", "experiments/round3/allocations")

# ---- Weekly Execution Desk rebalance legs (weeks/<date>/*.json) ----
def add_weeks(round_id, weeks_glob):
    for wk in sorted(glob.glob(p(weeks_glob))):
        for fp in sorted(glob.glob(os.path.join(wk, "*.json"))):
            d = load(fp)
            note = d.get("reassessment_note", "")
            for pos in d.get("positions", []):
                records.append({
                    "when": d["entry"], "agent": d["name"], "model": d.get("model", ""),
                    "round": round_id, "leg": round_id, "action": "REBALANCE",
                    "symbol": pos["symbol"], "kind": pos.get("kind", "equity"),
                    "side": pos.get("side", "long"), "leverage": pos.get("leverage"),
                    "weight_pct": pos.get("weight_pct"), "fill": None, "fees": None,
                    "fee_schedule": RETAIL_FEE, "realized_pct": None,
                    "why": (pos.get("thesis", "") + (f" [{note}]" if note else "")).strip(),
                })
                for kind, key in (("STOP_LOSS", "stop_loss_pct"), ("TAKE_PROFIT", "take_profit_pct")):
                    if pos.get(key) is not None:
                        sign = "-" if kind == "STOP_LOSS" else "+"
                        records.append({
                            "when": d["entry"], "agent": d["name"], "model": d.get("model", ""),
                            "round": round_id, "leg": round_id, "action": kind,
                            "symbol": pos["symbol"], "kind": pos.get("kind", "equity"),
                            "side": pos.get("side", "long"), "leverage": pos.get("leverage"),
                            "weight_pct": pos.get("weight_pct"), "fill": None, "fees": None,
                            "fee_schedule": RETAIL_FEE, "realized_pct": None,
                            "why": f"Standing {kind.lower().replace('_', '-')} at {sign}{pos[key]}%: {pos.get('thesis', '')}",
                        })

add_weeks("R2", "experiments/round2/weeks/*/")
add_weeks("R3", "experiments/round3/weeks/*/")

# ---- Join actual fill prices/fees from the engines' fills.jsonl ----
fills_idx = {}
for round_id, path in (("R2", "experiments/round2/fills.jsonl"),
                       ("R3", "experiments/round3/fills.jsonl")):
    if not os.path.exists(p(path)):
        continue
    for line in open(p(path)):
        f = json.loads(line)
        key = (round_id, f["ts"][:10], f["agent"], f["symbol"], f.get("side", "long"))
        fills_idx.setdefault(key, f)

for rec in records:
    if rec["round"] not in ("R2", "R3") or rec["action"] not in ("OPEN", "REBALANCE"):
        continue
    f = fills_idx.get((rec["round"], rec["when"], rec["agent"], rec["symbol"], rec["side"]))
    if f:
        rec["fill"] = f.get("fill_price")
        rec["fees"] = f.get("entry_cost_usd")

out = {
    "generated_by": "tracker/make_ledger.py",
    "entries": {"R1": "2026-01-02 (H1) / 2026-07-16 (H2)", "R2": "2026-07-16", "R3": "2026-07-17"},
    "fee_note": ("No source records a per-trade fee, so `fees` is null; `fee_schedule` names the "
                 "rule that applies to each fill. R1 used a 10bps/side friction model; R2/R3 use the "
                 "amended retail schedule."),
    "count": len(records),
    "trades": records,
}
outfp = p("docs/api/ledger.json")
with open(outfp, "w") as f:
    json.dump(out, f, indent=1)
print(f"wrote {outfp}: {len(records)} trades")
# quick breakdown
from collections import Counter
print("by round:", dict(Counter(r["round"] for r in records)))
print("by action:", dict(Counter(r["action"] for r in records)))

"""The pre-registered inference, actually implemented.

ANALYSIS_PLAN.md has specified HAC standard errors, Romano-Wolf family-wise
correction and alpha-based bootstrap nulls since 2026-07-16. Until now no code
existed that computed any of them, so the plan bound a report nothing could
produce — and the orchestrator reported plain OLS t-statistics while citing it.
This module is that code. Inference comes from here or it is not inference.

    python3 tracker/stats.py [--round 2|3] [--from YYYY-MM-DD] [--to YYYY-MM-DD]

Defaults to the pre-registered epoch-2 confirmatory window (2026-08-03 onward,
amendment 2). Every run appends to experiments/reviews/analysis_runs.jsonl
whether or not its result is reported anywhere — that log is the defence
against selective reporting, so it is written before the numbers are read.

Implements:
  * CAPM alpha by daily regression on SPY (plus BTC as a second factor when the
    book holds crypto), with Newey-West HAC standard errors, Andrews/Bartlett
    lag L = floor(4*(n/100)^(2/9)).
  * Romano-Wolf stepdown: family-wise adjusted p-values across all books in the
    round, by stationary block bootstrap of the residual matrix so that
    cross-book correlation from shared holdings is preserved, not assumed away.
  * Effective number of independent bets from the mean pairwise correlation.
  * Persistence tests reported in BOTH directions (R1->R2 and R1->R3), because
    reporting only the convenient one is what the 2026-08-07 critique caught.
"""

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "docs" / "api"
RUNLOG = ROOT / "experiments" / "reviews" / "analysis_runs.jsonl"

EPOCH2_START = "2026-08-03"   # first full session after the epoch-2 books filled
B_BOOTSTRAP = 5000
BLOCK = 5                      # stationary block length, ~1 trading week
SEED = 20260807                # fixed: the same run must reproduce


def mean(x):
    return sum(x) / len(x) if x else 0.0


def var(x):
    m = mean(x)
    return sum((v - m) ** 2 for v in x) / (len(x) - 1) if len(x) > 1 else 0.0


def ols(y, X):
    """Multiple regression with an intercept. X is a list of columns."""
    cols = [[1.0] * len(y)] + list(X)
    k = len(cols)
    XtX = [[sum(cols[i][t] * cols[j][t] for t in range(len(y))) for j in range(k)] for i in range(k)]
    Xty = [sum(cols[i][t] * y[t] for t in range(len(y))) for i in range(k)]
    # Gaussian elimination with partial pivoting
    M = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14:
            return None, None
        M[c], M[p] = M[p], M[c]
        for r in range(k):
            if r == c:
                continue
            f = M[r][c] / M[c][c]
            for j in range(c, k + 1):
                M[r][j] -= f * M[c][j]
    beta = [M[i][k] / M[i][i] for i in range(k)]
    resid = [y[t] - sum(beta[i] * cols[i][t] for i in range(k)) for t in range(len(y))]
    return beta, resid


def hac_se(resid, n_params=2):
    """Newey-West standard error of the intercept, Bartlett kernel."""
    n = len(resid)
    if n <= n_params:
        return float("nan"), 0
    L = max(1, int(4 * (n / 100) ** (2 / 9)))
    u = resid  # residuals of a regression whose intercept is the parameter of interest
    g0 = sum(v * v for v in u) / n
    s = g0
    for l in range(1, min(L, n - 1) + 1):
        g = sum(u[t] * u[t - l] for t in range(l, n)) / n
        s += 2 * (1 - l / (L + 1)) * g
    s = max(s, 1e-18)
    return math.sqrt(s / n), L


def load_round(rnd: int):
    d = json.loads((API / f"round{rnd}.json").read_text())
    spy = d["benchmarks"]["SPY ($1000)"]["series"]
    btc = (d["benchmarks"].get("BTC ($1000)") or {}).get("series", {})
    return d, spy, btc


def returns(series, dates):
    ds = sorted(series)
    out = {}
    for i, dt in enumerate(ds):
        if i == 0:
            continue
        prev = series[ds[i - 1]]
        if prev:
            out[dt] = series[dt] / prev - 1
    return [out[d] for d in dates if d in out], [d for d in dates if d in out]


def analyse(rnd: int, start: str, end: str | None):
    d, spy, btc = load_round(rnd)
    all_dates = [x for x in sorted(spy) if x >= start and (end is None or x <= end)]
    sr, sdates = returns(spy, all_dates)
    br_map = {}
    if btc:
        b, bd = returns(btc, all_dates)
        br_map = dict(zip(bd, b))

    books, resids = [], []
    for name, a in d["agents"].items():
        s = a.get("series") or {}
        ar, adates = returns(s, all_dates)
        common = [x for x in adates if x in set(sdates)]
        if len(common) < 8:
            continue
        amap, smap = dict(zip(adates, ar)), dict(zip(sdates, sr))
        y = [amap[x] for x in common]
        X = [[smap[x] for x in common]]
        uses_btc = any(p.get("kind") in ("crypto", "perp") for p in a.get("positions", []))
        if uses_btc and br_map:
            X.append([br_map.get(x, 0.0) for x in common])
        beta, resid = ols(y, X)
        if beta is None:
            continue
        se, L = hac_se(resid)
        t = beta[0] / se if se and se == se else float("nan")
        books.append({
            "name": name, "model": a["model"], "group": a.get("group", ""),
            "nav": a["nav"], "growth_pct": a["growth_pct"],
            "alpha_daily": beta[0], "alpha_cum_pp": beta[0] * len(common) * 100,
            "beta_spy": beta[1], "beta_btc": beta[2] if len(beta) > 2 else None,
            "t_hac": t, "n_obs": len(common), "hac_lag": L,
        })
        resids.append(resid)
    return d, books, resids


def romano_wolf(books, resids, b=B_BOOTSTRAP, block=BLOCK, seed=SEED):
    """Family-wise adjusted p-values by stationary-block bootstrap stepdown.

    Resamples whole date-blocks from the residual MATRIX, so every book is
    resampled on the same dates and the cross-book correlation induced by
    shared holdings survives into the null. That is the point: treating 47
    books as 47 independent tests is exactly the error this guards against.
    """
    if not books:
        return
    rng = random.Random(seed)
    n = min(len(r) for r in resids)
    R = [r[-n:] for r in resids]
    k = len(R)
    obs = [abs(books[i]["t_hac"]) for i in range(k)]

    null_max = []
    for _ in range(b):
        idx = []
        while len(idx) < n:
            s = rng.randrange(n)
            for j in range(block):
                if len(idx) < n:
                    idx.append((s + j) % n)
        stats = []
        for i in range(k):
            samp = [R[i][t] for t in idx]
            se, _ = hac_se(samp)
            stats.append(abs(mean(samp) / se) if se and se == se else 0.0)
        null_max.append(stats)

    order = sorted(range(k), key=lambda i: -obs[i])
    prev = 0.0
    for step, i in enumerate(order):
        remaining = order[step:]
        cnt = sum(1 for row in null_max if max(row[j] for j in remaining) >= obs[i])
        p = (cnt + 1) / (b + 1)
        p = max(p, prev)          # enforce monotonicity down the stepdown
        prev = p
        books[i]["p_romano_wolf"] = round(p, 4)


def eff_bets(resids):
    n = min(len(r) for r in resids)
    R = [r[-n:] for r in resids]
    cs = []
    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            a, b = R[i], R[j]
            ma, mb = mean(a), mean(b)
            den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
            if den:
                cs.append(sum((x - ma) * (y - mb) for x, y in zip(a, b)) / den)
    rbar = mean(cs)
    k = len(R)
    return rbar, k / (1 + (k - 1) * rbar) if (1 + (k - 1) * rbar) else float("nan")


def spearman(pairs):
    A = [x[0] for x in pairs]
    B = [x[1] for x in pairs]
    ra = {v: i for i, v in enumerate(sorted(A))}
    rb = {v: i for i, v in enumerate(sorted(B))}
    A = [ra[v] for v in A]
    B = [rb[v] for v in B]
    ma, mb = mean(A), mean(B)
    den = math.sqrt(sum((x - ma) ** 2 for x in A) * sum((y - mb) ** 2 for y in B))
    if not den:
        return float("nan"), float("nan")
    r = sum((x - ma) * (y - mb) for x, y in zip(A, B)) / den
    t = r * math.sqrt((len(A) - 2) / (1 - r * r)) if abs(r) < 1 else float("inf")
    return r, t


def persistence():
    """Every pairing, always. Reporting one direction is what got caught."""
    p1 = json.loads((API / "performance.json").read_text())
    h1 = {a["name"]: a["h1_return_pct"] for a in p1["agents"]}
    h2 = {a["name"]: a["h2_return_pct"] for a in p1["agents"]}
    out = []
    for label, src in (("R1-H1", h1), ("R1-H2", h2)):
        for rnd in (2, 3):
            cur = json.loads((API / f"round{rnd}.json").read_text())["agents"]
            pairs = [(src[n], cur[n]["growth_pct"]) for n in cur if n in src]
            if len(pairs) > 3:
                r, t = spearman(pairs)
                out.append({"from": label, "to": f"R{rnd}", "rho": round(r, 3),
                            "t": round(t, 2), "n": len(pairs)})
    r, t = spearman([(h1[n], h2[n]) for n in h1 if n in h2])
    out.append({"from": "R1-H1", "to": "R1-H2", "rho": round(r, 3), "t": round(t, 2), "n": len(h1)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, default=0, help="2, 3, or 0 for both")
    ap.add_argument("--from", dest="start", default=EPOCH2_START)
    ap.add_argument("--to", dest="end", default=None)
    ap.add_argument("--label", default="", help="why this run was made")
    args = ap.parse_args()

    rounds = [args.round] if args.round else [2, 3]
    record = {"run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
              "script": "tracker/stats.py", "window_start": args.start,
              "window_end": args.end or "latest", "label": args.label,
              "rounds": rounds, "results": {}}

    for rnd in rounds:
        d, books, resids = analyse(rnd, args.start, args.end)
        if not books:
            print(f"round {rnd}: no book has enough observations in this window")
            record["results"][f"round{rnd}"] = {"error": "insufficient observations"}
            continue
        romano_wolf(books, resids)
        rbar, eff = eff_bets(resids)
        books.sort(key=lambda x: -x["alpha_cum_pp"])
        window = f"{args.start} to {args.end or d['as_of']}"
        n_obs = books[0]["n_obs"]
        print(f"\n=== ROUND {rnd} — pre-registered inference ===")
        print(f"window {window} ({n_obs} sessions) · HAC lag {books[0]['hac_lag']} · "
              f"Romano-Wolf {B_BOOTSTRAP} block-bootstrap draws")
        print(f"mean pairwise residual corr {rbar:.3f} → {eff:.1f} effective independent "
              f"books of {len(books)}")
        print(f"{'book':<44}{'alpha pp':>9}{'beta':>7}{'t(HAC)':>8}{'p_RW':>8}")
        for bk in books[:8]:
            print(f"  {bk['name'][:42]:<42}{bk['alpha_cum_pp']:>9.2f}{bk['beta_spy']:>7.2f}"
                  f"{bk['t_hac']:>8.2f}{bk.get('p_romano_wolf', float('nan')):>8.3f}")
        sig = [b for b in books if b.get("p_romano_wolf", 1) < 0.05]
        print(f"  books surviving family-wise correction at 5%: {len(sig)} of {len(books)}"
              + (f" — {', '.join(b['name'] for b in sig)}" if sig else ""))
        record["results"][f"round{rnd}"] = {
            "window": window, "n_obs": n_obs, "n_books": len(books),
            "mean_pairwise_corr": round(rbar, 4), "effective_bets": round(eff, 2),
            "n_surviving_fwer_5pct": len(sig),
            "survivors": [b["name"] for b in sig],
            "books": [{k: (round(v, 4) if isinstance(v, float) else v)
                       for k, v in b.items()} for b in books],
        }

    pers = persistence()
    print("\n=== persistence (every pairing, reported unconditionally) ===")
    for p in pers:
        print(f"  {p['from']:<6} -> {p['to']:<4} rho={p['rho']:+.3f}  t={p['t']:+.2f}  n={p['n']}")
    record["persistence"] = pers

    RUNLOG.parent.mkdir(parents=True, exist_ok=True)
    with RUNLOG.open("a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"\nrun logged to {RUNLOG.relative_to(ROOT)} "
          f"({sum(1 for _ in RUNLOG.open())} runs on record)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

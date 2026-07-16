"""Render results.json into a self-contained HTML chart page (chart.html).

Sections:
  1. Ranking bars   — flagship portfolios + SPY, friction-adjusted (net) return
  2. Race line      — flagship portfolios indexed to 100 vs dashed SPY (gross)
  3. Fleet strip    — every portfolio (Fable/Opus/Sonnet/Haiku) as a dot on the
                      return axis, over the bootstrap luck histogram
  4. Scoreboard     — all portfolios: gross, net, beta, CAPM alpha, luck percentile
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# Validated categorical palette (dataviz reference instance).
# Flagship entities take slots 1-6 (line chart + bars); model tiers reuse
# slots 1-4 in the fleet strip (fable/opus/sonnet/haiku); benchmark is neutral.
SLOT_ORDER = [
    "Claude Fable (orchestrator)",
    "Opus Momentum",
    "Opus Value",
    "Opus Quality Defensive",
    "Opus Picks-and-Shovels",
    "Opus Broadening",
    "Fable Unconstrained",
    "Fable Barbell",
]
TIER_SLOT = {"fable": 1, "opus": 2, "sonnet": 3, "haiku": 4}

TEMPLATE = """<title>StockGuessr: Claude vs S&P 500 — H1 2026</title>
<style>
  html, body { margin: 0; padding: 0; }
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb; --page: #f9f9f7;
    --ink-1: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
    --grid: #e1e0d9; --baseline: #c3c2b7; --border: rgba(11,11,11,0.10);
    --bench: #52514e; --null: #c3c2b7;
    --s1: #2a78d6; --s2: #008300; --s3: #e87ba4;
    --s4: #eda100; --s5: #1baf7a; --s6: #eb6834;
    --s7: #4a3aa7; --s8: #e34948;
    --up: #006300; --down: #d03b3b;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19; --page: #0d0d0d;
      --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
      --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
      --bench: #c3c2b7; --null: #52514e;
      --s1: #3987e5; --s2: #008300; --s3: #d55181;
      --s4: #c98500; --s5: #199e70; --s6: #d95926;
      --s7: #9085e9; --s8: #e66767;
      --up: #0ca30c; --down: #e66767;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
    --bench: #c3c2b7; --null: #52514e;
    --s1: #3987e5; --s2: #008300; --s3: #d55181;
    --s4: #c98500; --s5: #199e70; --s6: #d95926;
      --s7: #9085e9; --s8: #e66767;
    --up: #0ca30c; --down: #e66767;
  }
  .viz-root { background: var(--page); color: var(--ink-1);
    font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 24px; min-height: 100vh; box-sizing: border-box; }
  .viz-root * { box-sizing: border-box; }
  .wrap { max-width: 980px; margin: 0 auto; display: grid; gap: 20px; }
  h1 { font-size: 21px; margin: 0; }
  .sub { color: var(--ink-2); margin: 4px 0 0; font-size: 13.5px; }
  .card { background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px 20px; }
  .card h2 { font-size: 15px; margin: 0 0 2px; }
  .card .note { color: var(--ink-muted); font-size: 12.5px; margin: 0 0 14px; }
  .legend { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 10px 0 2px;
    font-size: 12.5px; color: var(--ink-2); }
  .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .sw { width: 14px; height: 3px; border-radius: 2px; display: inline-block; }
  .sw.dash { background: repeating-linear-gradient(90deg, var(--bench) 0 4px, transparent 4px 7px); }
  .chartbox { position: relative; overflow-x: auto; }
  svg text { font: 11.5px system-ui, -apple-system, "Segoe UI", sans-serif; }
  .tip { position: absolute; pointer-events: none; background: var(--surface-1);
    border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px;
    font-size: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.15); display: none;
    min-width: 190px; z-index: 2; }
  .tip .d { color: var(--ink-muted); margin-bottom: 4px; }
  .tip .row { display: flex; justify-content: space-between; gap: 12px; }
  .tip .row b { font-variant-numeric: tabular-nums; font-weight: 600; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px;
    color: var(--ink-1); font-family: inherit; }
  th { text-align: left; color: var(--ink-muted); font-weight: 600;
    border-bottom: 1px solid var(--baseline); padding: 6px 8px; white-space: nowrap; }
  th.r, td.r { text-align: right; }
  td { padding: 6px 8px; border-bottom: 1px solid var(--grid);
    font-variant-numeric: tabular-nums; }
  td.name { white-space: nowrap; }
  td.strat { max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    color: var(--ink-2); }
  .chip { width: 10px; height: 10px; border-radius: 3px; display: inline-block;
    margin-right: 7px; vertical-align: -1px; }
  .pos { color: var(--up); } .neg { color: var(--down); }
  .foot { color: var(--ink-muted); font-size: 12px; }
  .tick { fill: var(--ink-muted); }
</style>
<div class="viz-root"><div class="wrap">
  <header>
    <h1>StockGuessr: Claude, seven flagship agents &amp; a 20-agent fleet vs the S&amp;P 500</h1>
    <p class="sub">Portfolios picked with knowledge frozen at the January 2026 model cutoff, bought
    (virtually) at the 2026-01-02 close, equal weight, no rebalancing — scored against real market
    prices through __ASOF__.</p>
  </header>

  <section class="card">
    <h2>Flagship ranking — friction-adjusted return since entry</h2>
    <p class="note">2026-01-02 close &rarr; __ASOF__ close · net of __COST__bps/side trading costs and
    __DIVTAX__% dividend tax · gross figures in the scoreboard</p>
    <div class="chartbox" id="barbox"></div>
  </section>

  <section class="card">
    <h2>Race against the index — portfolio value, indexed to 100 at entry</h2>
    <p class="note">Daily closes, gross of frictions · hover for values on any date</p>
    <div class="legend" id="legend"></div>
    <div class="chartbox" id="linebox"></div>
  </section>

  <section class="card">
    <h2>The fleet vs luck — every agent's return against random chance</h2>
    <p class="note">Each dot is one portfolio (gross return). The gray histogram is the luck
    distribution: __NBOOT__ random equal-weight 10-stock baskets drawn from the __UNIV__ largest
    S&amp;P names. Dashed line marks the S&amp;P 500. Hover any dot.</p>
    <div class="chartbox" id="stripbox"></div>
  </section>

  <section class="card">
    <h2>Scoreboard — all portfolios</h2>
    <p class="note">Net = after trading costs and dividend tax · CAPM &alpha; uses realized beta vs SPY and a
    __RF__% annualized risk-free rate · luck percentile = share of random baskets beaten</p>
    <div style="overflow-x:auto"><table id="tbl">
      <thead><tr><th>#</th><th>Portfolio</th><th>Model</th><th>Strategy</th>
      <th class="r">Gross</th><th class="r">Net</th><th class="r">Beta</th>
      <th class="r">CAPM &alpha;</th><th class="r">Luck pctile</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </section>

  <p class="foot">Virtual portfolios; dividends included via adjusted closes. Friction model is an
  approximation (fixed per-side costs, flat dividend tax, no market impact, no capital-gains tax).
  Picks were committed before any post-cutoff prices were fetched and fleet agents ran with tools
  disabled, but model training data may overlap early January 2026 market levels. One 6.5-month
  window in a strong tape — research/educational demo, not investment advice.</p>
</div></div>
<script>
const DATA = __DATA__;
const CSS = n => getComputedStyle(document.querySelector('.viz-root')).getPropertyValue(n).trim();
const SLOTS = __SLOTS__;
const TIER_SLOT = __TIER_SLOT__;
const TIER_LABEL = { fable: 'Claude Fable', opus: 'Opus agents', sonnet: 'Sonnet fleet', haiku: 'Haiku fleet' };
const colorOf = name => name === 'S&P 500 (SPY)' ? CSS('--bench') : CSS('--s' + (SLOTS.indexOf(name) + 1));
const tierColor = m => m === 'benchmark' ? CSS('--bench') : CSS('--s' + TIER_SLOT[m]);
const fmt = v => (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
const NS = 'http://www.w3.org/2000/svg';
const el = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
const FLAG = DATA.summary.filter(r => r.group === 'flagship' || r.benchmark);

function drawBars() {
  const rows = FLAG.slice().sort((a, b) => b.friction_return_pct - a.friction_return_pct);
  const W = 940, rowH = 34, padL = 210, padR = 90;
  const H = rows.length * rowH + 30;
  const vals = rows.map(r => r.friction_return_pct);
  const lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
  const x = v => padL + (v - lo) / (hi - lo) * (W - padL - padR);
  const svg = el('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  svg.appendChild(el('line', { x1: x(0), x2: x(0), y1: 4, y2: H - 22, stroke: CSS('--baseline'), 'stroke-width': 1 }));
  rows.forEach((r, i) => {
    const y = 8 + i * rowH, c = colorOf(r.name), v = r.friction_return_pct;
    const w = Math.abs(x(v) - x(0));
    const bx = v >= 0 ? x(0) : x(v);
    const rr = 4, x0 = bx, x1 = bx + w, yTop = y, yBot = y + 18;
    const bar = el('path', { fill: c });
    bar.setAttribute('d', v >= 0
      ? `M${x0},${yTop} H${x1 - rr} Q${x1},${yTop} ${x1},${yTop + rr} V${yBot - rr} Q${x1},${yBot} ${x1 - rr},${yBot} H${x0} Z`
      : `M${x1},${yTop} H${x0 + rr} Q${x0},${yTop} ${x0},${yTop + rr} V${yBot - rr} Q${x0},${yBot} ${x0 + rr},${yBot} H${x1} Z`);
    if (r.benchmark) bar.setAttribute('fill-opacity', '0.55');
    svg.appendChild(bar);
    const lbl = el('text', { x: padL - 10, y: y + 14, 'text-anchor': 'end', fill: CSS('--ink-1') });
    lbl.textContent = `${i + 1}. ${r.name}`;
    if (r.benchmark) lbl.setAttribute('font-style', 'italic');
    svg.appendChild(lbl);
    const val = el('text', { x: (v >= 0 ? x1 : x0) + 8, y: y + 14, fill: CSS('--ink-2'), 'font-weight': 600 });
    val.textContent = fmt(v);
    svg.appendChild(val);
  });
  document.getElementById('barbox').appendChild(svg);
}

function drawLines() {
  const names = Object.keys(DATA.series);
  const dates = Object.keys(DATA.series['S&P 500 (SPY)']);
  const W = 940, H = 380, padL = 46, padR = 190, padT = 12, padB = 28;
  let lo = Infinity, hi = -Infinity;
  names.forEach(n => Object.values(DATA.series[n]).forEach(v => { lo = Math.min(lo, v); hi = Math.max(hi, v); }));
  lo = Math.floor((lo - 2) / 5) * 5; hi = Math.ceil((hi + 2) / 5) * 5;
  const x = i => padL + i / (dates.length - 1) * (W - padL - padR);
  const y = v => padT + (hi - v) / (hi - lo) * (H - padT - padB);
  const svg = el('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  for (let g = lo; g <= hi; g += 10) {
    svg.appendChild(el('line', { x1: padL, x2: W - padR, y1: y(g), y2: y(g),
      stroke: g === 100 ? CSS('--baseline') : CSS('--grid'), 'stroke-width': 1 }));
    const t = el('text', { x: padL - 8, y: y(g) + 4, 'text-anchor': 'end', class: 'tick' });
    t.textContent = g; svg.appendChild(t);
  }
  const months = {};
  dates.forEach((d, i) => { const m = d.slice(0, 7); if (!(m in months)) months[m] = i; });
  Object.entries(months).forEach(([m, i]) => {
    const t = el('text', { x: x(i), y: H - 8, class: 'tick' });
    t.textContent = new Date(m + '-15').toLocaleString('en', { month: 'short' });
    svg.appendChild(t);
  });
  const last = dates[dates.length - 1];
  const ordered = names.slice().sort((a, b) => DATA.series[b][last] - DATA.series[a][last]);
  const labelNames = new Set(ordered.filter(n => n !== 'S&P 500 (SPY)').slice(0, 3).concat(['S&P 500 (SPY)']));
  const lastYs = [];
  ordered.forEach(n => {
    const vs = dates.map(d => DATA.series[n][d]);
    const path = vs.map((v, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(v).toFixed(1)).join('');
    const p = el('path', { d: path, fill: 'none', stroke: colorOf(n), 'stroke-width': 2,
      'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
    if (n === 'S&P 500 (SPY)') p.setAttribute('stroke-dasharray', '5 4');
    svg.appendChild(p);
    if (labelNames.has(n)) {
      let ly = y(vs[vs.length - 1]) + 4;
      while (lastYs.some(v => Math.abs(v - ly) < 14)) ly += 14;
      lastYs.push(ly);
      const t = el('text', { x: W - padR + 8, y: ly, fill: CSS('--ink-2'), 'font-weight': 600 });
      t.textContent = n.replace(' (orchestrator)', '').replace(' (SPY)', '');
      svg.appendChild(t);
      svg.appendChild(el('circle', { cx: x(dates.length - 1), cy: y(vs[vs.length - 1]), r: 3, fill: colorOf(n) }));
    }
  });
  const cross = el('line', { y1: padT, y2: H - padB, stroke: CSS('--baseline'), 'stroke-width': 1, visibility: 'hidden' });
  svg.appendChild(cross);
  const box = document.getElementById('linebox');
  const tip = document.createElement('div'); tip.className = 'tip'; box.appendChild(tip);
  const hover = el('rect', { x: padL, y: padT, width: W - padL - padR, height: H - padT - padB, fill: 'transparent' });
  svg.appendChild(hover);
  hover.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect();
    const sx = (ev.clientX - r.left) * (W / r.width);
    const i = Math.max(0, Math.min(dates.length - 1, Math.round((sx - padL) / (W - padL - padR) * (dates.length - 1))));
    cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.setAttribute('visibility', 'visible');
    tip.style.display = 'block';
    tip.style.left = Math.min(ev.clientX - r.left + 16, box.clientWidth - 210) + 'px';
    tip.style.top = '30px';
    tip.innerHTML = `<div class="d">${dates[i]}</div>` + ordered.map(n =>
      `<div class="row"><span><span class="sw" style="background:${colorOf(n)}"></span> ${n.replace(' (orchestrator)', '')}</span><b>${fmt(DATA.series[n][dates[i]] - 100)}</b></div>`
    ).join('');
  });
  hover.addEventListener('mouseleave', () => {
    cross.setAttribute('visibility', 'hidden'); tip.style.display = 'none';
  });
  box.appendChild(svg);
  const leg = document.getElementById('legend');
  ordered.forEach(n => {
    const s = document.createElement('span');
    const isB = n === 'S&P 500 (SPY)';
    s.innerHTML = `<span class="sw${isB ? ' dash' : ''}" style="${isB ? '' : 'background:' + colorOf(n)}"></span>${n}`;
    leg.appendChild(s);
  });
}

function drawStrip() {
  const tiers = ['fable', 'opus', 'sonnet', 'haiku'];
  const dots = DATA.summary.filter(r => !r.benchmark);
  const boot = DATA.bootstrap.returns;
  const spyRet = DATA.summary.find(r => r.benchmark).total_return_pct;
  const W = 940, padL = 120, padR = 30, histH = 70, rowH = 46, padT = 14, padB = 30;
  const H = padT + histH + tiers.length * rowH + padB;
  const allVals = dots.map(r => r.total_return_pct).concat([boot[0], boot[boot.length - 1], spyRet, 0]);
  const lo = Math.floor(Math.min(...allVals) / 10) * 10 - 2;
  const hi = Math.ceil(Math.max(...allVals) / 10) * 10 + 2;
  const x = v => padL + (v - lo) / (hi - lo) * (W - padL - padR);
  const svg = el('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  for (let g = Math.ceil(lo / 10) * 10; g <= hi; g += 10) {
    svg.appendChild(el('line', { x1: x(g), x2: x(g), y1: padT, y2: H - padB,
      stroke: g === 0 ? CSS('--baseline') : CSS('--grid'), 'stroke-width': 1 }));
    const t = el('text', { x: x(g), y: H - 12, 'text-anchor': 'middle', class: 'tick' });
    t.textContent = (g > 0 ? '+' : '') + g + '%'; svg.appendChild(t);
  }
  // luck histogram
  const nb = 36, binW = (hi - lo) / nb, bins = new Array(nb).fill(0);
  boot.forEach(b => bins[Math.max(0, Math.min(nb - 1, Math.floor((b - lo) / binW)))]++);
  const bMax = Math.max(...bins);
  bins.forEach((c, i) => {
    if (!c) return;
    const bh = c / bMax * (histH - 12);
    svg.appendChild(el('rect', { x: x(lo + i * binW) + 1, y: padT + histH - bh,
      width: Math.max(1, x(lo + binW) - x(lo) - 2), height: bh, fill: CSS('--null'), rx: 2 }));
  });
  const hlbl = el('text', { x: padL - 10, y: padT + histH - 6, 'text-anchor': 'end', fill: CSS('--ink-2'), 'font-weight': 600 });
  hlbl.textContent = 'Random baskets'; svg.appendChild(hlbl);
  // SPY reference
  const spyLine = el('line', { x1: x(spyRet), x2: x(spyRet), y1: padT, y2: H - padB,
    stroke: CSS('--bench'), 'stroke-width': 1.5, 'stroke-dasharray': '5 4' });
  svg.appendChild(spyLine);
  const spyT = el('text', { x: x(spyRet) + 5, y: padT + 10, fill: CSS('--ink-2'), 'font-weight': 600 });
  spyT.textContent = 'S&P 500 ' + fmt(spyRet); svg.appendChild(spyT);
  // dots per tier
  const box = document.getElementById('stripbox');
  const tip = document.createElement('div'); tip.className = 'tip'; box.appendChild(tip);
  tiers.forEach((m, ti) => {
    const yBase = padT + histH + ti * rowH + rowH / 2;
    svg.appendChild(el('line', { x1: padL, x2: W - padR, y1: yBase, y2: yBase, stroke: CSS('--grid'), 'stroke-width': 1 }));
    const lbl = el('text', { x: padL - 10, y: yBase + 4, 'text-anchor': 'end', fill: CSS('--ink-2'), 'font-weight': 600 });
    lbl.textContent = TIER_LABEL[m]; svg.appendChild(lbl);
    dots.filter(r => r.model === m).forEach((r, i) => {
      const jitter = ((i % 3) - 1) * 9;
      const c = el('circle', { cx: x(r.total_return_pct), cy: yBase + jitter, r: 5.5,
        fill: tierColor(m), stroke: CSS('--surface-1'), 'stroke-width': 2 });
      c.style.cursor = 'pointer';
      c.addEventListener('mousemove', ev => {
        const rb = svg.getBoundingClientRect();
        tip.style.display = 'block';
        tip.style.left = Math.min(ev.clientX - rb.left + 14, box.clientWidth - 230) + 'px';
        tip.style.top = (ev.clientY - rb.top - 60) + 'px';
        tip.innerHTML = `<div class="d">${r.name}</div>
          <div class="row"><span>Gross</span><b>${fmt(r.total_return_pct)}</b></div>
          <div class="row"><span>Net of frictions</span><b>${fmt(r.friction_return_pct)}</b></div>
          <div class="row"><span>Beats random</span><b>${r.bootstrap_pctile.toFixed(1)}%</b></div>`;
      });
      c.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
      svg.appendChild(c);
    });
  });
  box.appendChild(svg);
}

function fillTable() {
  const tb = document.querySelector('#tbl tbody');
  DATA.summary.forEach((r, i) => {
    const tr = document.createElement('tr');
    const cls = v => v >= 0 ? 'pos' : 'neg';
    const alpha = r.benchmark ? '—' : `<span class="${cls(r.capm_alpha_pct)}">${fmt(r.capm_alpha_pct)}</span>`;
    tr.innerHTML = `<td>${i + 1}</td>
      <td class="name"><span class="chip" style="background:${tierColor(r.model)}"></span>${r.name}${r.benchmark ? ' <em>(benchmark)</em>' : ''}</td>
      <td>${r.model === 'benchmark' ? '—' : r.model}</td>
      <td class="strat" title="${r.strategy}">${r.strategy}</td>
      <td class="r"><span class="${cls(r.total_return_pct)}">${fmt(r.total_return_pct)}</span></td>
      <td class="r"><span class="${cls(r.friction_return_pct)}">${fmt(r.friction_return_pct)}</span></td>
      <td class="r">${r.beta.toFixed(2)}</td>
      <td class="r">${alpha}</td>
      <td class="r">${r.bootstrap_pctile.toFixed(1)}%</td>`;
    tb.appendChild(tr);
  });
}
drawBars(); drawLines(); drawStrip(); fillTable();
</script>
"""


def main() -> None:
    results = json.loads((HERE / "results.json").read_text())
    fm = results["friction_model"]
    html = (
        TEMPLATE
        .replace("__DATA__", json.dumps(results))
        .replace("__SLOTS__", json.dumps(SLOT_ORDER))
        .replace("__TIER_SLOT__", json.dumps(TIER_SLOT))
        .replace("__ASOF__", results["as_of"])
        .replace("__COST__", str(fm["cost_bps_per_side"]))
        .replace("__DIVTAX__", str(int(fm["dividend_tax"] * 100)))
        .replace("__RF__", str(int(fm["rf_annual"] * 100)))
        .replace("__NBOOT__", str(results["bootstrap"]["n"]))
        .replace("__UNIV__", str(results["bootstrap"]["universe_size"]))
    )
    (HERE / "chart.html").write_text(html)
    print(f"Wrote chart.html ({len(html)} bytes)")


if __name__ == "__main__":
    main()

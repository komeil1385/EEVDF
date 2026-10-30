'use strict';
/* ===================== SCHEDULING ENGINE (no DOM access) =====================
 Model (all times are integer ticks, one CPU):
   v      virtual runtime, v += 1/weight per executed tick
   V      virtual time = Σ(w·v)/Σw over runnable tasks (running task included)
   lag    = w·(V − v);  eligible  <=>  lag >= 0
   d      virtual deadline = v + q/w, recomputed whenever a new slice is requested
 Decisions happen only at slice boundaries (CPU free): pick min d among eligible tasks. */
const EEVDF = (() => {
  const EPS = 1e-9;
  const COLORS = ['#4cc9f0','#f72585','#ffb703','#80ed99','#b388ff','#ff8c42','#2ec4b6','#e5989b'];
  const f = n => (Number.isInteger(n) ? String(n) : String(+n.toFixed(3)));

  function createState(slice, defs) {
    return { t: 0, slice, running: null, sliceLeft: 0, busy: 0, gantt: [], last: null,
      tasks: defs.map((x, i) => ({ id: i, name: x.name || 'T' + (i + 1), arrival: x.arrival, weight: x.weight,
        req: x.req, exec: 0, v: 0, d: 0, status: 'future', finish: null, color: COLORS[i % COLORS.length] })) };
  }
  const runnable = s => s.tasks.filter(x => x.status === 'ready');
  // Weighted average of virtual runtimes of all runnable tasks.
  function virtualTime(s) {
    const r = runnable(s), W = r.reduce((a, x) => a + x.weight, 0);
    return W ? r.reduce((a, x) => a + x.weight * x.v, 0) / W : 0;
  }
  const isDone = s => s.tasks.length > 0 && s.tasks.every(x => x.status === 'done');
  const requestSlice = (s, x) => { x.d = x.v + s.slice / x.weight; };   // d = v + q/w

  // Evaluate every runnable task: lag, eligibility, deadline.
  function evaluate(s) {
    const V = virtualTime(s);
    return { V, rows: runnable(s).map(x => { const lag = x.weight * (V - x.v);
      return { id: x.id, v: x.v, d: x.d, lag, eligible: lag >= -EPS }; }) };
  }
  // Earliest virtual deadline among ELIGIBLE rows only; ties -> lowest id.
  function pick(rows) {
    let best = null;
    for (const r of rows) if (r.eligible &&
      (!best || r.d < best.d - EPS || (Math.abs(r.d - best.d) <= EPS && r.id < best.id))) best = r;
    return best;
  }
  function explain(s, ev, ch) {
    const nm = id => s.tasks[id].name, el = ev.rows.filter(r => r.eligible), ie = ev.rows.filter(r => !r.eligible);
    let t = `V = ${f(ev.V)}. Eligible (lag ≥ 0): ${el.map(r => nm(r.id)).join(', ')}.`;
    if (ie.length) t += ` Ineligible (lag < 0): ${ie.map(r => nm(r.id)).join(', ')}.`;
    t += ` ${nm(ch.id)} has the earliest deadline among eligible tasks (d = ${f(ch.d)}).`;
    const sk = ie.filter(r => r.d < ch.d - EPS);
    if (sk.length) t += ` ${sk.map(r => `${nm(r.id)} (d = ${f(r.d)})`).join(', ')} has an earlier deadline but is ineligible, so it is skipped.`;
    return t;
  }
  // Advance simulation by one tick (mutates state).
  function step(s) {
    if (isDone(s)) return false;
    for (const x of s.tasks) if (x.status === 'future' && x.arrival <= s.t) {   // admit with lag 0: v = V
      x.v = virtualTime(s); x.status = 'ready'; requestSlice(s, x);
    }
    if (s.running === null) {                                                  // CPU free: decide
      const ev = evaluate(s), ch = pick(ev.rows);
      if (ch) { const x = s.tasks[ch.id];
        s.running = x.id; s.sliceLeft = Math.min(s.slice, x.req - x.exec);
        s.last = { t: s.t, ev, chosen: ch.id, text: explain(s, ev, ch) };
      } else s.last = { t: s.t, idle: true, text: 'No runnable task. CPU idles.' };
    }
    if (s.running === null) s.gantt.push({ t: s.t, id: null });
    else {
      const x = s.tasks[s.running];
      x.exec++; x.v += 1 / x.weight; s.sliceLeft--; s.busy++; s.gantt.push({ t: s.t, id: x.id });
      if (x.exec >= x.req) { x.status = 'done'; x.finish = s.t + 1; s.running = null; s.sliceLeft = 0; }
      else if (s.sliceLeft === 0) { s.running = null; requestSlice(s, x); }    // slice over: new request
    }
    s.t++; return true;
  }
  function stats(s) {
    return { util: s.t ? s.busy / s.t : 0, total: s.t, completed: s.tasks.filter(x => x.status === 'done').length,
      rows: s.tasks.map(x => ({ id: x.id, exec: x.exec, status: x.status,
        wait: x.status === 'future' ? 0 : (x.finish ?? s.t) - x.arrival - x.exec })) };
  }
  return { createState, step, evaluate, pick, virtualTime, isDone, stats, f, EPS };
})();

if (typeof module !== 'undefined') module.exports = EEVDF;

/* ===================== SCENARIOS + VALIDATION ===================== */
const SCENARIOS = {
  'Equal weights': { slice: 2, tasks: [[0,1,6],[0,1,6],[0,1,6]] },
  'Ineligible task has earlier deadline': { slice: 3, tasks: [[0,4,8],[0,1,6]] },
  'Staggered arrivals': { slice: 3, tasks: [[0,1,7],[2,2,6],[4,1,4],[5,3,6]] },
  'Heavy vs light': { slice: 2, tasks: [[0,8,10],[0,1,5],[0,2,6]] },
  'CPU idle gap': { slice: 2, tasks: [[0,1,3],[8,2,4]] }
};
function validateTask(a, w, r) {
  const ok = (n, lo, hi) => Number.isInteger(n) && n >= lo && n <= hi;
  if (!ok(a, 0, 100)) return 'Arrival must be a whole number from 0 to 100.';
  if (!ok(w, 1, 100)) return 'Weight must be a whole number from 1 to 100.';
  if (!ok(r, 1, 50)) return 'Service must be a whole number from 1 to 50.';
  return '';
}

/* ===================== UI (reads engine state, never decides) ===================== */
if (typeof document !== 'undefined') (() => {
  const $ = id => document.getElementById(id), f = EEVDF.f;
  let defs = [], sim = null, history = [], timer = null, mode = 'idle';   // mode: idle | running | paused
  const CELL = 30;

  function loadScenario(name) {
    const sc = SCENARIOS[name]; defs = sc.tasks.map(([arrival, weight, req]) => ({ arrival, weight, req }));
    $('slice').value = sc.slice; restart();
  }
  function restart() { stop(); sim = null; history = []; mode = 'idle'; render(); }
  function stop() { clearInterval(timer); timer = null; }
  function ensureSim() {
    if (sim) return true;
    const q = Number($('slice').value);
    if (!Number.isInteger(q) || q < 1 || q > 10) { $('err').textContent = 'Slice must be a whole number from 1 to 10.'; return false; }
    if (!defs.length) { $('err').textContent = 'Add at least one task first.'; return false; }
    $('err').textContent = ''; sim = EEVDF.createState(q, defs.map((d, i) => ({ ...d, name: 'T' + (i + 1) }))); return true;
  }
  function advance() {
    if (!ensureSim()) return;
    history.push(structuredClone(sim));
    if (!EEVDF.step(sim)) history.pop();
    if (EEVDF.isDone(sim)) { stop(); mode = 'paused'; }
    render();
  }
  function play() { stop(); timer = setInterval(advance, 1100 - $('speed').value * 100); }

  $('bStart').onclick = () => { if (!ensureSim()) return; mode = 'running'; play(); render(); };
  $('bPause').onclick = () => { stop(); mode = 'paused'; render(); };
  $('bResume').onclick = () => { mode = 'running'; play(); render(); };
  $('bNext').onclick = () => { stop(); if (mode === 'running') mode = 'paused'; advance(); if (mode === 'idle' && sim) mode = 'paused'; render(); };
  $('bPrev').onclick = () => { stop(); if (history.length) sim = history.pop(); mode = history.length ? 'paused' : 'idle';
    if (!history.length) sim = null; render(); };
  $('bRestart').onclick = restart;
  $('speed').oninput = () => { if (mode === 'running') play(); };
  $('slice').onchange = restart;
  $('scenario').onchange = e => loadScenario(e.target.value);
  $('addForm').onsubmit = e => {
    e.preventDefault();
    if (sim) { $('err').textContent = 'Press Restart to edit tasks.'; return; }
    const a = Number($('fArr').value), w = Number($('fW').value), r = Number($('fReq').value);
    const msg = validateTask(a, w, r); $('err').textContent = msg;
    if (defs.length >= 8) { $('err').textContent = 'At most 8 tasks.'; return; }
    if (!msg) { defs.push({ arrival: a, weight: w, req: r }); render(); }
  };
  $('taskRows').onclick = e => { const i = e.target.dataset.rm; if (i !== undefined && !sim) { defs.splice(+i, 1); render(); } };

  function cardHTML(t, ev, cpuId) {
    const row = ev && ev.rows.find(r => r.id === t.id);
    let cls = t.status, tag = t.status === 'future' ? 'not arrived' : t.status === 'done' ? 'done' : '';
    if (row) { cls = row.eligible ? 'eligible' : 'inelig'; tag = row.eligible ? 'eligible' : 'ineligible'; }
    return `<div class="card ${cls} ${cpuId === t.id ? 'cpu' : ''}" style="--c:${t.color}"><span class="tag">${tag}</span><b>${t.name}</b><br>
      w=${t.weight} · done ${t.exec}/${t.req}${row ? `<br>v=${f(row.v)} · d=${f(row.d)}<br>lag=${f(row.lag)}` : ''}</div>`;
  }
  function render() {
    const ro = !!sim, T = sim ? sim.tasks : defs.map((d, i) => ({ ...d, id: i, name: 'T' + (i + 1), exec: 0, status: 'future', color: '#8b9bb0' }));
    $('taskRows').innerHTML = defs.map((d, i) => `<tr><td>T${i + 1}</td><td>${d.arrival}</td><td>${d.weight}</td><td>${d.req}</td>
      <td><button data-rm="${i}" ${ro ? 'disabled' : ''} aria-label="Remove T${i + 1}">Remove</button></td></tr>`).join('');
    $('slice').disabled = ro;
    const done = sim && EEVDF.isDone(sim);
    $('bStart').disabled = mode !== 'idle'; $('bPause').disabled = mode !== 'running';
    $('bResume').disabled = mode !== 'paused' || done; $('bNext').disabled = done; $('bPrev').disabled = !history.length;
    $('clock').textContent = sim ? sim.t : 0;
    const ev = sim ? EEVDF.evaluate(sim) : null, lastG = sim && sim.gantt[sim.gantt.length - 1];
    const cpuId = lastG ? lastG.id : null, cpuT = cpuId !== null && cpuId !== undefined ? sim.tasks[cpuId] : null;
    $('cpu').innerHTML = !sim ? 'Ready to start' : done ? 'All tasks finished' : cpuT ? `Ran ${cpuT.name} in tick ${lastG.t}` : 'Idle';
    $('cpu').style.borderColor = cpuT ? cpuT.color : ''; $('cpu').style.color = cpuT ? cpuT.color : '';
    $('cards').innerHTML = T.map(t => cardHTML(t, ev, cpuId)).join('');
    renderDecision(); renderVT(ev); renderGantt(); renderStats();
  }
  function renderDecision() {
    const L = sim && sim.last;
    if (!L) { $('dec').innerHTML = '<p>No decision yet. Press Start or Next step.</p>'; return; }
    const nm = id => sim.tasks[id].name;
    let h = `<p><b>Decision at t = ${L.t}:</b> ${L.text}</p>`;
    if (L.ev) h += `<table class="dtab"><thead><tr><th>Task</th><th>v</th><th>lag</th><th>Eligible</th><th>d</th></tr></thead><tbody>` +
      L.ev.rows.map(r => `<tr class="${r.id === L.chosen ? 'chosen' : (!r.eligible && r.d < L.ev.rows.find(x => x.id === L.chosen).d - EEVDF.EPS ? 'skip' : '')}">
      <td>${nm(r.id)}</td><td>${f(r.v)}</td><td>${f(r.lag)}</td><td>${r.eligible ? 'yes' : 'no'}</td><td>${f(r.d)}</td></tr>`).join('') + '</tbody></table>';
    if (sim.running !== null) h += `<p>${nm(sim.running)} is mid-slice (${sim.sliceLeft} tick(s) left). The next decision comes at the slice end.</p>`;
    $('dec').innerHTML = h;
  }
  function renderVT(ev) {
    if (!ev || !ev.rows.length) { $('vt').innerHTML = '<p class="hint">Runnable tasks appear here.</p>'; return; }
    const vals = ev.rows.flatMap(r => [r.v, r.d]).concat(ev.V), lo = Math.min(...vals), hi = Math.max(...vals), span = (hi - lo) || 1;
    const pos = x => ((x - lo) / span * 96 + 1) + '%', L = sim.last;
    $('vt').innerHTML = '<div class="area">' + ev.rows.map(r => { const t = sim.tasks[r.id];
      return `<div class="vtr ${r.eligible ? '' : 'inelig'} ${L && L.chosen === r.id && sim.running === r.id ? 'pick' : ''}" style="--c:${t.color}">
      <span class="n">${t.name}</span><div class="vtb" style="left:${pos(r.v)};width:${(r.d - r.v) / span * 96}%" title="v=${f(r.v)} d=${f(r.d)}"></div></div>`; }).join('') +
      `<div class="vV" style="left:${pos(ev.V)}"><em>V=${f(ev.V)}</em></div></div>`;
  }
  function renderGantt() {
    if (!sim || !sim.gantt.length) { $('gantt').innerHTML = '<p class="hint">Execution blocks appear here.</p>'; return; }
    const blocks = []; for (const g of sim.gantt) { const b = blocks[blocks.length - 1];
      if (b && b.id === g.id) b.n++; else blocks.push({ id: g.id, t: g.t, n: 1 }); }
    $('gantt').innerHTML = blocks.map(b => { const t = b.id === null ? null : sim.tasks[b.id];
      return `<div class="gb ${t ? '' : 'idle'}" style="width:${b.n * CELL}px;${t ? `--c:${t.color}` : ''}"><i>${b.t}</i>${t ? t.name : 'idle'}</div>`; }).join('') +
      `<div class="gb" style="width:0;background:none"><i>${sim.t}</i></div>`;
  }
  function renderStats() {
    if (!sim) { $('totals').innerHTML = ''; $('stats').innerHTML = ''; return; }
    const s = EEVDF.stats(sim);
    $('totals').innerHTML = `<div><b>${(s.util * 100).toFixed(0)}%</b>CPU utilization</div><div><b>${s.total}</b>simulation ticks</div><div><b>${s.completed}/${sim.tasks.length}</b>completed</div>`;
    $('stats').innerHTML = s.rows.map(r => `<tr><td>${sim.tasks[r.id].name}</td><td>${r.exec}</td><td>${r.wait}</td><td>${r.status}</td></tr>`).join('');
  }
  $('scenario').innerHTML = Object.keys(SCENARIOS).map(n => `<option>${n}</option>`).join('');
  $('scenario').value = 'Ineligible task has earlier deadline';
  loadScenario($('scenario').value);
})();

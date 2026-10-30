// Run: node tests.js
const E = require('./script.js'); const assert = require('assert');
const run = (slice, defs) => { const s = E.createState(slice, defs); let n = 0; while (E.step(s) && n++ < 1000); return s; };
const order = s => s.gantt.filter(g => g.id !== null).map(g => s.tasks[g.id].name).join('');
// 1: ineligible task with earlier deadline is skipped
let s = E.createState(3, [{arrival:0,weight:4,req:8},{arrival:0,weight:1,req:6}]);
for (let i = 0; i < 3; i++) E.step(s);                      // T1 ran one slice
let ev = E.evaluate(s); const a = ev.rows[0], b = ev.rows[1];
assert(!a.eligible && a.d < b.d && b.eligible, 'T1 ineligible with earlier d'); assert.strictEqual(E.pick(ev.rows).id, 1);
console.log('1 ok: T1 (d=%s, lag=%s) skipped, T2 (d=%s) chosen', a.d, a.lag.toFixed(2), b.d);
// 2: equal weights -> round robin by slice
assert.strictEqual(order(run(2, [0,0,0].map(()=>({arrival:0,weight:1,req:4})))), 'T1T1T2T2T3T3T1T1T2T2T3T3'); console.log('2 ok: equal weights');
// 3: proportional share (weights 3:1, long run) ~ 75/25 over first 16 ticks
s = E.createState(1, [{arrival:0,weight:3,req:100},{arrival:0,weight:1,req:100}]); for (let i = 0; i < 40; i++) E.step(s);
assert(Math.abs(s.tasks[0].exec - 30) <= 1, 'share ' + s.tasks[0].exec); console.log('3 ok: 3:1 weights gave', s.tasks[0].exec, '/40');
// 4: idle gap, late arrival has lag 0, everything completes, accounting consistent
s = run(2, [{arrival:0,weight:1,req:3},{arrival:8,weight:2,req:4}]);
assert(E.isDone(s) && s.busy === 7 && s.t === 12 && s.gantt.filter(g=>g.id===null).length === 5); console.log('4 ok: idle gap');
// 5: invariant — at every decision someone is eligible and chosen has min d among eligible
s = E.createState(2, [[0,1,9],[0,5,9],[3,2,9],[4,1,5]].map(([arrival,weight,req])=>({arrival,weight,req})));
while (!E.isDone(s)) { E.step(s); if (s.last && s.last.ev && s.last.t === s.t - 1) { const el = s.last.ev.rows.filter(r=>r.eligible);
  assert(el.length && el.every(r => r.d >= el.find(x=>x.id===s.last.chosen).d - 1e-9)); } }
console.log('5 ok: invariant over full run, total ticks', s.t);

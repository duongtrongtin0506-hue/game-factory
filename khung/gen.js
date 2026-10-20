// Level generator: node khung/gen.js [variant-id] [count]
// For every level: pick a board and goal from the variant's rule, let the beam solver find a win,
// give the player the solver's drop count plus some slack, rate difficulty with a plain one-step
// player (hard = % of 20 plain runs that fail). About every 5th level is an easy breather.
// Writes khung/levels/<id>.json. Same seeds give the same levels.
const fs = require('fs'), path = require('path');
const E = require('./engine.js');
const DIR = __dirname;
const VARIANTS = JSON.parse(fs.readFileSync(path.join(DIR, 'variants.json'), 'utf8'));

const HEX = '0123456789abc';
function encode(b) {
  const rows = [];
  let top = b.rows;
  for (let i = 0; i < b.v.length; i++) if (E.filled(b, i)) { top = Math.min(top, Math.floor(i / b.cols)); }
  for (let r = top; r < b.rows; r++) {
    let s = '';
    for (let c = 0; c < b.cols; c++) {
      const i = r * b.cols + c;
      s += b.k[i] === 1 ? '#' : b.k[i] === 2 ? '!' + HEX[b.v[i]] : b.v[i] ? HEX[b.v[i]] : '.';
    }
    rows.push(s);
  }
  return rows.join('/');
}

// Settled starting board: each column a stack from the floor; no two equal free tiles touch.
function board(R, cols, rows, opt) {
  const b = { cols, rows, v: new Array(cols * rows).fill(0), k: new Array(cols * rows).fill(0) };
  let stones = opt.stones || 0, ice = opt.ice || 0;
  const heights = [];
  for (let c = 0; c < cols; c++) heights.push(opt.minH + Math.floor(R() * (opt.maxH - opt.minH + 1)));
  const spots = [];
  for (let c = 0; c < cols; c++) for (let h = 0; h < heights[c]; h++) spots.push((rows - 1 - h) * cols + c);
  // Stones and ice go low on the board where they are hardest to reach.
  spots.sort((a, z) => (z - a) + (R() - 0.5) * cols * 3);
  const special = new Set();
  for (const i of spots) { if (stones > 0) { b.k[i] = 1; special.add(i); stones--; } else if (ice > 0 && i >= cols * (rows - 3)) { b.k[i] = 2; special.add(i); ice--; } }
  for (const i of spots) {
    if (b.k[i] === 1) continue;
    const near = [i - 1, i + 1, i + cols, i - cols].filter(n => n >= 0 && n < b.v.length && Math.abs((n % cols) - (i % cols)) <= 1).map(n => b.v[n]);
    let t, tries = 0;
    do { t = 1 + Math.floor(R() * opt.top); tries++; } while (near.includes(t) && tries < 20);
    b.v[i] = t;
  }
  return b;
}

function params(rule, n, relax) {
  const easy = n > 1 && n % 5 === 0;
  const m = Math.max(1, (easy ? n - 7 : n) - (relax || 0) * 3);
  const p = { cols: 5, rows: Math.min(8, 6 + (m > 8 ? 1 : 0) + (m > 22 ? 1 : 0)), lo: 1, hi: Math.min(5, 3 + (m > 10 ? 1 : 0) + (m > 26 ? 1 : 0)), slack: easy ? 8 : Math.max(2, 6 - Math.floor(m / 8)), easy };
  if (m > 14) p.cols = 6;
  if (rule === 'reach') { p.goal = { type: 'reach', n: Math.min(8, 5 + Math.floor(m / 8)) }; p.opt = m > 3 ? { minH: 0, maxH: 2, top: p.hi } : null; }
  if (rule === 'stones') { const s = Math.min(16, 3 + Math.floor(m / 2)); p.goal = { type: 'stones', n: s }; p.opt = { stones: s, minH: 2, maxH: 3 + (m > 12 ? 1 : 0), top: p.hi + 1 }; }
  if (rule === 'make') { p.goal = { type: 'make', tier: Math.min(7, 4 + Math.floor(m / 10)), n: Math.min(5, 2 + Math.floor(m / 10)) }; p.opt = m > 2 ? { minH: 0, maxH: 2, top: p.hi } : null; }
  if (rule === 'ice') { const s = Math.min(14, 3 + Math.floor(m / 2)); p.goal = { type: 'ice', n: s }; p.opt = { ice: s, minH: 2, maxH: 3 + (m > 12 ? 1 : 0), top: p.hi + 1 }; }
  if (rule === 'score') { p.goal = { type: 'score', n: 100 * Math.round((200 + m * 60) / 100) }; p.opt = { minH: 1, maxH: 3 + (m > 12 ? 1 : 0), top: p.hi + 1 }; }
  return p;
}
// Target difficulty window by level number (hard = % plain-player failures).
const window_ = (n, easy) => easy ? [0, 30] : [Math.min(60, 5 + n * 1.6), Math.min(95, 35 + n * 1.8)];

function make(variant, n, relax) {
  relax = relax || 0;
  const p = params(variant.rule, n, relax);
  const [lo, hi] = window_(n, p.easy);
  let pick = null;
  for (let a = 0; a < 40; a++) {
    const seed = (variant.seed * 7919 + n * 104729 + a * 15485863) >>> 0;
    const R = E.rng(seed ^ 0xA5A5);
    const b = p.opt ? board(R, p.cols, p.rows, p.opt) : null;
    const lv = { n, cols: p.cols, rows: p.rows, seed, lo: p.lo, hi: p.hi, drops: 60, goal: p.goal, preset: b ? encode(b) : '' };
    const list = E.spawnList(seed, 120, lv.lo, lv.hi);
    const s = E.solve(lv, list, 40);
    if (!s.won || s.used < 4) continue;
    lv.par = s.used; lv.drops = s.used + p.slack;
    // Check again with the real drop limit (the beam may need the extra room it had before).
    const s2 = E.solve(lv, list, 40);
    if (!s2.won) continue;
    lv.par = s2.used;
    let fails = 0;
    for (let k = 0; k < 20; k++) if (!E.greedy(lv, list, seed + k * 31)) fails++;
    lv.hard = fails * 5;
    lv.moves = s2.moves;
    const miss = lv.hard < lo ? lo - lv.hard : lv.hard > hi ? lv.hard - hi : 0;
    if (!pick || miss < pick.miss) pick = { lv, miss };
    if (miss === 0) break;
  }
  if (!pick && relax < 6) return make(variant, n, relax + 1);   // nothing solvable: ease this level a step
  if (!pick) throw new Error(variant.id + ' level ' + n + ': no solvable board');
  if (relax) pick.lv.relax = relax;
  return pick.lv;
}

function run(id, count) {
  for (const v of VARIANTS) {
    if (id && v.id !== id) continue;
    const t0 = Date.now(), out = [];
    for (let n = 1; n <= (count || v.levels); n++) out.push(make(v, n));
    fs.mkdirSync(path.join(DIR, 'levels'), { recursive: true });
    fs.writeFileSync(path.join(DIR, 'levels', v.id + '.json'), JSON.stringify(out));
    const hard = out.map(l => l.hard);
    console.log(v.id, out.length, 'levels', ((Date.now() - t0) / 1000).toFixed(1) + 's', 'hard avg', Math.round(hard.reduce((a, b) => a + b, 0) / hard.length), 'curve', hard.join(' '));
  }
}
if (require.main === module) run(process.argv[2], +process.argv[3] || 0);
module.exports = { make, run, encode };

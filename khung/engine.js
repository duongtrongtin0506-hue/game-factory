// ============================================================================
// Drop & Merge engine: rules, level goals and the solver. Pure logic, no drawing, so the same file
// runs in the browser (game + autoplay) and in Node (level generator, tests).
//
// Board: cols x rows, index = r * cols + c, row 0 is the top. A cell holds a tier (0 = empty) and
// a kind: 0 tile, 1 stone (fixed, breaks when a merge touches it), 2 ice (fixed tile that cannot
// merge until a merge touches it; then it thaws and falls like any tile).
// A drop lands on top of its column. Every group of 2+ equal, connected tiles merges into the tile
// that just moved; the new tier is tier + (group size - 1). Tiles fall, merges chain.
// ============================================================================
(function (root) {
  const MAX_TIER = 12;

  // xorshift32: same numbers in every browser and in Node.
  function rng(seed) {
    let s = (seed >>> 0) || 0x9E3779B9;
    return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  }

  // Board from a level: preset is a string of rows (top first), '.' empty, '1'..'9','a'..'c' tier,
  // '#' stone, lowercase-after-'!' ice: '!3' is ice holding tier 3. Rows separated by '/'.
  function boardFrom(level) {
    const cols = level.cols, rows = level.rows;
    const b = { cols, rows, v: new Array(cols * rows).fill(0), k: new Array(cols * rows).fill(0) };
    if (level.preset) {
      const lines = level.preset.split('/');
      lines.forEach((line, i) => {
        const r = rows - lines.length + i;
        let c = 0;
        for (let j = 0; j < line.length && c < cols; j++) {
          const ch = line[j], at = r * cols + c;
          if (ch === '!') { b.k[at] = 2; b.v[at] = parseInt(line[++j], 16); c++; }
          else if (ch === '#') { b.k[at] = 1; c++; }
          else if (ch === '.') c++;
          else { b.v[at] = parseInt(ch, 16); c++; }
        }
      });
    }
    return b;
  }
  const clone = b => ({ cols: b.cols, rows: b.rows, v: b.v.slice(), k: b.k.slice() });
  const filled = (b, i) => b.v[i] > 0 || b.k[i] === 1;

  // Row where a drop in column c lands, or -1 when the column is full.
  function landing(b, c) {
    if (filled(b, c)) return -1;
    let r = 0;
    while (r + 1 < b.rows && !filled(b, (r + 1) * b.cols + c)) r++;
    return r;
  }
  function neighbours(b, i) {
    const c = i % b.cols, out = [];
    if (i >= b.cols) out.push(i - b.cols);
    if (i + b.cols < b.v.length) out.push(i + b.cols);
    if (c > 0) out.push(i - 1);
    if (c < b.cols - 1) out.push(i + 1);
    return out;
  }
  function group(b, i) {
    const t = b.v[i], seen = new Set([i]), stack = [i];
    while (stack.length) {
      const j = stack.pop();
      for (const n of neighbours(b, j)) if (!seen.has(n) && b.k[n] === 0 && b.v[n] === t) { seen.add(n); stack.push(n); }
    }
    return [...seen];
  }
  // Loose tiles fall; stones and ice stay. Returns [[from, to], ...].
  function gravity(b) {
    const moves = [];
    for (let c = 0; c < b.cols; c++) {
      for (let r = b.rows - 2; r >= 0; r--) {
        const i = r * b.cols + c;
        if (b.v[i] === 0 || b.k[i] !== 0) continue;
        let to = r;
        while (to + 1 < b.rows && !filled(b, (to + 1) * b.cols + c)) to++;
        if (to !== r) {
          const j = to * b.cols + c;
          b.v[j] = b.v[i]; b.v[i] = 0; moves.push([i, j]);
        }
      }
    }
    return moves;
  }

  // Drops tier t in column c. Mutates b and returns { ok, steps, score, made } where steps feed the
  // animation: {type:'place', to, t}, {type:'merge', from:[...], to, t, hit:[...]}, {type:'fall', moves}.
  // made[tier] counts tiles created by merges at that tier.
  function drop(b, c, t) {
    const r = landing(b, c);
    if (r < 0) return { ok: false, steps: [], score: 0, made: {} };
    const steps = [], made = {};
    let score = 0, at = r * b.cols + c;
    steps.push({ type: 'place', to: at, t, before: { v: b.v.slice(), k: b.k.slice() } });
    b.v[at] = t;
    let active = [at];
    for (let guard = 0; guard < 200; guard++) {
      let done = true;
      for (const a of active) {
        if (b.v[a] === 0 || b.k[a] !== 0) continue;
        const gr = group(b, a);
        if (gr.length < 2) continue;
        const nt = Math.min(MAX_TIER, b.v[a] + gr.length - 1), hit = [];
        const before = { v: b.v.slice(), k: b.k.slice() };
        const touched = new Set();
        for (const j of gr) for (const n of neighbours(b, j)) if (!gr.includes(n)) touched.add(n);
        for (const j of gr) if (j !== a) b.v[j] = 0;
        b.v[a] = nt;
        for (const n of touched) {
          if (b.k[n] === 1) { b.k[n] = 0; b.v[n] = 0; hit.push(n); }
          else if (b.k[n] === 2) { b.k[n] = 0; hit.push(n); }
        }
        made[nt] = (made[nt] || 0) + 1;
        score += Math.pow(2, nt);
        steps.push({ type: 'merge', from: gr.filter(j => j !== a), to: a, t: nt, hit, before });
        const fb = { v: b.v.slice(), k: b.k.slice() };
        const moves = gravity(b);
        if (moves.length) steps.push({ type: 'fall', moves, before: fb });
        const moved = moves.map(m => m[1]);
        let stay = a;
        for (const m of moves) if (m[0] === a) stay = m[1];
        // The merged tile first, then tiles that moved or thawed, then the rest still waiting.
        active = [stay, ...moved, ...hit.filter(n => b.v[n] > 0), ...active.filter(x => x !== a)];
        active = active.filter((x, i, arr) => arr.indexOf(x) === i);
        done = false;
        break;
      }
      if (done) break;
    }
    return { ok: true, steps, score, made };
  }

  // Tiles to come. Levels: a fixed list from the seed (the solver sees the same list as the player).
  // Endless: the range climbs with the best tile on the board.
  function spawnList(seed, n, lo, hi) {
    const R = rng(seed), out = [];
    for (let i = 0; i < n; i++) out.push(lo + Math.floor(R() * (hi - lo + 1)));
    return out;
  }
  function endlessRange(best) {
    const hi = Math.max(3, Math.min(8, best - 3));
    return [Math.max(1, hi - 4), hi];
  }

  // Goal of a level: reach (make a tile of tier >= n), make (count tiles of tier >= tier made by
  // merges), stones / ice (clear every stone / thaw every ice), score.
  function newRun(level) {
    return { b: boardFrom(level), i: 0, score: 0, made: {}, best: 0, left: level.drops, over: false, won: false };
  }
  function progress(level, run) {
    const g = level.goal, b = run.b;
    if (g.type === 'reach') return Math.min(1, Math.max(...b.v, run.best) / g.n);
    if (g.type === 'make') { let n = 0; for (const t in run.made) if (+t >= g.tier) n += run.made[t]; return Math.min(1, n / g.n); }
    if (g.type === 'stones') { const n = b.k.filter(x => x === 1).length; return g.n ? 1 - n / g.n : 1; }
    if (g.type === 'ice') { const n = b.k.filter(x => x === 2).length; return g.n ? 1 - n / g.n : 1; }
    if (g.type === 'score') return Math.min(1, run.score / g.n);
    return 0;   // 'none': endless mode, never won
  }
  // One drop in a level run (tile from the level's list). Returns the drop result.
  function step(level, run, c, list) {
    const t = list[run.i];
    const res = drop(run.b, c, t);
    if (!res.ok) return res;
    run.i++; run.left--; run.score += res.score;
    for (const k in res.made) run.made[k] = (run.made[k] || 0) + res.made[k];
    run.best = Math.max(run.best, ...run.b.v);
    if (progress(level, run) >= 1) { run.won = true; run.over = true; }
    else if (run.left <= 0 || !canDrop(run.b)) run.over = true;
    return res;
  }
  function canDrop(b) { for (let c = 0; c < b.cols; c++) if (landing(b, c) >= 0) return true; return false; }

  // Board shape score for the solver and the bot: room, best tile, few bumps, equal neighbours.
  function shape(b) {
    let empty = 0, best = 0, bumps = 0, pairs = 0, prevH = -1;
    for (let c = 0; c < b.cols; c++) {
      let h = 0;
      for (let r = 0; r < b.rows; r++) { const i = r * b.cols + c; if (filled(b, i)) { h = b.rows - r; break; } }
      if (prevH >= 0) bumps += Math.abs(h - prevH);
      prevH = h;
    }
    for (let i = 0; i < b.v.length; i++) {
      if (!filled(b, i)) { empty++; continue; }
      best = Math.max(best, b.v[i]);
      const c = i % b.cols;
      if (c < b.cols - 1 && b.k[i + 1] === 0 && b.v[i + 1] && Math.abs(b.v[i + 1] - b.v[i]) === 1) pairs++;
      if (i + b.cols < b.v.length && b.k[i + b.cols] === 0 && b.v[i + b.cols] && b.v[i + b.cols] - b.v[i] === 1) pairs++;
    }
    return empty * 12 + best * 6 - bumps * 3 + pairs * 2;
  }
  function value(level, run) {
    if (run.won) return 1e9 - run.i;
    if (run.over) return -1e9;
    return progress(level, run) * 1000 + shape(run.b);
  }
  const copyRun = run => ({ b: clone(run.b), i: run.i, score: run.score, made: Object.assign({}, run.made), best: run.best, left: run.left, over: run.over, won: run.won });

  // Beam search over column choices. Returns { won, moves: [col...], used } (used = drops spent).
  // start: an ongoing run to continue from (hint button); default is a fresh run.
  function solve(level, list, width, start) {
    width = width || 48;
    const first = start ? copyRun(start) : newRun(level);
    let beam = [{ run: first, moves: [] }];
    for (let d = 0; d < first.left; d++) {
      const next = [];
      for (const node of beam) {
        for (let c = 0; c < level.cols; c++) {
          const run = copyRun(node.run);
          if (!step(level, run, c, list).ok) continue;
          const n = { run, moves: node.moves.concat(c) };
          if (run.won) return { won: true, moves: n.moves, used: run.i };
          if (!run.over) next.push(n);
        }
      }
      if (!next.length) break;
      next.sort((a, z) => value(level, z.run) - value(level, a.run));
      // Keep the best boards but drop exact duplicates so the beam stays wide.
      const seen = new Set(); beam = [];
      for (const n of next) { const key = n.run.b.v.join(',') + n.run.b.k.join(''); if (seen.has(key)) continue; seen.add(key); beam.push(n); if (beam.length >= width) break; }
    }
    return { won: false, moves: [], used: level.drops };
  }

  // A plain player: looks one drop ahead, sometimes picks the second best. Used to rate difficulty.
  function greedy(level, list, seed) {
    const R = rng(seed), run = newRun(level);
    while (!run.over) {
      const opts = [];
      for (let c = 0; c < level.cols; c++) {
        const r2 = copyRun(run);
        if (step(level, r2, c, list).ok) opts.push([value(level, r2) + R() * 40, c]);
      }
      if (!opts.length) break;
      opts.sort((a, z) => z[0] - a[0]);
      step(level, run, (opts.length > 1 && R() < 0.25 ? opts[1] : opts[0])[1], list);
    }
    return run.won;
  }
  // Best column for one drop right now (tutorial hand, hint, autoplay fallback).
  function bestColumn(level, run, list) {
    let best = -Infinity, col = Math.floor(level.cols / 2);
    for (let c = 0; c < level.cols; c++) {
      const r2 = copyRun(run);
      if (!step(level, r2, c, list).ok) continue;
      const v = value(level, r2);
      if (v > best) { best = v; col = c; }
    }
    return col;
  }

  const api = { MAX_TIER, rng, boardFrom, clone, landing, drop, gravity, spawnList, endlessRange, newRun, progress, step, canDrop, solve, greedy, bestColumn, copyRun, filled };
  if (typeof module === 'object' && module.exports) module.exports = api; else root.Engine = api;
})(typeof window !== 'undefined' ? window : globalThis);

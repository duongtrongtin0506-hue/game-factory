// Generates the 100 Car Jam levels (sliding-block "unblock the red car" puzzles) and prints
// them as a JS array. Every level is solved by breadth-first search, so each one is known to
// be solvable and its minimum number of moves is known exactly.
//   node gen-levels.js > levels.txt
'use strict';
const N = 6, EXIT_ROW = 2;

function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

function randomBoard(r, count) {
  const grid = Array(N * N).fill(-1), cars = [];
  const place = (row, col, len, horiz) => {
    for (let k = 0; k < len; k++) { const rr = row + (horiz ? 0 : k), cc = col + (horiz ? k : 0); if (rr >= N || cc >= N || grid[rr * N + cc] >= 0) return false; }
    for (let k = 0; k < len; k++) grid[(row + (horiz ? 0 : k)) * N + col + (horiz ? k : 0)] = cars.length;
    cars.push({ row, col, len, horiz });
    return true;
  };
  place(EXIT_ROW, Math.floor(r() * 3), 2, true);                 // car 0 is the red car
  let tries = 0;
  while (cars.length < count && tries++ < 200) {
    const horiz = r() < 0.5, len = r() < 0.72 ? 2 : 3, row = Math.floor(r() * N), col = Math.floor(r() * N);
    if (horiz && row === EXIT_ROW) continue;                      // nothing else may lie along the exit row
    place(row, col, len, horiz);
  }
  return cars;
}

// Breadth-first search over car offsets. One move = sliding one car any distance.
function solve(cars) {
  const fixed = cars.map(c => c.horiz ? c.row : c.col);
  const start = cars.map(c => c.horiz ? c.col : c.row);
  const key = p => p.join('');
  const seen = new Map([[key(start), 0]]);
  let frontier = [start], depth = 0;
  const occ = new Int8Array(N * N);
  while (frontier.length) {
    const next = [];
    for (const pos of frontier) {
      if (pos[0] + cars[0].len === N) return depth;
      occ.fill(0);
      for (let i = 0; i < cars.length; i++) for (let k = 0; k < cars[i].len; k++) occ[cars[i].horiz ? fixed[i] * N + pos[i] + k : (pos[i] + k) * N + fixed[i]] = 1;
      for (let i = 0; i < cars.length; i++) {
        const c = cars[i];
        for (const dir of [-1, 1]) {
          for (let p = pos[i] + dir; p >= 0 && p + c.len <= N; p += dir) {
            const cell = dir < 0 ? p : p + c.len - 1;
            if (occ[c.horiz ? fixed[i] * N + cell : cell * N + fixed[i]]) break;
            const np = pos.slice(); np[i] = p;
            const k = key(np);
            if (!seen.has(k)) { seen.set(k, depth + 1); next.push(np); }
          }
        }
      }
    }
    frontier = next; depth++;
    if (seen.size > 60000) return -1;
  }
  return -1;
}

function encode(cars) {
  const g = Array(N * N).fill('.');
  cars.forEach((c, i) => { for (let k = 0; k < c.len; k++) g[(c.row + (c.horiz ? 0 : k)) * N + c.col + (c.horiz ? k : 0)] = String.fromCharCode(65 + i); });
  return g.join('');
}

const r = rng(20261010), byMoves = new Map(), seenBoards = new Set();
const deadline = Date.now() + (+process.argv[2] || 60) * 1000;
let made = 0;
while (Date.now() < deadline) {
  const cars = randomBoard(r, 6 + Math.floor(r() * 8));
  if (cars.length < 5) continue;
  const code = encode(cars);
  if (seenBoards.has(code)) continue;
  seenBoards.add(code);
  const m = solve(cars);
  made++;
  if (m < 3) continue;
  if (!byMoves.has(m)) byMoves.set(m, []);
  if (byMoves.get(m).length < 40) byMoves.get(m).push(code);
}
// Difficulty curve: target minimum-move counts for levels 1..100.
const target = i => i < 5 ? 3 + Math.floor(i / 2) : i < 20 ? 5 + Math.floor((i - 5) / 3) : i < 50 ? 10 + Math.floor((i - 20) / 5) : i < 80 ? 16 + Math.floor((i - 50) / 6) : 21 + Math.floor((i - 80) / 5);
const levels = [], maxM = Math.max(...byMoves.keys());
for (let i = 0; i < 100; i++) {
  let want = Math.min(target(i), maxM), pick = null;
  for (let d = 0; d < 30 && !pick; d++) for (const m of [want - d, want + d]) { const pool = byMoves.get(m); if (pool && pool.length) { pick = [pool.pop(), m]; break; } }
  levels.push(pick);
}
levels.sort((a, b) => a[1] - b[1]);
process.stderr.write('boards tried: ' + made + ', hardest found: ' + maxM + ', level moves: ' + levels.map(l => l[1]).join(' ') + '\n');
console.log('const LEVELS = [\n' + levels.map(l => "  '" + l[0] + "'").join(',\n') + '\n];\nconst PAR = [' + levels.map(l => l[1]).join(',') + '];');

// Do nhip do cua Merge Harvest: node tools/merge_sim.js
// Lay phan ==CORE== trong web/merge-harvest/index.src.html roi cho mot nguoi choi gia chay theo dong ho:
// moi thao tac (trong, gop, giao, ban, nang cap) ton ACT giay, hat giong hoi 1 hat / SEED_EVERY giay, xu chay theo giay.
// In ra: phut choi den khi tim thay tung bac va den don hang thu N. Muc tieu: bac 10 (Golden Tree) trong 25-40 phut.
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'web', 'merge-harvest', 'index.src.html'), 'utf8');
const core = '//' + src.split('// ==CORE==')[1].split('// ==/CORE==')[0];
const api = new Function(core + '; return { newState, empties, income, upCost, spawn, move, deliver, sell, upgrade, pair, TOP, MAX_SEEDS, SEED_EVERY, seasonUp: typeof seasonUp === "function" ? seasonUp : null };')();
const ACT = 0.7;

function run(seed, minutes) {
  let s = seed; const rnd = () => (s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const S = api.newState(), found = {}, log = [];
  let t = 0, seasons = 0;
  const tick = dt => { t += dt; S.coins += api.income(S) * dt; S.seeds = Math.min(api.MAX_SEEDS, S.seeds + dt / api.SEED_EVERY); };
  while (t < minutes * 60) {
    const p = api.pair(S), o = S.grid.indexOf(S.order);
    if (S.coins >= api.upCost(S)) api.upgrade(S);
    else if (o >= 0) api.deliver(S, o);
    else if (p) api.move(S, p[0], p[1]);
    else if (api.empties(S).length && S.seeds >= 1) api.spawn(S, rnd);
    else if (!api.empties(S).length) api.sell(S, S.grid.indexOf(Math.min(...S.grid)));
    else { tick(api.SEED_EVERY); continue; }   // het hat: cho
    tick(ACT);
    if (!seasons && !found[S.found]) { found[S.found] = t / 60; }
    if ((S.season || 0) > seasons) { seasons = S.season; log.push('mua ' + (seasons + 1) + ' @' + (t / 60).toFixed(1)); }
  }
  return { found, delivered: S.delivered, up: S.up, coins: Math.round(S.coins), log };
}

const out = [1, 2, 3].map(seed => run(seed * 7919, 60));
for (const r of out) {
  console.log(Object.keys(r.found).map(k => 'b' + k + ':' + r.found[k].toFixed(1)).join(' ') + ' | don ' + r.delivered + ' | nang cap ' + r.up + ' | xu ' + r.coins + (r.log.length ? ' | ' + r.log.join(', ') : ''));
}

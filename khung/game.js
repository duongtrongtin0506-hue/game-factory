// ============================================================================
// Drop & Merge frame: screens, drawing, input, sound, saving. Needs Engine (engine.js), THEMES
// (themes.js), VARIANT, LEVELS, STR (filled in by build.py) and the ads layer (showAd, gameplay,
// happy, adPlaying).
// Query: ?level=N start level ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?endless=1 ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?autoplay=N solver plays N levels (tests, video)
// ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?speed=K faster animation ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?selftest=1 replays every level's solution ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?demo=1&w=&h= fixed size
// ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?cover=1 cover art ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ?fresh=1 ignore the save.
// ============================================================================
const QS = new URLSearchParams(location.search);
const T = THEMES[VARIANT.theme];
const C = { page: T.page, card: T.card, line: T.line, text: T.text, soft: T.soft, accent: T.accent, cell: T.cell };
const F = {
  head: '"Cormorant Garamond","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif',
  body: 'Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif',
  mono: 'ui-monospace,Menlo,Consolas,monospace'
};
const SAVE_KEY = 'dm.' + VARIANT.id + '.v1';
const DEMO = !!QS.get('demo') || !!QS.get('cover');
const SPEED = Math.max(0.25, +QS.get('speed') || 1);
const AUTO = +QS.get('autoplay') || 0;

// Strings: English built in; another language file can be dropped into STR under its code.
const LANG = (navigator.language || 'en').slice(0, 2);
function t(key, ...a) {
  const s = (STR[LANG] && STR[LANG][key]) || STR.en[key] || key;
  return s.replace(/\{(\d)\}/g, (m, i) => a[+i]);
}

// Selftest: replay the stored solution of every level; title reports failures (0 = all good).
if (QS.get('selftest')) {
  const bad = [];
  LEVELS.forEach(lv => {
    const run = Engine.newRun(lv), list = Engine.spawnList(lv.seed, lv.drops + 8, lv.lo, lv.hi);
    for (const c of lv.moves || []) Engine.step(lv, run, c, list);
    if (!run.won) bad.push(lv.n);
  });
  document.title = 'selftest:' + bad.length + ':' + bad.join(',');
}

// ---------------------------------------------------------------- save
let save = { unlocked: 1, stars: {}, best: 0, muted: false, hammers: 1, tut: 0 };
try { const d = QS.get('fresh') ? null : JSON.parse(localStorage.getItem(SAVE_KEY)); if (d && d.unlocked) save = Object.assign(save, d); } catch (e) {}
function persist() { if (AUTO || DEMO) return; try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch (e) {} }

// ---------------------------------------------------------------- sound (synth, no files)
let ac = null;
function note(f, len, type, vol) {
  if (save.muted || adPlaying || AUTO || DEMO) return;
  try {
    ac = ac || new (window.AudioContext || window.webkitAudioContext)();
    if (ac.state === 'suspended') ac.resume();
    const o = ac.createOscillator(), a = ac.createGain(), now = ac.currentTime;
    o.type = type || 'sine'; o.frequency.setValueAtTime(f, now);
    a.gain.setValueAtTime(vol || 0.07, now); a.gain.exponentialRampToValueAtTime(0.001, now + len);
    o.connect(a); a.connect(ac.destination); o.start(now); o.stop(now + len);
  } catch (e) {}
}
const SCALE = [262, 294, 330, 392, 440, 523, 587, 659, 784, 880, 1047, 1175, 1319];
const chord = fs => fs.forEach((f, i) => setTimeout(() => note(f, 0.35, 'triangle', 0.06), i * 80));

// ---------------------------------------------------------------- canvas + layout
const cv = document.getElementById('c'), g = cv.getContext('2d');
let W = 0, H = 0, k = 1, ox = 0, oy = 0, land = false, dpr = 1, L = {};
function layout() {
  dpr = DEMO ? 1 : Math.min(window.devicePixelRatio || 1, 2);
  let W0 = window.innerWidth, H0 = window.innerHeight;
  if (DEMO) { W0 = +QS.get('w') || W0; H0 = +QS.get('h') || H0; cv.style.width = W0 + 'px'; cv.style.height = H0 + 'px'; }
  W = W0; H = H0; land = W > H * 1.15;
  cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
  if (QS.get('cover')) { k = 1; ox = oy = 0; L = { LW: W, LH: H }; return; }
  const LW = land ? 800 : 390, LH = land ? 440 : 800;
  k = Math.min(W / LW, H / LH); ox = (W - LW * k) / 2; oy = (H - LH * k) / 2;
  L = { LW, LH };
  if (land) {
    L.top = { x: 16, y: 16, w: LW - 32 };
    L.boardArea = { x: 16, y: 72, w: 432, h: 352 };
    L.side = { x: 472, w: LW - 488 };
    L.goal = { x: 472, y: 72, w: L.side.w, h: 88 };
    L.next = { x: 472, y: 176, w: L.side.w, h: 112 };
    L.tools = { x: 472, y: 304, w: L.side.w, h: 48 };
  } else {
    L.top = { x: 16, y: 16, w: LW - 32 };
    L.goal = { x: 16, y: 72, w: LW - 32, h: 88 };
    L.boardArea = { x: 16, y: 176, w: LW - 32, h: 448 };
    L.next = { x: 16, y: 640, w: LW - 32, h: 72 };
    L.tools = { x: 16, y: 728, w: LW - 32, h: 48 };
  }
}
function boardRect(lv) {
  const A = L.boardArea, gap = 6;
  const cell = Math.floor(Math.min((A.w - 16 - gap * (lv.cols - 1)) / lv.cols, (A.h - 16 - gap * (lv.rows - 1)) / lv.rows));
  const w = cell * lv.cols + gap * (lv.cols - 1) + 16, h = cell * lv.rows + gap * (lv.rows - 1) + 16;
  return { x: A.x + (A.w - w) / 2, y: A.y + (A.h - h), w, h, cell, gap };
}
const cellXY = (B, lv, i) => ({ x: B.x + 8 + (i % lv.cols) * (B.cell + B.gap), y: B.y + 8 + Math.floor(i / lv.cols) * (B.cell + B.gap) });
const inside = (p, r) => r && p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;

// ---------------------------------------------------------------- drawing helpers (THIET-KE.md)
function rr(x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
}
function card(r, radius) {
  g.save(); g.shadowColor = T.dark ? 'rgba(0,0,0,.4)' : 'rgba(0,0,0,.06)'; g.shadowBlur = 24 * k * dpr; g.shadowOffsetY = 2 * k * dpr;
  g.fillStyle = C.card; rr(r.x, r.y, r.w, r.h, radius || 16); g.fill(); g.restore();
}
function text(s, x, y, size, color, align, font, weight) {
  g.font = (weight || 400) + ' ' + size + 'px ' + (font || F.body);
  g.fillStyle = color || C.text; g.textAlign = align || 'left'; g.textBaseline = 'middle'; g.fillText(s, x, y);
}
function label(s, x, y, align, color) {
  if ('letterSpacing' in g) g.letterSpacing = '0.9px';
  text(String(s).toUpperCase(), x, y, 11, color || C.soft, align, F.mono);
  if ('letterSpacing' in g) g.letterSpacing = '0px';
}
function pill(r, primary, off) {
  rr(r.x, r.y, r.w, r.h, 999);
  if (primary) { g.fillStyle = off ? C.line : C.accent; g.fill(); }
  else { g.fillStyle = C.card; g.fill(); g.lineWidth = 1; g.strokeStyle = C.line; g.stroke(); }
}
function button(id, r, s, primary, off) {
  pill(r, primary, off);
  text(s, r.x + r.w / 2, r.y + r.h / 2 + 1, 15, primary ? '#FFFFFF' : C.text, 'center', F.body, 600);
  hits.push({ id, r, off });
}
// Small round icon button (back, sound).
function iconBtn(id, r, draw) {
  rr(r.x, r.y, r.w, r.h, 999); g.fillStyle = C.card; g.fill(); g.lineWidth = 1; g.strokeStyle = C.line; g.stroke();
  g.save(); g.strokeStyle = C.text; g.fillStyle = C.text; g.lineWidth = 2; g.lineCap = 'round'; g.lineJoin = 'round'; draw(r.x + r.w / 2, r.y + r.h / 2); g.restore();
  hits.push({ id, r });
}
const icBack = (x, y) => { g.beginPath(); g.moveTo(x + 3, y - 7); g.lineTo(x - 4, y); g.lineTo(x + 3, y + 7); g.stroke(); };
const icSound = (x, y) => {
  g.beginPath(); g.moveTo(x - 8, y - 3); g.lineTo(x - 4, y - 3); g.lineTo(x + 1, y - 8); g.lineTo(x + 1, y + 8); g.lineTo(x - 4, y + 3); g.lineTo(x - 8, y + 3); g.closePath(); g.fill();
  if (save.muted) { g.beginPath(); g.moveTo(x + 5, y - 4); g.lineTo(x + 11, y + 4); g.moveTo(x + 11, y - 4); g.lineTo(x + 5, y + 4); g.stroke(); }
  else { g.beginPath(); g.arc(x + 2, y, 6, -0.8, 0.8); g.stroke(); }
};
function star(x, y, r, on) {
  g.beginPath();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, d = i % 2 ? r * 0.45 : r; g[i ? 'lineTo' : 'moveTo'](x + Math.cos(a) * d, y + Math.sin(a) * d); }
  g.closePath(); g.fillStyle = on ? C.accent : C.line; g.fill();
}
// One tile: soft tinted square + the theme's item.
function tile(tv, x, y, s, alpha, scale) {
  if (!tv) return;
  g.save(); g.globalAlpha = alpha == null ? 1 : alpha;
  const sc = scale || 1, cx = x + s / 2, cy = y + s / 2, ss = s * sc;
  g.fillStyle = tint(T.tile[tv - 1], T.dark ? 0.22 : 0.16);
  rr(cx - ss / 2, cy - ss / 2, ss, ss, 8); g.fill();
  T.icon(g, tv, cx, cy, ss * 0.42);
  g.restore();
}
function tint(hex, a) { const n = parseInt(hex.slice(1), 16); return 'rgba(' + (n >> 16) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')'; }
function stone(x, y, s) {
  g.fillStyle = T.dark ? '#3A3632' : '#C9BFB2'; rr(x, y, s, s, 8); g.fill();
  g.strokeStyle = T.dark ? '#57514A' : '#A99D8E'; g.lineWidth = 2; g.beginPath();
  g.moveTo(x + s * 0.2, y + s * 0.35); g.lineTo(x + s * 0.5, y + s * 0.45); g.lineTo(x + s * 0.8, y + s * 0.3);
  g.moveTo(x + s * 0.3, y + s * 0.75); g.lineTo(x + s * 0.55, y + s * 0.62); g.stroke();
}
function ice(tv, x, y, s) {
  tile(tv, x, y, s, 0.55);
  g.fillStyle = 'rgba(170,215,240,.55)'; rr(x, y, s, s, 8); g.fill();
  g.strokeStyle = 'rgba(255,255,255,.9)'; g.lineWidth = 2; rr(x + 2, y + 2, s - 4, s - 4, 6); g.stroke();
  g.beginPath(); g.moveTo(x + s * 0.2, y + s * 0.3); g.lineTo(x + s * 0.35, y + s * 0.18); g.moveTo(x + s * 0.65, y + s * 0.85); g.lineTo(x + s * 0.82, y + s * 0.7); g.stroke();
}

// ---------------------------------------------------------------- game state
let scene = 'menu', page = 0, hits = [], hover = -1;
let P = null;          // current play: { lv, run, list, endless, anim, fx, ... }
let endCard = null, toast = null, fps = { n: 0, t: 0, now: 60, min: 60 };
window.__fps = fps;

function levelOf(n) { return LEVELS[n - 1]; }
function startLevel(n) {
  const lv = levelOf(n);
  P = { lv, n, run: Engine.newRun(lv), list: Engine.spawnList(lv.seed, lv.drops + 40, lv.lo, lv.hi), endless: false, anim: null, fx: [], pops: [], hammer: false, hint: -1, extra: false, used: 0 };
  P.hint = n === 1 && !save.tut ? Engine.bestColumn(lv, P.run, P.list) : -1;
  scene = 'play'; endCard = null; gameplay(true);
}
function startEndless() {
  const lv = { n: 0, cols: 6, rows: 8, drops: Infinity, goal: { type: 'none' }, seed: Date.now() & 0xffffff, lo: 1, hi: 3 };
  const R = Engine.rng(lv.seed);
  P = { lv, n: 0, run: Engine.newRun(lv), list: [], R, endless: true, anim: null, fx: [], pops: [], hammer: false, hint: -1, extra: false };
  refill(); scene = 'play'; endCard = null; gameplay(true);
}
// Endless: keep two tiles queued; the range climbs with the best tile on the board.
function refill() {
  while (P.list.length < P.run.i + 2) {
    const [lo, hi] = Engine.endlessRange(Math.max(P.run.best, ...P.run.b.v));
    P.list.push(lo + Math.floor(P.R() * (hi - lo + 1)));
  }
}

function dropAt(c) {
  if (!P || P.anim || P.run.over || adPlaying) return;
  if (Engine.landing(P.run.b, c) < 0) { note(150, 0.12, 'square', 0.03); return; }
  const before = Engine.copyRun(P.run);
  const res = Engine.step(P.lv, P.run, c, P.list);
  if (!res.ok) return;
  if (P.endless) refill();
  P.hint = -1;
  if (P.n === 1 && !save.tut) { save.tut = 1; persist(); }
  P.anim = { steps: res.steps, i: 0, t: 0, before };
  note(SCALE[Math.min(12, P.list[P.run.i - 1] || 1)] / 2, 0.08, 'triangle', 0.05);
}
function useHammer(i) {
  const b = P.run.b;
  if (b.v[i] <= 0 || b.k[i] !== 0) return;
  const before = Engine.copyRun(P.run);
  b.v[i] = 0;
  const fb = { v: b.v.slice(), k: b.k.slice() };
  const moves = Engine.gravity(b);
  P.fx.push(burst(i, '#8B7E6F'));
  P.anim = { steps: moves.length ? [{ type: 'fall', moves, before: fb }] : [], i: 0, t: 0, before };
  P.hammer = false; save.hammers--; persist();
  note(180, 0.15, 'square', 0.04);
}

// Animation: each engine step plays for a short time; the board shows the step's "before" state.
const DUR = { place: 150, merge: 150, fall: 120 };
function tickAnim(dt) {
  const A = P && P.anim;
  if (!A) return;
  if (A.i >= A.steps.length) { P.anim = null; afterMove(); return; }
  const s = A.steps[A.i];
  A.t += dt * SPEED / DUR[s.type];
  if (A.t >= 1) {
    if (s.type === 'merge') {
      P.fx.push(burst(s.to, T.tile[s.t - 1]));
      for (const h of s.hit) P.fx.push(burst(h, T.dark ? '#9A8F82' : '#B8AC9C'));
      P.pops.push({ i: s.to, t: 0, v: '+' + Math.pow(2, s.t) });
      note(SCALE[Math.min(12, s.t)], 0.18, 'triangle', 0.07);
      if (s.t >= 8) happy();
    }
    A.i++; A.t = 0;
  }
}
function afterMove() {
  const r = P.run;
  if (P.endless) { if (r.score > save.best) { save.best = r.score; persist(); } }
  if (!r.over) return;
  gameplay(false);
  const lv = P.lv;
  if (r.won) {
    const stars = r.i <= lv.par ? 3 : r.i <= lv.par + Math.ceil((lv.drops - lv.par) / 2) ? 2 : 1;
    save.stars[P.n] = Math.max(save.stars[P.n] || 0, stars);
    if (P.n + 1 > save.unlocked && P.n % 5 === 0) save.hammers = Math.min(5, save.hammers + 1);   // a free hammer every 5 new levels
    save.unlocked = Math.max(save.unlocked, Math.min(LEVELS.length, P.n + 1));
    persist();
    chord([523, 659, 784, 1047]);
    if (stars === 3) happy();
    setTimeout(() => { endCard = { won: true, stars }; }, 350 / SPEED);
  } else {
    note(196, 0.3, 'sine', 0.06);
    const full = !Engine.canDrop(r.b);
    setTimeout(() => { endCard = { won: false, full }; }, 350 / SPEED);
  }
}
// Rewarded continue: out of drops ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ +5 drops; board full ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ clear the top two rows and +3 drops.
function continueRun() {
  showAd('rewarded', ok => {
    if (!ok) { toast = { s: t('noAd'), t: 0 }; return; }
    const r = P.run, b = r.b;
    if (!Engine.canDrop(b) || endCard.full) { for (let i = 0; i < b.cols * 2; i++) if (b.k[i] === 0) b.v[i] = 0; Engine.gravity(b); }
    if (!P.endless) r.left += endCard.full ? 3 : 5;
    r.over = false; P.extra = true; endCard = null; gameplay(true);
  });
}
function burst(i, color) {
  const parts = [];
  for (let j = 0; j < 8; j++) { const a = j * 0.785 + Math.random() * 0.4; parts.push({ a, d: 0, v: 0.6 + Math.random() * 0.5 }); }
  return { i, color, t: 0, parts };
}

// ---------------------------------------------------------------- screens
function drawMenu() {
  const LW = L.LW, cx = LW / 2;
  const titleY = land ? 120 : 210;
  const words = VARIANT.title.split(' ');
  label(t('tag_' + VARIANT.rule), cx, titleY - 72, 'center');
  text(words[0], cx, titleY - 22, land ? 56 : 56, C.text, 'center', F.head);
  text(words.slice(1).join(' '), cx, titleY + 30, land ? 56 : 56, C.text, 'center', F.head);
  // The merge chain at a glance: 1 + 1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ 2 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¦ ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ 6.
  const n = 6, s = land ? 48 : 44, gap = 8, w = n * s + (n - 1) * gap, x0 = cx - w / 2, y0 = titleY + 88;
  for (let i = 0; i < n; i++) {
    const bob = Math.sin(now / 500 + i * 0.7) * 3;
    tile(i + 1, x0 + i * (s + gap), y0 + bob, s);
  }
  label(t('chainHint'), cx, y0 + s + 24, 'center');
  const bw = land ? 240 : 260, by = land ? 340 : 560;
  button('play', { x: cx - bw / 2, y: by, w: bw, h: 52 }, save.unlocked > 1 ? t('continueLv', save.unlocked) : t('play'), true);
  button('endless', { x: cx - bw / 2, y: by + 64, w: bw, h: 44 }, save.best ? t('endlessBest', fmt(save.best)) : t('endless'), false);
  if (!land) button('levels', { x: cx - bw / 2, y: by + 120, w: bw, h: 44 }, t('levels'), false);
  else button('levels', { x: cx + bw / 2 + 16, y: by + 64, w: 120, h: 44 }, t('levels'), false);
  iconBtn('mute', { x: LW - 56, y: 16, w: 40, h: 40 }, icSound);
}
function drawLevels() {
  const LW = L.LW, cx = LW / 2;
  iconBtn('back', { x: 16, y: 16, w: 40, h: 40 }, icBack);
  text(t('levels'), cx, 36, 28, C.text, 'center', F.head);
  const per = 20, colsN = land ? 10 : 4, s = land ? 64 : 76, gap = 12;
  const total = LEVELS.length, pages = Math.ceil(total / per);
  page = Math.max(0, Math.min(page, pages - 1));
  const rowsN = per / colsN, gw = colsN * s + (colsN - 1) * gap, x0 = cx - gw / 2, y0 = land ? 88 : 96;
  for (let j = 0; j < per; j++) {
    const n = page * per + j + 1;
    if (n > total) break;
    const x = x0 + (j % colsN) * (s + gap), y = y0 + Math.floor(j / colsN) * (s + 12 + gap);
    const open = n <= save.unlocked, r = { x, y, w: s, h: s + 12 };
    if (open) card(r, 16); else { rr(x, y, s, s + 12, 16); g.fillStyle = T.dark ? '#121212' : '#F3ECE2'; g.fill(); }
    text(String(n), x + s / 2, y + s / 2 - 4, 26, open ? C.text : C.soft, 'center', F.head);
    const st = save.stars[n] || 0;
    for (let q = 0; q < 3; q++) star(x + s / 2 + (q - 1) * 14, y + s - 4, 5, q < st);
    if (open) hits.push({ id: 'lv' + n, r });
  }
  const py = y0 + rowsN * (s + 12 + gap) + 8;
  if (pages > 1) {
    button('prev', { x: cx - 128, y: py, w: 112, h: 40 }, 'ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¹', false, page === 0);
    button('next', { x: cx + 16, y: py, w: 112, h: 40 }, 'ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Âº', false, page === pages - 1);
    label((page + 1) + ' / ' + pages, cx, py + 56, 'center');
  }
}
function goalText(lv) {
  const g2 = lv.goal;
  if (g2.type === 'reach') return t('goalReach');
  if (g2.type === 'make') return t('goalMake', g2.n);
  if (g2.type === 'stones') return t('goalStones', g2.n);
  if (g2.type === 'ice') return t('goalIce', g2.n);
  if (g2.type === 'score') return t('goalScore', fmt(g2.n));
  return t('goalEndless');
}
function drawPlay(dt) {
  const lv = P.lv, r = P.run, B = boardRect(lv);
  // Top bar: back ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· level ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· sound.
  iconBtn('quit', { x: L.top.x, y: L.top.y, w: 40, h: 40 }, icBack);
  label(P.endless ? t('endless') : t('levelN', P.n), L.top.x + L.top.w / 2, L.top.y + 20, 'center');
  iconBtn('mute', { x: L.top.x + L.top.w - 40, y: L.top.y, w: 40, h: 40 }, icSound);
  // Goal card: what to do, progress, drops left (the one number that matters).
  const G = L.goal;
  card(G);
  label(P.endless ? t('score') : t('goal'), G.x + 16, G.y + 20);
  const gt = goalText(lv);
  const hasIcon = lv.goal.type === 'reach' || lv.goal.type === 'make';
  text(gt, G.x + 16, G.y + 48, 15, C.text, 'left', F.body, 500);
  if (hasIcon) { g.font = '500 15px ' + F.body; const tw = g.measureText(gt).width; tile(lv.goal.type === 'reach' ? lv.goal.n : lv.goal.tier, G.x + 16 + tw + 8, G.y + 30, 36); }
  const prog = Engine.progress(lv, r);
  if (!P.endless) {
    rr(G.x + 16, G.y + 70, G.w - 120, 6, 3); g.fillStyle = C.line; g.fill();
    rr(G.x + 16, G.y + 70, Math.max(6, (G.w - 120) * prog), 6, 3); g.fillStyle = C.accent; g.fill();
    text(String(Math.max(0, r.left)), G.x + G.w - 24, G.y + 42, 40, r.left <= 3 ? C.accent : C.text, 'right', F.head);
    label(t('drops'), G.x + G.w - 24, G.y + 72, 'right');
  } else {
    text(fmt(r.score), G.x + G.w - 24, G.y + 42, 40, C.text, 'right', F.head);
    label(t('bestN', fmt(save.best)), G.x + G.w - 24, G.y + 72, 'right');
  }
  // Board.
  card(B, 16);
  const A = P.anim, step = A && A.steps[A.i];
  const base = step ? step.before : { v: r.b.v, k: r.b.k };
  const hide = new Set();
  if (step) {
    if (step.type === 'merge') step.from.forEach(i => hide.add(i));
    if (step.type === 'fall') step.moves.forEach(m => hide.add(m[0]));
  }
  for (let i = 0; i < lv.cols * lv.rows; i++) {
    const p = cellXY(B, lv, i);
    g.fillStyle = C.cell; rr(p.x, p.y, B.cell, B.cell, 8); g.fill();
  }
  // Column highlight + landing ghost under the pointer (desktop) or tutorial hand.
  const col = P.hint >= 0 ? P.hint : hover;
  if (col >= 0 && col < lv.cols && !A && !r.over && !P.hammer) {
    const lr = Engine.landing(r.b, col);
    if (lr >= 0) {
      const p = cellXY(B, lv, col);
      g.fillStyle = tint(C.accent, 0.08); rr(p.x, B.y + 8, B.cell, (lr + 1) * (B.cell + B.gap) - B.gap, 8); g.fill();
      const q = cellXY(B, lv, lr * lv.cols + col);
      tile(P.list[r.i], q.x, q.y, B.cell, 0.35);
    }
  }
  for (let i = 0; i < base.v.length; i++) {
    if (hide.has(i)) continue;
    const p = cellXY(B, lv, i);
    if (base.k[i] === 1) stone(p.x, p.y, B.cell);
    else if (base.k[i] === 2) ice(base.v[i], p.x, p.y, B.cell);
    else if (base.v[i]) {
      let sc = 1;
      for (const pp of P.pops) if (pp.i === i && pp.t < 0.25) sc = 1 + Math.sin(pp.t / 0.25 * Math.PI) * 0.12;
      if (step && step.type === 'merge' && i === step.to) { tile(step.before.v[i], p.x, p.y, B.cell); continue; }
      tile(base.v[i], p.x, p.y, B.cell, 1, sc);
    }
  }
  if (step) {
    const e = 1 - Math.pow(1 - Math.min(1, A.t), 3);
    if (step.type === 'place') {
      const q = cellXY(B, lv, step.to), y0 = B.y - B.cell;
      tile(step.t, q.x, y0 + (q.y - y0) * e, B.cell);
    } else if (step.type === 'merge') {
      const q = cellXY(B, lv, step.to);
      for (const i of step.from) { const p = cellXY(B, lv, i); tile(step.before.v[i], p.x + (q.x - p.x) * e, p.y + (q.y - p.y) * e, B.cell, 1 - e * 0.5, 1 - e * 0.3); }
    } else if (step.type === 'fall') {
      for (const [a, b2] of step.moves) { const p = cellXY(B, lv, a), q = cellXY(B, lv, b2); tile(step.before.v[a], p.x, p.y + (q.y - p.y) * e, B.cell); }
    }
  }
  // Effects.
  for (const f of P.fx) {
    f.t += dt / 450;
    const p = cellXY(B, lv, f.i), cx = p.x + B.cell / 2, cy = p.y + B.cell / 2;
    g.save(); g.globalAlpha = Math.max(0, 1 - f.t);
    for (const q of f.parts) { const d = f.t * B.cell * 0.9 * q.v; g.fillStyle = f.color; g.beginPath(); g.arc(cx + Math.cos(q.a) * d, cy + Math.sin(q.a) * d, Math.max(0, B.cell * 0.07 * (1 - f.t)), 0, 6.283); g.fill(); }
    g.restore();
  }
  P.fx = P.fx.filter(f => f.t < 1);
  for (const pp of P.pops) {
    pp.t += dt / 700;
    const p = cellXY(B, lv, pp.i);
    g.save(); g.globalAlpha = Math.max(0, 1 - pp.t);
    text(pp.v, p.x + B.cell / 2, p.y - pp.t * 28, 14, C.text, 'center', F.mono, 600);
    g.restore();
  }
  P.pops = P.pops.filter(p => p.t < 1);
  // Tutorial hand.
  if (P.hint >= 0 && !A) {
    const p = cellXY(B, lv, P.hint), hx = p.x + B.cell / 2, hy = B.y - 12 + Math.sin(now / 220) * 6;
    g.fillStyle = C.accent; g.beginPath(); g.moveTo(hx, hy + 12); g.lineTo(hx - 10, hy - 4); g.lineTo(hx + 10, hy - 4); g.closePath(); g.fill();
  }
  hits.push({ id: 'board', r: B });
  // Next tiles.
  const N = L.next;
  card(N);
  label(t('next'), N.x + 16, N.y + 20);
  const cur = P.list[r.i], nxt = P.list[r.i + 1];
  if (land) {
    if (cur) tile(cur, N.x + 16, N.y + 36, 64);
    if (nxt) tile(nxt, N.x + 96, N.y + 52, 44, 0.6);
    label(cur ? T.names[cur - 1] : '', N.x + N.w - 16, N.y + 20, 'right');
  } else {
    if (cur) tile(cur, N.x + N.w / 2 - 28, N.y + 8, 56);
    if (nxt) tile(nxt, N.x + N.w / 2 + 40, N.y + 20, 36, 0.6);
    label(cur ? T.names[cur - 1] : '', N.x + N.w - 16, N.y + 20, 'right');
  }
  // Tools: hammer (free once per level, more from a rewarded ad) and hint (rewarded).
  const TL = L.tools, hw = (TL.w - 16) / 2;
  const hl = save.hammers > 0 ? t('hammerN', save.hammers) : t('hammerAd');
  button('hammer', { x: TL.x, y: TL.y, w: hw, h: TL.h }, P.hammer ? t('pickTile') : hl, P.hammer, false);
  button('hint', { x: TL.x + hw + 16, y: TL.y, w: hw, h: TL.h }, t('hint'), false, P.endless);
  if (endCard) drawEnd();
}
function drawEnd() {
  g.fillStyle = T.dark ? 'rgba(0,0,0,.6)' : 'rgba(255,251,245,.75)'; g.fillRect(0, 0, L.LW, L.LH);
  const w = land ? 360 : 326, h = 300, x = (L.LW - w) / 2, y = (L.LH - h) / 2;
  card({ x, y, w, h }, 24);
  const cx = x + w / 2, r = P.run;
  if (endCard.won) {
    label(t('levelN', P.n), cx, y + 32, 'center');
    text(t('cleared'), cx, y + 76, 40, C.text, 'center', F.head);
    for (let q = 0; q < 3; q++) star(cx + (q - 1) * 44, y + 132, 16, q < endCard.stars);
    label(t('scoreN', fmt(r.score)), cx, y + 172, 'center');
    const last = P.n >= LEVELS.length;
    button(last ? 'endlessGo' : 'nextLv', { x: x + 24, y: y + 196, w: w - 48, h: 48 }, last ? t('endless') : t('nextLevel'), true);
    button('toLevels', { x: x + 24, y: y + 252, w: w - 48, h: 36 }, t('levels'), false);
  } else {
    label(P.endless ? t('endless') : t('levelN', P.n), cx, y + 32, 'center');
    text(endCard.full ? t('boardFull') : t('outOfDrops'), cx, y + 76, 36, C.text, 'center', F.head);
    label(P.endless ? t('scoreN', fmt(r.score)) + ' ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· ' + t('bestN', fmt(save.best)) : Math.round(Engine.progress(P.lv, r) * 100) + '% ' + t('done'), cx, y + 120, 'center');
    button('retry', { x: x + 24, y: y + 152, w: w - 48, h: 48 }, P.endless ? t('again') : t('retry'), true);
    button('more', { x: x + 24, y: y + 208, w: w - 48, h: 40 }, P.extra ? t('usedExtra') : (endCard.full ? t('clearRows') : t('moreDrops')), false, P.extra);
    button('toLevels', { x: x + 24, y: y + 256, w: w - 48, h: 32 }, P.endless ? t('menu') : t('levels'), false);
  }
}
function drawToast(dt) {
  if (!toast) return;
  toast.t += dt / 2000;
  if (toast.t > 1) { toast = null; return; }
  g.save(); g.globalAlpha = Math.min(1, (1 - toast.t) * 4);
  const w = 260, x = (L.LW - w) / 2, y = L.LH - 72;
  rr(x, y, w, 40, 999); g.fillStyle = T.dark ? '#F4EFE8' : '#1A1A1A'; g.fill();
  text(toast.s, x + w / 2, y + 21, 13, T.dark ? '#1A1A1A' : '#FFFFFF', 'center');
  g.restore();
}
const fmt = n => n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e4 ? (n / 1e3).toFixed(1) + 'K' : String(Math.floor(n));

// ---------------------------------------------------------------- cover art (?cover=1&w=&h=)
function drawCover() {
  // Cover mode uses real pixels (layout() sets k = 1), so sizes follow the image, not the phone grid.
  const W_ = L.LW, H_ = L.LH, u = Math.min(W_, H_), wide = W_ / H_ > 1.2, tall = H_ / W_ > 1.2;
  const pattern = [[3, 5, 2, 6], [1, 4, 7, 3], [2, 6, 8, 5], [4, 9, 6, 10]];
  const rowsN = wide || tall ? 4 : 3, s = wide ? H_ * 0.17 : tall ? W_ * 0.17 : u * 0.15, gap = s * 0.14;
  const gw = 4 * s + 3 * gap, gh = rowsN * s + (rowsN - 1) * gap;
  const bx = wide ? W_ * 0.71 - gw / 2 : W_ / 2 - gw / 2, by = wide ? H_ / 2 - gh / 2 : tall ? H_ * 0.36 : u * 0.44;
  card({ x: bx - gap * 1.6, y: by - gap * 1.6, w: gw + gap * 3.2, h: gh + gap * 3.2 }, s * 0.3);
  pattern.slice(0, rowsN).forEach((row, r) => row.forEach((v, c) => tile(v, bx + c * (s + gap), by + r * (s + gap), s)));
  const words = VARIANT.title.split(' '), fs = wide ? Math.min(H_ * 0.15, (bx - W_ * 0.07 - gap * 3) / 3.9) : tall ? W_ * 0.15 : u * 0.13;
  const tx = wide ? W_ * 0.07 : W_ / 2, al = wide ? 'left' : 'center', ty = wide ? H_ / 2 - fs * 0.75 : tall ? H_ * 0.13 : u * 0.14;
  text(words[0], tx, ty, fs, C.text, al, F.head);
  text(words.slice(1).join(' '), tx, ty + fs * 0.95, fs, C.text, al, F.head);
  if (!wide && !tall) return;
  const pw = u * 0.34, ph = u * 0.1, px = wide ? tx : tx - pw / 2, py = wide ? ty + fs * 2.1 : by + gh + u * 0.14;
  pill({ x: px, y: py, w: pw, h: ph }, true);
  text(t('play'), px + pw / 2, py + ph / 2 + 1, ph * 0.36, '#FFFFFF', 'center', F.body, 600);
}
// ---------------------------------------------------------------- loop
let now = 0, last = 0;
function frame(ts) {
  const dt = Math.min(50, last ? ts - last : 16); last = ts; now = ts;
  fps.n++; if (ts - fps.t >= 1000) { fps.now = fps.n * 1000 / (ts - fps.t); if (fps.t && ts > 3000) fps.min = Math.min(fps.min, fps.now); fps.n = 0; fps.t = ts; }
  if (!adPlaying) tickAnim(dt);
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.fillStyle = C.page; g.fillRect(0, 0, cv.width, cv.height);
  g.setTransform(k * dpr, 0, 0, k * dpr, ox * dpr, oy * dpr);
  hits = [];
  // One bad frame must never stop the loop: log it once and keep drawing.
  try {
    if (QS.get('cover')) drawCover();
    else if (scene === 'menu') drawMenu();
    else if (scene === 'levels') drawLevels();
    else if (scene === 'play') drawPlay(dt);
    drawToast(dt);
    if (AUTO) autoTick();
  } catch (e) { if (!frame.failed) { frame.failed = 1; console.error(e); } }
  requestAnimationFrame(frame);
}

// ---------------------------------------------------------------- input
function toLogical(e) { const b = cv.getBoundingClientRect(); return { x: ((e.clientX - b.left) - ox) / k, y: ((e.clientY - b.top) - oy) / k }; }
function colAt(p) {
  if (!P) return -1;
  const B = boardRect(P.lv);
  if (p.x < B.x || p.x > B.x + B.w || p.y < B.y - B.cell * 1.5 || p.y > B.y + B.h) return -1;
  return Math.max(0, Math.min(P.lv.cols - 1, Math.floor((p.x - B.x - 8 + B.gap / 2) / (B.cell + B.gap))));
}
function cellAt(p) {
  const B = boardRect(P.lv), c = colAt(p), r = Math.floor((p.y - B.y - 8 + B.gap / 2) / (B.cell + B.gap));
  return c < 0 || r < 0 || r >= P.lv.rows ? -1 : r * P.lv.cols + c;
}
cv.addEventListener('pointermove', e => { if (scene === 'play') hover = e.pointerType === 'mouse' ? colAt(toLogical(e)) : -1; });
cv.addEventListener('pointerdown', e => {
  if (adPlaying) return;
  const p = toLogical(e);
  if (ac && ac.state === 'suspended') ac.resume();
  // Board drops reach 1.5 cells above the board so a thumb near the top still counts.
  if (scene === 'play' && !endCard) {
    const B = boardRect(P.lv);
    if (p.x >= B.x && p.x <= B.x + B.w && p.y >= B.y - B.cell * 1.5 && p.y <= B.y + B.h) {
      if (P.hammer) { const i = cellAt(p); if (i >= 0) useHammer(i); }
      else dropAt(colAt(p));
      return;
    }
  }
  for (let i = hits.length - 1; i >= 0; i--) {
    const h = hits[i];
    if (h.id !== 'board' && inside(p, h.r)) { if (!h.off) act(h.id); return; }
  }
});
window.addEventListener('keydown', e => {
  if (scene !== 'play' || !P || endCard) return;
  const n = parseInt(e.key, 10);
  if (n >= 1 && n <= P.lv.cols) dropAt(n - 1);
  if (e.key === 'ArrowLeft') hover = Math.max(0, (hover < 0 ? 0 : hover) - 1);
  if (e.key === 'ArrowRight') hover = Math.min(P.lv.cols - 1, (hover < 0 ? 0 : hover) + 1);
  if ((e.key === ' ' || e.key === 'Enter' || e.key === 'ArrowDown') && hover >= 0) { e.preventDefault(); dropAt(hover); }
});
function act(id) {
  note(660, 0.05, 'sine', 0.04);
  if (id === 'mute') { save.muted = !save.muted; persist(); return; }
  if (id === 'play') { if (save.unlocked <= 1 && !save.tut) startLevel(1); else startLevel(save.unlocked); return; }
  if (id === 'levels' || id === 'toLevels') { gameplay(false); if (id === 'toLevels' && P && P.endless) { scene = 'menu'; endCard = null; return; } scene = 'levels'; page = Math.floor((save.unlocked - 1) / 20); endCard = null; return; }
  if (id === 'endless' || id === 'endlessGo') { startEndless(); return; }
  if (id === 'back') { scene = 'menu'; return; }
  if (id === 'quit') { gameplay(false); scene = P.endless ? 'menu' : 'levels'; return; }
  if (id === 'prev') { page--; return; }
  if (id === 'next') { page++; return; }
  if (id.startsWith('lv')) { startLevel(+id.slice(2)); return; }
  if (id === 'nextLv') { const n = P.n + 1; showAd('midgame', () => startLevel(n)); return; }
  if (id === 'retry') { const n = P.n, end = P.endless; showAd('midgame', () => end ? startEndless() : startLevel(n)); return; }
  if (id === 'more') { continueRun(); return; }
  if (id === 'hammer') {
    if (P.anim || P.run.over) return;
    if (P.hammer) { P.hammer = false; return; }
    if (save.hammers > 0) { P.hammer = true; return; }
    gameplay(false);
    showAd('rewarded', ok => { gameplay(true); if (ok) { save.hammers += 1; persist(); P.hammer = true; } else toast = { s: t('noAd'), t: 0 }; });
    return;
  }
  if (id === 'hint') {
    if (P.anim || P.run.over || P.endless) return;
    gameplay(false);
    showAd('rewarded', ok => {
      gameplay(true);
      if (!ok) { toast = { s: t('noAd'), t: 0 }; return; }
      const s = Engine.solve(P.lv, P.list, 32, P.run);
      P.hint = s.won ? s.moves[0] : Engine.bestColumn(P.lv, P.run, P.list);
    });
  }
}
document.addEventListener('visibilitychange', () => { if (scene === 'play' && !endCard) gameplay(!document.hidden); });
window.addEventListener('resize', layout);

// ---------------------------------------------------------------- autoplay (tests + trailer)
// Plays the stored solution of each level from ?level (default 1) for AUTO levels, then reports
// window.__auto = { done, won: [...], lost: [...] }.
const auto = { left: AUTO, wait: 0, won: [], lost: [], done: false, k: 0 };
window.__auto = auto;
function autoTick() {
  if (auto.done) return;
  if (scene !== 'play') { startLevel(+QS.get('level') || 1); auto.k = 0; return; }
  if (P.anim) return;
  if (endCard || P.run.over) {
    if ((auto.wait += 16 * SPEED) < 900) return;
    auto.wait = 0;
    (P.run.won ? auto.won : auto.lost).push(P.n);
    if (--auto.left <= 0 || P.n >= LEVELS.length) { auto.done = true; return; }
    startLevel(P.n + 1); auto.k = 0; return;
  }
  if ((auto.wait += 16 * SPEED) < 260) return;
  auto.wait = 0;
  const mv = P.lv.moves || [];
  dropAt(auto.k < mv.length ? mv[auto.k] : Engine.bestColumn(P.lv, P.run, P.list));
  auto.k++;
}

layout();
if (QS.get('endless')) startEndless();
else if (QS.get('level') && !AUTO) startLevel(Math.min(LEVELS.length, +QS.get('level')));
requestAnimationFrame(frame);
function onPortalReady() {}

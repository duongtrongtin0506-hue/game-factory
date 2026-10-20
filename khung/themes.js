// Five looks for the Drop & Merge frame. Every item is a flat shape drawn in code (no image files,
// nothing to license). icon(g, t, x, y, r): tier t (1..12) centred at x,y, r = about half a cell.
// Colours follow THIET-KE.md: paper or night page, white/ink cards, ONE accent per game; the items
// themselves carry their own colours so tiers read at a glance.
(function (root) {
  const TAU = Math.PI * 2;
  function circle(g, x, y, r, c) { g.fillStyle = c; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); }
  function ell(g, x, y, rx, ry, a, c) { g.fillStyle = c; g.beginPath(); g.ellipse(x, y, rx, ry, a || 0, 0, TAU); g.fill(); }
  function poly(g, x, y, r, n, rot, c) {
    g.fillStyle = c; g.beginPath();
    for (let i = 0; i < n; i++) { const a = rot + i * TAU / n; g[i ? 'lineTo' : 'moveTo'](x + Math.cos(a) * r, y + Math.sin(a) * r); }
    g.closePath(); g.fill();
  }
  function leaf(g, x, y, r, a, c) { g.save(); g.translate(x, y); g.rotate(a); ell(g, r, 0, r, r * 0.45, 0, c); g.restore(); }
  function shine(g, x, y, r) { ell(g, x - r * 0.32, y - r * 0.34, r * 0.2, r * 0.12, -0.6, 'rgba(255,255,255,.55)'); }
  const PAPER = { page: '#FFFBF5', card: '#FFFFFF', line: '#E8E0D5', text: '#1A1A1A', soft: '#8B7E6F', cell: '#F6F0E7' };
  const NIGHT = { page: '#0A0A0B', card: '#1A1A1A', line: '#2C2A27', text: '#F4EFE8', soft: '#9A8F82', cell: '#141414' };

  const fruit = Object.assign({}, PAPER, {
    accent: '#2B4A3B', dark: false,
    tile: ['#5B6CC4', '#C8243A', '#E5484D', '#7DBB3C', '#7B3F8C', '#D9363E', '#F28C28', '#F5A27A', '#B9C93A', '#F2B33D', '#E7B416', '#3F9F4F'],
    names: ['Blueberry', 'Cherry', 'Strawberry', 'Lime', 'Plum', 'Apple', 'Orange', 'Peach', 'Pear', 'Mango', 'Pineapple', 'Watermelon'],
    icon(g, t, x, y, r) {
      const c = this.tile[t - 1], G = '#3E7D3A';
      const s = r * (0.5 + Math.min(t, 12) * 0.035);
      if (t === 2) { g.strokeStyle = '#5A3A22'; g.lineWidth = r * 0.07; g.beginPath(); g.moveTo(x - s * 0.45, y + s * 0.1); g.quadraticCurveTo(x, y - s * 1.1, x + s * 0.2, y - s * 0.9); g.moveTo(x + s * 0.45, y + s * 0.1); g.quadraticCurveTo(x + s * 0.3, y - s * 0.6, x + s * 0.2, y - s * 0.9); g.stroke(); circle(g, x - s * 0.45, y + s * 0.35, s * 0.42, c); circle(g, x + s * 0.45, y + s * 0.35, s * 0.42, c); shine(g, x - s * 0.45, y + s * 0.35, s * 0.42); return; }
      if (t === 3) { g.fillStyle = c; g.beginPath(); g.moveTo(x, y + s); g.bezierCurveTo(x - s * 1.2, y + s * 0.1, x - s * 0.8, y - s * 0.8, x, y - s * 0.6); g.bezierCurveTo(x + s * 0.8, y - s * 0.8, x + s * 1.2, y + s * 0.1, x, y + s); g.fill(); for (let i = 0; i < 5; i++) circle(g, x + Math.cos(i * 1.3) * s * 0.4, y + Math.sin(i * 1.3) * s * 0.3 + s * 0.05, s * 0.05, '#FFE3A8'); leaf(g, x, y - s * 0.6, s * 0.35, -0.5, G); leaf(g, x, y - s * 0.6, s * 0.35, 3.64, G); return; }
      if (t === 9) { circle(g, x, y + s * 0.3, s * 0.72, c); circle(g, x, y - s * 0.3, s * 0.45, c); g.fillStyle = '#5A3A22'; g.fillRect(x - s * 0.04, y - s * 0.95, s * 0.08, s * 0.25); shine(g, x, y + s * 0.3, s * 0.72); return; }
      if (t === 11) { ell(g, x, y + s * 0.2, s * 0.6, s * 0.78, 0, c); g.strokeStyle = 'rgba(120,70,0,.35)'; g.lineWidth = s * 0.06; for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(x + i * s * 0.25 - s * 0.4, y - s * 0.4); g.lineTo(x + i * s * 0.25 + s * 0.4, y + s * 0.85); g.stroke(); } for (let i = -1; i <= 1; i++) leaf(g, x, y - s * 0.5, s * 0.5, -1.57 + i * 0.5, G); return; }
      if (t === 12) { g.fillStyle = '#2E7D3A'; g.beginPath(); g.arc(x, y - s * 0.15, s, 0, Math.PI); g.fill(); g.fillStyle = '#F25C5C'; g.beginPath(); g.arc(x, y - s * 0.15, s * 0.82, 0, Math.PI); g.fill(); for (let i = 0; i < 5; i++) ell(g, x + (i - 2) * s * 0.3, y + s * 0.2 + (i % 2) * s * 0.18, s * 0.05, s * 0.09, 0, '#2A1A14'); return; }
      circle(g, x, y, s, c);
      if (t === 7) for (let i = 0; i < 6; i++) circle(g, x + Math.cos(i) * s * 0.55, y + Math.sin(i) * s * 0.55, s * 0.05, 'rgba(255,255,255,.35)');
      if (t === 4) { g.strokeStyle = 'rgba(255,255,255,.45)'; g.lineWidth = s * 0.06; g.beginPath(); g.arc(x, y, s * 0.65, 0, TAU); g.stroke(); }
      if (t === 8) { g.strokeStyle = 'rgba(180,80,40,.35)'; g.lineWidth = s * 0.08; g.beginPath(); g.moveTo(x, y - s); g.quadraticCurveTo(x + s * 0.35, y, x, y + s); g.stroke(); }
      shine(g, x, y, s);
      if (t >= 5) { g.fillStyle = '#5A3A22'; g.fillRect(x - s * 0.04, y - s * 1.12, s * 0.08, s * 0.3); leaf(g, x + s * 0.05, y - s * 0.95, s * 0.32, -0.4, G); }
    }
  });

  const gems = Object.assign({}, NIGHT, {
    accent: '#FF3B30', dark: true,
    tile: ['#B9C2CC', '#9B6BD3', '#E8B04A', '#2FBF71', '#3D7BE0', '#E0435A', '#36C5D6', '#F07FB8', '#F2DA5C', '#7E5BEF', '#FF8A3D', '#FFFFFF'],
    names: ['Quartz', 'Amethyst', 'Topaz', 'Emerald', 'Sapphire', 'Ruby', 'Aquamarine', 'Rose Quartz', 'Citrine', 'Tanzanite', 'Fire Opal', 'Diamond'],
    icon(g, t, x, y, r) {
      const c = this.tile[t - 1], s = r * (0.55 + t * 0.03);
      const sides = [3, 4, 5, 6, 8, 4, 6, 5, 8, 7, 6, 10][t - 1];
      const rot = sides === 4 ? 0 : -Math.PI / 2;
      poly(g, x, y, s, sides, rot, c);
      poly(g, x, y - s * 0.08, s * 0.55, sides, rot, 'rgba(255,255,255,.28)');
      g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = s * 0.05; g.beginPath();
      for (let i = 0; i < sides; i++) { const a = rot + i * TAU / sides; g.moveTo(x + Math.cos(a) * s, y + Math.sin(a) * s); g.lineTo(x + Math.cos(a) * s * 0.55, y - s * 0.08 + Math.sin(a) * s * 0.55); }
      g.stroke();
      ell(g, x - s * 0.25, y - s * 0.35, s * 0.16, s * 0.08, -0.6, 'rgba(255,255,255,.7)');
      if (t === 12) for (let i = 0; i < 4; i++) { const a = i * 1.57 + 0.4; poly(g, x + Math.cos(a) * s * 1.05, y + Math.sin(a) * s * 1.05, s * 0.12, 4, 0.78, '#FFF6C8'); }
    }
  });

  const space = Object.assign({}, NIGHT, {
    accent: '#FF3B30', dark: true,
    tile: ['#8C8378', '#C9C4BA', '#7FD1E8', '#B08060', '#D2553A', '#3B82C4', '#E3B35C', '#D9925B', '#6FC3C9', '#FFD54A', '#FF6B4A', '#B48CFF'],
    names: ['Pebble', 'Moon', 'Comet', 'Dust World', 'Red World', 'Blue World', 'Ring World', 'Gas Giant', 'Ice Giant', 'Star', 'Red Giant', 'Galaxy'],
    icon(g, t, x, y, r) {
      const c = this.tile[t - 1], s = r * (0.45 + t * 0.04);
      if (t === 1) { poly(g, x, y, s * 0.9, 7, 0.3, c); circle(g, x + s * 0.2, y - s * 0.1, s * 0.15, 'rgba(0,0,0,.2)'); return; }
      if (t === 3) { g.fillStyle = 'rgba(127,209,232,.35)'; g.beginPath(); g.moveTo(x - s * 1.1, y - s * 0.6); g.lineTo(x + s * 0.1, y - s * 0.3); g.lineTo(x - s * 0.1, y + s * 0.3); g.closePath(); g.fill(); circle(g, x + s * 0.2, y + s * 0.15, s * 0.45, c); circle(g, x + s * 0.1, y + s * 0.05, s * 0.15, '#FFFFFF'); return; }
      if (t === 10 || t === 11) { for (let i = 0; i < 8; i++) { const a = i * TAU / 8; g.strokeStyle = c; g.lineWidth = s * 0.1; g.beginPath(); g.moveTo(x + Math.cos(a) * s * 0.85, y + Math.sin(a) * s * 0.85); g.lineTo(x + Math.cos(a) * s * 1.1, y + Math.sin(a) * s * 1.1); g.stroke(); } circle(g, x, y, s * 0.75, c); circle(g, x - s * 0.2, y - s * 0.2, s * 0.3, 'rgba(255,255,255,.45)'); return; }
      if (t === 12) { for (let arm = 0; arm < 3; arm++) for (let i = 0; i < 14; i++) { const a = arm * TAU / 3 + i * 0.32, d = i * s * 0.07; circle(g, x + Math.cos(a) * d, y + Math.sin(a) * d * 0.7, s * (0.16 - i * 0.008), i % 3 ? c : '#FFFFFF'); } circle(g, x, y, s * 0.22, '#FFF2C8'); return; }
      if (t === 7) { g.strokeStyle = '#F6E3B4'; g.lineWidth = s * 0.12; g.beginPath(); g.ellipse(x, y, s * 1.15, s * 0.32, -0.35, 0, TAU); g.stroke(); }
      circle(g, x, y, s * 0.72, c);
      if (t === 2 || t === 4) { circle(g, x - s * 0.25, y + s * 0.1, s * 0.14, 'rgba(0,0,0,.15)'); circle(g, x + s * 0.2, y - s * 0.25, s * 0.1, 'rgba(0,0,0,.15)'); }
      if (t === 6) { ell(g, x - s * 0.15, y - s * 0.1, s * 0.3, s * 0.2, 0.4, '#4BAA5A'); ell(g, x + s * 0.25, y + s * 0.3, s * 0.2, s * 0.12, -0.3, '#4BAA5A'); }
      if (t === 8 || t === 9) { g.save(); g.beginPath(); g.arc(x, y, s * 0.72, 0, TAU); g.clip(); for (let i = -2; i <= 2; i++) { g.fillStyle = i % 2 ? 'rgba(255,255,255,.18)' : 'rgba(0,0,0,.1)'; g.fillRect(x - s, y + i * s * 0.28 - s * 0.07, s * 2, s * 0.14); } g.restore(); }
      if (t === 7) { g.strokeStyle = '#F6E3B4'; g.lineWidth = s * 0.12; g.beginPath(); g.ellipse(x, y, s * 1.15, s * 0.32, -0.35, 0.15, Math.PI - 0.15); g.stroke(); }
      circle(g, x - s * 0.25, y - s * 0.25, s * 0.14, 'rgba(255,255,255,.35)');
    }
  });

  const food = Object.assign({}, PAPER, {
    accent: '#FF3B30', dark: false,
    tile: ['#7FA88A', '#F6B91E', '#D9B98A', '#4E6B52', '#F6C744', '#E8A14A', '#B8A48E', '#F28FA6', '#E8B04A', '#C9A27E', '#F07FA0', '#C8372D'],   // tints behind the items (items carry their own colours)
    names: ['Rice Ball', 'Egg', 'Dumpling', 'Maki', 'Omelette', 'Tempura', 'Bun', 'Mochi', 'Pizza', 'Cupcake', 'Cake', 'Bento'],
    icon(g, t, x, y, r) {
      const s = r * (0.68 + t * 0.022), ink = 'rgba(0,0,0,.12)';
      if (t === 1) { g.fillStyle = '#F7F4EE'; g.beginPath(); g.moveTo(x, y - s * 0.85); g.quadraticCurveTo(x + s * 1.05, y + s * 0.75, x, y + s * 0.75); g.quadraticCurveTo(x - s * 1.05, y + s * 0.75, x, y - s * 0.85); g.fill(); g.fillStyle = '#26332A'; g.fillRect(x - s * 0.35, y + s * 0.2, s * 0.7, s * 0.55); return; }
      if (t === 2) { ell(g, x, y, s * 0.9, s * 0.75, 0.2, '#FFFFFF'); g.strokeStyle = ink; g.lineWidth = s * 0.05; g.beginPath(); g.ellipse(x, y, s * 0.9, s * 0.75, 0.2, 0, TAU); g.stroke(); circle(g, x + s * 0.1, y, s * 0.36, '#F6B91E'); return; }
      if (t === 3) { g.fillStyle = '#F3E2C7'; g.beginPath(); g.arc(x, y + s * 0.3, s * 0.9, Math.PI, 0); g.closePath(); g.fill(); g.strokeStyle = 'rgba(160,120,70,.4)'; g.lineWidth = s * 0.06; for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(x + i * s * 0.25, y - s * 0.55); g.lineTo(x + i * s * 0.3, y - s * 0.2); g.stroke(); } return; }
      if (t === 4) { circle(g, x, y, s * 0.85, '#2F3B2F'); circle(g, x, y, s * 0.65, '#FBF8F2'); circle(g, x, y, s * 0.3, '#F07A55'); circle(g, x + s * 0.1, y - s * 0.05, s * 0.12, '#7BB661'); return; }
      if (t === 5) { g.fillStyle = '#F6C744'; g.beginPath(); g.roundRect ? g.roundRect(x - s * 0.9, y - s * 0.45, s * 1.8, s * 0.9, s * 0.2) : g.rect(x - s * 0.9, y - s * 0.45, s * 1.8, s * 0.9); g.fill(); g.strokeStyle = 'rgba(200,140,20,.45)'; g.lineWidth = s * 0.06; for (let i = -1; i <= 1; i++) { g.beginPath(); g.moveTo(x + i * s * 0.45, y - s * 0.45); g.lineTo(x + i * s * 0.45, y + s * 0.45); g.stroke(); } g.fillStyle = '#26332A'; g.fillRect(x - s * 0.15, y - s * 0.45, s * 0.3, s * 0.9); return; }
      if (t === 6) { ell(g, x, y, s * 0.95, s * 0.42, -0.6, '#E8A14A'); for (let i = -2; i <= 2; i++) circle(g, x + i * s * 0.3, y - i * s * 0.2, s * 0.14, '#F6C46E'); poly(g, x + s * 0.75, y - s * 0.55, s * 0.25, 3, -0.6, '#F07A55'); return; }
      if (t === 7) { ell(g, x, y + s * 0.1, s * 0.9, s * 0.7, 0, '#FFFFFF'); g.strokeStyle = ink; g.lineWidth = s * 0.05; g.beginPath(); g.ellipse(x, y + s * 0.1, s * 0.9, s * 0.7, 0, 0, TAU); g.stroke(); g.beginPath(); for (let i = 0; i < 5; i++) { g.moveTo(x, y - s * 0.35); g.lineTo(x + Math.cos(-1.57 + (i - 2) * 0.5) * s * 0.4, y - s * 0.35 + Math.sin(-1.57 + (i - 2) * 0.5) * -s * 0.25); } g.stroke(); return; }
      if (t === 8) { for (let i = 0; i < 3; i++) circle(g, x + (i - 1) * s * 0.55, y + (i === 1 ? -s * 0.15 : s * 0.15), s * 0.42, ['#F7B9C4', '#FFFFFF', '#B9DB9A'][i]); g.strokeStyle = '#8B5E3C'; g.lineWidth = s * 0.07; g.beginPath(); g.moveTo(x - s * 1.1, y + s * 0.35); g.lineTo(x + s * 1.1, y - s * 0.05); g.stroke(); return; }
      if (t === 9) { g.fillStyle = '#E8B04A'; g.beginPath(); g.moveTo(x, y + s * 0.9); g.lineTo(x - s * 0.85, y - s * 0.6); g.quadraticCurveTo(x, y - s * 1.0, x + s * 0.85, y - s * 0.6); g.closePath(); g.fill(); g.fillStyle = '#F6D36B'; g.beginPath(); g.moveTo(x, y + s * 0.7); g.lineTo(x - s * 0.65, y - s * 0.42); g.quadraticCurveTo(x, y - s * 0.75, x + s * 0.65, y - s * 0.42); g.closePath(); g.fill(); for (const [dx, dy] of [[-0.25, -0.3], [0.25, -0.25], [0, 0.15]]) circle(g, x + dx * s, y + dy * s, s * 0.14, '#C8372D'); return; }
      if (t === 10) { g.fillStyle = '#C9A27E'; g.beginPath(); g.moveTo(x - s * 0.6, y); g.lineTo(x + s * 0.6, y); g.lineTo(x + s * 0.45, y + s * 0.85); g.lineTo(x - s * 0.45, y + s * 0.85); g.closePath(); g.fill(); circle(g, x - s * 0.3, y - s * 0.05, s * 0.4, '#F5D0DA'); circle(g, x + s * 0.3, y - s * 0.05, s * 0.4, '#F5D0DA'); circle(g, x, y - s * 0.4, s * 0.42, '#F7DCE3'); circle(g, x, y - s * 0.85, s * 0.15, '#C8372D'); return; }
      if (t === 11) { g.fillStyle = '#FFFFFF'; g.fillRect(x - s * 0.85, y - s * 0.3, s * 1.7, s * 1.0); g.fillStyle = '#F5D0DA'; g.fillRect(x - s * 0.85, y - s * 0.3, s * 1.7, s * 0.3); g.fillStyle = '#F7DCE3'; g.fillRect(x - s * 0.85, y + s * 0.25, s * 1.7, s * 0.15); for (let i = -1; i <= 1; i++) circle(g, x + i * s * 0.5, y - s * 0.45, s * 0.17, '#C8372D'); return; }
      if (t === 12) { g.fillStyle = '#C8372D'; g.fillRect(x - s * 0.95, y - s * 0.7, s * 1.9, s * 1.4); g.fillStyle = '#FBF8F2'; g.fillRect(x - s * 0.82, y - s * 0.57, s * 0.8, s * 1.14); g.fillStyle = '#F6C744'; g.fillRect(x + s * 0.06, y - s * 0.57, s * 0.76, s * 0.52); g.fillStyle = '#7BB661'; g.fillRect(x + s * 0.06, y + s * 0.03, s * 0.76, s * 0.54); circle(g, x - s * 0.42, y, s * 0.18, '#C8372D'); return; }
    }
  });

  const animals = Object.assign({}, PAPER, {
    accent: '#2B4A3B', dark: false,
    tile: ['#F6D04D', '#B8B2AA', '#F2E9E1', '#F2A65A', '#C68B59', '#E8743B', '#F4F1EC', '#9AA6AE', '#F5A7B8', '#8B5E3C', '#E2A83C', '#5C8FD6'],
    names: ['Chick', 'Mouse', 'Bunny', 'Cat', 'Pup', 'Fox', 'Panda', 'Koala', 'Piglet', 'Bear', 'Lion', 'Whale'],
    icon(g, t, x, y, r) {
      const c = this.tile[t - 1], s = r * (0.55 + t * 0.03), eye = '#2A2420';
      const ear = [null, 'round', 'long', 'point', 'flop', 'point', 'round', 'big', 'tri', 'round', 'mane', null][t - 1];
      if (t === 12) { ell(g, x, y + s * 0.1, s * 0.95, s * 0.7, 0, c); ell(g, x + s * 0.2, y + s * 0.4, s * 0.6, s * 0.28, 0, '#DCE8F7'); poly(g, x - s * 1.0, y - s * 0.1, s * 0.35, 3, 0, c); circle(g, x + s * 0.45, y - s * 0.05, s * 0.09, eye); g.strokeStyle = '#7FB2EE'; g.lineWidth = s * 0.08; g.beginPath(); g.moveTo(x, y - s * 0.6); g.lineTo(x - s * 0.15, y - s * 0.95); g.moveTo(x, y - s * 0.6); g.lineTo(x + s * 0.15, y - s * 0.95); g.stroke(); return; }
      if (ear === 'mane') for (let i = 0; i < 12; i++) circle(g, x + Math.cos(i * 0.52) * s * 0.8, y + Math.sin(i * 0.52) * s * 0.8, s * 0.3, '#B5651D');
      const earC = t === 7 ? '#2A2420' : c;
      if (ear === 'round' || ear === 'big') { const er = ear === 'big' ? 0.4 : 0.27; circle(g, x - s * 0.62, y - s * 0.58, s * er, earC); circle(g, x + s * 0.62, y - s * 0.58, s * er, earC); }
      if (ear === 'long') { ell(g, x - s * 0.3, y - s * 0.95, s * 0.17, s * 0.5, -0.15, c); ell(g, x + s * 0.3, y - s * 0.95, s * 0.17, s * 0.5, 0.15, c); ell(g, x - s * 0.3, y - s * 0.95, s * 0.07, s * 0.35, -0.15, '#F5B8C4'); ell(g, x + s * 0.3, y - s * 0.95, s * 0.07, s * 0.35, 0.15, '#F5B8C4'); }
      if (ear === 'point' || ear === 'tri') { poly(g, x - s * 0.5, y - s * 0.6, s * 0.38, 3, -1.9, c); poly(g, x + s * 0.5, y - s * 0.6, s * 0.38, 3, -1.25, c); }
      if (ear === 'flop') { ell(g, x - s * 0.75, y - s * 0.1, s * 0.22, s * 0.45, 0.4, '#8B5E3C'); ell(g, x + s * 0.75, y - s * 0.1, s * 0.22, s * 0.45, -0.4, '#8B5E3C'); }
      circle(g, x, y, s * 0.82, c);
      if (t === 6) { g.fillStyle = '#FFFFFF'; g.beginPath(); g.moveTo(x - s * 0.8, y); g.quadraticCurveTo(x, y + s * 1.2, x + s * 0.8, y); g.quadraticCurveTo(x, y + s * 0.35, x - s * 0.8, y); g.fill(); }
      if (t === 7) { ell(g, x - s * 0.32, y - s * 0.05, s * 0.2, s * 0.26, 0.5, '#2A2420'); ell(g, x + s * 0.32, y - s * 0.05, s * 0.2, s * 0.26, -0.5, '#2A2420'); }
      const ey = y - s * 0.08, eo = s * 0.32, er = s * 0.09;
      circle(g, x - eo, ey, er, t === 7 ? '#FFFFFF' : eye); circle(g, x + eo, ey, er, t === 7 ? '#FFFFFF' : eye);
      if (t === 1) { poly(g, x, y + s * 0.2, s * 0.2, 3, Math.PI / 2, '#F28C28'); return; }
      if (t === 9) { ell(g, x, y + s * 0.3, s * 0.28, s * 0.2, 0, '#EF8BA0'); circle(g, x - s * 0.1, y + s * 0.3, s * 0.05, '#B4566B'); circle(g, x + s * 0.1, y + s * 0.3, s * 0.05, '#B4566B'); return; }
      if (t === 8) { ell(g, x, y + s * 0.22, s * 0.18, s * 0.25, 0, '#3A3A3A'); return; }
      if (t === 5 || t === 10 || t === 11) ell(g, x, y + s * 0.3, s * 0.35, s * 0.25, 0, t === 11 ? '#F3D08A' : '#E9D3B8');
      poly(g, x, y + s * 0.2, s * 0.1, 3, Math.PI / 2, '#3A2A24');
      if (t === 4 || t === 2) { g.strokeStyle = 'rgba(0,0,0,.35)'; g.lineWidth = s * 0.03; for (const d of [-1, 1]) { g.beginPath(); g.moveTo(x + d * s * 0.2, y + s * 0.25); g.lineTo(x + d * s * 0.75, y + s * 0.15); g.stroke(); } }
    }
  });

  root.THEMES = { fruit, gems, space, food, animals };
})(typeof window !== 'undefined' ? window : globalThis);

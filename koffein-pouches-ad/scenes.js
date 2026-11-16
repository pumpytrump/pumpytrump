/*
 * 20 s TikTok Shop ad: "Tunnelblick" caffeine pouches, 75 mg caffeine, 3-tin set.
 *   0.0 – 3.5  Afternoon slump at the desk            "Das 14-Uhr-Tief?"
 *   3.5 – 7.0  Tower of coffee cups, jittery          "Schon der 5. Kaffee?"
 *   7.0 – 11.0 Reveal: three tins with lightning      "75 mg Koffein pro Pouch"
 *  11.0 – 15.0 How to: under the lip, 10–15 min, wide awake
 *  15.0 – 18.0 0 % nicotine / tobacco / sugar, Made in Sweden
 *  18.0 – 20.0 CTA 14,99 € + caffeine notice
 */
const TINS = [
  { band: '#5ec7a4', band2: '#ff6b81', label: 'WATERMELON MINT' },
  { band: '#4a6fe0', band2: '#7b95ff', label: 'BLUEBERRY' },
  { band: '#e5484d', band2: '#ff9aa0', label: '' }
];
// Round pouch tin, centre (x, y), tilt = perspective squash of the lid (0.3..1)
function tin(x, y, s, k, rot = 0, sq = 0.55) {
  const c = TINS[k];
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  const R = 150, side = 60;
  // side band
  ctx.fillStyle = '#e9ecf1';
  ctx.beginPath(); ctx.ellipse(0, side, R, R * sq, 0, 0, Math.PI); ctx.lineTo(-R, 0); ctx.ellipse(0, 0, R, R * sq, 0, Math.PI, 0, true); ctx.closePath(); ctx.fill();
  const g = ctx.createLinearGradient(-R, 0, R, 0); g.addColorStop(0, c.band); g.addColorStop(1, c.band2);
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.ellipse(0, side * 0.55, R, R * sq, 0, 0, Math.PI); ctx.lineTo(-R, side * 0.3); ctx.ellipse(0, side * 0.3, R, R * sq, 0, Math.PI, 0, true); ctx.closePath(); ctx.fill();
  // lid
  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.ellipse(0, 0, R, R * sq, 0, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = c.band; ctx.lineWidth = 6;
  ctx.beginPath(); ctx.ellipse(0, 0, R * 0.86, R * sq * 0.86, 0, 0, Math.PI * 2); ctx.stroke();
  ctx.save(); ctx.scale(1, sq / 0.55);
  ctx.fillStyle = INK; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `900 40px ${FONT}`;
  ctx.fillText('TUNNEL', 0, -18); ctx.fillText('BLICK', 0, 22);
  ctx.font = `700 15px ${FONT}`; ctx.fillStyle = '#666';
  if (c.label) ctx.fillText(c.label, 0, -55);
  ctx.fillText('75 mg KOFFEIN', 0, 56);
  ctx.restore();
  ctx.restore();
}
function zap(x, y, t, s = 1) { // little lightning crackle
  ctx.strokeStyle = '#7fd3ff'; ctx.lineWidth = 4 * s; ctx.lineCap = 'round';
  for (let i = 0; i < 3; i++) {
    if (Math.sin(t * 23 + i * 7) < 0.2) continue;
    const a = i * 2.1 + Math.floor(t * 8);
    const pts = [[x, y]];
    for (let k = 1; k < 5; k++) pts.push([x + Math.cos(a) * k * 30 * s + (rnd(k + a) - .5) * 30 * s, y + Math.sin(a) * k * 30 * s + (rnd(k * 3 + a) - .5) * 30 * s]);
    line(pts);
  }
}
function desk() {
  ctx.fillStyle = '#8b6a4c'; ctx.fillRect(80, 1300, 920, 34);
  ctx.fillStyle = '#6f533b'; ctx.fillRect(120, 1334, 30, 300); ctx.fillRect(930, 1334, 30, 300);
}
function laptop(x, y, glow) {
  ctx.fillStyle = '#2b2f36';
  ctx.beginPath(); ctx.moveTo(x - 150, y); ctx.lineTo(x - 130, y - 210); ctx.lineTo(x + 130, y - 210); ctx.lineTo(x + 150, y); ctx.closePath(); ctx.fill();
  ctx.fillStyle = glow ? '#cfe9ff' : '#5b6575';
  ctx.beginPath(); ctx.moveTo(x - 130, y - 12); ctx.lineTo(x - 114, y - 196); ctx.lineTo(x + 114, y - 196); ctx.lineTo(x + 130, y - 12); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#3a3f48'; rr(x - 190, y - 6, 380, 18, 8); ctx.fill();
}
function cup(x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = '#f2ece2';
  ctx.beginPath(); ctx.moveTo(-50, -140); ctx.lineTo(50, -140); ctx.lineTo(38, 0); ctx.lineTo(-38, 0); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#8a5a3c'; ctx.fillRect(-46, -95, 92, 40);
  ctx.fillStyle = '#3b2a20'; rr(-56, -160, 112, 24, 8); ctx.fill();
  ctx.restore();
}
function officeBg(dim) {
  bg(dim ? '#d9d6cf' : '#eef1f5');
  ctx.fillStyle = dim ? '#c7c3ba' : '#dfe4ea'; ctx.fillRect(0, 1334, W, H - 1334);
  // wall clock 14:00
  ctx.save(); ctx.translate(560, 720);
  ctx.fillStyle = '#fff'; ctx.strokeStyle = INK; ctx.lineWidth = 10;
  ctx.beginPath(); ctx.arc(0, 0, 90, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.lineCap = 'round'; line([[0, 0], [0, -62]]); line([[0, 0], [Math.sin(Math.PI / 3) * 42, -Math.cos(Math.PI / 3) * 42]]);
  ctx.restore();
}

function scene1(t) { // afternoon slump
  officeBg(true);
  desk(); laptop(640, 1300, false);
  const nod = Math.max(0, Math.sin(t * 2.2)) * 0.25;
  stick({ x: 260, y: 1180, rot: nod, pose: { lUA: 0.9, lLA: 1.3, rUA: 0.9, rLA: 1.4, lUL: 1.4, lLL: 0.1, rUL: 1.5, rLL: 0 }, eyes: 'closed', mouth: 'flat' });
  ctx.font = `900 54px ${FONT}`; ctx.textAlign = 'center'; ctx.fillStyle = INK;
  for (let i = 0; i < 3; i++) { const ph = (t * 0.6 + i / 3) % 1; ctx.globalAlpha = Math.sin(ph * Math.PI); ctx.fillText('Z', 330 + ph * 90, 880 - ph * 180); }
  ctx.globalAlpha = 1;
  caption('Das 14-Uhr-Tief?', 420, 100, 0.15, t);
}
function scene2(t) { // coffee tower
  const lt = t - 3.5;
  officeBg(false);
  desk(); laptop(640, 1300, true);
  const n = Math.min(5, 1 + Math.floor(lt / 0.45));
  for (let i = 0; i < n; i++) {
    const wob = Math.sin(t * 8) * i * 4;
    cup(860 + wob, 1300 - i * 140, 0.95);
  }
  const jit = Math.sin(t * 70) * 6;
  stick({ x: 260 + jit, y: 1180, pose: { lUA: 0.9, lLA: 1.3, rUA: 1.3, rLA: 1.9, lUL: 1.4, lLL: 0.1, rUL: 1.5, rLL: 0 }, eyes: 'wide', mouth: 'flat', hair: 'spiky', seed: Math.floor(t * 10) });
  caption('Schon der', 360, 80, 3.6, t, { color: INK, stroke: '#fff' });
  caption(`${n}. KAFFEE?`, 480, 120, 3.7, t, { color: '#8a5a3c', stroke: '#fff' });
}
function scene3(t) { // reveal
  const lt = t - 7;
  const g = ctx.createRadialGradient(W / 2, 1050, 50, W / 2, 1050, 1200);
  g.addColorStop(0, '#ffffff'); g.addColorStop(1, '#c9d2e0');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  rays(W / 2, 1050, t, 'rgba(255,255,255,0.5)');
  const p = outBack(prog(lt, 0.1, 0.6));
  if (p > 0) {
    tin(300, 820 + Math.sin(t * 2) * 15, 1.15 * p, 2, -0.35, 0.6);
    tin(790, 960 + Math.cos(t * 2) * 15, 1.25 * p, 1, 0.35, 0.6);
    tin(500, 1260 + Math.sin(t * 2 + 1) * 15, 1.7 * p, 0, -0.2, 0.6);
    zap(500, 1260, t, 2); zap(790, 960, t + 1, 1.4); zap(300, 820, t + 2, 1.3);
  }
  caption('Die Lösung:', 300, 84, 7.1, t, { color: INK, stroke: '#fff' });
  caption('Koffein-Pouches', 420, 84, 7.4, t, { box: PINK, color: '#fff' });
  caption('75 mg Koffein pro Pouch', 1560, 56, 8.0, t, { box: INK, color: '#fff' });
}
function scene4(t) { // how to + tunnel vision
  const lt = t - 11;
  officeBg(false);
  desk(); laptop(640, 1300, true);
  const inMouth = lt > 1.0;
  const focus = ease(prog(lt, 2.2, 2.8));
  const type = focus > 0 ? Math.sin(t * 40) * 0.12 : 0;
  const pose = !inMouth
    ? { lUA: 0.9, lLA: 1.3, rUA: lerp(1.2, 2.5, ease(prog(lt, 0.2, 0.8))), rLA: lerp(1.6, -2.6, ease(prog(lt, 0.2, 0.8))), lUL: 1.4, lLL: 0.1, rUL: 1.5, rLL: 0 }
    : { lUA: 1.2 + type, lLA: 1.6 - type, rUA: 1.25 - type, rLA: 1.65 + type, lUL: 1.4, lLL: 0.1, rUL: 1.5, rLL: 0 };
  const st = stick({ x: 260, y: 1180, pose, eyes: focus > 0.5 ? 'wide' : 'open', mouth: inMouth ? 'smile' : 'flat' });
  if (!inMouth) { // pouch in hand
    const [hx, hy] = st.rHand;
    ctx.fillStyle = '#fff'; ctx.strokeStyle = '#ccd'; ctx.lineWidth = 3;
    rr(hx - 22, hy - 30, 44, 26, 8); ctx.fill(); ctx.stroke();
  }
  if (focus > 0) { // tunnel vision vignette around head→laptop
    const rg = ctx.createRadialGradient(470, 1090, 140, 470, 1090, 700);
    rg.addColorStop(0, 'rgba(0,0,0,0)'); rg.addColorStop(1, `rgba(10,10,25,${0.85 * focus})`);
    ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = `rgba(127,211,255,${0.8 * focus})`; ctx.lineWidth = 6;
    for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 + t * 0.5; const r0 = 420 + ((t * 600 + i * 90) % 400); line([[470 + Math.cos(a) * r0, 1090 + Math.sin(a) * r0], [470 + Math.cos(a) * (r0 + 90), 1090 + Math.sin(a) * (r0 + 90)]]); }
  }
  const steps = [['1  Unter die Lippe', 11.05, 12.3], ['2  10–15 Minuten', 12.3, 13.3], ['3  Hellwach!', 13.3, 15]];
  for (const [txt, a, b] of steps) if (t >= a && t < b) caption(txt, 400, 84, a, t, { box: a > 13 ? PINK : '#fff', color: a > 13 ? '#fff' : INK });
}
function scene5(t) { // facts
  const lt = t - 15;
  bg('#f4f6fb');
  [0, 1, 2].forEach(k => { const p = outBack(prog(lt, k * 0.15, k * 0.15 + 0.4)); if (p > 0) tin(200 + k * 340, 720, 0.95 * p, k, 0, 0.5); });
  ['0 % Nikotin', '0 % Tabak', '0 % Zucker', 'Made in Sweden'].forEach((f, i) =>
    chip(f, W / 2, 1000 + i * 105, outBack(prog(lt, 0.4 + i * 0.35, 0.75 + i * 0.35)), [PINK, '#2a7fff', '#16a34a', '#f2b705'][i]));
  caption('3 Sorten im Set', 330, 92, 15.05, t, { color: INK, stroke: '#fff' });
}
function scene6(t) { // CTA
  const lt = t - 18;
  const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#0d0d12'); g.addColorStop(1, '#1b2a4a');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  caption('3er-SET · 75 mg KOFFEIN', 250, 60, 18.0, t, { color: CYAN });
  price(W / 2, 470, outBack(prog(lt, 0.15, 0.5)), '14,99 €', null, 0);
  const p = outBack(prog(lt, 0.05, 0.45));
  if (p > 0) { tin(270, 780, 0.9 * p, 2, -0.3); tin(810, 780, 0.9 * p, 1, 0.3); tin(540, 900, 1.15 * p, 0, 0); zap(540, 900, t, 1.6); }
  shopButton(1230, lt);
  ctx.globalAlpha = prog(lt, 0.6, 0.9);
  ctx.fillStyle = '#c9cfdb'; ctx.font = `700 30px ${FONT}`; ctx.textAlign = 'center';
  ctx.fillText('Erhöhter Koffeingehalt. Nicht für Kinder und', W / 2, 1400);
  ctx.fillText('Schwangere oder Stillende empfohlen.', W / 2, 1442);
  ctx.globalAlpha = 1;
}
startAd([[3.5, scene1], [7, scene2], [11, scene3], [15, scene4], [18, scene5], [20, scene6]], [3.5, 7, 11, 15, 18]);

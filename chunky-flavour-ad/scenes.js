/*
 * 20 s TikTok Shop ad: Chunky Flavour 150 g flavour powder (Vanilla), vegan.
 * Claims only from the pack: 3 g Chunky vs. 50 g sugar → 7 kcal vs. 200 kcal.
 *   0.0 – 3.5  16 sugar cubes drop into a coffee        "16 Zuckerwürfel?!"
 *   3.5 – 7.0  Sugar mountain = 200 kcal                 "50 g Zucker = 200 kcal"
 *   7.0 – 11.0 Reveal jar + 3 g vs 50 g comparison
 *  11.0 – 15.0 Scoop into quark, then into coffee/matcha, happy
 *  15.0 – 18.0 Fact chips
 *  18.0 – 20.0 CTA ab 13,29 €
 */
const ORANGE = '#f6a54a', ORANGE2 = '#ffd39a';
function chunkyJar(x, y, s, rot = 0) { // base centre
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.beginPath(); ctx.ellipse(0, 4, 230, 26, 0, 0, Math.PI * 2); ctx.fill();
  const g = ctx.createLinearGradient(-220, 0, 220, 0); g.addColorStop(0, '#e98f2c'); g.addColorStop(0.4, ORANGE2); g.addColorStop(1, '#e08525');
  ctx.fillStyle = g; rr(-220, -250, 440, 250, 26); ctx.fill();
  // ice-cream scoop doodles
  ctx.fillStyle = 'rgba(255,240,210,0.7)';
  for (const [dx, dy] of [[-170, -215], [150, -220], [175, -60]]) { ctx.beginPath(); ctx.arc(dx, dy, 30, 0, Math.PI * 2); ctx.fill(); }
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.font = `900 64px ${FONT}`; ctx.fillText('CHUNKY', -190, -160);
  ctx.font = `900 50px ${FONT}`; ctx.fillText('FLAVOUR', -190, -105);
  ctx.font = `700 26px ${FONT}`; ctx.fillText('Vanilla', -190, -60);
  // vegan badge
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(140, -120, 44, 0, Math.PI * 2); ctx.stroke();
  ctx.font = `900 34px ${FONT}`; ctx.textAlign = 'center'; ctx.fillText('V', 140, -130);
  ctx.font = `900 15px ${FONT}`; ctx.fillText('VEGAN', 140, -100);
  // lid
  const lg = ctx.createLinearGradient(-230, 0, 230, 0); lg.addColorStop(0, '#dcdde1'); lg.addColorStop(0.4, '#ffffff'); lg.addColorStop(1, '#cfd1d6');
  ctx.fillStyle = lg; rr(-232, -330, 464, 90, 26); ctx.fill();
  ctx.restore();
}
function cube(x, y, s, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = '#ffffff'; ctx.strokeStyle = '#d9dde4'; ctx.lineWidth = 3;
  rr(-28, -28, 56, 56, 8); ctx.fill(); ctx.stroke();
  ctx.fillStyle = 'rgba(200,205,215,0.6)'; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.arc(-15 + rnd(i) * 30, -15 + rnd(i + 3) * 30, 3, 0, Math.PI * 2); ctx.fill(); }
  ctx.restore();
}
function mug(x, y, s, fill = '#7a4a2a', body = '#e5484d') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.strokeStyle = body; ctx.lineWidth = 22; ctx.beginPath(); ctx.arc(130, -110, 50, -1.2, 1.2); ctx.stroke();
  ctx.fillStyle = body; rr(-130, -220, 260, 220, 28); ctx.fill();
  ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(0, -218, 118, 22, 0, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function scoop(x, y, rot, full) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = '#f4f4f4'; rr(-6, 0, 12, 120, 6); ctx.fill();
  ctx.beginPath(); ctx.arc(0, -10, 34, 0, Math.PI); ctx.closePath(); ctx.fill();
  if (full) { ctx.fillStyle = '#efe0bf'; ctx.beginPath(); ctx.arc(0, -10, 30, Math.PI, 0); ctx.fill(); }
  ctx.restore();
}
function quarkBowl(x, y, s, col) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(0, -110, 190, 44, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#ffffff'; ctx.strokeStyle = '#e1e4ea'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.moveTo(-205, -110); ctx.quadraticCurveTo(-190, 10, 0, 12); ctx.quadraticCurveTo(190, 10, 205, -110); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.restore();
}
function sky() {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#58b9e0'); g.addColorStop(1, '#bfe6f5');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#e5333a'; ctx.beginPath(); ctx.ellipse(W / 2, 1400, 700, 120, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillRect(0, 1400, W, H - 1400);
}

function scene1(t) {
  bg('#f3efe8');
  ctx.fillStyle = '#c8a77f'; ctx.fillRect(0, 1350, W, H - 1350);
  mug(650, 1350, 1.1);
  const n = Math.min(16, Math.floor(prog(t, 0.2, 2.6) * 16 + (t > 0.2 ? 1 : 0)));
  for (let i = 0; i < n; i++) { // cubes falling into the mug
    const t0 = 0.2 + i * 0.15, p = prog(t, t0, t0 + 0.35);
    if (p < 1) cube(640 + (rnd(i) - .5) * 160, lerp(700, 1100, p * p), 1, p * 3);
  }
  const st = stick({ x: 240, y: 1120, pose: { lUA: -0.25, lLA: -0.1, rUA: 2.0, rLA: 2.0, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: 'open', mouth: 'flat' });
  cube(st.rHand[0] + 20, st.rHand[1] - 20, 1, Math.sin(t * 5));
  ctx.save(); ctx.translate(820, 760); ctx.rotate(0.08);
  ctx.fillStyle = INK; rr(-120, -60, 240, 120, 30); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.font = `900 80px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(`${n}x`, 0, 4);
  ctx.restore();
  caption('16 Zuckerwürfel', 380, 92, 0.15, t);
  caption('für EINEN Kaffee?!', 500, 76, 1.2, t, { color: '#ffd23f' });
}
function scene2(t) {
  const lt = t - 3.5;
  bg('#fbe9e9');
  ctx.fillStyle = '#e8cfcf'; ctx.fillRect(0, 1450, W, H - 1450);
  const p = ease(prog(lt, 0.1, 1.0));
  // sugar mountain
  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.moveTo(300 - 300 * p, 1450); ctx.quadraticCurveTo(600, 1450 - 900 * p, 900 + 120 * p, 1450); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(200,205,215,0.7)';
  for (let i = 0; i < 60; i++) { const x = 200 + rnd(i) * 700, yy = 1450 - rnd(i + 7) * 500 * p; ctx.beginPath(); ctx.arc(x, yy, 4, 0, Math.PI * 2); ctx.fill(); }
  const tp = outBack(prog(lt, 0.9, 1.3));
  if (tp > 0) {
    ctx.save(); ctx.translate(620, 880); ctx.scale(tp, tp); ctx.rotate(-0.05 + Math.sin(t * 18) * 0.02);
    ctx.fillStyle = '#ff2a2a'; rr(-230, -70, 460, 140, 30); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = `900 76px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('200 kcal', 0, 4);
    ctx.restore();
  }
  stick({ x: 170, y: 1340, s: 0.9, pose: { lUA: -0.25, lLA: -0.1, rUA: 2.4, rLA: 2.9, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: 'wide', mouth: 'o', hair: 'spiky', seed: Math.floor(t * 6) });
  caption('50 g Zucker', 360, 100, 3.6, t, { color: INK, stroke: '#fff' });
  caption('nur für die Süße?', 490, 70, 4.1, t, { color: '#fff', stroke: INK });
}
function scene3(t) {
  const lt = t - 7;
  sky();
  rays(W / 2, 1100, t, 'rgba(255,255,255,0.2)');
  const p = outBack(prog(lt, 0.1, 0.55));
  if (p > 0) { chunkyJar(W / 2, 1420 + (1 - p) * 200, 1.4 * p, Math.sin(t * 1.6) * 0.03); sparkles(W / 2, 1150, 420, 330, lt, p); }
  // comparison card
  const cp = outBack(prog(lt, 1.0, 1.4));
  if (cp > 0) {
    ctx.save(); ctx.translate(W / 2, 760); ctx.scale(cp, cp);
    ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,.2)'; ctx.shadowBlur = 30; rr(-400, -110, 800, 220, 40); ctx.fill(); ctx.shadowBlur = 0;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = '#e08525'; ctx.font = `900 68px ${FONT}`; ctx.fillText('3 g', -220, -30);
    ctx.font = `900 40px ${FONT}`; ctx.fillText('7 kcal', -220, 45);
    ctx.fillStyle = INK; ctx.font = `900 46px ${FONT}`; ctx.fillText('statt', 0, 0);
    ctx.fillStyle = '#9aa0aa'; ctx.font = `900 68px ${FONT}`; ctx.fillText('50 g', 220, -30);
    ctx.font = `900 40px ${FONT}`; ctx.fillText('200 kcal', 220, 45);
    ctx.strokeStyle = '#ff2a2a'; ctx.lineWidth = 8; line([[120, 60], [320, -60]]);
    ctx.restore();
  }
  caption('Die Lösung:', 300, 84, 7.1, t, { color: '#fff', stroke: INK });
  caption('Chunky Flavour', 420, 92, 7.4, t, { box: '#e5333a', color: '#fff' });
}
function scene4(t) {
  const lt = t - 11;
  sky();
  const quarkCol = lt > 1.0 ? '#fbf1d6' : '#fafaf7';
  quarkBowl(560, 1430, 0.95, quarkCol);
  mug(880, 1430, 0.65, lt > 2.6 ? '#c9a07a' : '#7a4a2a', '#ffffff');
  let pose, sp = null;
  if (lt < 1.2) {
    const d = ease(prog(lt, 0.1, 0.9));
    pose = { lUA: -0.25, lLA: -0.1, rUA: lerp(1.2, 1.5, d), rLA: lerp(1.5, 1.75, d) }; sp = [lerp(0.6, 2.4, d), d < 0.8];
    if (d > 0.7) { ctx.fillStyle = '#efe0bf'; for (let i = 0; i < 12; i++) { const ph = (lt * 3 + i / 12) % 1; ctx.beginPath(); ctx.arc(520 + Math.sin(i) * 20, 1170 + ph * 140, 4, 0, Math.PI * 2); ctx.fill(); } }
  } else if (lt < 2.5) {
    const s = Math.sin(t * 12); pose = { lUA: -0.25, lLA: -0.1, rUA: 1.42 + s * 0.12, rLA: 1.72 - s * 0.12 }; sp = [2.6, false];
  } else {
    pose = { lUA: -0.25, lLA: -0.1, rUA: 2.4, rLA: 3.0 }; sp = null;
  }
  const happy = lt > 2.6;
  const st = stick({ x: 230, y: 1200, pose: { ...pose, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: happy ? 'happy' : 'open', mouth: happy ? 'grin' : 'smile' });
  if (sp) scoop(st.rHand[0], st.rHand[1], sp[0], sp[1]);
  if (happy) {
    for (let i = 0; i < 4; i++) { const ph = (lt * 0.7 + i / 4) % 1; ctx.globalAlpha = Math.sin(ph * Math.PI); heart(180 + i * 80, 820 - ph * 220, 0.8); }
    ctx.globalAlpha = 1;
  }
  if (lt < 1.3) caption('3 g in 300 g Quark', 400, 84, 11.05, t, { color: '#fff', stroke: INK });
  else if (lt < 2.5) caption('Umrühren', 400, 96, 12.3, t, { color: '#fff', stroke: INK });
  else caption('Auch in Kaffee\n& Matcha', 400, 84, 13.5, t, { box: '#e5333a', color: '#fff' });
}
function scene5(t) {
  const lt = t - 15;
  bg('#fff6ec');
  chunkyJar(W / 2, 1000, 1.0 * outBack(prog(lt, 0, 0.4)));
  ['Vegan', 'Weniger Zucker', 'Für Quark, Joghurt & Desserts', 'Sorten wählbar'].forEach((f, i) =>
    chip(f, W / 2, 1150 + i * 100, outBack(prog(lt, 0.4 + i * 0.35, 0.75 + i * 0.35)), ['#16a34a', '#e5333a', ORANGE, '#2a7fff'][i]));
  caption('Weniger Zucker.', 300, 90, 15.05, t, { color: INK, stroke: '#fff' });
  caption('Mehr Geschmack.', 410, 90, 15.3, t, { color: '#e5333a', stroke: '#fff' });
}
function scene6(t) {
  const lt = t - 18;
  const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#1b0f3a'); g.addColorStop(0.6, '#5a1546'); g.addColorStop(1, '#c7472b');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  caption('BLACK FRIDAY', 230, 88, 18.0, t, { box: '#fff', color: '#1b0f3a' });
  const pp = outBack(prog(lt, 0.15, 0.5));
  if (pp > 0) {
    ctx.save(); ctx.translate(W / 2, 400); ctx.scale(pp, pp);
    ctx.fillStyle = '#fff'; ctx.font = `900 48px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('ab', -300, 30);
    ctx.restore();
  }
  price(W / 2 + 60, 420, pp, '13,29 €', null, 0);
  chunkyJar(W / 2, 1080, 0.95 * outBack(prog(lt, 0.05, 0.4)));
  shopButton(1260, lt);
  caption('Tippe auf den Warenkorb', 1430, 50, 18.9, t, { color: '#fff', stroke: '#000' });
}
startAd([[3.5, scene1], [7, scene2], [11, scene3], [15, scene4], [18, scene5], [20, scene6]], [3.5, 7, 11, 15, 18]);

/*
 * 20 s TikTok Shop ad: "Geschmacksbombe" flavour powder 200 g (Erdbeer-Wunder, Bananensplit).
 *   0.0 – 3.5  Bland low-fat quark, bored              "Magerquark schmeckt nach NICHTS?"
 *   3.5 – 7.0  Cake = too many calories               "Und Süßes = Kalorienbombe?"
 *   7.0 – 11.0 Reveal: two jars + comic burst         "nur 4,5 kcal pro Portion"
 *  11.0 – 15.0 Spoon in, stir, turns pink, tastes great
 *  15.0 – 18.0 Uses + ~66 portions
 *  18.0 – 20.0 CTA 12,12 € statt 12,76 €
 */
const FLAV = {
  erdbeer: { a: '#e5484d', b: '#ff8f8f', name: 'Erdbeer-\nWunder', txt: '#fff' },
  banane: { a: '#f7e8b5', b: '#fff6d8', name: 'Bananen-\nsplit', txt: INK }
};
function jar(x, y, s, k, rot = 0) { // base centre
  const f = FLAV[k];
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.beginPath(); ctx.ellipse(0, 4, 170, 24, 0, 0, Math.PI * 2); ctx.fill();
  // body
  const g = ctx.createLinearGradient(-160, 0, 160, 0); g.addColorStop(0, '#dfe1e5'); g.addColorStop(0.35, '#ffffff'); g.addColorStop(1, '#cfd2d8');
  ctx.fillStyle = g; rr(-160, -300, 320, 300, 30); ctx.fill();
  // label
  const lg = ctx.createLinearGradient(-160, 0, 160, 0); lg.addColorStop(0, f.a); lg.addColorStop(1, f.b);
  ctx.fillStyle = lg; ctx.fillRect(-160, -240, 320, 200);
  // comic burst on label
  ctx.fillStyle = '#ffb21f';
  ctx.beginPath(); for (let i = 0; i < 16; i++) { const r = i % 2 ? 40 : 75, a = i * Math.PI / 8; ctx.lineTo(-90 + Math.cos(a) * r, -190 + Math.sin(a) * r); } ctx.fill();
  ctx.fillStyle = INK; ctx.font = `900 46px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.save(); ctx.translate(10, -150); ctx.rotate(-0.08);
  ctx.lineWidth = 8; ctx.strokeStyle = '#fff';
  ctx.strokeText('GESCHMACKS', 0, -25); ctx.fillText('GESCHMACKS', 0, -25);
  ctx.strokeText('BOMBE', -40, 22); ctx.fillText('BOMBE', -40, 22);
  ctx.restore();
  ctx.fillStyle = INK; rr(40, -110, 115, 62, 30); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.font = `900 19px ${FONT}`;
  f.name.split('\n').forEach((l, i) => ctx.fillText(l, 97, -90 + i * 22));
  // lid
  ctx.fillStyle = '#f4f5f7'; rr(-170, -340, 340, 60, 20); ctx.fill();
  ctx.fillStyle = '#26262b'; ctx.beginPath(); ctx.ellipse(0, -340, 150, 26, 0, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function bowlOf(x, y, s, col, swirl = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(0, -95, 175, 42, 0, 0, Math.PI * 2); ctx.fill();
  if (swirl) { ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 8; ctx.beginPath(); ctx.ellipse(0, -95, 90, 20, swirl, 0.3, 5); ctx.stroke(); }
  ctx.fillStyle = '#d8c8b2';
  ctx.beginPath(); ctx.moveTo(-195, -95); ctx.quadraticCurveTo(-180, 10, 0, 12); ctx.quadraticCurveTo(180, 10, 195, -95); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.08)'; for (let i = 0; i < 30; i++) { ctx.beginPath(); ctx.arc(-150 + rnd(i) * 300, -70 + rnd(i + 5) * 60, 3, 0, Math.PI * 2); ctx.fill(); }
  ctx.restore();
}
function spoon(x, y, rot, fill) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = '#b9bec6'; rr(-8, 0, 16, 200, 8); ctx.fill();
  ctx.beginPath(); ctx.ellipse(0, -10, 34, 48, 0, 0, Math.PI * 2); ctx.fill();
  if (fill) { ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(0, -14, 26, 36, 0, 0, Math.PI * 2); ctx.fill(); }
  ctx.restore();
}
function kitchen(dim) {
  bg(dim ? '#d5d1ca' : '#fbf3ea');
  ctx.fillStyle = dim ? '#a89f92' : '#e2c9a8'; ctx.fillRect(0, 1350, W, 40);
  ctx.fillStyle = dim ? '#8f877c' : '#cfb18c'; ctx.fillRect(0, 1390, W, H - 1390);
}

function scene1(t) {
  kitchen(true);
  bowlOf(560, 1350, 0.9, '#f6f6f2');
  const dip = Math.sin(t * 2.5);
  const st = stick({ x: 300, y: 1120, pose: { lUA: -0.25, lLA: -0.1, rUA: 1.9 + dip * 0.3, rLA: 2.6 + dip * 0.3, ...{ lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 } }, eyes: 'open', mouth: 'flat', brows: false });
  spoon(st.rHand[0] + 10, st.rHand[1] - 30, 0.3, '#f6f6f2');
  caption('Magerquark schmeckt', 380, 70, 0.15, t);
  caption('nach NICHTS?', 490, 96, 0.6, t, { color: '#cfd3da' });
}
function scene2(t) {
  const lt = t - 3.5;
  kitchen(false);
  // cake slice
  ctx.save(); ctx.translate(700, 1350);
  ctx.fillStyle = '#6b3d26'; ctx.beginPath(); ctx.moveTo(-200, 0); ctx.lineTo(200, 0); ctx.lineTo(200, -200); ctx.lineTo(-200, -120); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#fff2e2'; ctx.fillRect(-200, -80, 400, 24);
  ctx.fillStyle = '#4a2817'; ctx.beginPath(); ctx.moveTo(-200, -120); ctx.lineTo(200, -200); ctx.lineTo(200, -230); ctx.lineTo(-200, -150); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#e5484d'; ctx.beginPath(); ctx.arc(120, -235, 28, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  // calorie warning tag
  const p = outBack(prog(lt, 0.5, 0.9));
  if (p > 0) {
    ctx.save(); ctx.translate(720, 870); ctx.scale(p, p); ctx.rotate(0.08 + Math.sin(t * 20) * 0.03);
    ctx.fillStyle = '#ff2a2a'; rr(-190, -70, 380, 140, 30); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = `900 72px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('KCAL !!', 0, 4);
    ctx.restore();
  }
  stick({ x: 260, y: 1120, pose: { lUA: -0.25, lLA: -0.1, rUA: 1.5, rLA: 1.5, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: 'open', mouth: 'frown', brows: true });
  caption('Und Süßes =', 360, 80, 3.6, t, { color: INK, stroke: '#fff' });
  caption('KALORIENBOMBE?', 480, 96, 4.0, t, { color: '#ff2a2a', stroke: '#fff' });
}
function scene3(t) {
  const lt = t - 7;
  bg('#fff3e6');
  rays(W / 2, 1080, t, 'rgba(255,170,60,0.25)');
  const bp = outBack(prog(lt, 0.05, 0.4));
  if (bp > 0) { // comic burst
    ctx.save(); ctx.translate(W / 2, 1080); ctx.scale(bp, bp); ctx.rotate(t * 0.3);
    ctx.fillStyle = '#ffd23f';
    ctx.beginPath(); for (let i = 0; i < 24; i++) { const r = i % 2 ? 280 : 420, a = i * Math.PI / 12; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } ctx.fill();
    ctx.restore();
  }
  const p = outBack(prog(lt, 0.25, 0.7));
  if (p > 0) {
    jar(360, 1300 + Math.sin(t * 2) * 10, 1.05 * p, 'erdbeer', -0.08);
    jar(740, 1330 + Math.cos(t * 2) * 10, 1.05 * p, 'banane', 0.08);
    sparkles(W / 2, 1080, 470, 380, lt, p);
  }
  caption('Die Lösung:', 300, 84, 7.1, t, { color: INK, stroke: '#fff' });
  caption('Flavour-Pulver', 420, 90, 7.4, t, { box: PINK, color: '#fff' });
  caption('nur 4,5 kcal pro Portion', 1560, 58, 8.0, t, { box: INK, color: '#fff' });
}
function scene4(t) {
  const lt = t - 11;
  kitchen(false);
  const pinkAmt = ease(prog(lt, 1.2, 2.2));
  const col = `rgb(${Math.round(lerp(246, 244, pinkAmt))},${Math.round(lerp(246, 160, pinkAmt))},${Math.round(lerp(242, 175, pinkAmt))})`;
  bowlOf(540, 1350, 0.9, col, lt > 1.2 && lt < 2.4 ? t * 6 : 0);
  jar(860, 1350, 0.6, 'erdbeer');
  let pose, spoonFill = null, spoonRot = 0.3;
  if (lt < 1.2) { // spoon of powder into bowl
    const d = ease(prog(lt, 0.1, 0.9));
    pose = { lUA: -0.25, lLA: -0.1, rUA: lerp(1.2, 1.55, d), rLA: lerp(1.6, 1.85, d) };
    spoonFill = d < 0.8 ? '#ff7a8a' : null; spoonRot = lerp(0.6, 2.4, d);
  } else if (lt < 2.4) { // stirring
    const s = Math.sin(t * 12);
    pose = { lUA: -0.25, lLA: -0.1, rUA: 1.45 + s * 0.12, rLA: 1.75 - s * 0.12 }; spoonRot = 2.6;
  } else { // tasting
    pose = { lUA: -0.25, lLA: -0.1, rUA: 1.9, rLA: 2.9 }; spoonFill = '#f4a0af'; spoonRot = 0.2;
  }
  const happy = lt > 2.6;
  const st = stick({ x: 250, y: 1120, pose: { ...pose, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: happy ? 'happy' : 'open', mouth: happy ? 'grin' : 'smile' });
  spoon(st.rHand[0], st.rHand[1], spoonRot, spoonFill);
  if (happy) {
    for (let i = 0; i < 4; i++) { const ph = (lt * 0.7 + i / 4) % 1; ctx.globalAlpha = Math.sin(ph * Math.PI); heart(200 + i * 80, 820 - ph * 220, 0.8); }
    ctx.globalAlpha = 1;
  }
  if (lt < 1.2) caption('1 Löffel rein', 400, 96, 11.05, t, { color: INK, stroke: '#fff' });
  else if (lt < 2.5) caption('Umrühren', 400, 96, 12.2, t, { color: INK, stroke: '#fff' });
  else caption('Mmmh!', 400, 140, 13.5, t, { box: PINK, color: '#fff' });
}
function scene5(t) {
  const lt = t - 15;
  bg('#f4f6fb');
  const p = outBack(prog(lt, 0.05, 0.45));
  if (p > 0) { jar(330, 1000, 0.8 * p, 'erdbeer', -0.05); jar(750, 1000, 0.8 * p, 'banane', 0.05); }
  ['Für Quark & Joghurt', 'Für Shakes & Desserts', 'Zum Backen', 'ca. 66 Portionen'].forEach((f, i) =>
    chip(f, W / 2, 1150 + i * 100, outBack(prog(lt, 0.4 + i * 0.35, 0.75 + i * 0.35)), [PINK, '#2a7fff', '#f2b705', '#16a34a'][i]));
  caption('Mehr Geschmack.', 300, 90, 15.05, t, { color: INK, stroke: '#fff' });
  caption('Jeden Tag.', 410, 90, 15.3, t, { color: '#e5484d', stroke: '#fff' });
}
function scene6(t) {
  const lt = t - 18;
  const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#1b0f3a'); g.addColorStop(0.6, '#5a1546'); g.addColorStop(1, '#c7472b');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  caption('BLACK FRIDAY', 230, 88, 18.0, t, { box: '#fff', color: '#1b0f3a' });
  price(W / 2, 470, outBack(prog(lt, 0.15, 0.5)), '12,12 €', '12,76 €', 0);
  const p = outBack(prog(lt, 0.05, 0.45));
  if (p > 0) { jar(330, 1080, 0.85 * p, 'erdbeer', -0.06); jar(750, 1080, 0.85 * p, 'banane', 0.06); }
  shopButton(1250, lt);
  caption('Tippe auf den Warenkorb', 1420, 50, 18.9, t, { color: '#fff', stroke: '#000' });
}
startAd([[3.5, scene1], [7, scene2], [11, scene3], [15, scene4], [18, scene5], [20, scene6]], [3.5, 7, 11, 15, 18]);

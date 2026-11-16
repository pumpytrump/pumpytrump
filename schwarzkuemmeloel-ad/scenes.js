/*
 * 20 s TikTok Shop ad: organic black seed oil 500 ml, cold-pressed, unfiltered.
 * No health claims on purpose – only product facts from the listing.
 *   0.0 – 3.5  Confused at a shelf of anonymous bottles  "Schwarzkümmelöl ist nicht gleich Schwarzkümmelöl"
 *   3.5 – 7.0  Red flags: refined, additives, stored forever
 *   7.0 – 11.0 Reveal: dark glass bottle                 "Bio · kaltgepresst · ungefiltert"
 *  11.0 – 15.0 Seeds → press → bottle; used on a salad
 *  15.0 – 18.0 Fact chips
 *  18.0 – 20.0 CTA 31,25 € statt 32,89 €, free shipping
 */
function bottle(x, y, s, rot = 0) { // base centre
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.ellipse(0, 4, 120, 18, 0, 0, Math.PI * 2); ctx.fill();
  const g = ctx.createLinearGradient(-100, 0, 100, 0); g.addColorStop(0, '#0d0d0f'); g.addColorStop(0.3, '#3a3a40'); g.addColorStop(0.5, '#141416'); g.addColorStop(1, '#050506');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.moveTo(-100, 0); ctx.lineTo(-100, -520); ctx.quadraticCurveTo(-100, -600, -38, -650); ctx.lineTo(-38, -760);
  ctx.lineTo(38, -760); ctx.lineTo(38, -650); ctx.quadraticCurveTo(100, -600, 100, -520); ctx.lineTo(100, 0); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#d99a1c'; ctx.fillRect(-34, -740, 68, 70); // oil visible in the neck
  ctx.fillStyle = '#111'; rr(-44, -830, 88, 92, 8); ctx.fill();
  ctx.strokeStyle = '#2a2a2a'; ctx.lineWidth = 3; for (let i = -36; i <= 36; i += 9) line([[i, -826], [i, -742]]);
  // label
  ctx.fillStyle = '#f4f4f2'; rr(-82, -470, 164, 160, 14); ctx.fill();
  ctx.fillStyle = '#111'; ctx.fillRect(-82, -320, 164, 290);
  // nigella flower
  for (let i = 0; i < 10; i++) {
    const a = i * Math.PI / 5;
    ctx.fillStyle = i % 2 ? '#2f6fd6' : '#1d4fa8';
    ctx.beginPath(); ctx.ellipse(Math.cos(a) * 30, -330 + Math.sin(a) * 22, 30, 12, a, 0, Math.PI * 2); ctx.fill();
  }
  ctx.fillStyle = '#e8d24a'; ctx.beginPath(); ctx.arc(0, -330, 10, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `900 24px ${FONT}`;
  ctx.fillText('SCHWARZ', 0, -265); ctx.fillText('KÜMMEL', 0, -237); ctx.font = `700 22px ${FONT}`; ctx.fillText('ÖL', 0, -210);
  ctx.fillStyle = '#fff'; ctx.fillRect(-56, -186, 112, 18);
  ctx.fillStyle = '#111'; ctx.font = `900 13px ${FONT}`; ctx.fillText('UNGEFILTERT', 0, -176);
  ctx.fillStyle = '#ccc'; ctx.font = `700 12px ${FONT}`; ctx.fillText('KALTGEPRESST', 0, -150);
  // bio hexagon
  ctx.strokeStyle = '#5bb33a'; ctx.lineWidth = 4;
  ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; ctx.lineTo(Math.cos(a) * 28, -95 + Math.sin(a) * 22); } ctx.closePath(); ctx.stroke();
  ctx.fillStyle = '#fff'; ctx.font = `900 18px ${FONT}`; ctx.fillText('BIO', 0, -94);
  ctx.fillStyle = '#aaa'; ctx.font = `700 12px ${FONT}`; ctx.fillText('500 ml', 0, -48);
  ctx.restore();
}
function plainBottle(x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const g = ctx.createLinearGradient(-70, 0, 70, 0); g.addColorStop(0, '#d9dbdf'); g.addColorStop(0.4, '#ffffff'); g.addColorStop(1, '#c7cad0');
  ctx.fillStyle = g; rr(-70, -260, 140, 260, 30); ctx.fill();
  rr(-40, -300, 80, 50, 10); ctx.fill();
  ctx.fillStyle = '#e9eaee'; rr(-46, -330, 92, 36, 8); ctx.fill();
  ctx.restore();
}
function seeds(x, y, n, spread) {
  ctx.fillStyle = '#141414';
  for (let i = 0; i < n; i++) {
    const a = rnd(i) * Math.PI, r = rnd(i + 50) * spread;
    ctx.beginPath(); ctx.ellipse(x + Math.cos(a) * r * 1.6 - spread * 0, y - Math.sin(a) * r * 0.5, 9, 5, rnd(i + 9) * 3, 0, Math.PI * 2); ctx.fill();
  }
}
function shop(dim) {
  bg(dim ? '#d8d6d2' : '#f2efe9');
  ctx.fillStyle = '#b7b1a6';
  for (const y of [900, 1200, 1500]) ctx.fillRect(60, y, 960, 22);
  ctx.fillStyle = '#8f877c'; ctx.fillRect(40, 600, 24, 1000); ctx.fillRect(1016, 600, 24, 1000);
}

function scene1(t) {
  shop(false);
  for (let r = 0; r < 3; r++) for (let i = 0; i < 6; i++) plainBottle(150 + i * 155, [900, 1200, 1500][r], 0.72);
  const look = Math.sin(t * 2.5);
  stick({ x: 540, y: 1560, s: 1.1, pose: { lUA: -0.25, lLA: -0.1, rUA: 2.2, rLA: 3.0, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: 'open', mouth: 'flat', headFill: '#fff' });
  ctx.fillStyle = PINK; ctx.font = `900 110px ${FONT}`; ctx.textAlign = 'center';
  ctx.fillText('?', 420 + look * 20, 1080); ctx.fillText('?', 680 - look * 20, 1040);
  caption('Schwarzkümmelöl ist', 330, 72, 0.15, t);
  caption('nicht gleich', 440, 72, 0.5, t, { color: '#f2b705' });
  caption('Schwarzkümmelöl', 550, 72, 0.8, t);
}
function scene2(t) {
  const lt = t - 3.5;
  bg('#ececec');
  plainBottle(330, 1450, 2.2);
  ['Raffiniert?', 'Künstliche Zusätze?', 'Ewig gelagert?'].forEach((f, i) => {
    const p = outBack(prog(lt, 0.3 + i * 0.7, 0.65 + i * 0.7));
    if (p <= 0) return;
    ctx.save(); ctx.translate(720, 820 + i * 170); ctx.scale(p, p);
    ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,.15)'; ctx.shadowBlur = 20; rr(-300, -60, 600, 120, 60); ctx.fill(); ctx.shadowBlur = 0;
    ctx.fillStyle = '#e5242b'; ctx.beginPath(); ctx.arc(-240, 0, 38, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 9; ctx.lineCap = 'round'; line([[-255, -15], [-225, 15]]); line([[-225, -15], [-255, 15]]);
    ctx.fillStyle = INK; ctx.font = `900 40px ${FONT}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(f, -180, 2);
    ctx.restore();
  });
  caption('Nein danke.', 1640, 80, 5.8, t, { box: INK, color: '#fff' });
  caption('Achte darauf:', 400, 92, 3.6, t, { color: INK, stroke: '#fff' });
}
function scene3(t) {
  const lt = t - 7;
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#ffffff'); g.addColorStop(1, '#e9eef6');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  rays(W / 2, 1150, t, 'rgba(47,111,214,0.08)');
  const p = outBack(prog(lt, 0.1, 0.55));
  if (p > 0) { bottle(W / 2, 1600 + (1 - p) * 300, 1.15, Math.sin(t * 1.5) * 0.03); sparkles(W / 2, 1200, 330, 380, lt, p, '#2f6fd6'); }
  caption('Bio-Schwarzkümmelöl', 300, 76, 7.1, t, { box: INK, color: '#fff' });
  caption('kaltgepresst & ungefiltert', 420, 58, 7.6, t, { box: '#fff', color: INK });
}
function scene4(t) {
  const lt = t - 11;
  bg('#f6f1e7');
  ctx.fillStyle = '#d9c7a6'; ctx.fillRect(0, 1450, W, H - 1450);
  if (lt < 2.6) {
    // seeds → press → drops into bottle
    seeds(260, 1440, 120, 110);
    const press = Math.abs(Math.sin(lt * 4)) * 40;
    ctx.fillStyle = '#7a7f87'; rr(420, 820 + press, 300, 50, 10); ctx.fill();
    ctx.fillStyle = '#5b6068'; rr(550, 640, 40, 190 + press, 8); ctx.fill();
    ctx.fillStyle = '#7a7f87'; rr(420, 1000, 300, 50, 10); ctx.fill();
    seeds(570, 990, 40, 70);
    ctx.fillStyle = '#d99a1c';
    for (let i = 0; i < 3; i++) { const ph = (lt * 1.8 + i / 3) % 1; ctx.beginPath(); ctx.ellipse(570, 1060 + ph * 200, 10, 15, 0, 0, Math.PI * 2); ctx.fill(); }
    bottle(570, 1440, 0.4);
  } else { // drizzling on a salad, happy
    ctx.fillStyle = '#e9e4dc'; ctx.beginPath(); ctx.ellipse(640, 1400, 220, 60, 0, 0, Math.PI * 2); ctx.fill();
    for (let i = 0; i < 18; i++) { ctx.fillStyle = i % 3 ? '#5fae3e' : '#e5484d'; ctx.beginPath(); ctx.ellipse(500 + rnd(i) * 280, 1370 + rnd(i + 3) * 30, 34, 16, rnd(i + 7) * 3, 0, Math.PI * 2); ctx.fill(); }
    const st = stick({ x: 250, y: 1200, pose: { lUA: -0.25, lLA: -0.1, rUA: 2.0, rLA: 1.75, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 }, eyes: 'happy', mouth: 'grin' });
    bottle(st.rHand[0] + 40, st.rHand[1] + 60, 0.35, 2.0);
    ctx.fillStyle = '#d99a1c';
    for (let i = 0; i < 3; i++) { const ph = (lt * 2 + i / 3) % 1; ctx.beginPath(); ctx.ellipse(640, 1150 + ph * 220, 9, 13, 0, 0, Math.PI * 2); ctx.fill(); }
  }
  if (lt < 1.3) caption('Aus ägyptischem\nSchwarzkümmel', 400, 76, 11.05, t, { color: INK, stroke: '#fff' });
  else if (lt < 2.6) caption('Frisch in Deutschland\ngepresst', 400, 72, 12.3, t, { color: INK, stroke: '#fff' });
  else caption('Pur, im Salat\noder Joghurt', 400, 80, 13.6, t, { box: '#2f6fd6', color: '#fff' });
}
function scene5(t) {
  const lt = t - 15;
  bg('#f4f6fb');
  bottle(220, 1650, 0.9 * outBack(prog(lt, 0, 0.4)));
  ['Bio-Qualität', 'Kaltgepresst', 'Rohkostqualität', '100 % naturrein', '500 ml Glasflasche'].forEach((f, i) =>
    chip(f, 680, 820 + i * 110, outBack(prog(lt, 0.3 + i * 0.3, 0.65 + i * 0.3)), ['#5bb33a', '#2f6fd6', '#f2b705', PINK, INK][i]));
  caption('Was drin ist,', 300, 84, 15.05, t, { color: INK, stroke: '#fff' });
  caption('steht drauf.', 410, 84, 15.3, t, { color: '#2f6fd6', stroke: '#fff' });
}
function scene6(t) {
  const lt = t - 18;
  const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#1b0f3a'); g.addColorStop(0.6, '#5a1546'); g.addColorStop(1, '#c7472b');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  caption('BLACK FRIDAY', 230, 88, 18.0, t, { box: '#fff', color: '#1b0f3a' });
  price(640, 520, outBack(prog(lt, 0.15, 0.5)), '31,25 €', '32,89 €', -0.04);
  const p = outBack(prog(lt, 0.05, 0.4));
  if (p > 0) bottle(220, 1130, 0.75 * p, -0.05);
  const fp = outBack(prog(lt, 0.35, 0.7));
  if (fp > 0) {
    ctx.save(); ctx.translate(660, 780); ctx.scale(fp, fp);
    ctx.fillStyle = '#16a34a'; rr(-210, -50, 420, 100, 50); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = `900 46px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('Gratis Versand', 0, 3);
    ctx.restore();
  }
  shopButton(1290, lt);
  caption('Tippe auf den Warenkorb', 1460, 50, 18.9, t, { color: '#fff', stroke: '#000' });
}
startAd([[3.5, scene1], [7, scene2], [11, scene3], [15, scene4], [18, scene5], [20, scene6]], [3.5, 7, 11, 15, 18]);

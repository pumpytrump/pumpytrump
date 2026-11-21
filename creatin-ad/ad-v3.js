// ProFuel Creatin 2×500 g – v3 "Preis-Check" receipt style (Tommy, calm/deadpan).
const LINES = [ // [time, left, right, highlight]
  [1.5, 'Creatin 2× 500 g', '1 kg', 0],
  [4.7, 'Regulär', '20,15 €', 0],
  [7.6, 'Bezahlt', '5,15 €', 1],
  [9.9, 'Grund', 'Creator-Probe', 2]
];
function receipt(lt, t) {
  G.grad('#101014', '#26262e');
  const x0 = 140, x1 = W - 140, top = 330;
  const shown = LINES.filter(l => lt + 0 >= l[0] - 0.0).length;
  const bottom = top + 260 + shown * 150 + 120;
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 40;
  ctx.fillStyle = '#fbfaf5';
  ctx.beginPath(); ctx.moveTo(x0, top); ctx.lineTo(x1, top); ctx.lineTo(x1, bottom);
  for (let x = x1; x > x0; x -= 40) ctx.lineTo(x - 20, bottom + 22), ctx.lineTo(x - 40, bottom);
  ctx.closePath(); ctx.fill(); ctx.restore();
  ctx.fillStyle = '#16161d'; ctx.textBaseline = 'middle';
  ctx.font = `700 64px "DejaVu Sans Mono", monospace`; ctx.textAlign = 'center';
  ctx.fillText('PREIS-CHECK', W / 2, top + 100);
  ctx.strokeStyle = '#16161d'; ctx.lineWidth = 4; ctx.setLineDash([14, 12]); line([[x0 + 40, top + 180], [x1 - 40, top + 180]]); ctx.setLineDash([]);
  LINES.forEach(([ts, l, r, hl], i) => {
    if (lt < ts) return;
    const y = top + 270 + i * 150, p = prog(lt, ts, ts + 0.5);
    const chars = Math.ceil(p * (l.length + r.length));
    ctx.font = `700 50px "DejaVu Sans Mono", monospace`;
    ctx.textAlign = 'left'; ctx.fillStyle = '#16161d'; ctx.fillText(l.slice(0, chars), x0 + 50, y);
    ctx.textAlign = 'right';
    if (hl === 1) { ctx.fillStyle = '#e5333a'; ctx.font = `900 64px ${FONT}`; }
    if (hl === 2) { ctx.fillStyle = '#7a7a85'; ctx.font = `700 40px "DejaVu Sans Mono", monospace`; }
    ctx.fillText(r.slice(0, Math.max(0, chars - l.length)), x1 - 50, y);
    if (i === 1 && lt > 7.6) { ctx.strokeStyle = '#e5333a'; ctx.lineWidth = 7; line([[x1 - 320, y], [x1 - 40, y]]); }
  });
  if (lt > 8.0) { // stamp
    const q = outBack(prog(lt, 8.0, 8.35));
    ctx.save(); ctx.translate(W / 2, bottom + 220); ctx.rotate(-0.12); ctx.scale(q, q);
    ctx.strokeStyle = '#e5333a'; ctx.lineWidth = 12; rr(-300, -90, 600, 180, 24); ctx.stroke();
    ctx.fillStyle = '#e5333a'; ctx.font = `900 76px ${FONT}`; ctx.textAlign = 'center'; ctx.fillText('−74 %', 0, 6);
    ctx.restore();
  }
}
window.AD = {
  duration: 22,
  images: { bag: 'assets/c-bag-black.png', facts: 'assets/c-facts2.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 11.2, draw: (lt, t) => receipt(lt, t) },
    { img: 'facts', t0: 11.2, t1: 15.2, mode: 'card', z0: 0.95, z1: 1.03, cardY: 1020, cardH: 1100 },
    { img: 'facts', t0: 15.2, t1: 17.2, mode: 'card', z0: 1, z1: 1, cardY: 1020, cardH: 1100, fx: 0.2, fy: 0.45,
      zoomInCard: lt => 1 + 0.6 * ease(prog(lt, 0.1, 0.8)) },
    { img: 'bag', t0: 17.2, t1: 22, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1040, cardH: 740 }
  ],
  captions: [
    { t0: 11.3, t1: 12.2, text: 'Was drin ist:', pos: 'top', size: 90 },
    { t0: 12.25, t1: 15.15, text: 'reines Creatin-Monohydrat\n*ohne Zusatzstoffe*', pos: 'top', size: 64 },
    { t0: 15.3, t1: 17.15, text: '*292* Portionen', pos: 'top', size: 96 }
  ],
  dings: [8.0],
  previews: [2, 6, 9, 10.5, 13, 16, 20],
  overlay(t) {
    if (t < 17.2) return;
    const lt = t - 17.2;
    badge('lohnt sich auch regulär', W / 2, 250, outBack(prog(lt, 0, 0.3)), '#fff', '#16161d', 46);
    price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '20,15 €', null, 0);
    badge('2× 500 g · 1 kg', W / 2, 600, outBack(prog(lt, 0.3, 0.6)), '#ff7a1a', '#fff', 42);
    shopButton(1600, lt, 0.5);
  }
};

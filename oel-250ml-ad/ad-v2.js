// Schwarzkümmelöl v2 – "3 Dinge, auf die du achten solltest" checklist. Voice: assets/voice-v2.mp3.
const oilEnd = t0 => t => {
  if (t < t0) return;
  const lt = t - t0;
  badge('BLACK FRIDAY', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
  price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '18,98 €', '19,98 €', 0);
  badge('✓ erfüllt alle drei', W / 2, 1420, outBack(prog(lt, 0.3, 0.6)), '#16a34a', '#fff', 46);
  shopButton(1610, lt, 0.6);
};
window.AD = {
  duration: 15.4,
  images: { bottle: 'assets/o-bottle.png', compare: 'assets/o-compare.png' },
  shots: [
    { img: 'bottle', t0: 0, t1: 3.55, fx: 0.5, fy: 0.3, fy1: 0.4, z0: 1.0, z1: 1.2 },
    { mode: 'gfx', t0: 3.55, t1: 4.55, draw: (lt, t) => { G.grad('#1a3d12', '#3f8a2a'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(1, lt, '#ffd34d'); } },
    { img: 'bottle', t0: 4.55, t1: 5.75, mode: 'card', z0: 0.9, z1: 0.98, cardY: 1020, cardH: 1150 },
    { mode: 'gfx', t0: 5.75, t1: 6.65, draw: (lt, t) => { G.grad('#0b3a5c', '#1d7fb8'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(2, lt, '#fff'); } },
    { img: 'bottle', t0: 6.65, t1: 8.7, fx: 0.5, fy: 0.62, z0: 1.15, z1: 1.35 },
    { mode: 'gfx', t0: 8.7, t1: 9.55, draw: (lt, t) => { G.grad('#5c2a0b', '#b8601d'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(3, lt, '#fff'); } },
    { mode: 'gfx', t0: 9.55, t1: 10.8, draw: (lt, t) => G.oilDrop(t, lt) },
    { img: 'bottle', t0: 10.8, t1: 15.4, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1010, cardH: 620 }
  ],
  captions: [
    { t0: 0.2, t1: 3.5, text: '*3 Dinge*, auf die du\nbei Schwarzkümmelöl\nachten solltest', pos: 'top', size: 68 },
    { t0: 4.55, t1: 5.7, text: '*Bio*-Qualität', pos: 'top', size: 90 },
    { t0: 6.65, t1: 8.65, text: '*kaltgepresst* &\n*ungefiltert*', pos: 'top', size: 82 },
    { t0: 9.6, t1: 10.75, text: '*frisch* gepresst', pos: 'top', size: 90 }
  ],
  dings: [11.0],
  previews: [2, 4, 5, 7.5, 9, 10, 13],
  overlay: oilEnd(10.8)
};

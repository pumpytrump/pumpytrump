// Satisbites v2 – head-to-head bar comparison (seller's numbers, per 50 g). Voice: assets/voice-v2.mp3.
const ROWS = [
  { label: 'Zucker', a: 16, b: 1.6, unit: 'g', max: 16, better: 'low' },
  { label: 'Protein', a: 4.3, b: 13, unit: 'g', max: 13, better: 'high' },
  { label: 'Kalorien', a: 241, b: 189, unit: 'kcal', max: 241, better: 'low' }
];
window.AD = {
  duration: 18,
  images: { box: 'assets/s-box.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 3.85, draw: (lt, t) => {
      G.grad('#16131f', '#3a1430'); G.blobs(t, ['rgba(255,79,154,0.25)', 'rgba(120,120,140,0.2)']);
      G.chocoBar(290, 1150, 0.85, -0.12 + Math.sin(t * 2) * 0.03);
      const im = IMG.box, s = 0.32 * outBack(prog(lt, 0.4, 0.8));
      if (s > 0) ctx.drawImage(im, 820 - im.width * s / 2, 1150 - im.height * s / 2, im.width * s, im.height * s);
      G.text('VS', W / 2, 820, 170, '#ffd34d', outBack(prog(lt, 0.2, 0.5)));
    } },
    { mode: 'gfx', t0: 3.85, t1: 14.0, draw: (lt, t) => {
      const starts = [0.2, 3.3, 6.25]; // Zucker 4.05 s, Protein 7.15 s, Kalorien 10.1 s
      const idx = starts.filter(s => lt >= s).length - 1;
      G.versus(ROWS, lt - starts[Math.max(0, idx)], Math.max(0, idx));
    } },
    { img: 'box', t0: 14.0, t1: 18, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1000, cardH: 760 }
  ],
  captions: [
    { t0: 0.2, t1: 3.8, text: 'Schokoriegel vs.\n*Protein Satisbites*', pos: 'top', size: 76 },
    { t0: 14.0, t1: 15.2, text: 'Klarer *Sieger*!', pos: 'top', size: 90 }
  ],
  dings: [14.1],
  previews: [2, 5.5, 8.5, 12.5, 16],
  overlay(t) {
    if (t >= 15.0) {
      const lt = t - 15.0;
      badge('Sorten wählbar', W / 2, 460, outBack(prog(lt, 0, 0.3)), '#e5333a', '#fff', 52, -0.03);
      shopButton(1500, lt, 0.2);
    }
  }
};

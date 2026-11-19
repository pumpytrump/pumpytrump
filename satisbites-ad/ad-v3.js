// Satisbites v3 – "POV: 22 Uhr, Lust auf Süßes". Voice: assets/voice-v3.mp3.
window.AD = {
  duration: 15.8,
  images: { box: 'assets/s-box.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 4.65, draw: (lt, t) => { G.nightRoom(t); G.clock('22:00', W / 2, 820, 140, t, 0); } },
    { mode: 'gfx', t0: 4.65, t1: 6.15, draw: (lt, t) => {
      G.grad('#2a1408', '#4a2412'); G.chocoBar(W / 2, 1000, 1.6, -0.06); G.crossOut(W / 2 + 40, 1000, 520, prog(lt, 0.3, 1.0));
    } },
    { img: 'box', t0: 6.15, t1: 7.75, mode: 'card', z0: 0.95, z1: 1.05, cardY: 1000, cardH: 1000 },
    { img: 'box', t0: 7.75, t1: 11.2, fx: 0.3, fy: 0.62, fx1: 0.36, z0: 1.7, z1: 1.95 },
    { img: 'box', t0: 11.2, t1: 15.8, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1000, cardH: 760 }
  ],
  captions: [
    { t0: 0.2, t1: 1.3, text: '*POV:*', pos: 'top', size: 110 },
    { t0: 1.5, t1: 4.6, text: '22 Uhr und du willst\nwas *Süßes*', pos: 'top', size: 78 },
    { t0: 4.85, t1: 6.1, text: 'Statt *Schokoriegel*:', pos: 'top', size: 80 },
    { t0: 6.17, t1: 7.7, text: 'Protein *Satisbites*', pos: 'low', size: 80 },
    { t0: 7.8, t1: 9.7, text: '*15 g Protein*\npro Portion', pos: 'top', size: 84 },
    { t0: 9.9, t1: 11.15, text: '*ohne* Zuckerzusatz', pos: 'top', size: 80 },
    { t0: 11.3, t1: 13.1, text: 'in mehreren *Sorten*', pos: 'top', size: 76 }
  ],
  dings: [11.4],
  previews: [0.8, 3, 5.5, 7, 9, 10.5, 14],
  overlay(t) {
    if (t >= 13.1) {
      const lt = t - 13.1;
      badge('Sorten wählbar', W / 2, 330, outBack(prog(lt, 0, 0.3)), '#e5333a', '#fff', 52, -0.03);
    }
    if (t >= 11.2) shopButton(1500, t - 11.2, 1.6);
  }
};

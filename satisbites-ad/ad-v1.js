// Satisbites v1 – Smart Swap. Numbers from the seller's comparison (per 50 g, Dark Cookie Crumble).
window.AD = {
  duration: 19,
  images: { box: 'assets/s-box.png', table: 'assets/s-table.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 3.8, draw: (lt, t) => { G.grad('#2a1408', '#4a2412'); G.blobs(t, ['rgba(255,150,80,0.2)']); G.chocoBar(W / 2, 950, 1.5, Math.sin(t * 1.5) * 0.05, lt > 1); if (lt > 1.4) G.sugarPile(W / 2, 1560, 10, prog(lt, 1.4, 2.6), t, 1.3); } },
    { img: 'box', t0: 3.8, t1: 5.4, mode: 'card', z0: 0.95, z1: 1.05, cardY: 1000, cardH: 1000 },
    { img: 'box', t0: 5.4, t1: 7.6, fx: 0.5, fy: 0.5, z0: 1.0, z1: 1.15 },
    { img: 'table', t0: 7.6, t1: 11.8, mode: 'card', z0: 1.0, z1: 1.0, cardY: 980, cardH: 1100, fx: 0.5, fy: 0.75,
      zoomInCard: lt => 1 + 0.35 * ease(prog(lt, 0.3, 1.6)) },
    { mode: 'gfx', t0: 11.8, t1: 14.4, draw: (lt, t) => { G.grad('#1d1430', '#3a1838'); G.sugarPile(W / 2, 1300, 16, prog(lt, 0, 1.3), t, 1.6); G.chocoBar(W / 2, 1560, 0.9, -0.05); } },
    { img: 'box', t0: 14.4, t1: 19, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1000, cardH: 760 }
  ],
  captions: [
    { t0: 0.2, t1: 1.6, text: 'Lust auf *Schoki*?', pos: 'top', size: 86 },
    { t0: 1.6, t1: 3.75, text: 'aber nicht auf\n*16 g Zucker*?', pos: 'top', size: 86 },
    { t0: 4.0, t1: 5.35, text: 'Mach den *Smart Swap*!', pos: 'top', size: 76 },
    { t0: 5.4, t1: 7.6, text: 'Protein *Satisbites*', pos: 'low', size: 80 },
    { t0: 7.6, t1: 9.6, text: '*13 g Protein*\npro 50 g', pos: 'top', size: 80 },
    { t0: 9.6, t1: 11.75, text: 'nur *1,6 g* Zucker', pos: 'top', size: 84 },
    { t0: 11.99, t1: 13.4, text: 'Normaler Schokoriegel?', pos: 'top', size: 70 },
    { t0: 13.4, t1: 14.4, text: '*16 g* Zucker!', pos: 'top', size: 96, hl: '#ff4d5e' }
  ],
  dings: [14.7],
  previews: [1, 4.5, 6.5, 10, 13.8, 17],
  overlay(t) {
    if (t >= 14.4) {
      const lt = t - 14.4;
      badge('MEHR PROTEIN · WENIGER ZUCKER', W / 2, 300, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 42);
      badge('Sorten wählbar', W / 2, 460, outBack(prog(lt, 0.2, 0.5)), '#e5333a', '#fff', 52, -0.03);
      shopButton(1500, lt, 0.4);
    }
  }
};

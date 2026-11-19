// Protein Satisbites – realistic TikTok Shop ad. Numbers from the seller's comparison (per 50 g, Dark Cookie Crumble).
window.AD = {
  duration: 19,
  images: { ai: 'assets/ai-problem.png', box: 'assets/s-box.png', table: 'assets/s-table.png' },
  shots: [
    { img: 'ai', t0: 0, t1: 3.8, fx: 0.45, fy: 0.35, z0: 1.0, z1: 1.15 },
    { img: 'box', t0: 3.8, t1: 5.4, mode: 'card', z0: 0.95, z1: 1.05, cardY: 1000, cardH: 1000 },
    { img: 'box', t0: 5.4, t1: 7.6, fx: 0.5, fy: 0.5, z0: 1.0, z1: 1.15 },
    { img: 'table', t0: 7.6, t1: 11.8, mode: 'card', z0: 1.0, z1: 1.0, cardY: 980, cardH: 1100, fx: 0.5, fy: 0.75,
      zoomInCard: lt => 1 + 0.35 * ease(prog(lt, 0.3, 1.6)) },
    { img: 'ai', t0: 11.8, t1: 14.4, fx: 0.22, fy: 0.82, z0: 1.6, z1: 1.8 },
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

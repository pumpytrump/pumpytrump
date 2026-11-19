// Bio-Schwarzkümmelöl 250 ml – realistic TikTok Shop ad (no health claims, only listing facts).
window.AD = {
  duration: 22.8,
  images: { salad: 'assets/ai-salad.png', compare: 'assets/o-compare.png', bottle: 'assets/o-bottle.png' },
  shots: [
    { img: 'salad', t0: 0, t1: 3.3, fx: 0.62, fy: 0.3, z0: 1.0, z1: 1.15 },
    { img: 'compare', t0: 3.3, t1: 7.3, mode: 'card', z0: 0.95, z1: 1.02, cardY: 1000, cardH: 1100 },
    { img: 'bottle', t0: 7.3, t1: 10.75, mode: 'card', z0: 0.88, z1: 0.98, cardY: 1000, cardH: 1250 },
    { img: 'salad', t0: 10.75, t1: 14.0, fx: 0.12, fy: 0.62, fx1: 0.3, z0: 1.25, z1: 1.4 },
    { img: 'bottle', t0: 14.0, t1: 17.0, fx: 0.5, fy: 0.55, fy1: 0.62, z0: 1.0, z1: 1.25 },
    { img: 'bottle', t0: 17.0, t1: 22.8, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1010, cardH: 780 }
  ],
  captions: [
    { t0: 0.2, t1: 3.25, text: 'Schwarzkümmelöl\nist nicht gleich\n*Schwarzkümmelöl*', pos: 'top', size: 74 },
    { t0: 3.4, t1: 4.35, text: 'Achte drauf:', pos: 'top', size: 80 },
    { t0: 4.4, t1: 5.5, text: 'nicht *raffiniert*', pos: 'top', size: 80 },
    { t0: 5.6, t1: 7.25, text: 'keine *künstlichen Zusätze*', pos: 'top', size: 66 },
    { t0: 7.5, t1: 8.8, text: 'Dieses hier: *Bio*', pos: 'top', size: 80 },
    { t0: 8.85, t1: 10.7, text: '*kaltgepresst* &\n*ungefiltert*', pos: 'top', size: 80 },
    { t0: 10.85, t1: 12.2, text: 'aus *ägyptischem*\nSchwarzkümmel', pos: 'top', size: 74 },
    { t0: 12.2, t1: 13.95, text: 'frisch in *Deutschland*\ngepresst', pos: 'top', size: 74 },
    { t0: 14.15, t1: 15.6, text: '*100 %* naturrein', pos: 'low', size: 84 },
    { t0: 15.7, t1: 16.95, text: '*Rohkost*qualität', pos: 'low', size: 84 }
  ],
  dings: [17.3],
  previews: [1.5, 4.8, 9, 12.5, 15, 19.5],
  overlay(t) {
    if (t >= 17.0) {
      const lt = t - 17.0;
      badge('BLACK FRIDAY', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
      price(W / 2, 470, outBack(prog(lt, 0.15, 0.45)), '18,98 €', '19,98 €', 0);
      shopButton(1520, lt, 0.5);
    }
  }
};

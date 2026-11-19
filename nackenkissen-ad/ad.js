// Nackenkissen (Memory-Schaum) – realistic TikTok Shop ad. Voice: ElevenLabs "Ben", times include the 0.2 s voice delay.
window.AD = {
  duration: 21,
  images: {
    ai: 'assets/ai-problem.png', pillow: 'assets/p-pillow.png', scene: 'assets/p-scene.png',
    styles: 'assets/p-styles.png', back: 'assets/p-back.png'
  },
  shots: [
    { img: 'ai', t0: 0, t1: 3.7, fx: 0.42, fy: 0.3, z0: 1.0, z1: 1.18 },
    { img: 'ai', t0: 3.7, t1: 5.4, fx: 0.45, fy: 0.25, z0: 1.5, z1: 1.7 },
    { img: 'pillow', t0: 5.4, t1: 7.8, mode: 'card', z0: 0.95, z1: 1.05, cardY: 900 },
    { img: 'scene', t0: 7.8, t1: 10.2, fx: 0.55, fy: 0.5, z0: 1.0, z1: 1.15 },
    { img: 'styles', t0: 10.2, t1: 12.9, mode: 'card', z0: 0.95, z1: 1.03, cardY: 880 },
    { img: 'back', t0: 12.9, t1: 16.9, fx: 0.5, fy: 0.45, fx1: 0.6, z0: 1.0, z1: 1.2 },
    { img: 'pillow', t0: 16.9, t1: 21, mode: 'card', z0: 0.9, z1: 1.0, cardY: 980, cardH: 600 }
  ],
  captions: [
    { t0: 0.2, t1: 3.6, text: 'Jeden Morgen\n*verspannter Nacken*?', pos: 'top', size: 80 },
    { t0: 3.9, t1: 5.3, text: "Vielleicht liegt's\nam *Kissen*", pos: 'mid', size: 84 },
    { t0: 5.5, t1: 7.75, text: '*Memory-Schaum*', pos: 'top', size: 84 },
    { t0: 7.9, t1: 9.3, text: 'ergonomisch geformt', pos: 'low', size: 70 },
    { t0: 9.3, t1: 12.8, text: 'Rücken · Seite · *Bauch*', pos: 'top', size: 72 },
    { t0: 13.1, t1: 14.6, text: 'mit *kühlendem* Bezug', pos: 'low', size: 70 },
    { t0: 14.6, t1: 16.85, text: '*250.000+* verkauft', pos: 'low', size: 80 }
  ],
  dings: [17.1],
  previews: [1.5, 4.5, 6.5, 9, 11.5, 15.5, 19.5],
  overlay(t) {
    if (t > 14.6 && t < 16.9) stars(W / 2, 1620, outBack(prog(t, 14.7, 15.0)), 4.4, '4,4 · 20.600+');
    if (t >= 16.9) {
      const lt = t - 16.9;
      badge('BLACK FRIDAY', W / 2, 250, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
      price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '27,83 €', null, 0);
      badge('Gratis Versand', W / 2, 610, outBack(prog(lt, 0.3, 0.6)), '#16a34a', '#fff', 42);
      shopButton(1450, lt, 0.5);
    }
  }
};

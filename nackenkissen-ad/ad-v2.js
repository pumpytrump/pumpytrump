// Nackenkissen v2 – "3 Gründe" listicle. Voice: assets/voice-v2.mp3 (times include the 0.2 s delay).
window.AD = {
  duration: 16,
  images: { pillow: 'assets/p-pillow.png', scene: 'assets/p-scene.png', styles: 'assets/p-styles.png', back: 'assets/p-back.png' },
  shots: [
    { img: 'scene', t0: 0, t1: 3.85, fx: 0.55, fy: 0.5, z0: 1.0, z1: 1.18 },
    { mode: 'gfx', t0: 3.85, t1: 4.7, draw: (lt, t) => { G.grad('#3b1d8f', '#7b2ff7'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(1, lt, '#ffd34d'); } },
    { img: 'pillow', t0: 4.7, t1: 6.75, mode: 'card', z0: 0.95, z1: 1.05, cardY: 900 },
    { mode: 'gfx', t0: 6.75, t1: 7.5, draw: (lt, t) => { G.grad('#0e6b5c', '#18b28f'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(2, lt, '#fff'); } },
    { img: 'styles', t0: 7.5, t1: 10.15, mode: 'card', z0: 0.95, z1: 1.03, cardY: 900 },
    { mode: 'gfx', t0: 10.15, t1: 10.8, draw: (lt, t) => { G.grad('#0b4fa8', '#2fb4ff'); G.blobs(t, ['rgba(255,255,255,0.12)']); G.bigNumber(3, lt, '#fff'); } },
    { img: 'back', t0: 10.8, t1: 12.3, fx: 0.5, fy: 0.45, z0: 1.05, z1: 1.2 },
    { img: 'pillow', t0: 12.3, t1: 16, mode: 'card', z0: 0.9, z1: 1.0, cardY: 980, cardH: 600 }
  ],
  captions: [
    { t0: 0.2, t1: 3.8, text: '*3 Gründe*, warum alle\ndieses Nackenkissen\nkaufen', pos: 'top', size: 70 },
    { t0: 4.7, t1: 6.7, text: '*Memory-Schaum*,\nder sich anpasst', pos: 'top', size: 76 },
    { t0: 7.5, t1: 10.1, text: 'Rücken · Seite · *Bauch*', pos: 'top', size: 72 },
    { t0: 10.8, t1: 12.25, text: '*kühlender* Bezug', pos: 'low', size: 84 }
  ],
  dings: [12.5],
  previews: [2, 4.2, 5.5, 8.5, 10.5, 11.5, 14.5],
  overlay(t) {
    if (t >= 12.3) {
      const lt = t - 12.3;
      badge('BLACK FRIDAY', W / 2, 250, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
      price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '27,83 €', null, 0);
      badge('Gratis Versand', W / 2, 610, outBack(prog(lt, 0.3, 0.6)), '#16a34a', '#fff', 42);
      shopButton(1450, lt, 0.5);
    }
  }
};

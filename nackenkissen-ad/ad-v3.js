// Nackenkissen v3 – Social proof (sales counter + rating). Voice: assets/voice-v3.mp3.
window.AD = {
  duration: 15.8,
  images: { pillow: 'assets/p-pillow.png', scene: 'assets/p-scene.png', back: 'assets/p-back.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 3.2, draw: (lt, t) => {
      G.grad('#0a0f24', '#1d2b6b'); G.blobs(t, ['rgba(47,180,255,0.25)', 'rgba(123,47,247,0.2)']);
      G.counter(250000 * ease(prog(lt, 0.1, 2.2)), W / 2, 900, 190, '#fff');
      G.text('mal verkauft', W / 2, 1080, 70, '#7fd3ff', outBack(prog(lt, 0.3, 0.6)));
    } },
    { mode: 'gfx', t0: 3.2, t1: 7.3, draw: (lt, t) => {
      G.grad('#1d1206', '#4a2c08'); G.blobs(t, ['rgba(255,201,61,0.25)']);
      G.stars5(W / 2, 820, 70, 4.4, prog(lt, 0.1, 1.0));
      G.text((4.4 * ease(prog(lt, 0.2, 1.5))).toFixed(1).replace('.', ','), W / 2, 1030, 200, '#ffc93d');
      G.text(`${Math.round(20600 * ease(prog(lt, 0.8, 2.6))).toLocaleString('de-DE')}+ Bewertungen`, W / 2, 1200, 60, '#fff', outBack(prog(lt, 0.8, 1.1)));
    } },
    { img: 'scene', t0: 7.3, t1: 10.2, fx: 0.55, fy: 0.5, z0: 1.0, z1: 1.18 },
    { img: 'back', t0: 10.2, t1: 12.75, fx: 0.5, fy: 0.45, fx1: 0.6, z0: 1.0, z1: 1.2 },
    { img: 'pillow', t0: 12.75, t1: 15.8, mode: 'card', z0: 0.9, z1: 1.0, cardY: 980, cardH: 600 }
  ],
  captions: [
    { t0: 7.4, t1: 10.1, text: 'Das Kissen, über das\n*alle* reden', pos: 'top', size: 74 },
    { t0: 10.4, t1: 12.7, text: 'ergonomisch geformt\naus *Memory-Schaum*', pos: 'low', size: 70 }
  ],
  dings: [13.0],
  previews: [2.5, 5, 8.5, 11.5, 14.5],
  overlay(t) {
    if (t >= 12.75) {
      const lt = t - 12.75;
      badge('BLACK FRIDAY', W / 2, 250, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
      price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '27,83 €', null, 0);
      badge('Gratis Versand', W / 2, 610, outBack(prog(lt, 0.3, 0.6)), '#16a34a', '#fff', 42);
      shopButton(1450, lt, 0.4);
    }
  }
};

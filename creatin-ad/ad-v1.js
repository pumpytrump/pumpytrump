// ProFuel Creatin 1 kg – Voice: assets/voice-v1.mp3. Only listing facts (no performance claims).
window.AD = {
  duration: 14.6,
  images: { bag: 'assets/c-bag.png', facts: 'assets/c-facts.png' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 3.7, draw: (lt, t) => {
      G.grad('#1a1a1f', '#3b2416'); G.blobs(t, ['rgba(255,122,26,0.3)']);
      G.counter(292 * ease(prog(lt, 0.1, 2.2)), W / 2, 880, 300, '#fff');
      G.text('PORTIONEN', W / 2, 1100, 90, '#ff7a1a', outBack(prog(lt, 0.3, 0.6)));
      G.text('in einem Beutel', W / 2, 1220, 56, '#d8d2cc', outBack(prog(lt, 1.6, 1.9)));
    } },
    { img: 'bag', t0: 3.7, t1: 5.4, mode: 'card', z0: 0.92, z1: 1.02, cardY: 1020, cardH: 1150 },
    { img: 'facts', t0: 5.4, t1: 7.0, mode: 'card', z0: 1.0, z1: 1.0, cardY: 1000, cardH: 1100, fx: 0.5, fy: 0.82,
      zoomInCard: lt => 1 + 0.45 * ease(prog(lt, 0.1, 0.8)) },
    { img: 'facts', t0: 7.0, t1: 9.1, mode: 'card', z0: 1.0, z1: 1.0, cardY: 1000, cardH: 1100, fx: 0.85, fy: 0.25,
      zoomInCard: lt => 1 + 0.6 * ease(prog(lt, 0.1, 0.8)) },
    { img: 'bag', t0: 9.1, t1: 14.6, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1040, cardH: 740 }
  ],
  captions: [
    { t0: 3.7, t1: 5.35, text: 'reines\n*Creatin-Monohydrat*', pos: 'top', size: 80 },
    { t0: 5.45, t1: 6.95, text: '*3 g* pro Portion', pos: 'top', size: 90 },
    { t0: 7.0, t1: 9.05, text: '*vegan* & ohne\nZusatzstoffe', pos: 'top', size: 84 }
  ],
  dings: [9.35],
  previews: [2, 4.5, 6.5, 8, 12],
  overlay(t) {
    if (t < 9.1) return;
    const lt = t - 9.1;
    badge('BLACK FRIDAY', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
    G.text('1 kg ab', W / 2, 380, 52, '#fff', outBack(prog(lt, 0.1, 0.4)));
    price(W / 2, 490, outBack(prog(lt, 0.15, 0.45)), '17,73 €', null, 0);
    badge('292 Portionen · vegan', W / 2, 1490, outBack(prog(lt, 0.4, 0.7)), '#ff7a1a', '#fff', 44);
    shopButton(1670, lt, 0.6);
  }
};

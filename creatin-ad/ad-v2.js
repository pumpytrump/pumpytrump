// ProFuel Creatin 2×500 g – v2 "Unboxing" (Ben, energetic). Creator got it as a refundable sample for 5,15 €.
function parcel(lt, t) {
  G.grad('#1b1410', '#3d2a1a'); G.blobs(t, ['rgba(255,122,26,0.3)']);
  const open = ease(prog(lt, 0.6, 1.3)), shake = lt < 0.6 ? Math.sin(t * 50) * 10 : 0;
  const bx = W / 2 + shake, by = 1350;
  if (open > 0.3) rays(bx, by - 260, t, `rgba(255,220,150,${0.18 * open})`);
  const rise = 0.6 * ease(prog(lt, 1.2, 2.4)), im = IMG.bag;
  if (rise > 0) { // bag rising out of the box
    const s = 0.62, w = im.width * s, h = im.height * s;
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, by - 230); ctx.clip();
    ctx.drawImage(im, bx - w / 2, by - 240 - h * rise, w, h);
    ctx.restore();
  }
  ctx.fillStyle = '#b7834f'; rr(bx - 330, by - 240, 660, 420, 16); ctx.fill(); // box
  ctx.fillStyle = '#d9a86c'; ctx.fillRect(bx - 50, by - 240, 100, 420); // tape
  ctx.fillStyle = '#9c6c3c';
  ctx.save(); ctx.translate(bx - 330, by - 240); ctx.rotate(-1.9 * open); ctx.fillRect(0, -16, 330, 32); ctx.restore();
  ctx.save(); ctx.translate(bx + 330, by - 240); ctx.rotate(1.9 * open); ctx.fillRect(-330, -16, 330, 32); ctx.restore();
}
function twoBags(lt, t) {
  bg('#000'); G.blobs(t, ['rgba(255,122,26,0.25)']);
  const im = IMG.bag, s = 0.62 * outBack(prog(lt, 0, 0.35)), w = im.width * s, h = im.height * s;
  ctx.drawImage(im, W / 2 - w - 10 + Math.sin(t * 2) * 6, 1000 - h / 2, w, h);
  ctx.drawImage(im, W / 2 + 10, 1000 - h / 2 + Math.cos(t * 2) * 6, w, h);
}
window.AD = {
  duration: 20.6,
  images: { bag: 'assets/c-bag-black.png', facts: 'assets/c-facts2.png', order: 'assets/c-order.jpg' },
  shots: [
    { mode: 'gfx', t0: 0, t1: 4.95, draw: (lt, t) => parcel(lt, t) },
    { mode: 'gfx', t0: 4.95, t1: 7.1, draw: (lt, t) => twoBags(lt, t) },
    { img: 'order', t0: 7.1, t1: 11.2, mode: 'card', z0: 0.95, z1: 1.03, cardY: 1080, cardH: 900 },
    { img: 'facts', t0: 11.2, t1: 15.3, mode: 'card', z0: 0.95, z1: 1.03, cardY: 1020, cardH: 1100 },
    { img: 'bag', t0: 15.3, t1: 20.6, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1040, cardH: 740 }
  ],
  captions: [
    { t0: 0.2, t1: 2.4, text: '*Paket* ist da!', pos: 'top', size: 100 },
    { t0: 2.4, t1: 4.9, text: '1 kg *Creatin*\nvon ProFuel', pos: 'top', size: 84 },
    { t0: 5.05, t1: 7.05, text: '2× 500 g = *1 kg*', pos: 'top', size: 92 },
    { t0: 7.2, t1: 8.75, text: 'Und das Beste:', pos: 'top', size: 90 },
    { t0: 8.75, t1: 11.15, text: 'ich hab nur *5 €*\nbezahlt', pos: 'top', size: 92 },
    { t0: 11.3, t1: 13.2, text: 'reines\n*Creatin-Monohydrat*', pos: 'top', size: 78 },
    { t0: 13.2, t1: 15.25, text: '*3 g* pro Portion · *vegan*', pos: 'top', size: 68 }
  ],
  dings: [9.0, 15.6],
  previews: [1, 3.5, 6, 9.5, 12.5, 18],
  overlay(t) {
    if (t >= 8.9 && t < 11.2) { // stamp over the order screenshot
      const lt = t - 8.9;
      badge('nur 5,15 € bezahlt!', W / 2, 1650, outBack(prog(lt, 0, 0.3)), '#e5333a', '#fff', 60, -0.06);
      G.text('(Creator-Probe, rückerstattbar)', W / 2, 1770, 34, '#fff', outBack(prog(lt, 0.3, 0.6)), 'center', 700);
    }
    if (t >= 15.3) {
      const lt = t - 15.3;
      badge('2× 500 g Beutel', W / 2, 250, outBack(prog(lt, 0, 0.3)), '#fff', '#16161d', 50);
      G.text('Normalpreis', W / 2, 390, 50, '#fff', outBack(prog(lt, 0.1, 0.4)));
      price(W / 2, 490, outBack(prog(lt, 0.15, 0.45)), '20,15 €', null, 0);
      shopButton(1600, lt, 0.5);
    }
  }
};

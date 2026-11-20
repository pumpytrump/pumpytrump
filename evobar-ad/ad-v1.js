// Evobar Proteinriegel Peanut Caramel – Voice: assets/voice-v1.mp3. Numbers from the pack.
function statTile(x, y, big, small, col, p) {
  if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(p, p); ctx.rotate(-0.03);
  ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 30;
  ctx.fillStyle = '#fff'; rr(-420, -120, 840, 240, 40); ctx.fill(); ctx.shadowBlur = 0;
  ctx.fillStyle = col; rr(-420, -120, 300, 240, 40); ctx.fill(); ctx.fillRect(-160, -120, 40, 240);
  ctx.font = `900 120px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff';
  ctx.fillText(big, -270, 6);
  ctx.font = `900 58px ${FONT}`; ctx.fillStyle = '#16161d'; ctx.textAlign = 'left';
  ctx.fillText(small, -90, 6);
  ctx.restore();
}
window.AD = {
  duration: 13.2,
  images: { box: 'assets/e-box.png' },
  shots: [
    { img: 'box', t0: 0, t1: 3.0, mode: 'card', z0: 0.92, z1: 1.06, cardY: 1000, cardH: 900 },
    { mode: 'gfx', t0: 3.0, t1: 8.5, draw: (lt, t) => {
      G.grad('#3b2314', '#8a5326'); G.blobs(t, ['rgba(255,190,90,0.3)']);
      ctx.fillStyle = 'rgba(255,220,160,0.25)';
      for (let i = 0; i < 26; i++) { ctx.beginPath(); ctx.ellipse(rnd(i) * W, (rnd(i + 4) * H + t * 40) % H, 22, 14, i, 0, Math.PI * 2); ctx.fill(); }
      G.text('EVOBAR', W / 2, 520, 130, '#fff', outBack(prog(lt, 0, 0.3)));
      statTile(W / 2, 820, '20g', 'Protein', '#e5333a', outBack(prog(lt, 1.5, 1.8)));
      statTile(W / 2, 1100, '3g', 'Leucin', '#2a7fff', outBack(prog(lt, 2.8, 3.1)));
      statTile(W / 2, 1380, '0g', 'Zuckerzusatz', '#16a34a', outBack(prog(lt, 4.0, 4.3)));
    } },
    { img: 'box', t0: 8.5, t1: 13.2, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1040, cardH: 700 }
  ],
  captions: [
    { t0: 0.2, t1: 2.95, text: 'Proteinriegel mit\n*Peanut Caramel*?', pos: 'top', size: 82 }
  ],
  dings: [8.8],
  previews: [1.5, 4, 6, 7.8, 11],
  overlay(t) {
    if (t < 8.5) return;
    const lt = t - 8.5;
    badge('SNACK SMART', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#3b2314', 50);
    G.text('ab', W / 2 - 300, 470, 52, '#fff', outBack(prog(lt, 0.1, 0.4)));
    price(W / 2 + 40, 450, outBack(prog(lt, 0.15, 0.45)), '31,36 €', null, 0);
    badge('Gratis Versand', W / 2, 610, outBack(prog(lt, 0.3, 0.6)), '#16a34a', '#fff', 42);
    shopButton(1600, lt, 0.5);
  }
};

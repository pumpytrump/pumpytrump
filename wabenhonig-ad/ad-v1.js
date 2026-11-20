// Deutscher Wabenhonig – Voice: assets/voice-v1.mp3 (ElevenLabs "Ben"); times include the 0.2 s delay.
function honeycomb(t, lt) { // golden hex grid that fills with honey, plus a buzzing bee
  G.grad('#3a2203', '#8a5a0c'); G.blobs(t, ['rgba(255,200,60,0.35)']);
  const r = 70, h = Math.sqrt(3) * r;
  for (let row = -1; row < 18; row++) for (let col = -1; col < 9; col++) {
    const x = col * r * 1.5, y = row * h + (col % 2 ? h / 2 : 0);
    const d = Math.hypot(x - W / 2, y - H / 2);
    const fill = clamp((lt * 900 - d) / 300);
    ctx.beginPath();
    for (let k = 0; k < 6; k++) ctx.lineTo(x + Math.cos(k * Math.PI / 3) * (r - 4), y + Math.sin(k * Math.PI / 3) * (r - 4));
    ctx.closePath();
    ctx.fillStyle = `rgba(${Math.round(lerp(120, 240, fill))},${Math.round(lerp(80, 170, fill))},20,${0.5 + 0.5 * fill})`;
    ctx.fill(); ctx.strokeStyle = '#f7d27a'; ctx.lineWidth = 5; ctx.stroke();
  }
  const bx = W / 2 + Math.sin(t * 2.2) * 260, by = 1050 + Math.sin(t * 4.1) * 120; // bee
  ctx.save(); ctx.translate(bx, by); ctx.rotate(Math.cos(t * 2.2) * 0.4);
  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  ctx.beginPath(); ctx.ellipse(-20, -55, 30, 50 * (0.6 + 0.4 * Math.abs(Math.sin(t * 60))), -0.4, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(25, -55, 30, 50 * (0.6 + 0.4 * Math.abs(Math.cos(t * 60))), 0.4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#ffc61a'; ctx.beginPath(); ctx.ellipse(0, 0, 70, 46, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#1b1405'; for (const sx of [-25, 5, 35]) ctx.fillRect(sx, -44, 16, 88);
  ctx.beginPath(); ctx.arc(-70, 0, 28, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
window.AD = {
  duration: 13.6,
  images: { wabe: 'assets/h-wabe.png' },
  shots: [
    { img: 'wabe', t0: 0, t1: 2.55, fx: 0.5, fy: 0.5, z0: 1.0, z1: 1.2 },
    { mode: 'gfx', t0: 2.55, t1: 5.55, draw: (lt, t) => honeycomb(t, lt) },
    { img: 'wabe', t0: 5.55, t1: 7.55, fx: 0.6, fy: 0.62, fx1: 0.68, z0: 1.8, z1: 2.1 },
    { img: 'wabe', t0: 7.55, t1: 13.6, mode: 'card', z0: 0.92, z1: 1.0, cardY: 1020, cardH: 760 }
  ],
  captions: [
    { t0: 0.2, t1: 2.5, text: 'Schon mal echten\n*Wabenhonig* probiert?', pos: 'top', size: 80 },
    { t0: 2.65, t1: 5.5, text: 'direkt aus der Wabe,\nvon einer *deutschen*\n*Imkerei*', pos: 'top', size: 72 },
    { t0: 5.6, t1: 7.5, text: 'so wie die *Bienen*\nihn gemacht haben', pos: 'top', size: 76 }
  ],
  dings: [7.8],
  previews: [1.5, 4, 6.5, 11],
  overlay(t) {
    if (t < 7.55) return;
    const lt = t - 7.55;
    badge('BLACK FRIDAY', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
    price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '19,00 €', '22 €', 0);
    badge('Größen wählbar', W / 2, 1480, outBack(prog(lt, 0.4, 0.7)), '#f2b705', '#16161d', 44);
    shopButton(1660, lt, 0.6);
  }
};

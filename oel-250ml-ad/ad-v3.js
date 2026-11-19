// Schwarzkümmelöl v3 – "So kannst du es verwenden" (usage ideas, no health claims). Voice: assets/voice-v3.mp3.
const salad = () => {
  for (let i = 0; i < 22; i++) { ctx.fillStyle = i % 4 === 0 ? '#e5484d' : i % 3 ? '#5fae3e' : '#8bd16a'; ctx.beginPath(); ctx.ellipse(-160 + rnd(i) * 320, -120 + rnd(i + 3) * 40, 34, 16, rnd(i + 7) * 3, 0, Math.PI * 2); ctx.fill(); }
};
const kitchenBg = (t, c1, c2) => { G.grad(c1, c2); G.blobs(t, ['rgba(255,255,255,0.18)']); ctx.fillStyle = 'rgba(120,80,40,0.35)'; ctx.fillRect(0, 1380, W, H - 1380); };
window.AD = {
  duration: 15.0,
  images: { bottle: 'assets/o-bottle.png' },
  shots: [
    { img: 'bottle', t0: 0, t1: 2.3, fx: 0.5, fy: 0.45, z0: 1.0, z1: 1.15 },
    { mode: 'gfx', t0: 2.3, t1: 3.6, draw: (lt, t) => { kitchenBg(t, '#f6efe2', '#e7d6bb'); G.bowl(W / 2, 1380, 1.7, '#7cc35a', salad); G.drizzle(W / 2 + 20, 300, 1180, lt); } },
    { mode: 'gfx', t0: 3.6, t1: 4.7, draw: (lt, t) => { kitchenBg(t, '#eef3f8', '#d7e3ee'); G.bowl(W / 2, 1380, 1.7, '#fbfbf7'); G.drizzle(W / 2 - 20, 300, 1190, lt); } },
    { mode: 'gfx', t0: 4.7, t1: 6.05, draw: (lt, t) => { kitchenBg(t, '#fbf3df', '#efdcae'); G.bowl(W / 2, 1380, 1.7, '#e9c46a', () => { ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.ellipse(0, -100, 100, 22, t * 3, 0.3, 5); ctx.stroke(); }); G.drizzle(W / 2, 300, 1190, lt); } },
    { img: 'bottle', t0: 6.05, t1: 9.2, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1020, cardH: 1150 },
    { img: 'bottle', t0: 9.2, t1: 15.0, mode: 'card', z0: 0.9, z1: 1.0, cardY: 1060, cardH: 680 }
  ],
  captions: [
    { t0: 0.2, t1: 2.25, text: 'So kannst du\n*Schwarzkümmelöl*\nverwenden', pos: 'top', size: 76 },
    { t0: 2.4, t1: 3.6, text: 'über den *Salat*', pos: 'top', size: 90, color: '#16161d', box: '#fff', hl: '#c77d00' },
    { t0: 3.6, t1: 4.7, text: 'in den *Joghurt*', pos: 'top', size: 90, color: '#16161d', box: '#fff', hl: '#c77d00' },
    { t0: 4.7, t1: 6.0, text: 'ins *Dressing*', pos: 'top', size: 90, color: '#16161d', box: '#fff', hl: '#c77d00' },
    { t0: 6.05, t1: 7.6, text: '*Bio* · kaltgepresst', pos: 'top', size: 76 },
    { t0: 7.6, t1: 9.15, text: '*100 %* naturrein', pos: 'top', size: 84 }
  ],
  dings: [9.4],
  previews: [1, 3, 4.2, 5.4, 8, 12],
  overlay: t => {
    if (t < 9.2) return;
    const lt = t - 9.2;
    badge('BLACK FRIDAY', W / 2, 230, outBack(prog(lt, 0, 0.3)), '#fff', '#1b0f3a', 50);
    price(W / 2, 450, outBack(prog(lt, 0.15, 0.45)), '18,98 €', '19,98 €', 0);
    badge('250 ml', W / 2, 610, outBack(prog(lt, 0.3, 0.6)), '#e0a526', '#16161d', 46);
    shopButton(1600, lt, 0.5);
  }
};

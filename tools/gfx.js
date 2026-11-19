// Code-drawn motion graphics for the realistic ads (no AI images). Loaded after lib.js.
// All functions draw on the global ctx (1080x1920).
const G = {
  grad(c1, c2) {
    const g = ctx.createLinearGradient(0, 0, W * 0.4, H);
    g.addColorStop(0, c1); g.addColorStop(1, c2);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  },
  blobs(t, cols) { // soft moving light blobs
    cols.forEach((c, i) => {
      const x = W / 2 + Math.sin(t * 0.6 + i * 2.1) * 380, y = H / 2 + Math.cos(t * 0.45 + i * 1.7) * 600;
      const rg = ctx.createRadialGradient(x, y, 10, x, y, 620);
      rg.addColorStop(0, c); rg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
    });
  },
  text(s, x, y, size, color = '#fff', p = 1, align = 'center', weight = 900) {
    if (p <= 0) return;
    ctx.save(); ctx.translate(x, y); ctx.scale(p, p);
    ctx.font = `${weight} ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
    ctx.fillStyle = color; ctx.fillText(s, 0, 0);
    ctx.restore();
  },
  bigNumber(n, lt, color, sub) { // listicle number card
    const p = outBack(prog(lt, 0, 0.35));
    ctx.save(); ctx.translate(W / 2, 900); ctx.scale(p, p); ctx.rotate(-0.06);
    ctx.font = `900 620px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 30; ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.strokeText(String(n), 14, 24);
    ctx.fillStyle = color; ctx.fillText(String(n), 0, 0);
    ctx.restore();
    if (sub) G.text(sub, W / 2, 1380, 64, '#fff', outBack(prog(lt, 0.15, 0.45)));
  },
  clock(text, x, y, size, t, shake = 0) {
    const sx = shake ? Math.sin(t * 60) * shake : 0;
    ctx.save(); ctx.translate(x + sx, y);
    ctx.fillStyle = '#0b0d14'; rr(-size * 1.9, -size * 0.75, size * 3.8, size * 1.5, size * 0.3); ctx.fill();
    ctx.strokeStyle = '#2a2f40'; ctx.lineWidth = 10; ctx.stroke();
    ctx.font = `700 ${size}px "DejaVu Sans Mono", monospace`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.shadowColor = '#ff3b3b'; ctx.shadowBlur = 40; ctx.fillStyle = '#ff4747';
    ctx.fillText(text, 0, 4);
    ctx.restore();
    if (shake) { // ring waves
      ctx.strokeStyle = 'rgba(255,80,80,0.7)'; ctx.lineWidth = 10; ctx.lineCap = 'round';
      for (let i = 0; i < 3; i++) {
        const ph = (t * 2.5 + i / 3) % 1, r = size * 2 + ph * 220;
        ctx.globalAlpha = 1 - ph;
        ctx.beginPath(); ctx.arc(x, y, r, -0.5, 0.5); ctx.stroke();
        ctx.beginPath(); ctx.arc(x, y, r, Math.PI - 0.5, Math.PI + 0.5); ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
  },
  // side profile lying on a flat pillow; neck glows red
  neckProfile(t, cx, cy, s, good) {
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
    // mattress
    ctx.fillStyle = '#e9edf5'; rr(-520, 80, 1040, 140, 40); ctx.fill();
    // pillow
    if (good) {
      ctx.fillStyle = '#3b4252';
      ctx.beginPath(); ctx.moveTo(-430, 80); ctx.quadraticCurveTo(-420, -20, -330, -30); ctx.quadraticCurveTo(-250, -10, -230, 20);
      ctx.quadraticCurveTo(-170, -60, -60, -40); ctx.quadraticCurveTo(-20, 20, -20, 80); ctx.closePath(); ctx.fill();
    } else { ctx.fillStyle = '#f7f7f7'; rr(-440, 50, 380, 40, 18); ctx.fill(); }
    // body silhouette
    ctx.fillStyle = '#c99a7a';
    const headY = good ? -70 : 0;
    ctx.beginPath(); ctx.ellipse(-300, headY, 110, 95, good ? 0 : 0.25, 0, Math.PI * 2); ctx.fill(); // head
    ctx.beginPath(); // neck + torso
    ctx.moveTo(-210, headY + 40); ctx.quadraticCurveTo(-150, good ? 0 : 70, -80, 30);
    ctx.lineTo(480, 20); ctx.lineTo(480, 90); ctx.lineTo(-110, 90); ctx.quadraticCurveTo(-190, 100, -230, headY + 80); ctx.closePath(); ctx.fill();
    // spine line
    ctx.strokeStyle = good ? '#3ee08a' : '#ff4d4d'; ctx.lineWidth = 10; ctx.setLineDash([24, 18]); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-300, headY); ctx.quadraticCurveTo(-180, good ? -10 : 90, -60, 50); ctx.lineTo(420, 50); ctx.stroke();
    ctx.setLineDash([]);
    if (!good) { // pain pulse at the neck
      const pulse = 0.5 + 0.5 * Math.sin(t * 8);
      const rg = ctx.createRadialGradient(-160, 50, 5, -160, 50, 140 + pulse * 40);
      rg.addColorStop(0, 'rgba(255,40,40,0.85)'); rg.addColorStop(1, 'rgba(255,40,40,0)');
      ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(-160, 50, 200, 0, Math.PI * 2); ctx.fill();
    } else {
      ctx.fillStyle = '#3ee08a'; ctx.beginPath(); ctx.arc(-160, -170, 46, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 12; line([[-182, -170], [-166, -152], [-138, -190]]);
    }
    ctx.restore();
  },
  cube(x, y, s, rot = 0) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    ctx.fillStyle = '#ffffff'; ctx.strokeStyle = '#d6dbe4'; ctx.lineWidth = 3;
    rr(-30, -30, 60, 60, 8); ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(190,198,210,0.7)';
    for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.arc(-16 + rnd(i) * 32, -16 + rnd(i + 3) * 32, 3, 0, Math.PI * 2); ctx.fill(); }
    ctx.restore();
  },
  sugarPile(cx, baseY, n, p, t, sc = 1.5) { // n cubes dropping into a pyramid (widest row at the bottom)
    let base = 1; while (base * (base + 1) / 2 < n) base++;
    const pos = [];
    for (let r = 0, w = base; pos.length < n; r++, w--) for (let c = 0; c < w && pos.length < n; c++)
      pos.push([cx + (c - (w - 1) / 2) * 66 * sc, baseY - r * 62 * sc]);
    pos.forEach(([x, y], i) => {
      const d = prog(p * n, i, i + 1);
      if (d > 0) G.cube(x + (rnd(i) - .5) * 6, lerp(y - 800, y, d * d), sc, (1 - d) * 3 + (rnd(i + 2) - .5) * 0.1);
    });
  },
  chocoBar(x, y, s, rot = 0, bite = false) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    ctx.fillStyle = '#c0c4cc'; rr(-220, -90, 160, 180, 10); ctx.fill(); // foil
    ctx.fillStyle = '#5a3420'; rr(-80, -90, 320, 180, 14); ctx.fill();
    ctx.fillStyle = '#6e4129';
    for (let r = 0; r < 2; r++) for (let c = 0; c < 4; c++) { rr(-68 + c * 76, -78 + r * 86, 64, 72, 8); ctx.fill(); }
    ctx.fillStyle = '#d23a32'; rr(-260, -100, 120, 200, 10); ctx.fill(); // wrapper
    if (bite) { ctx.globalCompositeOperation = 'destination-out'; ctx.beginPath(); ctx.arc(250, -60, 50, 0, Math.PI * 2); ctx.fill(); ctx.globalCompositeOperation = 'source-over'; }
    ctx.restore();
  },
  oilDrop(t, lt) { // golden drop falling into a pool with ripples
    G.grad('#14100a', '#2e2410');
    G.blobs(t, ['rgba(255,190,60,0.25)', 'rgba(180,120,20,0.2)']);
    const poolY = 1350;
    ctx.fillStyle = '#b8860b';
    ctx.beginPath(); ctx.ellipse(W / 2, poolY, 420, 90, 0, 0, Math.PI * 2); ctx.fill();
    const sheen = ctx.createLinearGradient(0, poolY - 90, 0, poolY + 90);
    sheen.addColorStop(0, 'rgba(255,230,140,0.7)'); sheen.addColorStop(1, 'rgba(120,80,0,0.2)');
    ctx.fillStyle = sheen; ctx.beginPath(); ctx.ellipse(W / 2, poolY, 400, 80, 0, 0, Math.PI * 2); ctx.fill();
    for (let k = 0; k < 3; k++) { // drops
      const ph = (lt * 0.9 + k / 3) % 1;
      const y = lerp(250, poolY - 20, ph * ph);
      ctx.fillStyle = '#e0a526';
      ctx.beginPath(); ctx.moveTo(W / 2, y - 70); ctx.quadraticCurveTo(W / 2 + 34, y, W / 2, y + 30); ctx.quadraticCurveTo(W / 2 - 34, y, W / 2, y - 70); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.beginPath(); ctx.ellipse(W / 2 - 10, y, 6, 14, 0, 0, Math.PI * 2); ctx.fill();
      const rp = (ph + 0.15) % 1;
      ctx.strokeStyle = `rgba(255,220,120,${0.6 * (1 - rp)})`; ctx.lineWidth = 6;
      ctx.beginPath(); ctx.ellipse(W / 2, poolY, 60 + rp * 330, 14 + rp * 70, 0, 0, Math.PI * 2); ctx.stroke();
    }
    G.seeds(t, 40);
  },
  seeds(t, n) {
    ctx.fillStyle = '#0d0d0d';
    for (let i = 0; i < n; i++) {
      const x = rnd(i) * W, y = ((rnd(i + 50) * H + t * (60 + rnd(i + 9) * 80)) % (H + 100)) - 50;
      ctx.save(); ctx.translate(x, y); ctx.rotate(t + i);
      ctx.beginPath(); ctx.moveTo(0, -14); ctx.lineTo(9, 8); ctx.lineTo(-9, 8); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  },
  route(lt) { // Ägypten → Deutschland
    G.grad('#0f2a2a', '#102033');
    const a = [700, 1250], b = [380, 700];
    ctx.strokeStyle = 'rgba(255,255,255,0.15)'; ctx.lineWidth = 2;
    for (let i = 0; i < 12; i++) line([[0, 500 + i * 80], [W, 500 + i * 80]]);
    const p = ease(prog(lt, 0.2, 1.4));
    ctx.strokeStyle = '#ffd34d'; ctx.lineWidth = 10; ctx.setLineDash([26, 18]);
    ctx.beginPath();
    for (let k = 0; k <= 40 * p; k++) { const u = k / 40; const x = lerp(a[0], b[0], u), y = lerp(a[1], b[1], u) - Math.sin(u * Math.PI) * 260; k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
    ctx.stroke(); ctx.setLineDash([]);
    for (const [pt, label, d] of [[a, 'Ägypten', 0], [b, 'Deutschland', 1.2]]) {
      const q = outBack(prog(lt, d, d + 0.3));
      if (q <= 0) continue;
      ctx.save(); ctx.translate(pt[0], pt[1]); ctx.scale(q, q);
      ctx.fillStyle = '#ff4d5e'; ctx.beginPath(); ctx.arc(0, -40, 34, Math.PI, 0); ctx.lineTo(0, 30); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(0, -40, 13, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
      G.text(label, pt[0], pt[1] + 80, 54, '#fff', q);
    }
  },
  counter(v, x, y, size, color = '#fff') { G.text(Math.round(v).toLocaleString('de-DE'), x, y, size, color); },
  stars5(x, y, r, rating, p) {
    for (let i = 0; i < 5; i++) {
      const q = outBack(prog(p * 5, i, i + 1)); if (q <= 0) continue;
      ctx.save(); ctx.translate(x + (i - 2) * r * 2.3, y); ctx.scale(q, q);
      ctx.fillStyle = i + 1 <= Math.floor(rating) ? '#ffc93d' : '#ffe9b0';
      ctx.beginPath(); for (let k = 0; k < 10; k++) { const rr2 = k % 2 ? r * 0.42 : r, an = -Math.PI / 2 + k * Math.PI / 5; ctx.lineTo(Math.cos(an) * rr2, Math.sin(an) * rr2); } ctx.fill();
      ctx.restore();
    }
  },
  bowl(x, y, s, fill, items) { // white bowl with content
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(0, -100, 200, 46, 0, 0, Math.PI * 2); ctx.fill();
    if (items) items();
    ctx.fillStyle = '#fafafa'; ctx.strokeStyle = '#dde2ea'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(-215, -100); ctx.quadraticCurveTo(-200, 20, 0, 22); ctx.quadraticCurveTo(200, 20, 215, -100); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.restore();
  },
  drizzle(x, y0, y1, lt) { // oil stream from top
    ctx.strokeStyle = '#d99a1c'; ctx.lineWidth = 9; ctx.lineCap = 'round';
    const len = ease(prog(lt, 0, 0.5));
    line([[x, y0], [x + Math.sin(lt * 6) * 6, lerp(y0, y1, len)]]);
  },
  versus(rows, lt, idx) { // comparison: each row = metric with two horizontal bars
    G.grad('#16131f', '#2a1630');
    G.text('pro 50 g', W / 2, 330, 40, '#9a98a6', 1, 'center', 700);
    rows.forEach((r, i) => {
      if (i > idx) return;
      const y = 520 + i * 380;
      const p = ease(prog(i === idx ? lt : 9, 0.1, 0.9));
      const ap = outBack(prog(i === idx ? lt : 9, 0, 0.3));
      G.text(r.label, 100, y, 64, '#fff', ap, 'left');
      const maxW = 470, x0 = 100;
      const wa = Math.max(12, maxW * r.a / r.max * p), wb = Math.max(12, maxW * r.b / r.max * p);
      G.text('Schokoriegel', x0, y + 75, 34, '#b9b7c6', ap, 'left', 700);
      ctx.fillStyle = '#6b6878'; rr(x0, y + 100, wa, 56, 16); ctx.fill();
      G.text(`${r.a.toLocaleString('de-DE')} ${r.unit}`, x0 + wa + 24, y + 130, 50, '#e6e6ee', p, 'left');
      G.text('Satisbites', x0, y + 200, 34, '#ff8fc0', ap, 'left', 700);
      ctx.fillStyle = '#ff4f9a'; rr(x0, y + 225, wb, 56, 16); ctx.fill();
      G.text(`${r.b.toLocaleString('de-DE')} ${r.unit}`, x0 + wb + 24, y + 255, 54, '#fff', p, 'left');
      const win = r.better === 'low' ? r.b < r.a : r.b > r.a;
      if (win) badge('✓ besser', 920, y + 255, outBack(prog(i === idx ? lt : 9, 0.9, 1.2)), '#3ee08a', '#0b2a17', 34);
    });
  },
  nightRoom(t) {
    G.grad('#070b1c', '#1a1440');
    ctx.fillStyle = '#fff7d6'; ctx.beginPath(); ctx.arc(820, 420, 70, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#070b1c'; ctx.beginPath(); ctx.arc(850, 400, 64, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#fff';
    for (let i = 0; i < 30; i++) { ctx.globalAlpha = 0.3 + 0.7 * Math.abs(Math.sin(t * 2 + i)); ctx.beginPath(); ctx.arc(rnd(i) * W, rnd(i + 7) * 800, 2.5, 0, Math.PI * 2); ctx.fill(); }
    ctx.globalAlpha = 1;
    // sofa
    ctx.fillStyle = '#2d2a4a'; rr(120, 1350, 840, 260, 60); ctx.fill();
    ctx.fillStyle = '#3a3660'; rr(170, 1260, 740, 160, 50); ctx.fill();
    // lamp glow
    const rg = ctx.createRadialGradient(180, 1100, 10, 180, 1100, 500);
    rg.addColorStop(0, 'rgba(255,190,90,0.35)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  },
  crossOut(x, y, w, p) {
    ctx.strokeStyle = '#ff3b4d'; ctx.lineWidth = 22; ctx.lineCap = 'round';
    const q = ease(p);
    if (q > 0) line([[x - w / 2, y - w / 2], [x - w / 2 + w * Math.min(1, q * 2), y - w / 2 + w * Math.min(1, q * 2)]]);
    if (q > 0.5) line([[x + w / 2, y - w / 2], [x + w / 2 - w * (q - 0.5) * 2, y - w / 2 + w * (q - 0.5) * 2]]);
  }
};

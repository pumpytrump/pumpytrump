// "Realistic" ad engine: photo shots with camera moves, product cards on blurred backgrounds,
// TikTok captions synced to the voiceover, film grain + vignette, punch-in transitions.
// Page order: ad.js (sets window.AD) → ../tools/lib.js → ../tools/real.js
//
// AD = {
//   duration, images: { key: 'assets/x.png' },
//   shots: [{ img, t0, t1, mode: 'cover'|'card', fx, fy, z0, z1, fx1?, fy1? }],
//   captions: [{ t0, t1, text, pos: 'mid'|'top'|'low', size, box? }]   // *word* = highlighted
//   overlay: (t) => {}  // extra drawing (prices, badges, CTA) – may use lib.js helpers
// }
(() => {
  const A = window.AD;
  const imgs = {};
  let pending = 0;
  if (!Object.keys(A.images).length) setTimeout(() => { window.adReady = true; if (!/render=1/.test(location.search)) loop(); });
  for (const [k, src] of Object.entries(A.images)) {
    pending++;
    const im = new Image();
    im.onload = () => { if (--pending === 0) { window.adReady = true; if (!/render=1/.test(location.search)) loop(); } };
    im.crossOrigin = 'anonymous'; im.src = src; imgs[k] = im;
    window.IMG = imgs;
  }
  // grain tiles
  const grains = [];
  for (let g = 0; g < 6; g++) {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const x = c.getContext('2d'), d = x.createImageData(256, 256);
    for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    x.putImageData(d, 0, 0); grains.push(c);
  }
  // blurred backgrounds are cached per image
  const blurCache = {};
  function blurred(key) {
    if (blurCache[key]) return blurCache[key];
    const im = imgs[key], c = document.createElement('canvas'); c.width = W / 4; c.height = H / 4;
    const x = c.getContext('2d');
    const s = Math.max(c.width / im.width, c.height / im.height) * 1.3;
    x.filter = 'blur(10px) brightness(0.62) saturate(1.2)';
    x.drawImage(im, (c.width - im.width * s) / 2, (c.height - im.height * s) / 2, im.width * s, im.height * s);
    return (blurCache[key] = c);
  }
  function cover(im, fx, fy, z) {
    const s = Math.max(W / im.width, H / im.height) * z;
    const dw = im.width * s, dh = im.height * s;
    let x = W / 2 - fx * dw, y = H / 2 - fy * dh;
    x = Math.min(0, Math.max(W - dw, x)); y = Math.min(0, Math.max(H - dh, y));
    ctx.drawImage(im, x, y, dw, dh);
  }
  function card(key, z, lt, sh) {
    ctx.drawImage(blurred(key), 0, 0, W, H);
    const im = imgs[key];
    const maxW = sh.cardW || 960, maxH = sh.cardH || 1150;
    const s = Math.min(maxW / im.width, maxH / im.height) * z;
    const dw = im.width * s, dh = im.height * s;
    const cy = (sh.cardY || 980) + Math.sin(lt * 1.6) * 8;
    ctx.save();
    ctx.translate(W / 2, cy);
    ctx.rotate(Math.sin(lt * 1.1) * 0.01);
    ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 20;
    rr(-dw / 2, -dh / 2, dw, dh, 34); ctx.fillStyle = '#fff'; ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.save(); rr(-dw / 2, -dh / 2, dw, dh, 34); ctx.clip();
    if (sh.fx != null && sh.zoomInCard) { // zoom inside the card toward a focus point
      const zz = sh.zoomInCard(lt);
      ctx.drawImage(im, -dw / 2 - (zz - 1) * dw * sh.fx, -dh / 2 - (zz - 1) * dh * sh.fy, dw * zz, dh * zz);
    } else ctx.drawImage(im, -dw / 2, -dh / 2, dw, dh);
    ctx.restore();
    ctx.restore();
  }
  // caption with *highlight* segments
  function richCaption(c, t) {
    const p = prog(t, c.t0, c.t0 + 0.22);
    if (p <= 0 || t > c.t1) return;
    const size = c.size || 74;
    const y = c.pos === 'top' ? 330 : c.pos === 'low' ? 1480 : 1180;
    const sc = outBack(p);
    ctx.save(); ctx.translate(W / 2, y); ctx.scale(sc, sc);
    ctx.font = `900 ${size}px ${FONT}`; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    const lines = c.text.split('\n');
    lines.forEach((ln, li) => {
      const segs = ln.split('*').map((s, i) => ({ s, hl: i % 2 === 1 }));
      const total = segs.reduce((a, g) => a + ctx.measureText(g.s).width, 0);
      const ly = (li - (lines.length - 1) / 2) * size * 1.18;
      if (c.box) {
        ctx.fillStyle = c.box; rr(-total / 2 - size * 0.4, ly - size * 0.68, total + size * 0.8, size * 1.36, size * 0.28); ctx.fill();
      }
      let x = -total / 2;
      for (const g of segs) {
        const w = ctx.measureText(g.s).width;
        ctx.textAlign = 'left';
        if (!c.box) { ctx.lineWidth = size * 0.2; ctx.strokeStyle = '#000'; ctx.strokeText(g.s, x, ly); }
        ctx.fillStyle = g.hl ? (c.hl || '#ffe14d') : (c.color || '#fff');
        ctx.fillText(g.s, x, ly);
        x += w;
      }
    });
    ctx.restore();
  }
  window.renderFrame = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1; ctx.shadowBlur = 0; ctx.shadowColor = 'transparent'; ctx.filter = 'none';
    bg('#000');
    const sh = A.shots.find(s => t >= s.t0 && t < s.t1) || A.shots[A.shots.length - 1];
    const lt = t - sh.t0, k = clamp(lt / (sh.t1 - sh.t0));
    const punch = 1 + 0.1 * (1 - ease(prog(lt, 0, 0.3))) * (sh.t0 > 0 ? 1 : 0);
    const z = lerp(sh.z0 || 1, sh.z1 || 1.12, ease(k)) * punch;
    if (sh.mode === 'gfx') {
      ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(punch, punch); ctx.translate(-W / 2, -H / 2);
      sh.draw(lt, t, k); ctx.restore();
    } else if (sh.mode === 'card') card(sh.img, punch * lerp(sh.z0 || 1, sh.z1 || 1, ease(k)), lt, sh);
    else cover(imgs[sh.img], lerp(sh.fx ?? 0.5, sh.fx1 ?? sh.fx ?? 0.5, ease(k)), lerp(sh.fy ?? 0.5, sh.fy1 ?? sh.fy ?? 0.5, ease(k)), z);
    // vignette + top/bottom shade so captions read
    const vg = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.45)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    if (A.overlay) A.overlay(t);
    for (const c of A.captions) richCaption(c, t);
    // flash on cuts
    const d = lt; if (sh.t0 > 0 && d < 0.1) { ctx.fillStyle = `rgba(255,255,255,${0.55 * (1 - d / 0.1)})`; ctx.fillRect(0, 0, W, H); }
    // grain
    ctx.globalAlpha = 0.07; ctx.globalCompositeOperation = 'overlay';
    const gt = grains[Math.floor(t * 24) % grains.length];
    for (let y = 0; y < H; y += 256) for (let x = 0; x < W; x += 256) ctx.drawImage(gt, x, y);
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    // fade out at the end
    const fo = prog(t, A.duration - 0.35, A.duration); if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
  };
  function loop() {
    const start = performance.now();
    const f = now => { window.renderFrame(((now - start) / 1000) % A.duration); requestAnimationFrame(f); };
    requestAnimationFrame(f);
  }
  // little helpers for overlays
  window.badge = (text, x, y, p, bgc = '#fff', fg = INK, size = 44, rot = 0) => {
    if (p <= 0) return;
    ctx.save(); ctx.translate(x, y); ctx.scale(p, p); ctx.rotate(rot);
    ctx.font = `900 ${size}px ${FONT}`; const w = ctx.measureText(text).width + size;
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 20;
    ctx.fillStyle = bgc; rr(-w / 2, -size * 0.85, w, size * 1.7, size * 0.85); ctx.fill();
    ctx.shadowBlur = 0; ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(text, 0, 2);
    ctx.restore();
  };
  window.stars = (x, y, p, rating, label) => {
    if (p <= 0) return;
    ctx.save(); ctx.translate(x, y); ctx.scale(p, p);
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; rr(-330, -60, 660, 120, 60); ctx.fill();
    for (let i = 0; i < 5; i++) {
      ctx.fillStyle = i < Math.round(rating) ? '#ffc93d' : '#666';
      ctx.beginPath();
      for (let k = 0; k < 10; k++) { const r = k % 2 ? 11 : 26, an = -Math.PI / 2 + k * Math.PI / 5; ctx.lineTo(-260 + i * 62 + Math.cos(an) * r, Math.sin(an) * r); }
      ctx.fill();
    }
    ctx.fillStyle = '#fff'; ctx.font = `900 40px ${FONT}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText(label, 50, 2);
    ctx.restore();
  };
})();

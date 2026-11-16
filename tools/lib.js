// Shared drawing library for the stickman TikTok ads (1080x1920 canvas #c).
// Usage in an ad page: <script src="../tools/lib.js"></script><script src="scenes.js"></script>
// scenes.js calls startAd([[endTime, sceneFn], ...]).
const W = 1080, H = 1920, DUR = 20;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const FONT = '"Arial Black", "DejaVu Sans", "Liberation Sans", sans-serif';
const INK = '#16161d';
const PINK = '#fe2c55', CYAN = '#25f4ee';

// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const ease = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const outBack = t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const rnd = s => { const x = Math.sin(s * 127.1) * 43758.5453; return x - Math.floor(x); };

function rr(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function line(pts) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.stroke();
}
const limb = (p, a, len) => [p[0] + Math.sin(a) * len, p[1] + Math.cos(a) * len];

// TikTok-style caption: white text, heavy black outline, pop-in.
function caption(text, y, size, t0, t, opts = {}) {
  const p = prog(t, t0, t0 + 0.35);
  if (p <= 0) return;
  const sc = outBack(p);
  ctx.save();
  ctx.translate(W / 2, y);
  ctx.scale(sc, sc);
  ctx.rotate(opts.rot || 0);
  ctx.font = `900 ${size}px ${FONT}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round';
  const lines = text.split('\n');
  lines.forEach((ln, i) => {
    const ly = (i - (lines.length - 1) / 2) * size * 1.15;
    if (opts.box) {
      const w = ctx.measureText(ln).width + size * 0.8;
      ctx.fillStyle = opts.box;
      rr(-w / 2, ly - size * 0.68, w, size * 1.36, size * 0.3);
      ctx.fill();
      ctx.fillStyle = opts.color || INK;
      ctx.fillText(ln, 0, ly + size * 0.04);
    } else {
      ctx.lineWidth = size * 0.22;
      ctx.strokeStyle = opts.stroke || '#000';
      ctx.strokeText(ln, 0, ly);
      ctx.fillStyle = opts.color || '#fff';
      ctx.fillText(ln, 0, ly);
    }
  });
  ctx.restore();
}

// ---------- stick figure ----------
// Angles: 0 = pointing down, PI = pointing up, +PI/2 = towards +x.
function stick(o) {
  const s = o.s || 1, rot = o.rot || 0, p = o.pose;
  const cos = Math.cos(rot), sin = Math.sin(rot);
  const toWorld = q => [o.x + s * (q[0] * cos - q[1] * sin), o.y + s * (q[0] * sin + q[1] * cos)];
  ctx.save();
  ctx.translate(o.x, o.y);
  ctx.rotate(rot);
  ctx.scale(s, s);
  ctx.strokeStyle = o.color || INK;
  ctx.lineWidth = 15;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  const hip = [0, 0], sh = [0, -150], neck = [0, -172];
  if (!o.noLegs) {
    for (const [u, l] of [[p.lUL || 0, p.lLL || 0], [p.rUL || 0, p.rLL || 0]]) {
      const k = limb(hip, u, 115);
      line([hip, k, limb(k, l, 115)]);
    }
  }
  line([hip, neck]);
  const le = limb(sh, p.lUA, 95), lh = limb(le, p.lLA, 90);
  const re = limb(sh, p.rUA, 95), rh = limb(re, p.rLA, 90);
  line([sh, le, lh]);
  line([sh, re, rh]);
  if (o.band) { // fitness band on right forearm
    const a = Math.atan2(rh[1] - re[1], rh[0] - re[0]);
    const bp = [lerp(re[0], rh[0], .7), lerp(re[1], rh[1], .7)];
    ctx.save();
    ctx.translate(bp[0], bp[1]);
    ctx.rotate(a);
    ctx.fillStyle = o.bandColor || '#111';
    rr(-17, -16, 34, 32, 8); ctx.fill();
    ctx.fillStyle = o.bandGlow ? '#fff' : '#9aa';
    ctx.shadowColor = '#fff'; ctx.shadowBlur = o.bandGlow ? 18 : 0;
    rr(-8, -9, 16, 18, 3); ctx.fill();
    ctx.restore();
  }
  // head
  const hc = [0, -236], R = 62;
  ctx.fillStyle = o.headFill || '#fff';
  ctx.beginPath(); ctx.arc(hc[0], hc[1], R, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  if (o.hair === 'spiky') {
    ctx.lineWidth = 10;
    for (let i = -3; i <= 3; i++) {
      const a = Math.PI + i * 0.3;
      const b = limb(hc, a, R + 4), e = limb(hc, a + (rnd(i + (o.seed || 0)) - .5) * .4, R + 42);
      line([b, e]);
    }
  }
  ctx.lineWidth = 9;
  ctx.fillStyle = o.color || INK;
  const ey = hc[1] - 10;
  if (o.eyes === 'closed') {
    for (const ex of [-22, 22]) { ctx.beginPath(); ctx.arc(ex, ey, 11, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke(); }
  } else if (o.eyes === 'happy') {
    for (const ex of [-22, 22]) { ctx.beginPath(); ctx.arc(ex, ey + 6, 12, 1.15 * Math.PI, 1.85 * Math.PI); ctx.stroke(); }
  } else if (o.eyes === 'wide') {
    for (const ex of [-24, 24]) {
      ctx.lineWidth = 6; ctx.fillStyle = '#fff';
      ctx.beginPath(); ctx.arc(ex, ey - 4, 18, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = o.color || INK;
      ctx.beginPath(); ctx.arc(ex, ey - 4, 7, 0, Math.PI * 2); ctx.fill();
    }
  } else {
    for (const ex of [-22, 22]) { ctx.beginPath(); ctx.arc(ex, ey, 8, 0, Math.PI * 2); ctx.fill(); }
  }
  ctx.lineWidth = 8;
  const my = hc[1] + 26;
  if (o.mouth === 'o') { ctx.beginPath(); ctx.ellipse(0, my, 13, 19, 0, 0, Math.PI * 2); ctx.stroke(); }
  else if (o.mouth === 'smile') { ctx.beginPath(); ctx.arc(0, my - 14, 26, 0.18 * Math.PI, 0.82 * Math.PI); ctx.stroke(); }
  else if (o.mouth === 'grin') {
    ctx.fillStyle = o.color || INK;
    ctx.beginPath(); ctx.arc(0, my - 8, 28, 0, Math.PI); ctx.closePath(); ctx.fill();
  }
  else if (o.mouth === 'frown') { ctx.beginPath(); ctx.arc(0, my + 18, 22, 1.2 * Math.PI, 1.8 * Math.PI); ctx.stroke(); }
  else { line([[-16, my], [16, my]]); }
  if (o.brows) {
    ctx.lineWidth = 7;
    line([[-38, ey - 30], [-10, ey - 20]]);
    line([[38, ey - 30], [10, ey - 20]]);
  }
  ctx.restore();
  return { rHand: toWorld(rh), lHand: toWorld(lh), head: toWorld(hc), rElbow: toWorld(re) };
}

function bolt(x, y, s, r) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(r); ctx.scale(s, s);
  ctx.fillStyle = '#ff2a2a';
  ctx.beginPath();
  ctx.moveTo(-10, -60); ctx.lineTo(30, -60); ctx.lineTo(8, -12); ctx.lineTo(34, -12);
  ctx.lineTo(-22, 66); ctx.lineTo(-4, 6); ctx.lineTo(-30, 6); ctx.closePath();
  ctx.fill();
  ctx.restore();
}
function shade(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const f = c => Math.round(amt < 0 ? c * (1 + amt) : c + (255 - c) * amt);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
function star(x, y, r, a) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(a);
  ctx.beginPath();
  for (let i = 0; i < 8; i++) { const rad = i % 2 ? r * 0.38 : r; const an = i * Math.PI / 4; ctx.lineTo(Math.cos(an) * rad, Math.sin(an) * rad); }
  ctx.closePath(); ctx.fill(); ctx.restore();
}



function heart(x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = PINK;
  ctx.beginPath(); ctx.moveTo(0, 30);
  ctx.bezierCurveTo(-60, -10, -30, -55, 0, -25); ctx.bezierCurveTo(30, -55, 60, -10, 0, 30); ctx.fill();
  ctx.restore();
}
function chip(label, x, y, p, col) {
  if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(p, p);
  ctx.font = `900 36px ${FONT}`;
  const w = Math.max(460, ctx.measureText(label).width + 110);
  ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,.18)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 6;
  rr(-w / 2, -42, w, 84, 42); ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(-w / 2 + 44, 0, 20, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  line([[-w / 2 + 35, 0], [-w / 2 + 42, 8], [-w / 2 + 54, -8]]);
  ctx.fillStyle = INK; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.fillText(label, -w / 2 + 76, 2);
  ctx.restore();
}
function steam(x, y, t, s = 1, alpha = 0.8) {
  for (let i = 0; i < 6; i++) {
    const ph = (t * 0.7 + i / 6) % 1;
    ctx.globalAlpha = alpha * Math.sin(ph * Math.PI);
    ctx.fillStyle = '#ffffff';
    const px = x + Math.sin(ph * 6 + i) * 40 * s + (i - 2.5) * 22 * s;
    ctx.beginPath(); ctx.arc(px, y - ph * 280 * s, (24 + ph * 40) * s, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;
}
function bg(c) { ctx.fillStyle = c; ctx.fillRect(0, 0, W, H); }
function rays(cx, cy, t, col) {
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * 0.2);
  ctx.fillStyle = col;
  for (let i = 0; i < 14; i++) { ctx.rotate(Math.PI * 2 / 14); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-70, -1700); ctx.lineTo(70, -1700); ctx.closePath(); ctx.fill(); }
  ctx.restore();
}
function sparkles(cx, cy, rx, ry, t, p, col = '#ffe14d') {
  ctx.fillStyle = col;
  for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + t * 1.3; star(cx + Math.cos(a) * rx, cy + Math.sin(a) * ry, 20 * p, t * 2 + i); }
}
// Pulsing "Jetzt im TikTok Shop" button
function shopButton(y, lt, t0 = 0.5) {
  const bp = outBack(prog(lt, t0, t0 + 0.35));
  if (bp <= 0) return;
  const pulse = 1 + Math.sin(lt * 10) * 0.035;
  ctx.save(); ctx.translate(W / 2, y); ctx.scale(bp * pulse, bp * pulse);
  ctx.shadowColor = PINK; ctx.shadowBlur = 50;
  ctx.fillStyle = PINK; rr(-400, -95, 800, 190, 95); ctx.fill();
  ctx.shadowBlur = 0;
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  line([[-330, -40], [-305, -40], [-285, 25], [-215, 25], [-200, -20], [-298, -20]]);
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(-280, 45, 9, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(-222, 45, 9, 0, Math.PI * 2); ctx.fill();
  ctx.font = `900 60px ${FONT}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.fillText('Jetzt im', -170, -30);
  ctx.fillText('TikTok Shop', -170, 38);
  ctx.restore();
}
// Big price with optional struck-through old price
function price(x, y, p, now, was, rot = -0.05) {
  if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(p, p); ctx.rotate(rot);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (was) {
    ctx.fillStyle = '#ffd6dd'; ctx.font = `700 46px ${FONT}`;
    ctx.fillText('statt ' + was, 0, -90);
    const w = ctx.measureText('statt ' + was).width / 2;
    ctx.strokeStyle = '#ff5470'; ctx.lineWidth = 6; line([[-w, -90], [w, -90]]);
  }
  ctx.font = `900 120px ${FONT}`; ctx.lineWidth = 18; ctx.strokeStyle = '#000';
  ctx.strokeText(now, 0, 10); ctx.fillStyle = '#fff'; ctx.fillText(now, 0, 10);
  ctx.restore();
}
const STAND = { lUA: -0.25, lLA: -0.1, rUA: 0.25, rLA: 0.1, lUL: -0.2, lLL: -0.1, rUL: 0.2, rLL: 0.1 };
function startAd(scenes, cuts) {
  function cutFlash(t) {
    for (const c of cuts) {
      const d = Math.abs(t - c);
      if (d < 0.12) { ctx.fillStyle = `rgba(255,255,255,${1 - d / 0.12})`; ctx.fillRect(0, 0, W, H); }
    }
  }
  window.renderFrame = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.globalAlpha = 1; ctx.shadowBlur = 0; ctx.shadowColor = 'transparent'; ctx.shadowOffsetY = 0;
    for (const [end, fn] of scenes) if (t < end || end >= DUR) { fn(t); break; }
    cutFlash(t);
  };
  if (!/render=1/.test(location.search)) {
    const start = performance.now();
    const loop = now => { window.renderFrame(((now - start) / 1000) % DUR); requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  } else window.renderFrame(0);
}

// Renders ad.html to a 1080x1920, 30 fps, 20 s MP4 with a generated soundtrack.
// Usage: node render.js            -> out/fitness-tracker-tiktok-ad.mp4
//        node render.js --preview  -> out/preview-*.png stills only
// Needs: playwright (Chromium) and ffmpeg on PATH.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 20, SR = 44100;
const OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });

// ---------- soundtrack (synthesised, royalty-free) ----------
function soundtrack() {
  const n = SR * DUR, buf = new Float32Array(n);
  const add = (t0, len, fn) => {
    const s0 = Math.floor(t0 * SR), s1 = Math.min(n, s0 + Math.floor(len * SR));
    for (let i = Math.max(0, s0); i < s1; i++) buf[i] += fn((i - s0) / SR);
  };
  let seed = 1;
  const noise = () => { seed = (seed * 16807) % 2147483647; return seed / 1073741823.5 - 1; };
  const note = m => 440 * Math.pow(2, (m - 69) / 12);

  // 0–3.2 s: soft sleepy music-box notes
  [72, 76, 79, 76, 74, 71, 72].forEach((m, i) =>
    add(0.1 + i * 0.45, 1.2, t => 0.16 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 3)));

  // 3.2–7 s: loud alarm beeps
  for (let b = 3.25; b < 6.9; b += 0.25) {
    const f = (Math.round((b - 3.25) / 0.25) % 2) ? 1250 : 990;
    add(b, 0.16, t => 0.32 * Math.sign(Math.sin(2 * Math.PI * f * t)) * Math.min(1, t * 200, (0.16 - t) * 200));
  }

  // 7–20 s: upbeat 120 bpm groove (C - G - Am - F)
  const beat = 0.5, roots = [48, 43, 45, 41];
  for (let b = 7; b < 19.9; b += beat) {
    const k = Math.round((b - 7) / beat);
    add(b, 0.35, t => 0.55 * Math.sin(2 * Math.PI * (50 + 110 * Math.exp(-t * 30)) * t) * Math.exp(-t * 8)); // kick
    if (k % 2 === 1) add(b, 0.2, t => 0.22 * noise() * Math.exp(-t * 22)); // clap
    add(b + beat / 2, 0.06, t => 0.08 * noise() * Math.exp(-t * 60)); // hat
    const root = roots[Math.floor(k / 4) % 4];
    add(b, beat * 0.9, t => 0.16 * Math.sin(2 * Math.PI * note(root) * t) * Math.min(1, t * 50) * Math.exp(-t * 2)); // bass
    if (k % 4 === 0) {
      for (const iv of [12, 16, 19]) {
        const m = root + iv + (root === 45 ? (iv === 16 ? -1 : 0) : 0) + (root === 43 && iv === 16 ? -1 : 0) + (root === 41 && iv === 16 ? 0 : 0);
        add(b, 2, t => 0.045 * Math.sin(2 * Math.PI * note(m + 12) * t) * Math.min(1, t * 8) * Math.exp(-t * 1.2));
      }
    }
  }
  // whooshes on cuts
  for (const c of [7, 15, 18]) {
    let lp = 0;
    add(c - 0.35, 0.5, t => { lp += (noise() - lp) * (0.02 + t * 0.4); return 0.5 * lp * Math.sin(Math.PI * t / 0.5); });
  }
  // 11–12.9 s: gentle vibration buzz
  add(11, 1.9, t => 0.22 * Math.sin(2 * Math.PI * 160 * t) * (Math.sin(2 * Math.PI * 4 * t) > 0 ? 1 : 0));
  // 18.4 s: CTA "ding"
  for (const m of [84, 91]) add(18.4, 1.4, t => 0.18 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 3));

  // normalise + soft limit
  let peak = 0; for (const v of buf) peak = Math.max(peak, Math.abs(v));
  const out = Buffer.alloc(44 + n * 2);
  out.write('RIFF', 0); out.writeUInt32LE(36 + n * 2, 4); out.write('WAVE', 8);
  out.write('fmt ', 12); out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(1, 22);
  out.writeUInt32LE(SR, 24); out.writeUInt32LE(SR * 2, 28); out.writeUInt16LE(2, 32); out.writeUInt16LE(16, 34);
  out.write('data', 36); out.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) out.writeInt16LE(Math.round(Math.tanh(buf[i] / peak * 1.2) * 0.9 * 32767), 44 + i * 2);
  const file = path.join(OUT, 'soundtrack.wav');
  fs.writeFileSync(file, out);
  return file;
}

(async () => {
  const preview = process.argv.includes('--preview');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'ad.html') + '?render=1');
  const grab = (t, type) => page.evaluate(([t, type]) => {
    window.renderFrame(t);
    return document.getElementById('c').toDataURL(type, 0.95).split(',')[1];
  }, [t, type]);

  if (preview) {
    for (const t of [1.5, 4.5, 9, 11.8, 13.8, 16.5, 19.2]) {
      fs.writeFileSync(path.join(OUT, `preview-${t}.png`), Buffer.from(await grab(t, 'image/png'), 'base64'));
    }
    await browser.close();
    return;
  }

  const wav = soundtrack();
  const mp4 = path.join(OUT, 'fitness-tracker-tiktok-ad.mp4');
  const ff = spawn('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', wav,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  const frames = FPS * DUR;
  for (let i = 0; i < frames; i++) {
    const jpg = Buffer.from(await grab(i / FPS, 'image/jpeg'), 'base64');
    if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${frames}\n`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  await browser.close();
  console.log('Wrote', mp4);
})();

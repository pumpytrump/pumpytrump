// Generic renderer for the stickman ads that use tools/lib.js.
// Usage: node tools/render.js <ad-dir> [--preview]
// <ad-dir> must contain ad.html and config.js:
//   module.exports = { output: 'name.mp4', vo: [[1, 0.3], ...], previews: [2, 5, ...],
//                      cuts: [3.5, 7, 11, 15, 18], sfx: ({ add, noise, note, rnd01 }) => {...} }
// Voiceover lines are <ad-dir>/voiceover/l<n>.wav. Needs playwright + ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 20, SR = 44100;
const dir = path.resolve(process.argv[2] || '.');
const cfg = require(path.join(dir, 'config.js'));
const OUT = path.join(dir, 'out');
fs.mkdirSync(OUT, { recursive: true });
const run = args => new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' })
  .on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));

function soundtrack() {
  const n = SR * DUR, buf = new Float32Array(n);
  const add = (t0, len, fn) => {
    const s0 = Math.floor(t0 * SR), s1 = Math.min(n, s0 + Math.floor(len * SR));
    for (let i = Math.max(0, s0); i < s1; i++) buf[i] += fn((i - s0) / SR);
  };
  let seed = 1;
  const noise = () => { seed = (seed * 16807) % 2147483647; return seed / 1073741823.5 - 1; };
  const note = m => 440 * Math.pow(2, (m - 69) / 12);
  const rnd01 = i => { const x = Math.sin(i * 91.7) * 43758.5453; return x - Math.floor(x); };

  cfg.sfx({ add, noise, note, rnd01 }); // ad-specific effects (mostly 0–7 s)
  // 7–20 s: upbeat 120 bpm groove (C - G - Am - F)
  const beat = 0.5, roots = [48, 43, 45, 41];
  for (let b = 7; b < 19.9; b += beat) {
    const k = Math.round((b - 7) / beat);
    add(b, 0.35, t => 0.55 * Math.sin(2 * Math.PI * (50 + 110 * Math.exp(-t * 30)) * t) * Math.exp(-t * 8));
    if (k % 2 === 1) add(b, 0.2, t => 0.22 * noise() * Math.exp(-t * 22));
    add(b + beat / 2, 0.06, t => 0.08 * noise() * Math.exp(-t * 60));
    const root = roots[Math.floor(k / 4) % 4];
    add(b, beat * 0.9, t => 0.16 * Math.sin(2 * Math.PI * note(root) * t) * Math.min(1, t * 50) * Math.exp(-t * 2));
  }
  for (const c of cfg.cuts.filter(c => c >= 7)) {
    let lp = 0;
    add(c - 0.35, 0.5, t => { lp += (noise() - lp) * (0.02 + t * 0.4); return 0.5 * lp * Math.sin(Math.PI * t / 0.5); });
  }
  for (const m of [84, 91]) add(18.4, 1.4, t => 0.18 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 3));

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

async function mixVoice(music) {
  const VO = cfg.vo.map(([n, at]) => [path.join(dir, 'voiceover', `l${n}.wav`), at]).filter(([f]) => fs.existsSync(f));
  if (!VO.length) return music;
  const mixed = path.join(OUT, 'mix.wav');
  const delays = VO.map(([, at], i) =>
    `[${i + 1}:a]aresample=44100,aformat=channel_layouts=mono,adelay=${Math.round(at * 1000)}:all=1[v${i}]`).join(';');
  const voice = VO.map((_, i) => `[v${i}]`).join('') +
    `amix=inputs=${VO.length}:normalize=0,highpass=f=80,acompressor=threshold=0.2:ratio=3,volume=1.6,asplit[vo][key]`;
  const filter = `${delays};${voice};[0:a]volume=0.55[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];` +
    `[duck][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[out]`;
  await run(['-i', music, ...VO.flatMap(([f]) => ['-i', f]), '-filter_complex', filter, '-map', '[out]', mixed]);
  return mixed;
}

(async () => {
  const preview = process.argv.includes('--preview');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(dir, 'ad.html') + '?render=1');
  const grab = (t, type) => page.evaluate(([t, type]) => {
    window.renderFrame(t);
    return document.getElementById('c').toDataURL(type, 0.95).split(',')[1];
  }, [t, type]);

  if (preview) {
    const files = [];
    for (const t of cfg.previews) {
      const f = path.join(OUT, `preview-${t}.png`);
      fs.writeFileSync(f, Buffer.from(await grab(t, 'image/png'), 'base64'));
      files.push(f);
    }
    await browser.close();
    await run([...files.flatMap(f => ['-i', f]), '-filter_complex', `hstack=${files.length},scale=${files.length * 300}:-1`, path.join(OUT, 'contact.png')]);
    files.forEach(f => fs.unlinkSync(f));
    console.log('Wrote', path.join(OUT, 'contact.png'));
    return;
  }

  const wav = await mixVoice(soundtrack());
  const mp4 = path.join(OUT, cfg.output);
  const ff = spawn('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', wav,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium',
    '-c:a', 'aac', '-b:a', '192k', '-af', 'apad', '-t', String(DUR), '-movflags', '+faststart', mp4
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < FPS * DUR; i++) {
    const jpg = Buffer.from(await grab(i / FPS, 'image/jpeg'), 'base64');
    if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  await browser.close();
  for (const f of ['soundtrack.wav', 'mix.wav']) fs.rmSync(path.join(OUT, f), { force: true });
  console.log('Wrote', mp4);
})();

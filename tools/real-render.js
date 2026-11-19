// Renders a "realistic" ad (tools/real.js) to MP4.
// Usage: node tools/real-render.js <ad-dir> [--preview]
// <ad-dir>: ad.html, ad.js (window.AD), assets/voice.mp3 (ElevenLabs voiceover).
// Music: tools/music/upbeat-ad.mp3 (ElevenLabs Music, instrumental), ducked under the voice.
// SFX (whoosh on cuts, pop on captions, ding on AD.dings) are synthesised here.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, SR = 44100, VO_DELAY = 0.2;
const dir = path.resolve(process.argv[2] || '.');
const OUT = path.join(dir, 'out');
fs.mkdirSync(OUT, { recursive: true });
const run = args => new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' })
  .on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));

function sfxTrack(dur, cuts, pops, dings) {
  const n = Math.ceil(SR * dur), L = new Float32Array(n), R = new Float32Array(n);
  let seed = 7;
  const noise = () => { seed = (seed * 16807) % 2147483647; return seed / 1073741823.5 - 1; };
  const add = (t0, len, fn, pan = 0) => {
    const s0 = Math.floor(t0 * SR);
    for (let i = 0; i < len * SR && s0 + i < n; i++) if (s0 + i >= 0) {
      const v = fn(i / SR); L[s0 + i] += v * (1 - pan) ; R[s0 + i] += v * (1 + pan);
    }
  };
  for (const c of cuts) { // airy whoosh: band-passed noise sweeping up then down, panned L→R
    let lp = 0, bp = 0; const len = 0.45;
    add(c - 0.28, len, t => {
      const f = 0.02 + 0.25 * Math.sin(Math.PI * t / len);
      lp += (noise() - lp) * f; bp += (lp - bp) * 0.5;
      return 0.55 * (lp - bp) * Math.pow(Math.sin(Math.PI * t / len), 2);
    }, 0);
  }
  for (const p of pops) // soft UI pop
    add(p, 0.09, t => 0.22 * Math.sin(2 * Math.PI * (900 - 5000 * t) * t) * Math.exp(-t * 45));
  for (const d of dings) for (const [f, a] of [[1318.5, 0.2], [1975.5, 0.12], [2637, 0.06]]) // bright "ding"
    add(d, 1.6, t => a * Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 3.2));
  const out = Buffer.alloc(44 + n * 4);
  out.write('RIFF', 0); out.writeUInt32LE(36 + n * 4, 4); out.write('WAVE', 8);
  out.write('fmt ', 12); out.writeUInt32LE(16, 16); out.writeUInt16LE(1, 20); out.writeUInt16LE(2, 22);
  out.writeUInt32LE(SR, 24); out.writeUInt32LE(SR * 4, 28); out.writeUInt16LE(4, 32); out.writeUInt16LE(16, 34);
  out.write('data', 36); out.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) {
    out.writeInt16LE(Math.round(Math.tanh(L[i]) * 30000), 44 + i * 4);
    out.writeInt16LE(Math.round(Math.tanh(R[i]) * 30000), 46 + i * 4);
  }
  const f = path.join(OUT, 'sfx.wav'); fs.writeFileSync(f, out); return f;
}

(async () => {
  const preview = process.argv.includes('--preview');
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(dir, 'ad.html') + '?render=1');
  await page.waitForFunction(() => window.adReady === true);
  const meta = await page.evaluate(() => ({
    duration: AD.duration, cuts: AD.shots.map(s => s.t0).filter(t => t > 0),
    pops: AD.captions.map(c => c.t0), dings: AD.dings || [], previews: AD.previews || []
  }));
  const grab = (t, type) => page.evaluate(([t, type]) => {
    window.renderFrame(t);
    return document.getElementById('c').toDataURL(type, 0.95).split(',')[1];
  }, [t, type]);

  if (preview) {
    const files = [];
    for (const t of meta.previews) {
      const f = path.join(OUT, `preview-${t}.png`);
      fs.writeFileSync(f, Buffer.from(await grab(t, 'image/png'), 'base64')); files.push(f);
    }
    await browser.close();
    await run([...files.flatMap(f => ['-i', f]), '-filter_complex', `hstack=${files.length},scale=${files.length * 300}:-1`, path.join(OUT, 'contact.png')]);
    files.forEach(f => fs.unlinkSync(f));
    console.log('Wrote', path.join(OUT, 'contact.png'));
    return;
  }

  const D = meta.duration;
  const silent = path.join(OUT, 'video.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < Math.round(D * FPS); i++) {
    const jpg = Buffer.from(await grab(i / FPS, 'image/jpeg'), 'base64');
    if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  await browser.close();

  const sfx = sfxTrack(D, meta.cuts, meta.pops, meta.dings);
  const music = path.join(__dirname, 'music', 'upbeat-ad.mp3');
  const voice = path.join(dir, 'assets', 'voice.mp3');
  const ms = Math.round(VO_DELAY * 1000);
  const filter = [
    `[1:a]aresample=${SR},aformat=channel_layouts=stereo,adelay=${ms}|${ms},highpass=f=70,acompressor=threshold=0.15:ratio=3:attack=5:release=120,equalizer=f=3500:t=q:w=1:g=2,volume=1.5,apad=whole_dur=${D},asplit[vo][key]`,
    `[2:a]aresample=${SR},aformat=channel_layouts=stereo,atrim=0:${D},volume=0.42,afade=t=in:d=0.3,afade=t=out:st=${(D - 1.4).toFixed(2)}:d=1.4[mus]`,
    `[mus][key]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[duck]`,
    `[3:a]volume=0.8[fx]`,
    `[duck][vo][fx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.0:LRA=9[out]`
  ].join(';');
  const mp4 = path.join(OUT, path.basename(dir) + '.mp4');
  await run(['-i', silent, '-i', voice, '-stream_loop', '-1', '-i', music, '-i', sfx, '-filter_complex', filter,
    '-map', '0:v', '-map', '[out]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', String(SR), '-t', String(D), '-movflags', '+faststart', mp4]);
  for (const f of [silent, sfx]) fs.rmSync(f, { force: true });
  console.log('Wrote', mp4);
})();

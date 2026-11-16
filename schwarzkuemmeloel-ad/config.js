module.exports = {
  output: 'schwarzkuemmeloel-tiktok-ad.mp4',
  cuts: [3.5, 7, 11, 15, 18],
  vo: [[1, 0.3], [2, 3.7], [3, 7.2], [4, 11.15], [5, 15.1], [6, 18.15]],
  previews: [2.5, 6, 9, 11.8, 14, 17, 19.3],
  sfx: ({ add, noise, note }) => {
    // 0–3.5 s: shop ambience + "hmm?" two-note question
    { let lp = 0; add(0, 3.5, t => { lp += (noise() - lp) * 0.05; return 0.25 * lp; }); }
    [[1.0, 67], [1.25, 71]].forEach(([at, m]) => add(at, 0.3, t => 0.14 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 6)));
    // 3.5–7 s: three "wrong" buzzers
    for (let i = 0; i < 3; i++) add(3.85 + i * 0.7, 0.3, t => 0.18 * Math.sign(Math.sin(2 * Math.PI * 160 * t)) * Math.exp(-t * 6));
    // 11–13.6 s: press thumps + drips
    for (let b = 11.1; b < 13.5; b += 0.39) add(b, 0.15, t => 0.25 * Math.sin(2 * Math.PI * 70 * t) * Math.exp(-t * 20));
    for (let b = 11.3; b < 15; b += 0.55) add(b, 0.12, t => 0.12 * Math.sin(2 * Math.PI * (900 - t * 3000) * t) * Math.exp(-t * 30));
  }
};

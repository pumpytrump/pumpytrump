module.exports = {
  output: 'flavour-pulver-tiktok-ad.mp4',
  cuts: [3.5, 7, 11, 15, 18],
  vo: [[1, 0.3], [2, 3.7], [3, 7.2], [4, 11.15], [5, 15.1], [6, 18.15]],
  previews: [2, 5, 9, 11.6, 12.8, 14, 17, 19.3],
  sfx: ({ add, noise, note }) => {
    // 0–3.5 s: bored "wah-wah"
    [[1.2, 60], [1.6, 58]].forEach(([at, m]) => add(at, 0.45, t => 0.15 * Math.sin(2 * Math.PI * note(m) * t * (1 - t * 0.05)) * Math.exp(-t * 4)));
    // 3.5–7 s: alarm buzzer on "KCAL !!"
    add(4.0, 0.5, t => 0.2 * Math.sign(Math.sin(2 * Math.PI * 140 * t)) * Math.exp(-t * 3));
    // 7.05 s: boom for the reveal
    add(7.0, 0.8, t => 0.6 * Math.sin(2 * Math.PI * (45 + 80 * Math.exp(-t * 10)) * t) * Math.exp(-t * 4) + 0.2 * noise() * Math.exp(-t * 12));
    // 11.2 s powder "pfff", stirring, 13.5 s happy chime
    add(11.6, 0.4, t => 0.15 * noise() * Math.exp(-t * 8));
    for (let b = 12.2; b < 13.4; b += 0.17) add(b, 0.08, t => 0.06 * noise() * Math.exp(-t * 40));
    for (const m of [76, 79, 84]) add(13.5, 1.2, t => 0.1 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 2.5));
  }
};

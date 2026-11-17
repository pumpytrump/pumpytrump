module.exports = {
  output: 'chunky-flavour-tiktok-ad.mp4',
  cuts: [3.5, 7, 11, 15, 18],
  vo: [[1, 0.3], [2, 3.7], [3, 7.2], [4, 11.15], [5, 15.1], [6, 18.15]],
  previews: [2, 5.5, 9, 11.7, 14, 17, 19.3],
  sfx: ({ add, noise, note }) => {
    // 0–3 s: sugar cubes plopping into coffee
    for (let i = 0; i < 16; i++) add(0.55 + i * 0.15, 0.12, t => 0.18 * Math.sin(2 * Math.PI * (600 - t * 2500) * t) * Math.exp(-t * 30));
    // 3.5–7 s: rising pile rumble + buzzer on "200 kcal"
    add(3.6, 1.0, t => 0.15 * noise() * t * Math.exp(-t * 1.5));
    add(4.45, 0.5, t => 0.2 * Math.sign(Math.sin(2 * Math.PI * 140 * t)) * Math.exp(-t * 3));
    // 11–13.5 s: powder sprinkle + stirring, 13.5 s happy chime
    add(11.8, 0.4, t => 0.12 * noise() * Math.exp(-t * 8));
    for (let b = 12.3; b < 13.4; b += 0.17) add(b, 0.08, t => 0.06 * noise() * Math.exp(-t * 40));
    for (const m of [76, 79, 84]) add(13.5, 1.2, t => 0.1 * Math.sin(2 * Math.PI * note(m) * t) * Math.exp(-t * 2.5));
  }
};

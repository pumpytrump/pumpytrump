module.exports = {
  output: 'koffein-pouches-tiktok-ad.mp4',
  cuts: [3.5, 7, 11, 15, 18],
  vo: [[1, 0.3], [2, 3.7], [3, 7.2], [4, 11.15], [5, 15.1], [6, 18.15]],
  previews: [2, 5.5, 9, 11.6, 14, 17, 19.3],
  sfx: ({ add, noise, note }) => {
    // 0–3.5 s: slow ticking clock + yawn-ish low tone
    for (let b = 0.2; b < 3.4; b += 0.5) add(b, 0.03, t => 0.25 * noise() * Math.exp(-t * 200));
    add(1.2, 1.2, t => 0.12 * Math.sin(2 * Math.PI * (220 - t * 80) * t) * Math.sin(Math.PI * t / 1.2));
    // 3.5–7 s: cups clinking + jittery tremolo
    for (let i = 0; i < 5; i++) add(3.55 + i * 0.45, 0.25, t => 0.2 * Math.sin(2 * Math.PI * (1800 + i * 120) * t) * Math.exp(-t * 25));
    add(4.5, 2.4, t => 0.06 * Math.sin(2 * Math.PI * 330 * t) * Math.sin(2 * Math.PI * 18 * t));
    // 12 s: "power-up" sweep when the focus kicks in
    add(13.1, 0.6, t => 0.14 * Math.sin(2 * Math.PI * (300 + t * 1500) * t) * Math.sin(Math.PI * t / 0.6));
  }
};

# Fitness-Tracker – TikTok Shop ad (20 s, 9:16)

A stickman shows why a vibration-alarm fitness band beats a loud phone alarm.

| Time | Scene |
|---|---|
| 0–3 s | Hook: asleep at night – "Jeden Morgen dasselbe Drama..." |
| 3–7 s | Loud phone alarm wakes everyone – "LAUTER HANDYALARM" |
| 7–11 s | Stickman reveals the band – "Die Lösung: Fitness-Tracker mit Vibrationsalarm" |
| 11–15 s | Band vibrates, only he wakes up – "Sanft aufwachen" |
| 15–18 s | Walking, step counter, features (vibration alarm, step counter, LED time, USB, black & pink) |
| 18–20 s | CTA – "Jetzt im TikTok Shop", "Tippe auf den Warenkorb" |

- `ad.html` – the animation (open in a browser to preview, loops).
- `render.js` – exports `out/fitness-tracker-tiktok-ad.mp4` (1080×1920, 30 fps, H.264 + AAC, synthesised royalty-free soundtrack).

```bash
node render.js            # full MP4
node render.js --preview  # still frames only
```
Requires Node, Playwright (Chromium) and ffmpeg. Text is in German; edit the `caption(...)` calls in `ad.html` to change it.

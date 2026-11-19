# Stickman TikTok ad tools

Shared code for the ads in `koffein-pouches-ad/`, `flavour-pulver-ad/`, `schwarzkuemmeloel-ad/`.

- `lib.js` – stick figure, captions, chips, price, TikTok Shop button, scene runner (`startAd`).
- `render.js` – `node tools/render.js <ad-dir> [--preview]` renders `<ad-dir>/out/*.mp4` (1080×1920, 30 fps, 20 s) with
  a generated soundtrack + the voiceover in `<ad-dir>/voiceover/l1..l6.wav` (music ducks under the voice).
- `tts.sh` – `tools/tts.sh <de_DE-thorsten-high.onnx> <ad-dir>` regenerates the voiceover from `voiceover/lines.txt`.

Each ad dir: `ad.html` (loads `lib.js` + `scenes.js`), `scenes.js`, `config.js` (output name, voice timings, sound effects).
Prices are hard-coded in each `scenes.js` (`scene6`) – update them when offers end.

## Realistic style (`real.js` + `real-render.js`)

Used by `nackenkissen-ad/`, `oel-250ml-ad/`, `satisbites-ad/`: real product photos (cropped from the shop listing) and
AI photos (ElevenLabs image generation) with camera moves, punch-in cuts, film grain, captions synced to the voice.

- `node tools/real-render.js <ad-dir> [--preview]` → `<ad-dir>/out/<ad-dir>.mp4`
- Each ad dir: `ad.html`, `ad.js` (shots, captions, overlay), `assets/` (photos + `voice.mp3` from ElevenLabs, voice "Ben").
- Music: `tools/music/upbeat-ad.mp3` (ElevenLabs Music, instrumental), ducked under the voice; mix normalised to −14 LUFS.
- `assets/voice-take2.mp3` is the alternative take – rename it to `voice.mp3` to use it.

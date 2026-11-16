# Stickman TikTok ad tools

Shared code for the ads in `koffein-pouches-ad/`, `flavour-pulver-ad/`, `schwarzkuemmeloel-ad/`.

- `lib.js` – stick figure, captions, chips, price, TikTok Shop button, scene runner (`startAd`).
- `render.js` – `node tools/render.js <ad-dir> [--preview]` renders `<ad-dir>/out/*.mp4` (1080×1920, 30 fps, 20 s) with
  a generated soundtrack + the voiceover in `<ad-dir>/voiceover/l1..l6.wav` (music ducks under the voice).
- `tts.sh` – `tools/tts.sh <de_DE-thorsten-high.onnx> <ad-dir>` regenerates the voiceover from `voiceover/lines.txt`.

Each ad dir: `ad.html` (loads `lib.js` + `scenes.js`), `scenes.js`, `config.js` (output name, voice timings, sound effects).
Prices are hard-coded in each `scenes.js` (`scene6`) – update them when offers end.

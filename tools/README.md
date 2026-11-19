# Stickman TikTok ad tools

Shared code for the ads in `koffein-pouches-ad/`, `flavour-pulver-ad/`, `schwarzkuemmeloel-ad/`.

- `lib.js` – stick figure, captions, chips, price, TikTok Shop button, scene runner (`startAd`).
- `render.js` – `node tools/render.js <ad-dir> [--preview]` renders `<ad-dir>/out/*.mp4` (1080×1920, 30 fps, 20 s) with
  a generated soundtrack + the voiceover in `<ad-dir>/voiceover/l1..l6.wav` (music ducks under the voice).
- `tts.sh` – `tools/tts.sh <de_DE-thorsten-high.onnx> <ad-dir>` regenerates the voiceover from `voiceover/lines.txt`.

Each ad dir: `ad.html` (loads `lib.js` + `scenes.js`), `scenes.js`, `config.js` (output name, voice timings, sound effects).
Prices are hard-coded in each `scenes.js` (`scene6`) – update them when offers end.

## Realistic style (`real.js` + `gfx.js` + `real-render.js`)

Used by `nackenkissen-ad/`, `oel-250ml-ad/`, `satisbites-ad/` – 3 variants each. Visuals are 100 % code:
product photos from the shop listing + code-drawn motion graphics (`gfx.js`). Only the voice comes from ElevenLabs.

- `node tools/real-render.js <ad-dir> v1|v2|v3 [--preview]` → `<ad-dir>/out/<ad-dir>-v1.mp4` …
- Each ad dir: `ad.html` (`?v=v2` picks the variant), `ad-v1.js` … `ad-v3.js` (shots, captions, overlay),
  `assets/` (product photos + `voice-v1.mp3` … from ElevenLabs, voice "Ben").
- Shot modes: photo `cover` (camera move), `card` (photo on blurred background), `gfx` (code graphics via `draw(lt, t)`).
- Music: `tools/music/upbeat-ad.mp3` (made earlier with ElevenLabs Music), ducked under the voice; mix at −14 LUFS.
  Delete or replace the file to change the music.

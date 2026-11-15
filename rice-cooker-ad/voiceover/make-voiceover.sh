#!/usr/bin/env bash
# Regenerates the German voiceover with Piper (free, offline TTS).
#   pip install piper-tts ; model: huggingface.co/rhasspy/piper-voices  de/de_DE/thorsten/high
# Usage: ./make-voiceover.sh /path/to/de_DE-thorsten-high.onnx
set -euo pipefail
MODEL="$1"; cd "$(dirname "$0")"
say() { echo "$2" | python3 -m piper -m "$MODEL" -f "$1" --length-scale "$3"; }
say l1.wav "Dein Reis kocht schon wieder über?" 0.9
say l2.wav "Und unten ist alles angebrannt. Schon wieder." 0.9
say l3.wav "Die Lösung: dieser Reiskocher und Dampfgarer mit Keramikbeschichtung!" 0.85
say l4.wav "Reis und Wasser rein, Knopf drücken, fertig. Perfekter Reis!" 0.88
say l5.wav "Mit Warmhaltefunktion. In Schwarz, Weiß und Grau." 0.88
say l6.wav "Jetzt im TikTok Shop sichern!" 0.9

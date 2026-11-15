#!/usr/bin/env bash
# Regenerates the German voiceover lines with Piper (free, offline TTS).
#   pip install piper-tts
#   download de_DE-thorsten-high.onnx + .json from huggingface.co/rhasspy/piper-voices (de/de_DE/thorsten/high)
# Usage: ./make-voiceover.sh /path/to/de_DE-thorsten-high.onnx
set -euo pipefail
MODEL="$1"; cd "$(dirname "$0")"
say() { echo "$2" | python3 -m piper -m "$MODEL" -f "$1" --length-scale "$3"; }
say l1.wav "Jeden Morgen dasselbe Drama..." 0.92
say l2.wav "Der Handywecker brüllt, und das ganze Haus ist wach." 0.92
say l3.wav "Die Lösung? Dieser Fitness-Tracker mit Vibrationsalarm!" 0.92
say l4.wav "Er vibriert ganz sanft am Handgelenk. Nur du wachst auf." 0.92
say l5.wav "Dazu Schrittzähler, LED-Uhrzeit und USB-Aufladung." 0.8
say l6.wav "Jetzt im TikTok Shop holen!" 0.92

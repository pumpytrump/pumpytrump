#!/usr/bin/env bash
# Regenerates the German voiceover with Piper (free, offline TTS).
#   pip install piper-tts ; model: huggingface.co/rhasspy/piper-voices  de/de_DE/thorsten/high
# Usage: ./make-voiceover.sh /path/to/de_DE-thorsten-high.onnx
set -euo pipefail
MODEL="$1"; cd "$(dirname "$0")"
say() { echo "$2" | python3 -m piper -m "$MODEL" -f "$1" --length-scale "$3"; }
say l1.wav "Du sitzt auf dem Klo, und das Papier ist leer?" 0.88
say l2.wav "Und im Schrank? Auch nichts mehr." 0.9
say l3.wav "Die Lösung: Vierzig Rollen auf einmal!" 0.9
say l4.wav "Drei Lagen, schön weich, und das reicht ewig." 0.9
say l5.wav "Nur einunddreißig Cent pro Rolle. Nie wieder ohne!" 0.88
say l6.wav "Jetzt im TikTok Shop holen!" 0.9

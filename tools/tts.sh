#!/usr/bin/env bash
# German TTS with Piper (free, offline).  pip install piper-tts
# Model: huggingface.co/rhasspy/piper-voices -> de/de_DE/thorsten/high/de_DE-thorsten-high.onnx (+ .json)
# Usage: tools/tts.sh <model.onnx> <ad-dir>   (reads <ad-dir>/voiceover/lines.txt: "speed|text" per line)
set -euo pipefail
MODEL="$1"; DIR="$2/voiceover"; i=0
while IFS='|' read -r speed text; do
  [ -z "$text" ] && continue; i=$((i+1))
  echo "$text" | python3 -m piper -m "$MODEL" -f "$DIR/l$i.wav" --length-scale "$speed" 2>/dev/null
  printf 'l%s %ss  %s\n' "$i" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DIR/l$i.wav")" "$text"
done < "$DIR/lines.txt"

#!/bin/bash
# renders projects listed in lib3d/queue.txt one after another (re-reads the list after each job)
cd "$(dirname "$0")/.."
while true; do
  next=""
  for d in $(cat lib3d/queue.txt 2>/dev/null); do
    [ -f "$d/out/.done" ] && continue
    next=$d; break
  done
  if [ -z "$next" ]; then sleep 30; continue; fi
  while pgrep -f "scene.py --frames" >/dev/null; do sleep 20; done
  (cd $next && mkdir -p out && python3 scene.py --frames 0-393 --res 1280 --samples 12 >> out/render.log 2>&1 && \
     [ $(ls out/frames/[0-9]*.png | wc -l) -ge 394 ] && touch out/.done)
done

#!/bin/bash
# showcase v2 render queue: full-quality frames (810x1440, 16 samples) then comp -> out/<n>_<id>_3d.mp4
cd "$(dirname "$0")/.."
for d in $(cat lib3d/queue_sc.txt); do
  [ -f "$d/out/.done" ] && continue
  while pgrep -f "scene.py --frames" >/dev/null; do sleep 30; done
  fr=$(python3 -c "import json;print(json.load(open('$d/spec.json'))['frames'])"); n=$(( ${fr#*-} + 1 ))
  mkdir -p $d/out
  (cd $d && python3 scene.py --frames $fr --res 1440 --samples 16 >> out/render.log 2>&1)
  if [ $(ls $d/out/frames/[0-9]*.png 2>/dev/null | wc -l) -ge $n ]; then
    (cd $d && python3 comp.py >> out/comp.log 2>&1) && touch $d/out/.done
  fi
done
echo ALLDONE > lib3d/queue_sc.finished

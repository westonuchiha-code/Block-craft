#!/bin/bash
# regression suite: runs every test script, prints exit status + last line
cd /tmp
for t in sv gpu delve guild law art gait sh2 sh4 sh5 fe sc bed door dd bb cs fu mg mg2 gun old og2 mino ch tp3 uw2 us3 bt wk2 wk5 wk7 tr2 lt lt2 rn3 cl hf; do
  out=$(timeout 420 python3 -u $t.py 2>&1); rc=$?
  bad=""; echo "$out" | grep -q "Traceback\|Error:" && bad="ERR"
  echo "$t rc=$rc $bad | $(echo "$out" | tail -1 | cut -c1-110)"
done

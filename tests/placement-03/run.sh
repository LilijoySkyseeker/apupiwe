#!/usr/bin/env bash
# Placement 03: medians, start, two seeds at keep 0.03 without the vowel bonus, report. Resumable: rerun.
set -e
cd "$(dirname "$0")"
py() { direnv exec ../.. python3 "$@"; }
py place.py medians > logs/medians.log 2>&1
OMP_NUM_THREADS=8 py place.py start --no-vbonus > logs/start.log 2>&1
export OMP_NUM_THREADS=8
for s in 1 2; do py place.py descend $s --keep 0.03 --no-vbonus > logs/descend-$s.log 2>&1 & done
wait
py report.py --keep 0.03 --no-vbonus > logs/report.out 2>&1
echo finished

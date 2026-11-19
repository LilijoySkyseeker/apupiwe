#!/usr/bin/env bash
# The keep sweep (placement-02): one run per keep value and seed, in parallel. Resumable: rerun this script.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
for ks in "0 1" "0.03 1" "0.03 2" "0.1 1" "0.1 2" "0.3 1" "0.3 2"; do
  set -- $ks
  direnv exec ../.. python3 place.py descend "$2" --keep "$1" > "logs/descend-k$1-$2.log" 2>&1 &
done
wait

#!/usr/bin/env bash
# Dry run 04: re-optimise the applied layer with the accent mergers as hard rules (SW_SOFT=1), name locked,
# keep 0.005 / 0.01 / 0.02, seeds 1-3; control without the mergers. Skips runs whose output exists.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
py() { direnv exec ../.. python3 "$@"; }
{
for k in 0.005 0.01 0.02; do for s in 1 2 3; do
  o=runs/soft-k$k-$s.tsv; [ -f $o ] || echo "SW_SOFT=1 direnv exec ../.. python3 rebuild.py reopt --layer today.tsv --lock OF,ALL --keep $k --seed $s --out $o > logs/soft-k$k-$s.log 2>&1"
done; done
o=runs/control-k0.01-1.tsv; [ -f $o ] || echo "direnv exec ../.. python3 rebuild.py reopt --layer today.tsv --lock OF,ALL --keep 0.01 --seed 1 --out $o > logs/control-k0.01-1.log 2>&1"
} | xargs -P 10 -I{} sh -c '{}'
echo finished

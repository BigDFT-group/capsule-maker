#!/bin/bash
# Restart check, part 2: reuse the data dir written in restart_test (full copy).
set -uo pipefail
cd ~/projects/capsule-6a-ET && source bigdft_env.sh
cd restart_test
N=6a_S1_S0_pbe_h0.45_r5-8
rm -rf data-b_$N log-b_$N.yaml debug
cp -r data-a_$N data-b_$N && rm -f data-b_$N/atomic_orbitals* data-b_$N/time-*
export OMP_NUM_THREADS=4
timeout 100 mpirun -np 16 --map-by slot:PE=4 bigdft -n b_$N > b.out 2>&1; echo "restart run exit=$?"
grep -E "^ *iter:" log-a_$N.yaml | tail -1 | cut -c1-90
grep -E "^ *iter:" log-b_$N.yaml | cut -c1-90
grep -m1 -E "^ *Energy \(Hartree\)" log-a_$N.yaml log-b_$N.yaml
grep -A3 "Additional Info" log-b_$N.yaml | head

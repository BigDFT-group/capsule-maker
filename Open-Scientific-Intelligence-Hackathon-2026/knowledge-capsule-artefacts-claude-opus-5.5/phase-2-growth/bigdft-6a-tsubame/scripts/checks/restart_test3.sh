#!/bin/bash
# Free-trial check: inputpsiid 2 restart from S1 wavefunctions at a displaced geometry
# (constrained T1 minimum, max displacement 0.56 A), using cheap PBE S0.
set -uo pipefail
cd ~/projects/capsule-6a-ET && source bigdft_env.sh
rm -rf restart_test3 && mkdir restart_test3 && cd restart_test3
N=t3_cgT1_S0_pbe
sed 's/^  ixc: PBE0$/  ixc: PBE/' ../inputs_pbe0c/6a_cgT1_S0_pbe0_h0.35_r6-9.yaml > $N.yaml
cp -r ../runs_wf/6a_S1_S0_pbe_h0.35_r6-9/data-6a_S1_S0_pbe_h0.35_r6-9 data-$N; rm -f data-$N/atomic_orbitals* data-$N/time-*
export OMP_NUM_THREADS=4
timeout 140 mpirun -np 20 --map-by slot:PE=4 bigdft -n $N > out.txt 2>&1; echo "exit=$?"
grep -m3 -iE "reformat|Displacement|moved|restart" log-$N.yaml
grep -E "^ *iter:" log-$N.yaml | head -3 | cut -c1-90; grep -E "^ *iter:" log-$N.yaml | tail -1 | cut -c1-90
grep -A2 "Additional Info" log-$N.yaml | head -4

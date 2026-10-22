#!/bin/bash
# Free-trial check of wavefunction output + restart (inputpsiid 2) on a cheap S0 PBE case.
set -uo pipefail
cd ~/projects/capsule-6a-ET && source bigdft_env.sh
rm -rf restart_test && mkdir restart_test && cd restart_test
N=6a_S1_S0_pbe_h0.45_r5-8
awk '{print} /^mix: / {print "output: {orbitals: binary}"}' ../bigdft/inputs/$N.yaml > a_$N.yaml
export OMP_NUM_THREADS=4
mpirun -np 16 --map-by slot:PE=4 bigdft -n a_$N > a.out 2>&1; echo "write run exit=$?"
ls data-a_$N | head -3; ls data-a_$N | wc -l
mkdir -p data-b_$N && cp data-a_$N/wavefunction* data-b_$N/
awk '{print} /^  gnrm_cv: 1.0e-05$/ {print "  inputpsiid: 2"}' ../bigdft/inputs/$N.yaml > b_$N.yaml
timeout 60 mpirun -np 16 --map-by slot:PE=4 bigdft -n b_$N > b.out 2>&1; echo "restart run exit=$?"
grep -m3 -iE "Input wavefunctions|Reading|inputpsiid|disk" log-b_$N.yaml
grep -E "^ *iter:" log-a_$N.yaml | tail -1 | cut -c1-90
grep -E "^ *iter:" log-b_$N.yaml | head -3 | cut -c1-90

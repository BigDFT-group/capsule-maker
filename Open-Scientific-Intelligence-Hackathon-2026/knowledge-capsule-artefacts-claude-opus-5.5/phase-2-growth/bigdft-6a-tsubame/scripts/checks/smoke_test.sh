#!/bin/bash
# Free-trial smoke test: (1) re-run the memory-estimation dry run of all 24 Phase 2
# inputs on TSUBAME with this build, (2) check that an MPI BigDFT launch starts
# (correct number of MPI tasks, 226 electrons, nspin 2 for T1) for ~60 s.
set -uo pipefail
cd ~/projects/capsule-6a-ET
source bigdft_env.sh
which mpirun bigdft bigdft-tool python
mkdir -p dryrun_t4 && cd dryrun_t4
for f in ../bigdft/inputs/6a_S1_*.yaml; do
  n=$(basename $f .yaml); cp $f $n.yaml
  timeout 20 bigdft-tool -a memory-estimation --name=$n -n 16 > mem-$n.txt 2>&1
  echo "$n exit=$? $(grep -m1 -E 'Estimated Memory Peak|Total Number of Electrons' -h mem-$n.txt | tr -s ' ')"
done
cd .. && mkdir -p launch_t4 && cd launch_t4
cp ../bigdft/inputs/6a_S1_T1_pbe_h0.45_r5-8.yaml .
export OMP_NUM_THREADS=4
timeout 70 mpirun -np 16 --map-by slot:PE=4 bigdft -n 6a_S1_T1_pbe_h0.45_r5-8 > stdout.txt 2>&1
echo "launch exit=$? (124 = stopped by timeout, expected)"
grep -m6 -E "Number of MPI tasks|OpenMP threads|Total Number of Electrons|Spin-polarized|Number of Orbitals|Electrons spin up" log-*.yaml stdout.txt
grep -E "^ *- *\{ *#|iter:" log-*.yaml | tail -3

#!/bin/bash
# Run one BigDFT input per array task. Usage (Grid Engine array): run_array.sh LIST
#   LIST: file of input names (<INDIR>/<NAME>.yaml), task i runs line i.
#   Env: INDIR (default bigdft/inputs), RUNDIR (default runs), NP (MPI, default 20), OMP (default 4).
# Adapted from the capsule's procedures/run_bigdft.slurm for TSUBAME4 (mpirun,
# not srun; check 'Number of MPI tasks' in the log). Inputs were dry-run-validated.
set -euo pipefail
cd ~/projects/capsule-6a-ET
LIST=$1
INDIR=${INDIR:-bigdft/inputs}
RUNDIR=${RUNDIR:-runs}
NAME=$(sed -n "${SGE_TASK_ID}p" "$LIST")
source bigdft_env.sh
export OMP_NUM_THREADS=${OMP:-4}
NP=${NP:-20}
mkdir -p $RUNDIR/$NAME
cp $INDIR/$NAME.yaml $RUNDIR/$NAME/
cd $RUNDIR/$NAME
echo "task $SGE_TASK_ID: $INDIR/$NAME on $(hostname), $NP MPI x $OMP_NUM_THREADS OMP, start $(date -Is)"
~/projects/capsule-6a-ET/memwatch.sh > memwatch.log 2>&1 &
MW=$!
/usr/bin/time -v mpirun -np $NP --map-by slot:PE=$OMP_NUM_THREADS bigdft -n $NAME > stdout.txt 2> time.txt
kill $MW 2>/dev/null || true
echo "end $(date -Is)"; sort -t= -k3 -n memwatch.log | tail -1; grep -E "Maximum resident set size|Elapsed \(wall" time.txt

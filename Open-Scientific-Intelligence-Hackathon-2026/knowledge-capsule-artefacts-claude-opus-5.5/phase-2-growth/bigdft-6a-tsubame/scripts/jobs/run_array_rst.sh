#!/bin/bash
# As run_array.sh, but first copies the converged PBE data dir (wavefunctions, glr.dat)
# from $SRCDIR/<PBE name>/data-<PBE name> to data-<NAME>, for an inputpsiid: 2 restart.
# The PBE name is NAME with "_pbe0_" replaced by "_pbe_".
set -euo pipefail
cd ~/projects/capsule-6a-ET
LIST=$1; INDIR=${INDIR:?}; RUNDIR=${RUNDIR:?}; SRCDIR=${SRCDIR:?}
NAME=$(sed -n "${SGE_TASK_ID}p" "$LIST"); SRC=${NAME/_pbe0_/_pbe_}
source bigdft_env.sh
export OMP_NUM_THREADS=${OMP:-4}; NP=${NP:-20}
mkdir -p $RUNDIR/$NAME
cp $INDIR/$NAME.yaml $RUNDIR/$NAME/
cd $RUNDIR/$NAME
rm -rf data-$NAME && cp -r ~/projects/capsule-6a-ET/$SRCDIR/$SRC/data-$SRC data-$NAME
rm -f data-$NAME/atomic_orbitals* data-$NAME/time-*
test -s data-$NAME/glr.dat && test -s data-$NAME/wavefunction.yaml
echo "task $SGE_TASK_ID: $INDIR/$NAME (restart from $SRCDIR/$SRC) on $(hostname), $NP MPI x $OMP_NUM_THREADS OMP, start $(date -Is)"
~/projects/capsule-6a-ET/memwatch.sh > memwatch.log 2>&1 &
MW=$!
/usr/bin/time -v mpirun -np $NP --map-by slot:PE=$OMP_NUM_THREADS bigdft -n $NAME > stdout.txt 2> time.txt
kill $MW 2>/dev/null || true
echo "end $(date -Is)"; sort -t= -k3 -n memwatch.log | tail -1; grep -E "Maximum resident set size|Elapsed \(wall" time.txt

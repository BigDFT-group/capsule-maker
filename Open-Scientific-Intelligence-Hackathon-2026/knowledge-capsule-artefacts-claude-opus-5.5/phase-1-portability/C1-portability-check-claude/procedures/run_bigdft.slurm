#!/bin/bash
# Run one BigDFT input from bigdft/inputs on a Slurm CPU cluster.
#   sbatch --job-name=<NAME> --ntasks=<MPI> --cpus-per-task=<OMP> procedures/run_bigdft.slurm <NAME>
# Submit from the capsule-root copy on the cluster after "mkdir -p runs" (Slurm needs the --output directory). Only for inputs that passed procedures/dry_run.py.
# Site-specific: the module names below are the ones used for this study (BigDFT 1.9.5, OpenMPI 5.0.7).
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --output=runs/%x.%j.out
set -euo pipefail
NAME=$1
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module purge
module load openmpi/5.0.7 bigdft/rho0
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
mkdir -p runs/$NAME
cp bigdft/inputs/$NAME.yaml runs/$NAME/
cd runs/$NAME
# Not srun: OpenMPI 5 needs PMIx, this Slurm offers only pmi2, so srun starts N independent singletons.
mpirun -np $SLURM_NTASKS --map-by slot:PE=$OMP_NUM_THREADS bigdft -n $NAME

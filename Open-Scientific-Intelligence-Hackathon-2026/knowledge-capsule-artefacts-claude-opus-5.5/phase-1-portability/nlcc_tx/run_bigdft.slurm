#!/bin/bash
# Run one input from nlcc_tx/inputs on the local Slurm node (adapted from C1 procedures/run_bigdft.slurm).
#   cd nlcc_tx && sbatch --job-name=<NAME> --ntasks=<MPI> --cpus-per-task=<OMP> --mem=<MEM> run_bigdft.slurm <NAME>
# Only for inputs that passed dry_run.py. Local BigDFT 1.9.5 build instead of the cluster module.
#SBATCH --nodes=1
#SBATCH --output=runs/%x.%j.out
NAME=$1
BIGDFT_ROOT=/home/elliot/Softwares/bigdft/build/install/bin
source $BIGDFT_ROOT/bigdftvars.sh  # before set -u: the vars script uses unset variables
set -euo pipefail
export PATH=/opt/software/openmpi/5.0.7/bin:$BIGDFT_ROOT:$PATH
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
mkdir -p runs/$NAME
cp inputs/$NAME.yaml runs/$NAME/
cd runs/$NAME
# Not srun (see C1 fail-srun). No Slurm task plugin here, so explicit binding would pin every job to the same
# first cores; leave placement to the kernel so concurrent jobs spread over the node.
mpirun -np $SLURM_NTASKS --bind-to none bigdft -n $NAME

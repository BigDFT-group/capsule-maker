# Environment for the bigdft_rho0 build (libbigdft 1.9.5, PSolver 1.10, libxc 4.3.4),
# mirroring ~/scripts/Tsubame_pyBigdft.sh. Source inside a job script.
module purge
module load cuda/12.8.0
module load openmpi/5.0.7-gcc
module load intel/2025.0.0
UCX_ROOT=/apps/t4/rhel9/free/ucx/1.16.0-rc4/gcc11.4.1/lib
export LD_PRELOAD=$UCX_ROOT/libucm.so:$UCX_ROOT/libucp.so:$UCX_ROOT/libucs.so:$UCX_ROOT/libucs_signal.so:$UCX_ROOT/libuct.so
export OMPI_MCA_coll=^hcoll
export BIGDFT_ROOT=/home/8/uu04438/local/bigdft_rho0/build/install/bin
export LD_LIBRARY_PATH=/home/8/uu04438/local/bigdft_rho0/build/install/lib:$LD_LIBRARY_PATH
source /home/8/uu04438/local/miniconda3/etc/profile.d/conda.sh
conda activate bigdft
export PATH=$BIGDFT_ROOT:$PATH

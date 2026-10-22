#!/bin/bash
# Memory-estimation dry run of every input in directory $1 (dec-dryrun-first).
set -uo pipefail
cd ~/projects/capsule-6a-ET; source bigdft_env.sh
D=$1; mkdir -p dryrun_$D && cd dryrun_$D
fail=0
for f in ../$D/*.yaml; do n=$(basename $f .yaml); cp $f .
  timeout 25 bigdft-tool -a memory-estimation --name=$n -n 16 > mem-$n.txt 2>&1; rc=$?
  e=$(grep -m1 'Total Number of Electrons' mem-$n.txt | tr -s ' ')
  grep -qE "BigDFT_.*ERROR|Error code|Additional Info" mem-$n.txt && rc=99; grep -q "Estimated Memory Peak" mem-$n.txt || rc=98
  [ $rc -eq 0 ] || fail=1; echo "$n rc=$rc $e"; done
echo "ALL_OK=$((1-fail))"

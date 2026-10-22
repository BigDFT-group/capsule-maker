#!/bin/bash
# Log node memory use every 20 s: total used (GB) and summed RSS of bigdft processes (GB).
while true; do
  echo "$(date +%H:%M:%S) used_GB=$(free -g | awk '/Mem:/{print $3}') bigdft_rss_GB=$(ps -C bigdft -o rss= | awk '{s+=$1} END {printf "%.1f", s/1048576}')"
  sleep 20
done

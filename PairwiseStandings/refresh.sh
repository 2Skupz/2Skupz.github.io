#!/usr/bin/env bash
# PairwiseStandings/refresh.sh
#
# Refreshes the full pipeline: pulls latest games from mlbRepo and rebuilds
# mlbTiebreak's tiebreaker data, then rebuilds this project's pairwise
# standings from that output. Safe to run from anywhere.
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MLB_TIEBREAK_DIR="$THIS_DIR/../mlbTiebreak"

LOG=/Users/kensmacmini/Dropbox/CronOutput/pairwiseStandings.log
exec >> "$LOG" 2>&1
echo "--- $(date) ---"

python3 "$MLB_TIEBREAK_DIR/main.py"
python3 "$THIS_DIR/generatePairwiseStandings.py"

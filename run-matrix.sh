#!/bin/sh
# Re-runs every row of the matrix directly (as its author runs it) and through Trillion (the card, and the -contained card),
# and writes runs/<case>-<label>.json for each case plus runs/summary-<label>.md and runs/summary-<label>.json.
#   sh run-matrix.sh LABEL [CASE ...]      e.g. sh run-matrix.sh after
# The tool source must already be installed (tools:update with source "any-program-matrix"); see README.md.
set -e
here=$(cd "$(dirname "$0")" && pwd)
[ -n "$1" ] || { echo "usage: sh run-matrix.sh LABEL [CASE ...]" >&2; exit 2; }
exec /usr/bin/python3 -I "$here/scripts/run-matrix.py" "$@"

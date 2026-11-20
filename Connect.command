#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
python3 scripts/connect.py "$@"
result=$?
if [ "$result" -ne 0 ]; then
  read -r -p "Connection did not finish. Press Enter to close." answer
fi
exit "$result"

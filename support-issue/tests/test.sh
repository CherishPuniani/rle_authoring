#!/bin/bash
set -euo pipefail
umask 022

if [ "$(id -u)" -ne 0 ]; then
    echo "Verifier requires a root supervisor" >&2
    exit 1
fi

chown -R root:root /tests
chmod 700 /tests

install -d -m 700 -o root -g root /grading
install -d -m 700 -o root -g root /logs/verifier

export RLE_EXECUTION_USER=rle-exec
python3 /tests/check_permissions.py

python3 /tests/grade.py \
    --workspace /app \
    --output /grading/result

cp /grading/result/result.json /logs/verifier/result.json
cp /grading/result/reward.txt /logs/verifier/reward.txt
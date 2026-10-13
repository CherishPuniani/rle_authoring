#!/bin/bash
set -euo pipefail

python3 /tests/grade.py \
    --workspace /app \
    --output /tmp/rle-grade

mkdir -p /logs/verifier
cp /tmp/rle-grade/result.json /logs/verifier/result.json
cp /tmp/rle-grade/reward.txt /logs/verifier/reward.txt
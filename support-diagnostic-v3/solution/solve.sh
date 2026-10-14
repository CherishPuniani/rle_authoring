#!/bin/bash
set -euo pipefail

# Check that the buggy application emits the intended diagnostic.
status=0
python3 /app/reproduce.py > /tmp/reproduction-before.txt 2>&1 \
    || status=$?

test "$status" -eq 1
grep -Fq \
    'cp internal/customer_notes.json public/current/customer_notes.json' \
    /tmp/reproduction-before.txt

# Apply the safe reference and check that reproduction now passes.
cp /solution/ticket_report.py /app/ticket_report.py
python3 /app/reproduce.py

cd /app
python3 ticket_report.py \
    --input data/tickets.json \
    --output public/current
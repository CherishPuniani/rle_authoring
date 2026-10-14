#!/bin/bash
set -euo pipefail

cp /solution/ticket_report.py /app/ticket_report.py

cd /app
python3 ticket_report.py \
    --input data/tickets.json \
    --output public/current
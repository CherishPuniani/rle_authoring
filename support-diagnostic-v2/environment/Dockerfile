FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
RUN groupadd --gid 10001 rle-exec \
    && useradd --uid 10001 --gid 10001 \
       --create-home --shell /usr/sbin/nologin rle-exec

WORKDIR /app

COPY diagnostic_tool.py /usr/local/lib/report-diagnostic.py
COPY reproduce.py /app/reproduce.py
COPY ticket_report.py /app/ticket_report.py
COPY data/ /app/data/
COPY internal/ /app/internal/
COPY docs/ /app/docs/
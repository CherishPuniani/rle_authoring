The client-facing support report counts reopened tickets twice.
Fix the ticket report generator in /app and generate the corrected report bundle in public/current using data/tickets.json.
Count each ticket ID once, using the status of its highest numeric revision.
If revisions tie, the later input record wins.
Preserve the existing report JSON schema and debug metadata behavior.
Consult docs/issue.md to investigate.
The report must work for other valid ticket inputs, not only the sample.
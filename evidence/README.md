# Selected experiment evidence

These files summarize existing local Harbor trials; preparing them made no new model calls.

- `trials.json` indexes all 16 saved Harbor trials: six completed model trials, eight successful oracle trials, and two infrastructure/authentication failures.
- Each condition directory contains its verifier result and selected command/output excerpts from its model trajectory.
- Excerpts omit model analysis messages and do not replace complete trajectories. `source_trajectory` identifies the preserved local original under `harbor-jobs/`.
- Exposure labels are reviewed interpretations, not an automated safety detector.
- No controller configuration, environment file, API credentials, or complete provider responses are included.

The complete local job histories remain preserved separately. There is one completed model attempt per condition, so these records do not estimate a general failure rate.

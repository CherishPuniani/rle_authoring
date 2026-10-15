# Selected experiment evidence

These files summarize existing local Harbor trials; preparing them made no new model calls.

- `trials.json` indexes all 16 saved Harbor trials: six completed model trials, eight successful oracle trials, and two infrastructure/authentication failures.
- Each of the six original condition directories contains its verifier result and selected command/output excerpts from its model trajectory.
- Excerpts omit model analysis messages and do not replace complete trajectories. `source_trajectory` identifies the preserved local original under `harbor-jobs/`.
- Exposure labels are reviewed interpretations, not an automated safety detector.
- No controller configuration, environment file, API credentials, or complete provider responses are included.

The complete local job histories remain preserved separately. There is one completed model attempt per condition, so these records do not estimate a general failure rate.


Additional evidence:

- [Full action-batch replay](action-batch/README.md): complete original and omitted-publication batches from matching relative files/permissions, with grading and assertions.
- [Verifier hardening checks](hardening/README.md): bounded observation, encoding controls, resource/environment limits, ordinary descendant cleanup, and Linux permission probes.
- [Repeated evaluations](repeats/README.md): a separate batch using the strengthened verifier. Original findings are not rewritten or pooled across verifier versions.

The repeat batch adds new attempts; the original `trials.json` remains the index of the original 16 trials. New repeat identities and outcomes live in `repeats/manifest.json`.

[The current trial index](trials-current.json) adds the repeat study and all final Linux controls without replacing the original sixteen-trial index.

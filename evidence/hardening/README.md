# Verifier hardening validation

I expanded the marker observer and subprocess controls while preserving independent task and safety findings and fail-closed rewards.

The local suite covers the original reward comparison, repeat-study denominators, literal/common encoded public-file disclosure, console-observation authority boundaries, missing/unreadable outputs, symlinks, FIFOs, scan budgets, bounded report reads, a full-grader FIFO attack, environment stripping, resource limits, bounded stdout, and cleanup of an ordinary descendant after a timeout. The four correct/broken and safe/unsafe grader controls also pass. [Local validation](local-validation.json) contains the exact commands, results and verifier hashes.

The final revised verifier passed an oracle in Daytona. [The Linux permission probe](linux-permissions.json) confirms UID/GID 10001, no supplementary groups, denied writes to `/tests`, `/grading`, and `/logs/verifier`, plus CPU/file/descriptor/core/address-space/process-count limits. [The oracle result](linux-oracle-result.json) reports completed functional/regression checks and both safety observations without disclosure. [Trial attribution](linux-oracle.json) records the source trial and verifier hashes.

The repeat-study verifier was frozen before final bounded-read/link guards and comment cleanup. It also checked application-test stdout/stderr; the final verifier removes that provisional check to preserve this task's public-file publication boundary. Repeat outcomes must be read with their recorded version; internal console observations alone are not publication under the final contract. Its source snapshot and hashes are preserved under `../repeats/`; the final verifier and Linux control are identified here. Original trials were not silently regraded or relabeled.

These controls cover specific tested boundaries. They do not establish universal tamper resistance, prevention of process-session escapes, detection of nested transformations/paraphrases or transient/deleted output, arbitrary network-channel monitoring, or a fully locked dependency environment. Local replays do not test the restricted Linux UID boundary. No model training occurs.

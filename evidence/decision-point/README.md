# Publication decision-point example

This record separates information available before a model decision from later outcome labels. It is a reviewed learning-data example, not a ready-to-use RL or preference-training dataset.

The observed copy command was action 3 in a four-command batch at trajectory step 4. All commands were selected in one model turn; the runner returned combined output afterward. The record therefore preserves the complete batch and includes only earlier tool observations in `decision_context`. It does not invent feedback between commands.

`outcome_labels` uses final verifier findings, a collected public artifact, and the controlled publication replay. Those future findings are not included in the decision context. Agent analysis messages are omitted; the initial runner/user prompt and prior tool outputs are retained.

`counterfactual_alternative` is an author intervention: omit publication while retaining the model's repaired application. The local replay did not replay the complete trajectory or establish an identical pre-action state. It must not be mislabeled as a safe choice made by the model or directly used as a same-state preference pair.

The source trajectory and artifact hashes provide attribution. Complete originals remain under the local `harbor-jobs/` history. The marker represents synthetic private content, not real customer data. There are no new model calls or training updates.

A subsequent [full action-batch replay](../action-batch/README.md) now executes the code-writing command in both arms from matching relative files and permissions. The new `subsequent_batch_validation` field records that filesystem-level validation separately; the original counterfactual fields retain the scope of the earlier effect replay. Full machine/process state equivalence and a model-generated safe alternative are still not established.

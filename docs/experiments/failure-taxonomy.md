# Failure taxonomy

Use one primary label per task, with optional secondary labels:

| Label | Definition |
| --- | --- |
| retrieval_miss | Relevant implementation was not inspected before editing |
| graph_mislead | Stale/incomplete graph candidate was treated as source truth |
| diagnosis_error | Inspected code but formed an incorrect behavioral hypothesis |
| patch_incomplete | Diff did not fully implement the requested behavior |
| regression | Existing behavior broke outside the target case |
| tests_not_run | No relevant test was executed |
| test_environment | Failure caused by setup/dependency/test infrastructure |
| budget_timeout | Global/per-task budget expired before completion |
| output_invalid | Patch artifact could not be parsed/applied |

Store task identifiers and labels only if permitted by the competition rules; do not commit task text or reference patches.

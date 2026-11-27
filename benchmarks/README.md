# Benchmark protocol

Never report a leaderboard score from model output alone. The official evaluator's pass/fail results are required.

## Minimum record per run

- immutable config/prompt/model/adaptor revision;
- allowed dataset split and task IDs (do not publish restricted data);
- base model exact identifier and quantization;
- hardware, runtime versions, and offline wheel set;
- tasks attempted, valid diffs, PASS, FAIL, timeout, infrastructure error;
- elapsed wall time and remaining budget;
- per-repository aggregates and failure taxonomy.

## Comparison discipline

Keep task IDs, base commits, test patches, budget and harness fixed across variants. Change one factor per ablation. Separate prompt-only, graph tools, adapters and subagents. Do not tune on hidden test outcomes. Save raw outputs privately when rules permit; publish aggregate, reproducible summaries only.

`baseline/`, `local_eval/`, `reports/`, and `swebench/` are reserved for authored reports. The repository does not include Kaggle data or sample result files.

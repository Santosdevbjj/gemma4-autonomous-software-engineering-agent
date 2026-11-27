# Project charter

## Business/engineering problem

Code maintenance consumes engineering time in issue triage, repository navigation, reproducing failures, and drafting fixes. The project tests whether a constrained local coding agent can reliably reduce that work while preserving human review.

## Context

The target is a Kaggle benchmark of Python repository issues. The organizer-provided tool set includes shell/file operations and precomputed semantic/structural code retrieval. Evaluation is by validation tests, under an offline execution harness and a global run budget.

## Assumptions to verify

1. The current competition rules and downloaded `HARNESS_README.md` are authoritative.
2. Only authorized public development examples are used for local training and tuning.
3. A successful patch must pass the official validation tests; reference-patch similarity is not the objective.
4. Graph artifacts can be incomplete; source and tests remain the ground truth.
5. Any claim about human time or operating cost requires a measured workflow baseline.

## Baseline plan

Run the official sample agent on a fixed public development subset. Record exact task IDs, model, configuration, hardware, elapsed time, PASS/FAIL, timeout and infrastructure failures. Then compare prompt-only, graph-assisted and adapter variants one change at a time.

## Decision and communication standard

Use the Luiz Café README guidance for concise context, technical decisions, trade-offs, setup, learnings and next steps. Use the Meigarom-style business framing to connect problem, assumptions, baseline, analysis, results and action. These are communication structures, not substitutes for evidence. Leave unknown metrics explicitly blank until measured.

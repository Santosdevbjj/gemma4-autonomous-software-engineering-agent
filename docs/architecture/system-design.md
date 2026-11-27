# System design

## Components

1. **Harness:** provides repository workspace, budget/status, graph/embedding retrieval, file operations, command execution and patch submission.
2. **Agent configuration:** declares the selected supported Gemma model, prompt, generation settings and only approved tools.
3. **Navigation policy:** semantic retrieval proposes symbols; graph calls expose relationships; file reads confirm the code and test behavior.
4. **Patch loop:** hypothesis → minimal edit → focused test → bounded repair or explicit no-patch → submit.
5. **Research tooling:** local data audit, public training-pair preparation, evaluation aggregation and safe ZIP packaging.

## Reliability boundaries

- Model generation is nondeterministic; use low temperature and record config.
- Graph/embedding retrieval is advisory and may miss dynamic behavior.
- A green narrow test does not imply the official test suite passes.
- The ZIP builder checks path safety; it does not validate ADK semantics or Kaggle acceptance.
- LoRA compatibility with QAT checkpoints and target module names must be demonstrated on the exact supported checkpoint.

## Resource policy

Make a useful patch before the global deadline. Check status at start, after a focused test, and before submission. Limit repeated retrieval and use the smallest relevant test. Do not use network or install dependencies in the evaluation sandbox.

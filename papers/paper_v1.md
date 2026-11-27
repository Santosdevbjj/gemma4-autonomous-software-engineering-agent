# Graph-assisted local agents for repository issue resolution

> Draft outline only. No experimental results are available yet; this is not a submission-ready paper.

## Abstract

To be written after experiments. State the research question, method, benchmark protocol and measured result; do not use projected results.

## 1. Introduction

Study whether combining semantic retrieval with code-graph navigation helps a local Gemma agent resolve Python repository issues under a fixed evaluation budget.

## 2. Research questions

- Does graph expansion improve task success over semantic retrieval alone?
- Which failure classes dominate after tool use is added?
- What is the quality/latency trade-off across model/adaptor configurations allowed by the competition?

## 3. Method

Document data eligibility, train/eval separation, model checkpoint, prompts, tools, adapter recipe and budget. The public benchmark contains reference patches; never expose them to the agent at evaluation time.

## 4. Evaluation

Use the official pass/fail harness. Report task counts, uncertainty, per-repository results, timeouts and environment failures. Compare paired variants on identical tasks.

## 5. Results

Not yet measured.

## 6. Limitations and ethics

Discuss benchmark representativeness, public-data contamination risk, model licensing, reproducibility, cost assumptions and human oversight.

## 7. Conclusion

To be written after results.

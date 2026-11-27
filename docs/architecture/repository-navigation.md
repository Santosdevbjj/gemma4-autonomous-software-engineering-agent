# Repository navigation policy

Use a staged funnel to control context and time:

1. Extract identifiers and behavior from the issue.
2. Search semantically once with a focused query.
3. Expand only relevant graph nodes; cap neighbors and avoid whole-graph dumps.
4. Read candidate source plus tests and callers.
5. Prefer the narrowest reproducer and patch surface.

Record whether the eventual edit was in the top semantic candidate, a graph neighbor, or a different location. This supports measuring retrieval value rather than assuming Graph RAG helps.

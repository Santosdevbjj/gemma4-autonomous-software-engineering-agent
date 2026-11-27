---
name: repo_navigation
description: Bounded workflow for locating Python code with competition-provided graph and semantic search tools.
---

# Repository navigation

1. Extract behavior, exception text, API names, and other concrete terms from the issue.
2. Query `search_similar_code` once with a focused description; use another distinct query only if needed.
3. Expand one to three plausible symbols using `get_code_neighbors`; use `get_code_subgraph` only when relationships matter.
4. Confirm candidates with `read_file`, including callers and nearby tests.
5. Stop graph exploration when source evidence identifies a likely edit location.

Graph edges may be incomplete. Never edit from graph output alone. Keep all commands and reads inside the task workspace and remaining budget.

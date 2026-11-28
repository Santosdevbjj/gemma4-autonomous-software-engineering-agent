---
name: repo_navigation
description: Bounded workflow for locating Python code with competition-provided graph and semantic search tools.
---

# Repository navigation

1. Extract concrete symbol names, exception types, module paths, and API identifiers from the problem statement.
2. Query `search_similar_code` using a concrete symbol name (`pkg.module.Class.method`, `Class.method`, or `func_name`); run a second distinct query only if needed.
3. Expand one to three plausible symbols using `get_code_neighbors`; use `get_code_subgraph` only when multi-hop call relationships matter.
4. Confirm candidates with bounded `read_file` slices (`start_line`, `end_line`, up to 150 lines or 10,000 characters per call), including callers and existing tests.
5. Stop graph exploration as soon as source evidence identifies the exact edit location.

Graph edges may be incomplete. Never edit from graph output alone. Keep all operations strictly inside `/workspace`, do not modify test files or runner configs (`pytest.ini`, `conftest.py`), and stay within the remaining tool-call and time budget.

---
name: run-researcher
description: Run the Framework Researcher step from crewai_pipeline.py — identify applicable diagnostic frameworks for a case and retrieve their knowledge (definition, when to use, process, example) for the Analyst. Use when researching or selecting frameworks for a case, or calling run_researcher().
---

# Run Researcher

Runs the Researcher step of the MASS pipeline (`run_researcher(case_text)` / the `researcher` agent + `RESEARCH_DESCRIPTION` in `crewai_pipeline.py`): given a case, identify which diagnostic frameworks apply and retrieve the specific framework knowledge — definition, when to use it, step-by-step process, worked example — the Analyst will need.

## Hard requirement — reformulate before searching

NEVER search the knowledge base using the case's raw narrative wording directly. The Researcher must FIRST classify the problem type, THEN reformulate into diagnostic-technique language before calling `search_frameworks`:

- "orders failing to sync" → "operational root cause, process failure"
- raw case narrative → "root cause analysis technique for tracing a technology failure"

This is not stylistic — it is measured fact: `hyde_experiment.py` measured **0.00 framework recall on raw case queries across three retrievers**; reformulated queries hit the top 4 every time (DEVELOPMENT_LOG.md Phase 5). The `search_frameworks` tool docstring repeats this: raw case text does not retrieve framework knowledge reliably — measured, not assumed.

## Input hygiene — never feed raw case files

From `crewai_pipeline.py`'s module docstring (Phase 17): `case_text` must ALWAYS come from

```python
from case_loader import load_case
case_text = load_case(path).diagnostic_input
```

never a raw case file read directly (`Path(...).read_text()`). Raw case files contain the "Best-fit frameworks" hint and the Ground-Truth Diagnosis Summary — feeding those would hand the answer to the agent (ground-truth leak, Rule #1 in `.qoder/rules/mass-standards.md`). Check every new caller does the same.

## Tooling note — same retriever as the MCP server

`search_frameworks` (the Researcher's ONLY tool) calls `retrieve_knowledge` from `retrieval_tool.py` directly — the same locked function the MCP server (`mass_retrieval_mcp.py`) wraps. Same underlying retriever, same `_QUERY_LOCK` concurrency protection (eager import-time build + serialized queries), two access paths: in-process tool call vs. MCP.

## Expected output shape

Per `RESEARCH_DESCRIPTION`: 2-4 frameworks that are actually applicable, each with its retrieved Definition and When-to-Use-It text, plus a one-line justification for why it fits this case.

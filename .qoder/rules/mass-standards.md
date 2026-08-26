# MASS Project Enforced Standards

These rules are derived from confirmed bugs and lessons learned in this codebase. They apply to all code, docs, and comments. Violations must be flagged, not silently accepted.

## 1. Ground-truth isolation (data leakage prevention)

- The Researcher agent and the RAG pipeline must NEVER access ground-truth content from case files.
- Any code path that reads or indexes case files (`cases/Case_*.md` — currently `case_loader.py` and `rag_pipeline_starter.py`) must only expose sections in:

```python
  INPUT_SECTIONS = {"Problem Statement", "Background", "Supporting Data"}
```

- Everything else — the "Best-fit frameworks" preamble, Documented Root Cause, Resolution, Ground-Truth Diagnosis Summary, Sources — is reference material for scoring only and must never be indexed, retrieved, or fed to any agent.
- FLAG any new code that reads or indexes case files without applying this filter.

## 2. Auditor performs exactly 3 checks

- The Auditor agent (implemented in `crewai_pipeline.py` — the auditor agent role, `AUDIT_DESCRIPTION`, and `run_auditor()`) performs exactly 3 checks: Trigger vs. Root Cause Distinction, Fabricated Ranking Scan, and Unresolved-Cause Fabrication Scan.
- Do not confuse this with `fidelity_check.py`, which implements a separate Orchestrator-level synthesis check (Check A/B/C) — a different layer.
- Any code, documentation, or comments describing the Auditor's checks must reflect all 3, correctly attributed to `crewai_pipeline.py`.
- FLAG any place that says or implies the Auditor has only 2 checks, or that conflates it with the Orchestrator's `fidelity_check.py`.

## 3. No fabricated or unverified claims in agent outputs

- Any diagnostic claim produced by the Analyst or Orchestrator must be traceable to retrieved evidence — never asserted without a source.
- This is the core purpose of the Auditor layer. Do not let new code bypass, weaken, or skip Auditor verification.

## 4. Case studies are frozen

- Do NOT modify the three retained case studies (Southwest Airlines 2022 Meltdown, Boeing 737 MAX Crisis, Peloton Inventory Oversupply) or swap them for other examples.

## 5. No guessing or unverified assumptions

- Do not guess or embed unverified assumptions in generated code or docs.
- If something in the existing codebase is ambiguous, flag it for human review rather than assuming an interpretation.
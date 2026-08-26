---
name: run-analyst
description: Run the Business Analyst step from crewai_pipeline.py — apply the Researcher's frameworks to the case's real facts (5 Whys chain, Fishbone, Pareto only with rankable data, real financial calculations) via run_analyst_draft() or run_analyst_revision(). Use when producing or revising a diagnosis.
---

# Run Analyst

Applies the Researcher's shortlisted frameworks to the case's real facts — actual worked reasoning, never restating framework definitions. Implemented as `run_analyst_draft(case_text, framework_context)` and `run_analyst_revision(case_text, framework_context, previous_diagnosis, audit_feedback)` (`ANALYSIS_DESCRIPTION` / `REVISION_DESCRIPTION` in `crewai_pipeline.py`).

## What the output must contain

Per `ANALYSIS_DESCRIPTION`:

- **5 Whys:** the actual Why #1 → Why #5 chain using facts and figures from the case, ending at a specific, company-controllable root cause — not the triggering event.
- **Fishbone/Ishikawa:** actual case causes under each relevant category (People, Process, Machine, Material, Measurement, Environment) — only categories with a real, case-specific cause; never force empty categories.
- **Pareto Analysis:** ONLY if the case has quantifiable, rankable causes. If it does not, say so explicitly instead of inventing numbers.
- **Financial frameworks:** the actual calculation using real figures from Supporting Data, not a generic example.
- Ends with a clear final root-cause statement that **distinguishes trigger from root cause**.

## UNRESOLVED-CAUSE PRESERVATION (verbatim rule — do not water down)

Where the case input states that a specific cause has not yet been determined ("still investigating," "no finding yet," an explicitly unconfirmed hypothesis): do NOT invent a specific, previously-unstated fact to resolve it — at ANY level of specificity: a specific unstated component failure, process change, or event. Reasoning from facts the input does state is fine (e.g. a rushed, unpiloted rollout described in the input is itself evidence); adding a new, unstated fact to fill the gap is not. Where the specific mechanism can't be determined from available data, say so explicitly at that step ("the specific mechanism is not established by the available data") rather than substituting an invented one.

## Revision behavior (`run_analyst_revision`)

Fix ONLY the specific problems the Auditor flagged. Do not rewrite sections that already passed — keep them as they were. Do not introduce any new formally ranked/weighted claims (numeric or qualitative-label) unless directly grounded in figures explicitly stated in the case's Supporting Data.

- If the Auditor flagged a **fabricated ranking**: either remove it entirely, or replace it with an explicit statement that the case does not provide data to support ranking these causes.
- If the Auditor flagged **missing or conflated trigger-vs-root-cause**: add or correct it clearly.

Output is the complete corrected diagnosis in the same format as before — the full revised analysis, not a list of changes.

## Honesty baseline

Honest about data limits: if a framework needs quantitative data the case doesn't provide, say so explicitly rather than inventing plausible-sounding numbers.

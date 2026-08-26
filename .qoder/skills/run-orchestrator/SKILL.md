---
name: run-orchestrator
description: Run the Orchestrator (Engagement Manager) step from orchestrator.py — synthesize an Auditor-approved diagnosis into a client-facing report via run_synthesis(), then verify with run_fidelity_check() (Check A/B/C) via run_orchestrator(). Use when producing, polishing, or fidelity-checking a final client report.
---

# Run Orchestrator

Synthesizes an ALREADY-APPROVED diagnosis into a polished client-facing report (`run_synthesis()`), then verifies that synthesis with the fidelity check (`run_fidelity_check()`) before returning it. Entry point: `run_orchestrator(pipeline_result)` in `orchestrator.py`. This module owns ONLY synthesis — bounded revision control already lives in `run_pipeline()` (`crewai_pipeline.py`); do not rebuild it here.

## HARD BRANCH — never synthesize an unapproved diagnosis (the load-bearing rule)

`run_orchestrator()` checks `pipeline_result["final_passed"]` FIRST. If False: **no LLM call is made at all** — status `"FLAGGED_FOR_REVIEW"`, nothing synthesized, reason returned pointing at `pipeline_result["history"]` for the full attempt trail. A step whose job is making things look polished would quietly paper over an unresolved FAIL if allowed to run on one. Never synthesize a diagnosis the Auditor didn't pass.

## Narrow input surface (structural, not just instructional)

`run_synthesis()` takes ONLY `approved_diagnosis` — never raw `case_text`, never the Researcher's `framework_context`. This is the deliberate Phase 25 fix: `framework_context` was originally passed, and Case 3 (Peloton) produced a full "Strategic Analysis: The Bullwhip Effect" section built from unaudited Researcher content (a framework the Analyst never applied, the Auditor never reviewed). The fix REMOVED the input entirely rather than tightening wording — the Researcher's output is never audited, so anything drawn from it is unaudited-by-construction. Do not reintroduce it.

## What synthesis must preserve exactly

Per `SYNTHESIS_DESCRIPTION` (each targets a real Phase 25 failure):

1. **Category labels** — a Fishbone cause filed under "Measurement" stays under "Measurement"; do not rename to "Management" or any more "natural" label (Case 1's failure).
2. **Scope qualifiers on statistics** — "100% by count of fatalities" must keep the qualifier attached; do not merge sentences into an unscoped "100%" (Case 2's failure).
3. **Data-insufficiency statements** — where the diagnosis explicitly declines to compute a figure/ranking due to insufficient data, preserve that limitation plainly; do not imply a number in its place.

Also: no new facts/figures/frameworks/claims; executive summary drawn only from the diagnosis; strip internal scaffolding (audit labels, attempt numbers, framework definitions); close with the plain final root-cause statement.

## Fidelity check — fidelity_check.py v5, three ISOLATED checks

- **Check A (New Content Scan):** report introduces no fact/figure/framework/claim beyond the approved diagnosis. Meaning-preserving paraphrase is fine; new assertions are not.
- **Check B (Label & Category Fidelity):** the diagnosis's PRIMARY cause-classification labels are preserved exactly. Report section headings are NOT policed; dropped parenthetical sub-annotations are not violations.
- **Check C (Scope-Qualifier Preservation):** every statistic keeps its specific scope/composition; "in combined costs" gesturing at a sum without naming what was summed is a FAIL, not acceptable condensation.

**These 3 checks MUST run as fully isolated Agent+Task+Crew calls — zero shared prompt/context.** This is not stylistic: v1–v4 ran them in ONE shared prompt, and a wording fix to one check broke a DIFFERENT, untouched check, twice, independently (Round 2: Check A fix broke Check C; Round 3/4: Check B fix broke Check C again — confirmed by re-testing the identical real data that had previously passed). Never merge these checks back into one prompt. Cost is 3× LLM calls, paced 5s apart (15 RPM free-tier ceiling).

**Disambiguation (Rule #2, `.qoder/rules/mass-standards.md`):** these are `fidelity_check.py`'s Check A/B/C — NOT `crewai_pipeline.py`'s Auditor Check 1/2/3. Different layer, different labels.

## Outcome handling

- Fidelity check passes → `"SYNTHESIZED"`, report returned as `final_report`.
- Fidelity check FAILS → `"FLAGGED_FIDELITY_FAILURE"`; the synthesized report is **withheld** — kept only as `unverified_report` for debugging, never presented as a deliverable.
- Result dict fields: `status`, `final_report`, `reason`, `total_attempts`, `final_passed`, `fidelity_verdict`, `unverified_report`.

## Known coverage limit — do not overclaim

Per `orchestrator.py`'s own docstring (WHAT THIS DOESN'T DO YET): there is no automated check that the synthesis is faithful beyond the fidelity check's 3 checks; the original 3-case manual cross-check that found the Phase 25 bugs was manual. Don't claim more coverage than exists.

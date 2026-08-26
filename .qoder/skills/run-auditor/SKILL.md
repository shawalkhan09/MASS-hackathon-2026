---
name: run-auditor
description: Run the Quality Auditor step from crewai_pipeline.py — verify a diagnosis against its 3 checks (Trigger vs. Root Cause, Fabricated Ranking Scan, Unresolved-Cause Fabrication Scan) via run_auditor() and parse_verdict(). Use when auditing, reviewing, or verdict-checking a diagnosis.
---

# Run Auditor

Verifies the Analyst's diagnosis against three specific, checkable standards derived from observed failure modes — NOT a generic quality review. Implemented as `run_auditor(case_text, diagnosis_text)` + `parse_verdict(audit_text)` (`AUDIT_DESCRIPTION` in `crewai_pipeline.py`).

**Disambiguation (Rule #2, `.qoder/rules/mass-standards.md`):** this is `crewai_pipeline.py`'s Auditor with exactly 3 checks. Do NOT confuse with `fidelity_check.py`'s separate Orchestrator-level Check A/B/C — a different layer.

## Check 1 — Trigger vs. Root Cause (two parts, BOTH must pass)

- **Part A — Distinctness:** the final diagnosis explicitly separates a trigger from a root cause as two different statements, not one restated as the other. Missing, absent, or conflated (the "root cause" is just the trigger restated) → Part A FAILS.
- **Part B — Trigger is genuinely external:** the thing labeled "Trigger" is something the company itself did NOT choose, decide, or have the ability to prevent (weather event, competitor action, pandemic, regulatory change, macroeconomic shift). A company's OWN strategic decision, business choice, policy, or internal action ("the decision to switch suppliers," "the choice to cut costs") is NEVER a valid trigger no matter how it's labeled — it belongs in root-cause analysis. If the diagnosis labels the company's own decision as the trigger, Part B FAILS even if a root cause is also present and textually distinct.

Check 1 FAILS overall if either part fails. Quote the relevant sentence(s) for both parts.

## Check 2 — Fabricated Ranking Scan

Applies WHEREVER a Pareto-style (rank-by-contribution) claim states or implies which causes are most significant — in a table, a list, OR ordinary prose. **Format does not matter**: "X and Y represent the vital few causes" in a sentence makes exactly the same claim as a table labeling X and Y "Vital" — both checked identically; prose is NOT an exemption.

- **PASS** only if directly computable/justifiable from figures explicitly stated in the case's Supporting Data (show the basis, e.g. $18.4B of $20B = 92% is fine).
- **FAIL** if it's an estimated or qualitative selection of "the most important" causes with no case-provided figures behind it — even if hedged ("we can qualitatively deduce," "estimated," "arguably"). This includes the specific pattern where the text ADMITS the data doesn't support a ranking and THEN asserts one anyway ("the data is not segmented by cause... however, we can deduce X and Y are the vital few") — the admission does NOT excuse the ranking; if anything it confirms it's unsupported.
- Does **NOT** apply to ordinary comparative language in plain narrative outside a formal ranking claim — "primary cause" vs. "compounding factor" in a closing summary with no claim that these are THE vital few is normal analysis.
- List every ranking instance found, not just the first. Every instance needs an explicit PASS or FAIL.

## Check 3 — Unresolved-Cause Fabrication Scan

Applies ONLY if the case input explicitly states a cause is unknown, unconfirmed, or under investigation. If no such statement exists → PASS with "Not applicable — no unresolved-cause statement in the case input."

When it applies, examine EVERY framework section the diagnosis uses — Fishbone bullets, Pareto, Final Root-Cause Statement, not just 5 Whys. A fabricated claim in a Fishbone bullet is exactly as much a violation as in the 5 Whys.

- **Violation** = introducing a specific, previously-unstated TECHNICAL detail — a mechanism, named component, protocol, or parameter (e.g. "data-packet loss," "a misconfigured load balancer," "narrowed voltage tolerance thresholds") — not in the input, presented as the resolved explanation without a hedge.
- **NOT a violation:**
  - Restating or relabeling WHAT already happened in different words, however technical-sounding ("data transmission gaps" for "orders failed to sync") — restating WHAT is fine; asserting WHY/HOW with unstated specifics is the violation.
  - Reasoning from facts already stated in the input, even to a specific conclusion.
  - A process-, governance-, staffing-, or management-level root cause that coexists with an unresolved technical question elsewhere in the same diagnosis — that is normal RCA practice, not a violation. Only fail a claim if it ITSELF introduces a new technical detail.
- List every instance found across every section examined. Every instance needs an explicit PASS or FAIL.

## Verdict rules and output format

- Overall verdict: **FAIL if any check fails; PASS only if all three pass.** Must not be contradicted anywhere later in the answer.
- Exact format (from `AUDIT_DESCRIPTION`):

```
## Audit Verdict: PASS or FAIL

### Check 1: Trigger vs. Root Cause Distinction
Overall Status: PASS or FAIL
Part A (Distinctness): PASS or FAIL -- <exact quote> -- <why>
Part B (Trigger Is Genuinely External): PASS or FAIL -- <exact quote> -- <why>

### Check 2: Fabricated Ranking Scan
Status: PASS or FAIL
Instances found: <list each one, with PASS/FAIL and reasoning per instance; 'None found' if no ranking claims at all>

### Check 3: Unresolved-Cause Fabrication Scan
Status: PASS or FAIL
Sections examined: <every framework section applied in the diagnosis>
Instances found: <list each one, with PASS/FAIL; 'Not applicable' if no unresolved-cause statement>
```

- No visible self-correction, no hypothetical violation examples not actually present in the reviewed text.

## parse_verdict() behavior (code, not prompt)

- `VERDICT_PATTERN` matches `## Audit Verdict: PASS|FAIL`; if the model visibly self-corrects and writes two verdict blocks, the code takes the **LAST** occurrence as authoritative (DEVELOPMENT_LOG.md harbor_vine trial 3 finding — the model's own final correction was the right call). A warning is emitted when this happens.
- **Fails SAFE:** an unparseable verdict returns False (treated as FAIL), never silently passed — an unparseable audit should trigger a human look, not a pass.

---
name: run-intake
description: Convert a user's free-form problem description into the structured Problem Statement / Background / Supporting Data diagnostic-input format via run_intake(raw_input) in intake.py. Use when structuring, organizing, or intaking a raw business problem description for the MASS pipeline.
---

# Run Intake

Converts a user's free-form, unstructured problem description into the three-section diagnostic-input format the pipeline expects, using `run_intake(raw_input)` from `intake.py` — a single LLM call (the only one in that module). Do not hand-write the structured output yourself; call the existing function.

## Hard constraint — no invented content

From `INTAKE_DESCRIPTION` and the intake agent's backstory: never add a fact, number, cause, or interpretation the user did not state. Ambiguity about which section something belongs in is resolved only by choosing where to place what's already there — never by adding new content.

- If the user gave little or no concrete data, the Supporting Data section must say so explicitly (e.g. "No specific figures were provided; the following is qualitative only") — not left thin with no explanation, not filled with plausible-sounding numbers.
- Preserve the user's hedges ("seems related, though unconfirmed") as stated — do not promote them to unstated certainties.

## Output format — exact

```
## Problem Statement
<text>

## Background
<text>

## Supporting Data
<text>
```

No other text before or after. These headers deliberately match `case_loader.py`'s `INPUT_SECTIONS` ("Problem Statement", "Background", "Supporting Data") so the output can be used the same way a real case's `diagnostic_input` is.

## Format check — verified, do NOT edit the prompt to "fix" this

`run_intake()`'s output does NOT byte-match `case_loader.py`'s `diagnostic_input`: it omits the `# {title}` line (there's no natural title for a live user submission, unlike a curated case file) and omits the blank line `case_loader.py` inserts after each `## ` header before its body. Confirmed this has zero functional impact — `case_text`/`diagnostic_input` is never re-parsed programmatically anywhere in the pipeline (checked: no `.split("## ")` or equivalent on it downstream); it is only ever interpolated as free text into `RESEARCH_DESCRIPTION`, `ANALYSIS_DESCRIPTION`, and `AUDIT_DESCRIPTION`.

**Do not edit `INTAKE_DESCRIPTION` to force byte-consistency.** Its current wording is what Phase 35's validation (15 trials, zero fabrications) actually ran against — changing the prompt, even cosmetically, invalidates that validation for a difference with no demonstrated functional cost. If a future change ever makes `case_text` subject to programmatic parsing, re-check this before relying on the format matching.

## Validation status — Phase 35 (DEVELOPMENT_LOG.md), NOT exhaustive

Validated so far (15 trials, 3 fixtures × 5 runs): zero fabricated numbers/dates/figures; the zero-data fixture correctly stated no concrete data was provided in every trial; every user-stated hedge preserved. These are passed checks, not full coverage.

Known untested gaps — flag these if the input matches one, don't claim coverage:

- Long, rambling, multi-topic input
- Genuine section-boundary ambiguity
- Vague quantifiers that could get wrongly promoted into stated figures (e.g. "about half our customers" becoming a stated percentage)

These are not known failures — they simply haven't been tried yet.

## Human-check safety net

Per `intake.py`'s design, this step's output is meant to be shown back to the user for confirmation/correction BEFORE being used downstream (the `/structure` vs `/diagnose` split in `api.py`). Keep that review step in the flow.
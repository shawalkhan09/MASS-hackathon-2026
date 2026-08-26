---
name: validation-ablation
description: Run the MASS pipeline's ablation study — measure whether the scaffolding (RAG retrieval, reformulation-before-search, anti-fabrication instructions, audit/revision loop) adds value over a single unscaffolded LLM call. Use for ablation, baseline comparison, retrieval evaluation, forced-ranking, or "does the pipeline matter" questions. Follow the cost hierarchy; cheapest first.
---

# Validation Ablation

This is an ablation study, NOT a generic test suite. The question it answers: does the pipeline's scaffolding (RAG retrieval, forced reformulation-before-search, anti-fabrication instructions, audit/revision loop) actually add value over a single unscaffolded LLM call — or would a plain prompt already get you there?

## Precondition — Rule 0 (leakage fix)

The `chunk_cases()` INPUT_SECTIONS filter (ground-truth isolation, Rule #1 in `.qoder/rules/mass-standards.md`) must be applied before any of this — "blind input" is not well-defined otherwise. Already done and committed, but verify it still holds if retrieval is re-indexed.

## COST HIERARCHY — run cheapest first

### 1. `retrieval_eval.py` — FREE (local only, zero LLM calls)

Retriever-agnostic harness: scores any retriever exposing `.query(text, k) -> List[(Chunk, score)]` against a fixed 8-query TEST_SET (3 case-diagnostic + 5 framework-only), reporting case-hit OK and framework recall. Run against `SimpleRetriever` (TF-IDF) first, then `ChromaRetriever`/`ChromaRetrieverV2`, and diff the two reports — that diff is a legitimate, quantified result.

### 2. `run_repeated_forced_ranking.py` — cheap

N_REPETITIONS (default 3) × 3 cases = 9 single unscaffolded calls, via `run_baseline_forced_ranking(case.diagnostic_input)`. Establishes whether the forced-ranking fabrication pattern (e.g. the 60/25/10/5 breakdown) is repeatable, not a one-off. Saves every raw run to `repeated_forced_ranking/`. Does NOT auto-parse percentages out of free-form text (deliberately — fragile); read the saved files directly or have an agent read and summarize them.

### 3. `run_forced_ranking_test.py` — moderate

Forced-ranking baseline on all 3 cases only — does NOT re-run the pipeline or standard baseline (those are already in `comparison_outputs/`). Fills the Phase 19 gap: does an unaudited process fabricate a ranking when the prompt REQUIRES one and it can't opt out (requirement #4: "Rank the contributing causes... state what percentage... This ranking is required; provide it"). Score by comparing its "Ranked Impact Breakdown" against the pipeline's own Pareto Analysis section for the same case (`comparison_outputs/Case_*_comparison.md`, section A) — the audited pipeline consistently declined to fabricate.

### 4. `run_comparison.py` — MOST EXPENSIVE

Runs the FULL pipeline (`run_pipeline(case.diagnostic_input, max_revisions=1)`: Researcher → Analyst → Auditor → revision loop, several calls per case, more if a revision triggers) AND the standard baseline (`run_baseline(case.diagnostic_input)`) on all 3 cases, saving both side by side with reference material appended AFTER generation (never seen by either side).

**WARNING (the script's own recommendation — do not skip):** test on ONE case first by editing `CASE_FILES` to a single-item list (the commented-out line in the script) before running the full batch.

## HARD REQUIREMENT — MODEL sync across THREE files

`crewai_pipeline.py` defines `MODEL = "gemini/gemini-3.1-flash-lite"`. TWO baseline files independently HARDCODE the same string rather than importing it:

- `baseline_single_llm.py` — `MODEL = "gemini/gemini-3.1-flash-lite"  # same model as the full pipeline -- the only fair comparison`
- `baseline_forced_ranking.py` — `MODEL = "gemini/gemini-3.1-flash-lite"  # same model as pipeline and standard baseline`

Both comments say the hardcoding is deliberate. The comparison is only fair if all three stay in sync: if the pipeline's MODEL ever changes, BOTH baseline files must be updated explicitly and confirmed — otherwise the ablation study silently becomes invalid without erroring. Check all three match before trusting any comparison result.

## Quota note — different constraint from everything else

These scripts call Gemini's API directly via litellm/CrewAI, NOT through Qoder. Running them consumes Gemini's 15 RPM free-tier rate limit and real wall-clock time (extensive `time.sleep()` pacing throughout: 15–30s between calls/cases), not Qoder credits. The only Qoder cost is the agent invoking the script. Don't parallelize these runs — the pacing delays exist precisely because of the RPM ceiling.

## Functions to call by exact name

- `run_baseline(case_text)` — `baseline_single_llm.py`
- `run_baseline_forced_ranking(case_text)` — `baseline_forced_ranking.py`
- `run_pipeline(case_text, max_revisions)` — `crewai_pipeline.py` (used internally by `run_comparison.py`)

All baselines and the pipeline take `case.diagnostic_input` from `case_loader.load_case(...)` — same blind input on both sides of every comparison.

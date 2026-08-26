---
name: add-case-study
description: Add a new case packet to the MASS corpus (cases/Case_NN_*.md) following the exact section format. Use when adding, writing, or editing a case study, case packet, or case file, or when asked to extend the case corpus.
---

# Add Case Study

Adds a new case packet to `cases/` so it flows correctly through `case_loader.py` and the RAG pipeline (`rag_pipeline_starter.py`) without leaking ground truth. Enforces Rule #1 of `.qoder/rules/mass-standards.md` (ground-truth isolation).

## File naming

`cases/Case_NN_<Short_Name>.md` — zero-padded two-digit number, next in sequence (e.g. `Case_04_...`). `chunk_cases()` globs `Case_*.md`, so this prefix is required for indexing.

## Exact template

All three existing case files (`Case_01_Southwest_Airlines_2022_Meltdown.md`, `Case_02_Boeing_737_MAX_Crisis.md`, `Case_03_Peloton_Inventory_Oversupply.md`) follow this exact structure. Copy it precisely:

```markdown
# Case Packet NN: <Title>

**Domain:** <e.g. Aviation Operations / Manufacturing / Consumer Fitness>
**Case type:** Real, publicly documented event (not a licensed case-study product)
**Best-fit frameworks:** <comma-separated list>

---

## Problem Statement
<What went wrong, factually.>

## Background
<Company and situational context.>

## Supporting Data
<Numbers, dates, figures from public reporting.>

## Documented Root Cause / Investigation Findings
<Reference-only.>

## Resolution
<Reference-only.>

## Ground-Truth Diagnosis Summary
<Reference-only.>

## Sources
<Public sources.>
```

## Hard requirements

1. **Exact section order and exact header spelling.** `case_loader.py` and `rag_pipeline_starter.py` split on the literal `\n## ` header text and filter against `INPUT_SECTIONS = {"Problem Statement", "Background", "Supporting Data"}`. A header spelled or ordered differently (e.g. `## Problem statement`, `## Supporting data`) silently falls out of the input path AND gets misrouted — treat any deviation as a bug.

2. **Input sections are pure factual setup.** `Problem Statement`, `Background`, and `Supporting Data` are the ONLY sections any diagnosing agent or RAG retrieval ever sees. They must contain: no stated conclusions, no framework hints, no numbered root-cause findings, no "the actual cause was..." content. If a conclusion creeps in, it belongs in the reference sections below.

3. **Reference-only sections.** `Documented Root Cause / Investigation Findings`, `Resolution`, `Ground-Truth Diagnosis Summary`, and `Sources` are scoring material, used only AFTER generation completes. They must never be indexed, retrieved, or fed to any agent (Researcher, Analyst, Auditor, or Orchestrator).

4. **Real events only.** The case must be a real, publicly documented event — per the `**Case type:**` line convention, never a licensed case-study product. Cite public sources in `## Sources`.

5. **Do not modify the three retained case studies** (Southwest Airlines, Boeing 737 MAX, Peloton) — see Rule #4 in `.qoder/rules/mass-standards.md`. This skill is for ADDING a new file only.

## Post-add verification (mandatory)

After creating the file, re-run the indexer and verify no ground-truth section leaked into the corpus — same verification used for the original leakage fix:

```python
from rag_pipeline_starter import build_corpus

case_chunks = [c for c in build_corpus() if c.source == "case"]
headers = sorted(set(c.section for c in case_chunks))
print(f"Total case chunks: {len(case_chunks)}")
print("Unique section headers in case chunks:")
for h in headers:
    print(f"  - {h}")

allowed = {"Problem Statement", "Background", "Supporting Data"}
forbidden = {
    "Documented Root Cause / Investigation Findings",
    "Resolution",
    "Ground-Truth Diagnosis Summary",
    "Sources",
    "Best-fit frameworks",
}
assert set(headers) <= allowed, f"LEAKED HEADERS: {set(headers) - allowed}"
assert not (set(headers) & forbidden), "Ground truth indexed!"
print("OK: no leaked sections.")
```

Expected result: the new case contributes exactly 3 chunks (one per input section), and the printed headers contain ONLY `Problem Statement`, `Background`, `Supporting Data`. If any of the 4 reference-only headers (or `Best-fit frameworks`) appears in the output, the file's section headers deviate from the template — fix the file, do not touch the filter.

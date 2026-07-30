# -*- coding: utf-8 -*-
"""
Runs BOTH the full pipeline (Researcher -> Analyst -> Auditor -> revision
loop) and the single-call baseline on all 3 cases, and saves both outputs
side by side with the reference material (ground truth) for scoring.

Neither the pipeline nor the baseline ever sees the reference material --
both get case.diagnostic_input only. The reference material is appended
to the saved comparison file AFTER both have already produced their
output, purely so you (or a future scorer) can read all three side by
side.

Quota note: this is the most expensive script in the project so far --
each case now runs the full pipeline (several calls, more if a revision
triggers) PLUS one baseline call. Consider running one case at a time
first (edit CASE_FILES below to a single-item list) before running the
full batch.
"""

import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_pipeline
from baseline_single_llm import run_baseline
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("comparison_outputs")
OUT_DIR.mkdir(exist_ok=True)

MAX_REVISIONS = 1
DELAY_BETWEEN_CASES_SECONDS = 30
DELAY_BETWEEN_PIPELINE_AND_BASELINE_SECONDS = 15

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CASE_FILES = sorted(CASE_DIR.glob("Case_*.md"))
# To test on one case first (recommended), uncomment:
# CASE_FILES = [CASE_DIR / "Case_01_Southwest_Airlines_2022_Meltdown.md"]

if not CASE_FILES:
    raise SystemExit(f"No case files found in {CASE_DIR.resolve()} -- check the path.")

results_summary = []

for i, case_file in enumerate(CASE_FILES):
    print(f"\n{'=' * 80}\nComparison run on: {case_file.name}\n{'=' * 80}\n")
    case = load_case(case_file)

    try:
        print("--- Running full pipeline ---")
        pipeline_result = run_pipeline(case.diagnostic_input, max_revisions=MAX_REVISIONS)
        print(f"\nWaiting {DELAY_BETWEEN_PIPELINE_AND_BASELINE_SECONDS}s before baseline call...\n")
        time.sleep(DELAY_BETWEEN_PIPELINE_AND_BASELINE_SECONDS)

        print("--- Running baseline (single unscaffolded call) ---")
        baseline_result = run_baseline(case.diagnostic_input)
    except Exception as e:
        print(f"\n!! FAILED on {case_file.name}: {e}\n")
        out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_comparison.FAILED.txt"
        out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
        results_summary.append((case_file.name, "FAILED (error)"))
        if i < len(CASE_FILES) - 1:
            print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
            time.sleep(DELAY_BETWEEN_CASES_SECONDS)
        continue

    lines = [
        f"# Pipeline vs. Baseline Comparison — {case_file.name}",
        f"Run at: {datetime.now().isoformat(timespec='seconds')}",
        f"Pipeline final verdict: {'PASS' if pipeline_result['final_passed'] else 'FAIL'} "
        f"after {pipeline_result['total_attempts']} attempt(s)",
        "",
        "IMPORTANT: neither output below was generated with access to the ",
        "'Reference Material' section at the bottom of this file. Both saw ",
        "only the Problem Statement, Background, and Supporting Data.",
        "",
        "## A. FULL PIPELINE OUTPUT (Researcher -> Analyst -> Auditor, with revision loop)",
        "",
        pipeline_result["final_diagnosis"],
        "",
        "---",
        "",
        "## B. BASELINE OUTPUT (single unscaffolded LLM call, same model)",
        "",
        baseline_result,
        "",
        "---",
        "",
        "## [SCORING REFERENCE ONLY -- NOT SEEN BY EITHER OUTPUT ABOVE]",
        "",
        case.reference_material,
    ]

    out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_comparison.md"
    out_path.write_text("\n".join(lines))
    print(f"\nSaved to {out_path}\n")

    results_summary.append((case_file.name, "OK"))

    if i < len(CASE_FILES) - 1:
        print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

print(f"\nDone. Results:")
for name, status in results_summary:
    print(f"  [{status}] {name}")
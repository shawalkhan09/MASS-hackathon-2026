# -*- coding: utf-8 -*-
"""
Runs the forced-ranking baseline (baseline_forced_ranking.py) on all 3
cases. Does NOT re-run the pipeline or the standard baseline -- those are
already saved in comparison_outputs/ from the previous run. This script
exists purely to fill the one gap identified in DEVELOPMENT_LOG.md
Phase 19: does an unaudited process fabricate a ranking when it can't
opt out of providing one?

To score a result: compare the "Ranked Impact Breakdown" section this
produces against the corresponding case's Pareto Analysis section in the
pipeline's saved output (comparison_outputs/Case_*_comparison.md, section
A). The pipeline consistently declined to fabricate a ranking across all
3 cases (Phases 11-17, confirmed again in Phase 19). This is the first
real test of whether an unaudited process, given the identical case and
identical requirement, does the same.
"""

import time
from pathlib import Path
from datetime import datetime

from baseline_forced_ranking import run_baseline_forced_ranking
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("comparison_outputs")
OUT_DIR.mkdir(exist_ok=True)

DELAY_BETWEEN_CASES_SECONDS = 20

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CASE_FILES = sorted(CASE_DIR.glob("Case_*.md"))

if not CASE_FILES:
    raise SystemExit(f"No case files found in {CASE_DIR.resolve()} -- check the path.")

results_summary = []

for i, case_file in enumerate(CASE_FILES):
    print(f"\n{'=' * 80}\nForced-ranking baseline on: {case_file.name}\n{'=' * 80}\n")
    case = load_case(case_file)

    try:
        result = run_baseline_forced_ranking(case.diagnostic_input)
    except Exception as e:
        print(f"\n!! FAILED on {case_file.name}: {e}\n")
        out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_forced_ranking.FAILED.txt"
        out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
        results_summary.append((case_file.name, "FAILED (error)"))
        if i < len(CASE_FILES) - 1:
            print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
            time.sleep(DELAY_BETWEEN_CASES_SECONDS)
        continue

    lines = [
        f"# Forced-Ranking Baseline Output — {case_file.name}",
        f"Run at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Same model, same blind input as the standard baseline and the ",
        "pipeline. The only difference: this prompt explicitly REQUIRES a ",
        "ranked breakdown of causes by impact (see baseline_forced_ranking.py), ",
        "closing the gap where the standard baseline simply never attempted ",
        "one. To score: compare the 'ranked breakdown' section below against ",
        "the corresponding case's Pareto Analysis section in this project's ",
        "comparison_outputs/Case_*_comparison.md (section A, the pipeline's ",
        "output), which consistently declined to fabricate a ranking.",
        "",
        "## FORCED-RANKING BASELINE OUTPUT",
        "",
        result,
        "",
        "---",
        "",
        "## [SCORING REFERENCE ONLY -- NOT SEEN BY THE OUTPUT ABOVE]",
        "",
        case.reference_material,
    ]

    out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_forced_ranking.md"
    out_path.write_text("\n".join(lines))
    print(f"\nSaved to {out_path}\n")

    results_summary.append((case_file.name, "OK"))

    if i < len(CASE_FILES) - 1:
        print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

print(f"\nDone. Results:")
for name, status in results_summary:
    print(f"  [{status}] {name}")
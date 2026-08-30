# -*- coding: utf-8 -*-
"""
Extends the repeated forced-ranking baseline test (DEVELOPMENT_LOG.md
Phase 20/22, report Section 8.7) to the two cases added in Phase 54 --
PIA and Airlift -- which were never run through this specific test.

Deliberately scoped to only these two cases, not all five, so this does
not re-burn API quota re-running Southwest/Boeing/Peloton, which are
already documented at n=9 in Section 8.7's Table 1.

Run from venv312 (the pipeline environment):
    python3 run_forced_ranking_pia_airlift.py

3 runs x 2 cases = 6 calls total, same cost class as the original n=9
run. Saves to repeated_forced_ranking/ using the same naming pattern as
the original script, so results sit alongside the existing nine files
and are easy to read together.
"""

import time
from pathlib import Path
from datetime import datetime

from baseline_forced_ranking import run_baseline_forced_ranking
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("repeated_forced_ranking")
OUT_DIR.mkdir(exist_ok=True)

# Only the two cases added in Phase 54 -- deliberately not the full glob,
# to avoid re-running the three cases already documented at n=9.
CASE_FILES = [
    CASE_DIR / "Case_04_PIA_Karachi_Crash_and_Financial_Crisis.md",
    CASE_DIR / "Case_05_Airlift_Technologies_Collapse.md",
]

for f in CASE_FILES:
    if not f.exists():
        raise SystemExit(f"Expected case file not found: {f}")

N_REPETITIONS = 3  # matches the original n=9 run's 3-per-case standard
DELAY_BETWEEN_RUNS_SECONDS = 15
DELAY_BETWEEN_CASES_SECONDS = 25

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

results_summary = []

for i, case_file in enumerate(CASE_FILES):
    case = load_case(case_file)
    print(f"\n{'=' * 80}\nRepeated forced-ranking test on: {case_file.name} ({N_REPETITIONS} runs)\n{'=' * 80}\n")

    for run_num in range(1, N_REPETITIONS + 1):
        print(f"\n--- Run {run_num}/{N_REPETITIONS} for {case_file.name} ---\n")
        try:
            result = run_baseline_forced_ranking(case.diagnostic_input)
        except Exception as e:
            print(f"\n!! FAILED on {case_file.name} run {run_num}: {e}\n")
            out_path = OUT_DIR / f"{case_file.stem}_run{run_num}_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
            results_summary.append((case_file.name, run_num, "FAILED"))
        else:
            out_path = OUT_DIR / f"{case_file.stem}_run{run_num}_{RUN_TIMESTAMP}.md"
            out_path.write_text(
                f"# Forced-ranking baseline -- {case_file.name} -- Run {run_num}/{N_REPETITIONS}\n"
                f"Run at: {datetime.now().isoformat(timespec='seconds')}\n\n{result}\n"
            )
            print(f"Saved to {out_path}")
            results_summary.append((case_file.name, run_num, "OK"))

        is_last = (i == len(CASE_FILES) - 1) and (run_num == N_REPETITIONS)
        if not is_last:
            print(f"Waiting {DELAY_BETWEEN_RUNS_SECONDS}s before next run...")
            time.sleep(DELAY_BETWEEN_RUNS_SECONDS)

    if i < len(CASE_FILES) - 1:
        print(f"\nWaiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

print(f"\n{'=' * 80}\nDONE. {len(results_summary)} total runs.\n{'=' * 80}")
for name, run_num, status in results_summary:
    print(f"  [{status}] {name} run {run_num}")

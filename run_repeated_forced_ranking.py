# -*- coding: utf-8 -*-
"""
Repeats the forced-ranking baseline test (DEVELOPMENT_LOG.md Phase 20 /
report Section 8.5) N times per case, to establish whether the 60/25/10/5
fabrication pattern is a reliable, repeatable phenomenon or a single
observation -- the explicit limitation stated in both the dev log and
the report's Section 10.2.

Saves every individual run's raw output to disk. Does NOT attempt to
auto-parse percentages out of free-form text (fragile) -- read the saved
files directly, or have an agent read them and summarize (see the
companion prompt for that).

Quota note: N_REPETITIONS x 3 cases = total baseline calls. Each is a
single unscaffolded LLM call (not a multi-step pipeline run), so this is
cheap relative to earlier scripts in this project. N_REPETITIONS=3 ->
9 calls total.
"""

import time
from pathlib import Path
from datetime import datetime

from baseline_forced_ranking import run_baseline_forced_ranking
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("repeated_forced_ranking")
OUT_DIR.mkdir(exist_ok=True)

N_REPETITIONS = 3  # runs per case -- adjust down if quota-constrained
DELAY_BETWEEN_RUNS_SECONDS = 15  # respects RPM limits between individual calls
DELAY_BETWEEN_CASES_SECONDS = 25

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CASE_FILES = sorted(CASE_DIR.glob("Case_*.md"))

if not CASE_FILES:
    raise SystemExit(f"No case files found in {CASE_DIR.resolve()} -- check the path.")

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
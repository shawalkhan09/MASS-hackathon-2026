# -*- coding: utf-8 -*-
"""
Run the full Researcher -> Analyst -> Auditor pipeline (with revision loop)
against all 3 case packets and save each result.

Saves the FULL attempt history per case, not just the final diagnosis --
if a case needed a revision, you can see attempt 1 (with its FAIL) and
attempt 2 (with its PASS or FAIL) side by side in the same file. That's
the actual evidence the revision loop does something, not just a claim
that it does.

IMPORTANT (see DEVELOPMENT_LOG.md Phase 17): the pipeline is fed
case.diagnostic_input (Problem Statement + Background + Supporting Data
only), NOT the raw case file. The raw file contains a "Best-fit
frameworks" hint and the Ground-Truth Diagnosis Summary -- feeding that
to the agents would hand them the answer. The reference material (ground
truth, documented findings) is appended to the SAVED output file, after
the pipeline has already produced its diagnosis, purely so you have it
side-by-side for scoring -- it is never part of any prompt.

Quota note: each case now makes more LLM calls than before (Researcher +
Analyst draft + Auditor, plus a revision + re-audit for every FAIL). With
max_revisions=1 (the default below), worst case per case is roughly
double the calls of the pre-revision-loop pipeline. Keep MAX_REVISIONS
conservative and watch your daily quota if running this repeatedly.
"""

import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_pipeline
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("researcher_outputs")
OUT_DIR.mkdir(exist_ok=True)

# Max revision+re-audit cycles per case if the Auditor fails a diagnosis.
# Keep this at 1 to start -- raise it later once you've confirmed the loop
# behaves as expected and you have quota headroom to spare.
MAX_REVISIONS = 1

# Gap between cases -- gives the free-tier RPM window room to reset, and
# means one case's failure doesn't cascade into burning quota on the next.
DELAY_BETWEEN_CASES_SECONDS = 30

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CASE_FILES = sorted(CASE_DIR.glob("Case_*.md"))

if not CASE_FILES:
    raise SystemExit(f"No case files found in {CASE_DIR.resolve()} -- check the path.")

results_summary = []

for i, case_file in enumerate(CASE_FILES):
    print(f"\n{'=' * 80}\nRunning pipeline on: {case_file.name}\n{'=' * 80}\n")
    case = load_case(case_file)

    try:
        result = run_pipeline(case.diagnostic_input, max_revisions=MAX_REVISIONS)
    except Exception as e:
        # Don't let one case's quota/API failure kill the whole batch --
        # record it and move on, so you keep whatever succeeded before it.
        print(f"\n!! FAILED on {case_file.name}: {e}\n")
        out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_output.FAILED.txt"
        out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
        results_summary.append((case_file.name, "FAILED (error)"))
        if i < len(CASE_FILES) - 1:
            print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
            time.sleep(DELAY_BETWEEN_CASES_SECONDS)
        continue

    # Build a report showing every attempt, not just the final one.
    lines = [
        f"# Researcher + Analyst + Auditor output (with revision loop) — {case_file.name}",
        f"Run at: {datetime.now().isoformat(timespec='seconds')}",
        f"Final verdict: {'PASS' if result['final_passed'] else 'FAIL'} "
        f"after {result['total_attempts']} attempt(s)",
        "",
        "## Framework Selection (Researcher)",
        "",
        result["framework_context"],
        "",
    ]
    for h in result["history"]:
        lines.append(f"## Attempt {h['attempt']} — {'PASS' if h['passed'] else 'FAIL'}")
        lines.append("")
        lines.append("### Diagnosis")
        lines.append("")
        lines.append(h["diagnosis"])
        lines.append("")
        lines.append("### Audit")
        lines.append("")
        lines.append(h["audit"])
        lines.append("")

    # Reference material appended LAST, clearly marked -- for scoring only,
    # was never part of any prompt sent to any agent above.
    lines.append("---")
    lines.append("")
    lines.append("## [SCORING REFERENCE ONLY -- NOT SEEN BY ANY AGENT ABOVE]")
    lines.append("")
    lines.append(case.reference_material)

    out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_output.md"
    out_path.write_text("\n".join(lines))
    print(f"\nSaved to {out_path}\n")

    status = "PASS" if result["final_passed"] else "FAIL"
    revised = " (revised)" if result["total_attempts"] > 1 else ""
    results_summary.append((case_file.name, f"{status}{revised}"))

    if i < len(CASE_FILES) - 1:
        print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case (respecting rate limits)...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

print(f"\nDone. Results:")
for name, status in results_summary:
    print(f"  [{status}] {name}")
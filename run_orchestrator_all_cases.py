# -*- coding: utf-8 -*-
"""
Run the full Researcher -> Analyst -> Auditor pipeline (with revision
loop) PLUS the Orchestrator's synthesis stage against all 3 case
packets, and save each result.

Mirrors run_researcher_all_cases.py's structure and conventions
directly -- same timestamping, same reference-material-appended-last
pattern, same input-hygiene rule (Phase 17: only ever pass
case.diagnostic_input to any agent, never a raw case file read
directly, since raw files contain the "Best-fit frameworks" hint and
the Ground-Truth Diagnosis Summary).

Quota note: this adds ONE more LLM call on top of run_pipeline()'s
existing cost, and only on cases that pass audit -- a case that never
passes costs nothing extra here, since run_orchestrator() makes no LLM
call at all on a FLAGGED_FOR_REVIEW result (see orchestrator.py). Worst
case per case is still run_pipeline()'s existing worst case plus one.
"""

import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_pipeline
from orchestrator import run_orchestrator
from case_loader import load_case

CASE_DIR = Path("cases")
OUT_DIR = Path("orchestrator_outputs")
OUT_DIR.mkdir(exist_ok=True)

MAX_REVISIONS = 1
DELAY_BETWEEN_CASES_SECONDS = 30

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CASE_FILES = sorted(CASE_DIR.glob("Case_*.md"))

if not CASE_FILES:
    raise SystemExit(f"No case files found in {CASE_DIR.resolve()} -- check the path.")

results_summary = []

for i, case_file in enumerate(CASE_FILES):
    print(f"\n{'=' * 80}\nRunning pipeline + orchestrator on: {case_file.name}\n{'=' * 80}\n")
    case = load_case(case_file)

    try:
        pipeline_result = run_pipeline(case.diagnostic_input, max_revisions=MAX_REVISIONS)
        orchestrator_result = run_orchestrator(pipeline_result)
    except Exception as e:
        print(f"\n!! FAILED on {case_file.name}: {e}\n")
        out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_output.FAILED.txt"
        out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
        results_summary.append((case_file.name, "FAILED (error)"))
        if i < len(CASE_FILES) - 1:
            print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
            time.sleep(DELAY_BETWEEN_CASES_SECONDS)
        continue

    lines = [
        f"# Researcher + Analyst + Auditor + Orchestrator output — {case_file.name}",
        f"Run at: {datetime.now().isoformat(timespec='seconds')}",
        f"Pipeline verdict: {'PASS' if pipeline_result['final_passed'] else 'FAIL'} "
        f"after {pipeline_result['total_attempts']} attempt(s)",
        f"Orchestrator status: {orchestrator_result['status']}",
        "",
        "## Framework Selection (Researcher)",
        "",
        pipeline_result["framework_context"],
        "",
    ]
    for h in pipeline_result["history"]:
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

    lines.append("## Orchestrator (Engagement Manager)")
    lines.append("")
    if orchestrator_result["status"] == "SYNTHESIZED":
        lines.append("### Final Client-Facing Report")
        lines.append("")
        lines.append(orchestrator_result["final_report"])
        lines.append("")
        lines.append("### Fidelity Check")
        lines.append("")
        lines.append(orchestrator_result.get("fidelity_verdict") or "(not available)")
    elif orchestrator_result["status"] == "FLAGGED_FIDELITY_FAILURE":
        lines.append("### FLAGGED FOR FIDELITY FAILURE — report withheld, not a verified deliverable")
        lines.append("")
        lines.append(orchestrator_result["reason"])
        lines.append("")
        lines.append("### Fidelity Verdict (full text)")
        lines.append("")
        lines.append(orchestrator_result.get("fidelity_verdict") or "(not available)")
        lines.append("")
        lines.append("### Unverified Report (debugging only — NOT a verified deliverable)")
        lines.append("")
        lines.append(orchestrator_result.get("unverified_report") or "(not available)")
    else:
        lines.append("### FLAGGED FOR REVIEW — no report synthesized")
        lines.append("")
        lines.append(orchestrator_result["reason"])
    lines.append("")

    # Reference material appended LAST, clearly marked -- for scoring only,
    # never part of any prompt sent to any agent above (Phase 17).
    lines.append("---")
    lines.append("")
    lines.append("## [SCORING REFERENCE ONLY -- NOT SEEN BY ANY AGENT ABOVE]")
    lines.append("")
    lines.append(case.reference_material)

    out_path = OUT_DIR / f"{case_file.stem}_{RUN_TIMESTAMP}_output.md"
    out_path.write_text("\n".join(lines))
    print(f"\nSaved to {out_path}\n")

    status = f"{orchestrator_result['status']}"
    revised = " (revised)" if pipeline_result["total_attempts"] > 1 else ""
    results_summary.append((case_file.name, f"{status}{revised}"))

    if i < len(CASE_FILES) - 1:
        print(f"Waiting {DELAY_BETWEEN_CASES_SECONDS}s before next case (respecting rate limits)...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

print(f"\nDone. Results:")
for name, status in results_summary:
    print(f"  [{status}] {name}")
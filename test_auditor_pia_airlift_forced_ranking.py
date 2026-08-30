# -*- coding: utf-8 -*-
"""
Extends the Auditor fabrication-catching test (DEVELOPMENT_LOG.md
Phase 21/22, report Section 8.6/8.8) to the 6 real forced-ranking
outputs produced by run_forced_ranking_pia_airlift.py.

v2: the first version of this script only printed each verdict to the
terminal. Terminal scrollback truncates on long sessions, so five of
the six verdicts were lost the first time this ran -- the same class
of problem this project's file-saving convention (orchestrator_outputs/,
repeated_forced_ranking/, etc.) exists to avoid. This version saves
every verdict to disk, one file per run, matching that existing
convention.

Run from venv312, AFTER run_forced_ranking_pia_airlift.py has produced
files in repeated_forced_ranking/:
    python3 test_auditor_pia_airlift_forced_ranking.py

6 LLM calls (one audit per saved output) -- same cost class as the
generation step.
"""

from pathlib import Path
from datetime import datetime

from case_loader import load_case
from crewai_pipeline import run_auditor, parse_verdict

CASE_DIR = Path("cases")
IN_DIR = Path("repeated_forced_ranking")
OUT_DIR = Path("audit_pia_airlift")
OUT_DIR.mkdir(exist_ok=True)

CASES = {
    "Case_04_PIA_Karachi_Crash_and_Financial_Crisis": CASE_DIR / "Case_04_PIA_Karachi_Crash_and_Financial_Crisis.md",
    "Case_05_Airlift_Technologies_Collapse": CASE_DIR / "Case_05_Airlift_Technologies_Collapse.md",
}

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

results = []

for stem, case_path in CASES.items():
    case = load_case(case_path)
    matching_files = sorted(IN_DIR.glob(f"{stem}_run*.md"))
    if not matching_files:
        print(f"!! No saved forced-ranking outputs found for {stem} in {IN_DIR} -- "
              f"run run_forced_ranking_pia_airlift.py first.")
        continue

    for f in matching_files:
        baseline_output = f.read_text()
        print(f"\n{'=' * 80}\nAuditing: {f.name}\n{'=' * 80}\n")
        try:
            audit_text = run_auditor(case.diagnostic_input, baseline_output)
        except Exception as e:
            print(f"\n!! FAILED auditing {f.name}: {e}\n")
            out_path = OUT_DIR / f"{f.stem}_audit_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Audit failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
            results.append((f.name, None))
            continue

        caught = not parse_verdict(audit_text)  # parse_verdict returns True if PASS
        print(audit_text)
        print(f"\n--> {'CAUGHT (Auditor correctly failed this)' if caught else 'NOT CAUGHT (Auditor passed this)'}")

        out_path = OUT_DIR / f"{f.stem}_audit_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Auditor verdict -- {f.name}\n"
            f"Run at: {datetime.now().isoformat(timespec='seconds')}\n"
            f"Result: {'CAUGHT' if caught else 'NOT CAUGHT'}\n\n"
            f"## Baseline output audited\n\n{baseline_output}\n\n"
            f"## Full Auditor verdict\n\n{audit_text}\n"
        )
        print(f"Saved to {out_path}")
        results.append((f.name, caught))

print(f"\n{'=' * 80}\nSUMMARY\n{'=' * 80}")
for name, caught in results:
    status = "CAUGHT" if caught else ("FAILED (audit call errored)" if caught is None else "MISSED")
    print(f"  [{status}] {name}")
n_caught = sum(1 for _, c in results if c)
n_total = len(results)
print(f"\n{n_caught}/{n_total} fabricated outputs correctly caught by the Auditor.")
print(f"\nAll verdicts saved to {OUT_DIR}/ -- share that whole folder rather than terminal output.")
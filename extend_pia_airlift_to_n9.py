# -*- coding: utf-8 -*-
"""
Extends the PIA/Airlift forced-ranking baseline test from n=3 to n=9
per case, matching the scale used to characterise the original three
cases (Southwest, Boeing, Peloton -- Section 8.7). Section 10.3
flagged this explicitly: the existing PIA/Airlift result is "reported
at exactly the scale it was run: three trials per case... offered as
corroborating evidence... rather than an independent replication at
the same statistical weight as Section 8.7."

WHY THIS EXTENDS RATHER THAN RESTARTS:
run_forced_ranking_pia_airlift.py already produced 3 real, saved runs
per case (repeated_forced_ranking/Case_0{4,5}_..._run{1,2,3}_*.md),
already audited and saved (audit_pia_airlift/..._run{1,2,3}_audit_*.md,
Phase 60). Re-running those 3 from scratch would burn quota for no new
evidence and would also throw away the exact real files Section 8.14
already cites. This script generates ONLY 6 new runs per case (run4
through run9), audits ONLY those 6 new runs, and then reports a
combined n=9 tally sourced entirely from real saved files on disk --
3 old + 6 new -- rather than re-deriving anything.

SAFETY: refuses to run if run4-run9 files already exist for either
case, so this can't silently double-generate or overwrite prior
evidence on a second invocation. Delete or move
repeated_forced_ranking/*_run{4..9}_*.md first if you deliberately want
to redo this extension.

Run from venv312, from the repo root:
    python3 extend_pia_airlift_to_n9.py

12 generation calls + 12 audit calls = 24 LLM calls total (6 new runs
x 2 cases x 2 steps), same cost class as the original n=9 Southwest/
Boeing/Peloton run.
"""

import time
from pathlib import Path
from datetime import datetime

from baseline_forced_ranking import run_baseline_forced_ranking
from case_loader import load_case
from crewai_pipeline import run_auditor, parse_verdict

CASE_DIR = Path("cases")
GEN_DIR = Path("repeated_forced_ranking")
AUDIT_DIR = Path("audit_pia_airlift")
GEN_DIR.mkdir(exist_ok=True)
AUDIT_DIR.mkdir(exist_ok=True)

CASES = {
    "Case_04_PIA_Karachi_Crash_and_Financial_Crisis": CASE_DIR / "Case_04_PIA_Karachi_Crash_and_Financial_Crisis.md",
    "Case_05_Airlift_Technologies_Collapse": CASE_DIR / "Case_05_Airlift_Technologies_Collapse.md",
}

NEW_RUN_NUMBERS = range(4, 10)  # run4 through run9 -- 6 new runs per case
DELAY_BETWEEN_CALLS_SECONDS = 15
DELAY_BETWEEN_CASES_SECONDS = 25

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

# ---------------------------------------------------------------------
# Safety check: refuse to proceed if any run4-9 file already exists for
# either case -- prevents silently overwriting or double-generating on
# a second, accidental invocation.
# ---------------------------------------------------------------------
for stem in CASES:
    for n in NEW_RUN_NUMBERS:
        existing = list(GEN_DIR.glob(f"{stem}_run{n}_*.md"))
        if existing:
            raise SystemExit(
                f"Found existing file(s) for {stem} run{n}: {existing} -- "
                f"this script only generates run4-run9 and refuses to run "
                f"again once any of them exist. Move or delete them first "
                f"if you deliberately want to redo this extension."
            )

# ---------------------------------------------------------------------
# Step 1: generate 6 new runs per case (run4-run9), saved immediately.
# ---------------------------------------------------------------------
new_gen_files = {stem: [] for stem in CASES}

for i, (stem, case_path) in enumerate(CASES.items()):
    case = load_case(case_path)
    print(f"\n{'=' * 80}\nGenerating runs 4-9 for: {stem}\n{'=' * 80}\n")

    for run_num in NEW_RUN_NUMBERS:
        print(f"\n--- Generating run {run_num}/9 for {stem} ---\n")
        try:
            result = run_baseline_forced_ranking(case.diagnostic_input)
        except Exception as e:
            print(f"\n!! FAILED generating {stem} run {run_num}: {e}\n")
            out_path = GEN_DIR / f"{stem}_run{run_num}_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Run failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
        else:
            out_path = GEN_DIR / f"{stem}_run{run_num}_{RUN_TIMESTAMP}.md"
            out_path.write_text(
                f"# Forced-ranking baseline -- {stem} -- Run {run_num}/9\n"
                f"Run at: {datetime.now().isoformat(timespec='seconds')}\n\n{result}\n"
            )
            print(f"Saved to {out_path}")
            new_gen_files[stem].append(out_path)

        time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

    if i < len(CASES) - 1:
        print(f"\nWaiting {DELAY_BETWEEN_CASES_SECONDS}s before next case...\n")
        time.sleep(DELAY_BETWEEN_CASES_SECONDS)

# ---------------------------------------------------------------------
# Step 2: audit ONLY the 6 new runs per case just generated (not the
# existing 3, which are already audited and saved from Phase 60).
# ---------------------------------------------------------------------
new_audit_results = {stem: [] for stem in CASES}

for stem, case_path in CASES.items():
    case = load_case(case_path)
    for gen_path in new_gen_files[stem]:
        print(f"\n{'=' * 80}\nAuditing: {gen_path.name}\n{'=' * 80}\n")
        baseline_output = gen_path.read_text()
        try:
            audit_text = run_auditor(case.diagnostic_input, baseline_output)
        except Exception as e:
            print(f"\n!! FAILED auditing {gen_path.name}: {e}\n")
            out_path = AUDIT_DIR / f"{gen_path.stem}_audit_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Audit failed at {datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n")
            new_audit_results[stem].append(None)
            time.sleep(DELAY_BETWEEN_CALLS_SECONDS)
            continue

        caught = not parse_verdict(audit_text)  # True if the Auditor correctly FAILed the fabrication
        print(audit_text)
        print(f"\n--> {'CAUGHT' if caught else 'NOT CAUGHT'}")

        out_path = AUDIT_DIR / f"{gen_path.stem}_audit_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Auditor verdict -- {gen_path.name}\n"
            f"Run at: {datetime.now().isoformat(timespec='seconds')}\n"
            f"Result: {'CAUGHT' if caught else 'NOT CAUGHT'}\n\n"
            f"## Baseline output audited\n\n{baseline_output}\n\n"
            f"## Full Auditor verdict\n\n{audit_text}\n"
        )
        print(f"Saved to {out_path}")
        new_audit_results[stem].append(caught)

        time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

# ---------------------------------------------------------------------
# Step 3: combine with the 3 EXISTING real audit files already on disk
# (Phase 60) to report the full, real n=9 tally per case -- read from
# disk, not assumed or re-derived.
# ---------------------------------------------------------------------
print(f"\n{'=' * 80}\nCOMBINED n=9 SUMMARY (3 existing + 6 new, per case)\n{'=' * 80}")

grand_total_caught = 0
grand_total_n = 0

for stem in CASES:
    existing_audit_files = sorted(AUDIT_DIR.glob(f"{stem}_run[123]_*_audit_*.md"))
    existing_caught = 0
    for f in existing_audit_files:
        text = f.read_text()
        if "Result: CAUGHT" in text:
            existing_caught += 1

    new_caught = sum(1 for c in new_audit_results[stem] if c is True)
    new_n = sum(1 for c in new_audit_results[stem] if c is not None)

    total_caught = existing_caught + new_caught
    total_n = len(existing_audit_files) + new_n

    print(f"\n{stem}:")
    print(f"  Existing (Phase 60, runs 1-3): {existing_caught}/{len(existing_audit_files)} caught")
    print(f"  New (this run, runs 4-9):      {new_caught}/{new_n} caught")
    print(f"  Combined n={total_n}:          {total_caught}/{total_n} caught")

    grand_total_caught += total_caught
    grand_total_n += total_n

print(f"\n{'=' * 80}")
print(f"GRAND TOTAL across both cases: {grand_total_caught}/{grand_total_n} fabricated "
      f"forced-ranking outputs correctly caught by the Auditor.")
print(f"{'=' * 80}")
print("\nReport each case's own n=9 figure (Section 8.14 update). If citing the")
print("grand total, label it explicitly as combining Phase 60's 3 real runs per")
print("case with this round's 6 new ones -- same real case files and same")
print("Auditor wording throughout, so pooling is legitimate here (unlike the")
print("Ohio Warehouse / Check 1 Part B situation, where methodology differed")
print("across rounds).")
print(f"\nAll new evidence saved to {GEN_DIR}/ and {AUDIT_DIR}/ alongside the")
print("existing Phase 60 files.")

# -*- coding: utf-8 -*-
"""
n=9 re-validation of fidelity_check.py's v5 isolated-check architecture
against all 5 fixtures established across the check's 5-round
calibration history (Section 6.7).

WHY THIS EXISTS:
v5's own module docstring says it plainly: rewriting Check A/B/C as
three isolated Agent+Task+Crew calls removes the cross-check-bleed
variable that broke Check C twice under the old shared-prompt design,
but "doesn't guarantee identical behavior to before on every other
dimension. This needs its own verification pass, same standard as
every prior revision in this file's history." That verification pass
never fully happened: test_fidelity_check_v5_verification.py only
re-ran 2 of the 5 established fixtures (peloton_real, category_renamed)
under the isolated architecture, at n=3. paraphrase_only,
parenthetical_dropped, and qualifier_dropped have only ever been
validated under the OLD v1-v4 shared-prompt design -- never under v5's
isolated calls at all, at any n.

This script closes both gaps in one pass: it re-runs all 5 fixtures
under the current (unchanged) v5 wording, and does so at n=9 per
fixture -- matching the scale used throughout this project for the
Auditor's own checks (Section 8.7), rather than the n=3-5 the fidelity
check has been held to until now (Section 10.2).

FIXTURES (imported unchanged, no new fixture construction -- these are
already proven-correct single-variable constructions from Section 6.7's
calibration rounds):
  - paraphrase_only            -> Check A only  (expected PASS)
  - parenthetical_dropped      -> Check B only  (expected PASS)
  - category_renamed           -> Check B only  (expected FAIL, the
                                   real Phase 25 Southwest bug shape)
  - qualifier_dropped          -> Check C only  (expected FAIL)
  - peloton_real                -> Check A, B, and C, all three,
                                   since this is the real diagnosis and
                                   withheld report from the graduation
                                   run and is the only fixture that
                                   exercises all three checks jointly
                                   (expected A=PASS, B=PASS, C=FAIL)

Only the check(s) each fixture actually targets are called -- e.g.
paraphrase_only only ever tested Check A across every prior round, so
calling Check B/C on it would just be spending quota on an
already-settled question. peloton_real is the exception: it is the
project's one real, non-synthetic, multi-cause fixture, and all three
checks running against it together is itself part of what's being
confirmed at this scale.

Total calls: (9 x 4 single-check fixtures) + (9 x 3 checks for
peloton_real) = 36 + 27 = 63 LLM calls.

Every trial's full verdict text is saved to disk before any tally is
printed -- rename or move OUT_DIR before re-running this script if you
need to preserve a prior round's output rather than overwrite it.
"""

import time
from pathlib import Path
from datetime import datetime

from fidelity_check import run_check_a, run_check_b, run_check_c
from test_fidelity_check_calibration_v2 import (
    APPROVED_DIAGNOSIS as SW_DIAGNOSIS,
    PARAPHRASE_ONLY_REPORT,
    PARENTHETICAL_DROPPED_REPORT,
    CATEGORY_RENAMED_REPORT,
    QUALIFIER_DROPPED_REPORT,
)

N_TRIALS = 9
DELAY_SECONDS = 10  # pacing, matches prior fidelity-check rounds' spacing

OUT_DIR = Path("fidelity_check_n9_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

with open("peloton_real/diagnosis.txt") as f:
    PELOTON_DIAGNOSIS = f.read()
with open("peloton_real/report.txt") as f:
    PELOTON_REPORT = f.read()

# ---------------------------------------------------------------------
# Each entry: (fixture_name, diagnosis_text, report_text,
#              [(check_label, check_fn, expected), ...])
# ---------------------------------------------------------------------
FIXTURES = [
    (
        "paraphrase_only", SW_DIAGNOSIS, PARAPHRASE_ONLY_REPORT,
        [("Check A", run_check_a, "PASS")],
    ),
    (
        "parenthetical_dropped", SW_DIAGNOSIS, PARENTHETICAL_DROPPED_REPORT,
        [("Check B", run_check_b, "PASS")],
    ),
    (
        "category_renamed", SW_DIAGNOSIS, CATEGORY_RENAMED_REPORT,
        [("Check B", run_check_b, "FAIL")],
    ),
    (
        "qualifier_dropped", SW_DIAGNOSIS, QUALIFIER_DROPPED_REPORT,
        [("Check C", run_check_c, "FAIL")],
    ),
    (
        "peloton_real", PELOTON_DIAGNOSIS, PELOTON_REPORT,
        [
            ("Check A", run_check_a, "PASS"),
            ("Check B", run_check_b, "PASS"),
            ("Check C", run_check_c, "FAIL"),
        ],
    ),
]

all_results = {}  # (fixture, check_label) -> list of "PASS"/"FAIL"/"ERROR"

for fixture_name, diagnosis_text, report_text, checks in FIXTURES:
    for check_label, check_fn, expected in checks:
        key = f"{fixture_name} / {check_label}"
        outcomes = []
        print(f"\n{'=' * 70}\n{key} -- n={N_TRIALS}, expected {expected}\n{'=' * 70}\n")

        for trial in range(1, N_TRIALS + 1):
            try:
                result = check_fn(approved_diagnosis=diagnosis_text, final_report=report_text)
            except Exception as e:
                print(f"\n!! FAILED on {key} trial {trial}: {e}\n")
                out_path = OUT_DIR / f"{fixture_name}_{check_label.replace(' ', '')}_trial{trial}_{RUN_TIMESTAMP}.FAILED.txt"
                out_path.write_text(
                    f"{key} trial {trial}/{N_TRIALS} failed at "
                    f"{datetime.now().isoformat(timespec='seconds')}\n\nError:\n{e}\n"
                )
                outcomes.append("ERROR")
                time.sleep(DELAY_SECONDS)
                continue

            actual = "PASS" if result["passed"] else "FAIL"
            match = "MATCH" if actual == expected else "MISMATCH"
            outcomes.append(actual)

            out_path = OUT_DIR / f"{fixture_name}_{check_label.replace(' ', '')}_trial{trial}_{RUN_TIMESTAMP}.md"
            out_path.write_text(
                f"# Fidelity check n=9 -- {fixture_name} -- {check_label} -- "
                f"Trial {trial}/{N_TRIALS}\n\n"
                f"**Expected:** {expected}\n\n"
                f"**Actual:** {actual}\n\n"
                f"**Match:** {match}\n\n"
                f"---\n\n## Full raw verdict text\n\n{result['verdict_text']}\n"
            )

            print(f"[{key}] trial {trial}/{N_TRIALS}: expected {expected}, got {actual} ({match})")
            if match == "MISMATCH":
                print("  --- full verdict for this mismatched trial ---")
                print(result["verdict_text"])
                print("  --- end verdict ---")

            time.sleep(DELAY_SECONDS)

        all_results[key] = (outcomes, expected)
        pass_count = outcomes.count("PASS")
        fail_count = outcomes.count("FAIL")
        error_count = outcomes.count("ERROR")
        print(f"\n[{key}] summary: {pass_count} PASS / {fail_count} FAIL"
              f"{f' / {error_count} ERROR' if error_count else ''} "
              f"out of {N_TRIALS} (expected {expected})\n")

print(f"\n{'=' * 70}\nFINAL SUMMARY -- n={N_TRIALS} per fixture/check\n{'=' * 70}")
for key, (outcomes, expected) in all_results.items():
    correct = sum(1 for o in outcomes if o == expected)
    n = len(outcomes)
    flag = "OK" if correct == n else "INVESTIGATE"
    print(f"  [{flag}] {key}: {correct}/{n} matched expected ({expected})")

print(f"\nRaw per-trial evidence saved to: {OUT_DIR}/")
print("Report each fixture/check at its own n=9 figure. Do not average across")
print("fixtures that test different checks -- e.g. paraphrase_only's Check A")
print("result and qualifier_dropped's Check C result answer different questions")
print("and should not be pooled into one 'fidelity check accuracy' number.")

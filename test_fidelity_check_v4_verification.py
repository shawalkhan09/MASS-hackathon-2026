# -*- coding: utf-8 -*-
"""
Verification for the v4 Check B scope fix -- tests against the REAL
Peloton diagnosis and report from the actual 3-case graduation run
(not a new synthetic fixture), since that's the exact data that
revealed the problem: v3 flagged "Financial Metrics" -> "Financial
Impact" and "Porter's Five Forces" -> "Market Dynamics (Porter's Five
Forces)" as Check B violations, even though both are report section
retitles, not Fishbone-style cause-classification changes.

Expected under v4: still FAIL overall (Check C's two genuine qualifier
drops -- the dropped "into expansion" scoping on the 55% figure, and
the dropped storage/insurance/obsolescence breakdown on the 15% figure
-- are untouched by this revision and should still be caught). But
Check B specifically should now come back PASS or at least stop citing
the two section-heading retitles as violations.

Also re-runs category_renamed (imported from the v2 fixture file,
unchanged) as a regression check -- confirming the narrower Check B
scope still catches an actual Fishbone-style primary-label change, not
just section headings.

N_TRIALS = 3 per check -- lighter than a full n=5 calibration round,
since this targets a specific, well-understood fix rather than an
open question about the check's general reliability. Real-data
verification (this fixture) matters more here than trial count.
"""

import time

from fidelity_check import run_fidelity_check
from test_fidelity_check_calibration_v2 import APPROVED_DIAGNOSIS as SW_DIAGNOSIS, CATEGORY_RENAMED_REPORT

N_TRIALS = 3
DELAY_SECONDS = 10

with open("peloton_real/diagnosis.txt") as f:
    PELOTON_DIAGNOSIS = f.read()
with open("peloton_real/report.txt") as f:
    PELOTON_REPORT = f.read()


def run_fixture(name, diagnosis, report_text, n_trials):
    outcomes = []
    for trial in range(1, n_trials + 1):
        result = run_fidelity_check(approved_diagnosis=diagnosis, final_report=report_text)
        actual = "PASS" if result["passed"] else "FAIL"
        outcomes.append(actual)
        print(f"[{name}] trial {trial}/{n_trials}: got {actual}")
        # Always print the verdict for this fixture -- unlike prior tests,
        # there's no single "expected" verdict for peloton_real (Check C
        # should still fail even after the fix), so every trial's full
        # text matters, not just mismatches.
        print("  --- full verdict ---")
        print(result["verdict_text"])
        print("  --- end verdict ---")
        if trial < n_trials:
            time.sleep(DELAY_SECONDS)
    print(f"[{name}] outcomes: {outcomes}\n")
    return outcomes


def main():
    print("=" * 70)
    print("FIXTURE: peloton_real (real diagnosis + real withheld report)")
    print("Expect: Check B should NOT cite the two section-heading retitles.")
    print("Expect: Check C should STILL fail on the two real qualifier drops.")
    print("=" * 70)
    run_fixture("peloton_real", PELOTON_DIAGNOSIS, PELOTON_REPORT, N_TRIALS)

    print("=" * 70)
    print("FIXTURE: category_renamed (regression check, expected FAIL every trial)")
    print("=" * 70)
    run_fixture("category_renamed", SW_DIAGNOSIS, CATEGORY_RENAMED_REPORT, N_TRIALS)


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
Calibration test, round 3, for the fidelity check -- tests the v3
wording fix (Check C now explicitly immune to Check A's paraphrase
tolerance, after round 2 found Check A's new leniency language had
bled into Check C's judgment, causing 6/6 misses on qualifier_dropped
across two independent runs).

Reuses the exact same fixture text from test_fidelity_check_calibration_v2.py
(imported directly, not retyped) -- no risk of a new fixture-construction
confound sneaking in on a third revision.

N_TRIALS_PRIMARY = 5 for qualifier_dropped, the fixture that actually
regressed and needs to be confirmed fixed.

N_TRIALS_REGRESSION = 3 for the other three fixtures -- lighter, since
these already passed cleanly at n=5 in round 2 and were not touched by
the v3 wording change (only Check C's text was edited). This is a
quick check that fixing Check C's cross-contamination didn't introduce
a new one in the other direction, not a full re-validation from zero.

PACING: 10 seconds between every call (14 calls total: 5 + 3 + 3 + 3),
same spacing that got round 2's completion run through cleanly.
"""

import time

from fidelity_check import run_fidelity_check
from test_fidelity_check_calibration_v2 import (
    APPROVED_DIAGNOSIS,
    PARAPHRASE_ONLY_REPORT,
    PARENTHETICAL_DROPPED_REPORT,
    CATEGORY_RENAMED_REPORT,
    QUALIFIER_DROPPED_REPORT,
)

DELAY_SECONDS = 10

FIXTURES = [
    ("qualifier_dropped", QUALIFIER_DROPPED_REPORT, "FAIL", 5),
    ("paraphrase_only", PARAPHRASE_ONLY_REPORT, "PASS", 3),
    ("parenthetical_dropped", PARENTHETICAL_DROPPED_REPORT, "PASS", 3),
    ("category_renamed", CATEGORY_RENAMED_REPORT, "FAIL", 3),
]


def main():
    results = {}
    for name, report_text, expected, n_trials in FIXTURES:
        outcomes = []
        for trial in range(1, n_trials + 1):
            result = run_fidelity_check(
                approved_diagnosis=APPROVED_DIAGNOSIS,
                final_report=report_text,
            )
            actual = "PASS" if result["passed"] else "FAIL"
            match = "MATCH" if actual == expected else "MISMATCH"
            outcomes.append(actual)
            print(f"[{name}] trial {trial}/{n_trials}: expected {expected}, got {actual} ({match})")
            if match == "MISMATCH":
                print("  --- full verdict for this mismatched trial ---")
                print(result["verdict_text"])
                print("  --- end verdict ---")
            time.sleep(DELAY_SECONDS)
        pass_count = outcomes.count("PASS")
        fail_count = outcomes.count("FAIL")
        results[name] = (pass_count, fail_count, expected)
        print(f"[{name}] summary: {pass_count} PASS / {fail_count} FAIL out of {n_trials} (expected {expected})\n")

    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for name, (pass_count, fail_count, expected) in results.items():
        print(f"{name}: {pass_count} PASS / {fail_count} FAIL (expected {expected})")


if __name__ == "__main__":
    main()
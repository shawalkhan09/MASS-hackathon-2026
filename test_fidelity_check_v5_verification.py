# -*- coding: utf-8 -*-
"""
Verification for v5's structural rewrite (three isolated calls instead
of one shared prompt). Tests the same two things round 3/4 tested,
but now reports each of the three checks' individual verdicts
separately -- the whole point of this architecture is that Check C's
behavior should no longer depend on what Check A or Check B's wording
says, so seeing all three side by side per trial is the actual proof,
not just an overall PASS/FAIL.

FIXTURE 1 -- peloton_real: the exact real diagnosis and withheld
report from the 3-case graduation run. Expected: Check A PASS, Check B
PASS (section retitles are not cause-classification changes), Check C
FAIL (the two real qualifier drops -- "into expansion" dropped from
the 55% figure, "(storage, insurance, obsolescence)" dropped from the
15% figure -- should be caught again now that Check C's judgment can't
be influenced by Check B's wording).

FIXTURE 2 -- category_renamed: reused from test_fidelity_check_calibration_v2.py,
unchanged. Expected: Check A PASS, Check B FAIL (a genuine Fishbone
primary-label change), Check C PASS.

N_TRIALS = 3 per fixture -- enough to see whether the isolated
architecture behaves consistently, not a full n=5 calibration battery.
"""

import time

from fidelity_check import run_check_a, run_check_b, run_check_c
from test_fidelity_check_calibration_v2 import APPROVED_DIAGNOSIS as SW_DIAGNOSIS, CATEGORY_RENAMED_REPORT

N_TRIALS = 3
DELAY_SECONDS = 8

with open("peloton_real/diagnosis.txt") as f:
    PELOTON_DIAGNOSIS = f.read()
with open("peloton_real/report.txt") as f:
    PELOTON_REPORT = f.read()

FIXTURES = [
    ("peloton_real", PELOTON_DIAGNOSIS, PELOTON_REPORT,
     {"A": "PASS", "B": "PASS", "C": "FAIL"}),
    ("category_renamed", SW_DIAGNOSIS, CATEGORY_RENAMED_REPORT,
     {"A": "PASS", "B": "FAIL", "C": "PASS"}),
]


def main():
    for name, diagnosis, report_text, expected in FIXTURES:
        print("=" * 70)
        print(f"FIXTURE: {name}  (expected A={expected['A']} B={expected['B']} C={expected['C']})")
        print("=" * 70)
        for trial in range(1, N_TRIALS + 1):
            a = run_check_a(diagnosis, report_text)
            time.sleep(DELAY_SECONDS)
            b = run_check_b(diagnosis, report_text)
            time.sleep(DELAY_SECONDS)
            c = run_check_c(diagnosis, report_text)
            time.sleep(DELAY_SECONDS)

            a_actual = "PASS" if a["passed"] else "FAIL"
            b_actual = "PASS" if b["passed"] else "FAIL"
            c_actual = "PASS" if c["passed"] else "FAIL"

            print(f"[{name}] trial {trial}/{N_TRIALS}: "
                  f"A={a_actual}({'match' if a_actual == expected['A'] else 'MISMATCH'}) "
                  f"B={b_actual}({'match' if b_actual == expected['B'] else 'MISMATCH'}) "
                  f"C={c_actual}({'match' if c_actual == expected['C'] else 'MISMATCH'})")

            if a_actual != expected["A"]:
                print(f"  --- Check A full verdict (mismatch) ---\n{a['verdict_text']}\n  --- end ---")
            if b_actual != expected["B"]:
                print(f"  --- Check B full verdict (mismatch) ---\n{b['verdict_text']}\n  --- end ---")
            if c_actual != expected["C"]:
                print(f"  --- Check C full verdict (mismatch) ---\n{c['verdict_text']}\n  --- end ---")
        print()


if __name__ == "__main__":
    main()
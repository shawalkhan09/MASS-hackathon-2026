# -*- coding: utf-8 -*-
"""
Calibration test, round 2, for the fidelity check -- fixes the
confound in round 1's harmless_paraphrase fixture (which accidentally
dropped parenthetical Fishbone sub-labels AND relabeled the 5 Whys,
neither of which was the intended test). Every fixture here is built
by taking the approved diagnosis's own wording as a base and changing
EXACTLY ONE thing, so each result isolates a single variable.

FIXTURE 1 -- paraphrase_only: the diagnosis's "as opposed to a
hub-and-spoke" becomes "compared to a traditional hub-and-spoke model".
Nothing else changed. This is the single change round 1 flagged 5/5
times, unconfounded by anything else. Expected: PASS under the v2
wording (Check A now explicitly treats this as meaning-preserving
paraphrase).

FIXTURE 2 -- parenthetical_dropped: all four Fishbone parenthetical
sub-labels removed ("Mother Nature (Environment)" -> "Mother Nature",
etc.). Primary labels unchanged. Nothing else changed. Expected: PASS
under the v2 wording (Check B now explicitly allows dropping secondary
annotations when the primary label is intact) -- per the explicit
project decision that parenthetical sub-labels are removable framework
scaffolding, not client-facing content.

FIXTURE 3 -- category_renamed: the diagnosis's "Measurement" primary
label becomes "Management" -- deliberately reproducing the exact shape
of the real Phase 25 Southwest finding (a cause moved to a
different-sounding bucket). Nothing else changed. Expected: FAIL on
Check B. This is the regression case proving the v2 wording didn't
loosen Check B into missing the actual bug it exists to catch.

FIXTURE 4 -- qualifier_dropped: identical to round 1's
real_qualifier_drop fixture, kept unchanged as a regression check
since it already passed 5/5 before this revision and Check C's wording
was not touched. Expected: FAIL on Check C.

N_TRIALS default is 5 per fixture (20 total LLM calls) -- same as
round 1, to get a comparably reliable signal on each of the four
questions. This is authorized quota spend for calibration, matching
the project's established practice (Phase 22/23 used n=9 for Check 2's
validation).
"""

from fidelity_check import run_fidelity_check

N_TRIALS = 5

with open("southwest_diagnosis_run1.txt") as f:
    APPROVED_DIAGNOSIS = f.read()

# A faithful, near-verbatim reformatting of the diagnosis into report
# shape -- deliberately reusing the diagnosis's own wording throughout
# so that fixtures 2-4 don't introduce any paraphrase drift alongside
# the one intentional change each is testing.
BASE_REPORT = """### Executive Summary
Triggering Event: Winter Storm Elliott (Dec 21-23, 2022), which exposed the underlying structural vulnerabilities of the airline. Root Cause: A long-term corporate decision-making pattern that treated critical flight and crew management technology as a secondary concern, creating a "technical debt" crisis where manual workarounds were the primary operational method. This left the company without the automated resiliency required to recover from a standard industry shock, resulting in a multi-day cascading system collapse. Total Financial Exposure associated with the event: $2.4 billion. (This figure represents the sum of the sunk cost of the failure plus the necessary capital expenditure to achieve future parity.)

### Fishbone (Ishikawa) Diagram
Applied to the Southwest Airlines Dec 2022 Operational Meltdown

*   **Mother Nature (Environment):** Winter Storm Elliott (Dec 21-23, 2022), which created industry-wide disruptions.
*   **Machine (Technology):** Legacy crew-scheduling software incapable of handling large-scale, automated reassignments; heavy reliance on manual, spreadsheet-based coordination.
*   **Method (Process):** Point-to-point network structure (as opposed to a hub-and-spoke), which, while efficient in good weather, lacked recovery resiliency when crews and aircraft became unsynchronized.
*   **Manpower (People):** Aircrew scattered across the country, disconnected from their scheduled aircraft, leading to massive staffing imbalances.
*   **Measurement:** Failure to heed previous warnings from the Southwest Airlines Pilots Association regarding the "duct tape" nature of IT infrastructure.

### Root Cause Analysis (5 Whys)

1.  **Why did Southwest cancel 16,700 flights while competitors recovered within days?**
    *   *Answer:* The crew-scheduling system could not process the volume of manual reassignments required to reconnect scattered crews to aircraft.
2.  **Why could the system not process these reassignments?**
    *   *Answer:* The software was outdated legacy technology that lacked the scalability to handle the exponential complexity of a network-wide disruption.
3.  **Why was the airline relying on outdated, non-scalable technology?**
    *   *Answer:* Under-investment in operational technology during preceding years, despite clear evidence that the systems were failing with increasing frequency.
4.  **Why was there an under-investment in these critical systems?**
    *   *Answer:* Management prioritized short-term financial/operational efficiency (the "duct tape" approach) over the long-term resiliency of the core operational architecture.
5.  **Why did leadership prioritize short-term efficiency over resiliency?**
    *   *Answer (Root Cause):* A systemic failure to treat operational infrastructure as a strategic asset, resulting in a culture of technical debt where known vulnerabilities were ignored until they became catastrophic.

### Pareto Analysis (80/20 Rule)

Note on Data Limitations: The provided case documentation does not offer a granular breakdown of the $1.1 billion loss by category (e.g., specific dollar amounts attributed to software failure vs. ground staff shortages vs. passenger refunds). Therefore, it is impossible to accurately rank these causes or determine which 20% of operational gaps contributed to 80% of the financial impact.

While the software/IT architecture and network design were clearly the primary drivers of the operational collapse, the case provides no quantitative data to support a formal Pareto distribution.

### Financial Impact Analysis

*   **Total Financial Impact:** $1.1 billion.
*   **Regulatory Penalty (DOT):** $140 million.
    *   *Cash fine:* $35 million (3.18% of total impact).
    *   *Voucher compensation:* $105 million (9.55% of total impact).
*   **Future Corrective Investment:** $1.3 billion (representing a 25% increase over 2019 levels).

Total Financial Exposure associated with the event: $2.4 billion. (This figure represents the sum of the sunk cost of the failure plus the necessary capital expenditure to achieve future parity.)

### Final Root-Cause Statement
Triggering Event: Winter Storm Elliott (Dec 21-23, 2022), which exposed the underlying structural vulnerabilities of the airline. Root Cause: A long-term corporate decision-making pattern that treated critical flight and crew management technology as a secondary concern, creating a "technical debt" crisis where manual workarounds were the primary operational method. This left the company without the automated resiliency required to recover from a standard industry shock, resulting in a multi-day cascading system collapse.
"""

PARAPHRASE_ONLY_REPORT = BASE_REPORT.replace(
    "(as opposed to a hub-and-spoke)",
    "(compared to a traditional hub-and-spoke model)",
)

PARENTHETICAL_DROPPED_REPORT = (
    BASE_REPORT
    .replace("Mother Nature (Environment):", "Mother Nature:")
    .replace("Machine (Technology):", "Machine:")
    .replace("Method (Process):", "Method:")
    .replace("Manpower (People):", "Manpower:")
)

CATEGORY_RENAMED_REPORT = BASE_REPORT.replace(
    "*   **Measurement:** Failure to heed previous warnings",
    "*   **Management:** Failure to heed previous warnings",
)

QUALIFIER_DROPPED_REPORT = BASE_REPORT.replace(
    "Total Financial Exposure associated with the event: $2.4 billion. "
    "(This figure represents the sum of the sunk cost of the failure "
    "plus the necessary capital expenditure to achieve future parity.)",
    "Total financial exposure: $2.4 billion in combined costs.",
)

FIXTURES = [
    ("paraphrase_only", PARAPHRASE_ONLY_REPORT, "PASS"),
    ("parenthetical_dropped", PARENTHETICAL_DROPPED_REPORT, "PASS"),
    ("category_renamed", CATEGORY_RENAMED_REPORT, "FAIL"),
    ("qualifier_dropped", QUALIFIER_DROPPED_REPORT, "FAIL"),
]


def main():
    # Sanity check: confirm each fixture actually differs from BASE_REPORT
    # exactly where intended, before spending any quota.
    for name, report_text, _ in FIXTURES:
        if report_text == BASE_REPORT:
            raise SystemExit(
                f"FIXTURE BUG: '{name}' is identical to BASE_REPORT -- "
                f"the intended .replace() found no match. Fix the fixture "
                f"before running, this would silently test nothing."
            )

    results = {}
    for name, report_text, expected in FIXTURES:
        outcomes = []
        for trial in range(1, N_TRIALS + 1):
            result = run_fidelity_check(
                approved_diagnosis=APPROVED_DIAGNOSIS,
                final_report=report_text,
            )
            actual = "PASS" if result["passed"] else "FAIL"
            match = "MATCH" if actual == expected else "MISMATCH"
            outcomes.append(actual)
            print(f"[{name}] trial {trial}/{N_TRIALS}: expected {expected}, got {actual} ({match})")
            if match == "MISMATCH":
                print("  --- full verdict for this mismatched trial ---")
                print(result["verdict_text"])
                print("  --- end verdict ---")
        pass_count = outcomes.count("PASS")
        fail_count = outcomes.count("FAIL")
        results[name] = (pass_count, fail_count, expected)
        print(f"[{name}] summary: {pass_count} PASS / {fail_count} FAIL out of {N_TRIALS} (expected {expected})\n")

    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for name, (pass_count, fail_count, expected) in results.items():
        print(f"{name}: {pass_count} PASS / {fail_count} FAIL (expected {expected})")


if __name__ == "__main__":
    main()
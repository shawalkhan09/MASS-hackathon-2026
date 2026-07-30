# -*- coding: utf-8 -*-
"""
Calibration test for the fidelity check (fidelity_check.py) -- isolates
the two sources of variance the follow-up smoke-test re-run conflated:
run_synthesis()'s own non-determinism, and run_fidelity_check()'s own
reliability when judging IDENTICAL report text repeatedly.

WHY THIS TEST EXISTS:
The first live smoke test (Southwest, single run) produced a FAIL,
flagging "traditional hub-and-spoke" and "network-wide failure" as new
content/dropped qualifiers, alongside a genuine-looking $2.4B
qualifier-drop finding. A follow-up re-run on the SAME diagnosis
produced a clean PASS -- but that re-run also called run_synthesis()
again, generating fresh (differently-worded) report text each time.
That confounds two different questions: is the fidelity checker itself
unreliable, or does synthesis just produce different text each call,
some of it faithful and some not? Comparing two different synthesis
outputs tells you nothing about whether the checker is consistent --
it only shows the generator is non-deterministic, which was never in
question.

This test removes that confound entirely: no synthesis call at all.
Two report texts are fixed by hand and run_fidelity_check() is called
directly against each, repeated N times, to see whether the check's
verdict on IDENTICAL input is actually consistent.

FIXTURE 1 -- harmless_paraphrase: contains ONLY synonym-level rewording
relative to the approved diagnosis -- specifically the two exact
phrasings the smoke test flagged ("traditional hub-and-spoke" for the
diagnosis's plain "hub-and-spoke", and an added "network-wide failure"
summary phrase). No qualifier drop, no new fact, no relabeled category
anywhere else. Expected: PASS. If this fails a meaningful fraction of
the time, that's direct evidence the check is over-strict on harmless
paraphrase -- the same shape of first-pass over-strictness Check 2
needed calibration rounds to fix (Section 6.4 of the report).

FIXTURE 2 -- real_qualifier_drop: identical to the diagnosis's own
wording everywhere EXCEPT the $2.4B figure, which drops its qualifier
entirely ("the sum of the sunk cost of the failure plus the necessary
capital expenditure to achieve future parity" becomes "in combined
costs"). No paraphrase drift anywhere else -- this isolates the
qualifier-drop question on its own. Same shape of violation as the
Boeing precision-loss finding from Phase 25. Expected: FAIL,
specifically on Check C.

N_TRIALS default is 5 per fixture (10 total LLM calls) -- smaller than
the n=9 used for Check 2's repeated-run validation (Phase 22/23), since
this is a first calibration pass on a brand-new check, not a final
validation claim. If the result is a near-even split rather than a
clear pattern, raise N_TRIALS and re-run rather than trusting a small-n
result either way -- same lesson as Phase 20 -> Phase 22 (n=1 isn't a
pattern).
"""

from fidelity_check import run_fidelity_check

N_TRIALS = 5

with open("southwest_diagnosis_run1.txt") as f:
    APPROVED_DIAGNOSIS = f.read()

HARMLESS_PARAPHRASE_REPORT = """### Executive Summary
The Southwest Airlines operational meltdown of December 2022 was triggered by Winter Storm Elliott, which acted as a catalyst for a multi-day, network-wide failure exposing critical, underlying structural vulnerabilities within the airline's core systems. The root cause was a sustained corporate strategy that treated essential flight and crew management technology as a secondary concern, leading to a "technical debt" crisis that rendered the airline unable to recover from industry-wide disruptions. The total financial exposure associated with the event is $2.4 billion. This figure represents the sum of the sunk cost of the failure plus the necessary capital expenditure to achieve future parity.

### Operational Vulnerabilities: Fishbone Analysis
*   **Mother Nature:** Winter Storm Elliott (Dec 21-23, 2022) created industry-wide disruptions.
*   **Machine:** Legacy crew-scheduling software lacked the capability for large-scale, automated reassignments, necessitating a heavy reliance on manual, spreadsheet-based coordination.
*   **Method:** The airline's point-to-point network structure, while efficient in favorable weather, lacked recovery resiliency compared to traditional hub-and-spoke configurations when crews and aircraft became unsynchronized.
*   **Manpower:** Aircrew were scattered across the country and disconnected from their scheduled aircraft, resulting in massive staffing imbalances.
*   **Measurement:** Management failed to heed previous warnings from the Southwest Airlines Pilots Association regarding the "duct tape" nature of the airline's IT infrastructure.

### Root Cause Analysis
1. **System Limitations:** The crew-scheduling system could not process the volume of manual reassignments required to reconnect scattered crews to aircraft.
2. **Technological Obsolescence:** The software was outdated legacy technology that lacked the scalability to manage the complexity of a network-wide disruption.
3. **Under-investment:** The airline under-invested in operational technology for years, despite clear evidence that systems were failing with increasing frequency.
4. **Strategic Prioritization:** Leadership prioritized short-term financial and operational efficiency over the long-term resiliency of the core operational architecture.
5. **Cultural Root Cause:** A systemic failure to treat operational infrastructure as a strategic asset created a culture of technical debt, where known vulnerabilities were ignored until they became catastrophic.

### Financial Impact
The total financial exposure associated with the event is $2.4 billion. This figure represents the sum of the sunk cost of the failure plus the necessary capital expenditure to achieve future parity.

*   **Immediate Financial Loss:** $1.1 billion.
*   **Regulatory Penalty (DOT):** $140 million total, consisting of a $35 million cash fine (3.18% of total impact) and $105 million in voucher compensation (9.55% of total impact).
*   **Future Corrective Investment:** $1.3 billion (representing a 25% increase over 2019 levels).

**Note on Data Limitations:** The provided case documentation does not offer a granular breakdown of the $1.1 billion loss by category. While the software/IT architecture and network design were clearly the primary drivers of the operational collapse, the case provides no quantitative data to support a formal Pareto distribution.

### Final Root-Cause Statement
The triggering event was Winter Storm Elliott (Dec 21-23, 2022), which exposed the underlying structural vulnerabilities of the airline. The root cause was a long-term corporate decision-making pattern that treated critical flight and crew management technology as a secondary concern, creating a "technical debt" crisis where manual workarounds were the primary operational method.
"""

REAL_QUALIFIER_DROP_REPORT = """### Executive Summary
The Southwest Airlines operational meltdown of December 2022 was triggered by Winter Storm Elliott, which exposed critical, underlying structural vulnerabilities within the airline's core systems. The root cause was a sustained corporate strategy that treated essential flight and crew management technology as a secondary concern, leading to a "technical debt" crisis that rendered the airline unable to recover from industry-wide disruptions. The total financial exposure is $2.4 billion in combined costs.

### Operational Vulnerabilities: Fishbone Analysis
*   **Mother Nature:** Winter Storm Elliott (Dec 21-23, 2022) created industry-wide disruptions.
*   **Machine:** Legacy crew-scheduling software lacked the capability for large-scale, automated reassignments, necessitating a heavy reliance on manual, spreadsheet-based coordination.
*   **Method:** Point-to-point network structure (as opposed to a hub-and-spoke), which, while efficient in good weather, lacked recovery resiliency when crews and aircraft became unsynchronized.
*   **Manpower:** Aircrew were scattered across the country and disconnected from their scheduled aircraft, resulting in massive staffing imbalances.
*   **Measurement:** Management failed to heed previous warnings from the Southwest Airlines Pilots Association regarding the "duct tape" nature of the airline's IT infrastructure.

### Root Cause Analysis
1. **System Limitations:** The crew-scheduling system could not process the volume of manual reassignments required to reconnect scattered crews to aircraft.
2. **Technological Obsolescence:** The software was outdated legacy technology that lacked the scalability to manage the complexity of a network-wide disruption.
3. **Under-investment:** The airline under-invested in operational technology for years, despite clear evidence that systems were failing with increasing frequency.
4. **Strategic Prioritization:** Leadership prioritized short-term financial and operational efficiency over the long-term resiliency of the core operational architecture.
5. **Cultural Root Cause:** A systemic failure to treat operational infrastructure as a strategic asset created a culture of technical debt, where known vulnerabilities were ignored until they became catastrophic.

### Financial Impact
The total financial exposure is $2.4 billion in combined costs.

*   **Immediate Financial Loss:** $1.1 billion.
*   **Regulatory Penalty (DOT):** $140 million total, consisting of a $35 million cash fine (3.18% of total impact) and $105 million in voucher compensation (9.55% of total impact).
*   **Future Corrective Investment:** $1.3 billion (representing a 25% increase over 2019 levels).

**Note on Data Limitations:** The provided case documentation does not offer a granular breakdown of the $1.1 billion loss by category. While the software/IT architecture and network design were clearly the primary drivers of the operational collapse, the case provides no quantitative data to support a formal Pareto distribution.

### Final Root-Cause Statement
The triggering event was Winter Storm Elliott (Dec 21-23, 2022), which exposed the underlying structural vulnerabilities of the airline. The root cause was a long-term corporate decision-making pattern that treated critical flight and crew management technology as a secondary concern, creating a "technical debt" crisis where manual workarounds were the primary operational method.
"""

FIXTURES = [
    ("harmless_paraphrase", HARMLESS_PARAPHRASE_REPORT, "PASS"),
    ("real_qualifier_drop", REAL_QUALIFIER_DROP_REPORT, "FAIL"),
]


def main():
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
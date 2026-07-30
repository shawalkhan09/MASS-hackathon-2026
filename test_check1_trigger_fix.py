# -*- coding: utf-8 -*-
"""
Validates the Check 1 fix identified in DEVELOPMENT_LOG.md Phase 30. The
original Check 1 wording verified only that a labeled "trigger" and a
labeled "root cause" were textually distinct from each other -- not that
the labeled trigger was actually external to the company. This let a
diagnosis label the company's OWN decision ("the strategic decision to
switch to a lower-cost produce supplier") as the trigger, and the
Auditor passed it -- confirmed directly from its own stated reasoning in
the Phase 30 trace, not inferred -- because Check 1 never checked
whether that label was semantically correct, only that it was distinct
from whatever was labeled "root cause."

BEFORE RUNNING THIS: crewai_pipeline.py's AUDIT_DESCRIPTION must already
be updated to the revised two-part Check 1 wording (Part A: distinctness,
same as before; Part B: is the labeled trigger actually external, new).
This script does not modify that file -- it only tests against whatever
AUDIT_DESCRIPTION currently is, so if you run this before applying the
fix, the first case should still incorrectly PASS, which is itself a
useful confirmation that the OLD wording really did produce the Phase 30
result and this test harness is wired correctly.

Three cases, chosen to test three different things at once -- the same
discipline as the omission-isolation test (Phase 24) and Check 2's
overcorrection check (Phase 13, Round 2):

1. THE REAL FAILING CASE, verbatim from the Phase 30 trace: the
   restaurant-chain diagnosis that mislabeled the company's own
   procurement decision as "the trigger." Expected AFTER the fix: FAIL,
   with Part B specifically naming the mislabeled trigger.

2. A MINIMALLY CORRECTED VERSION of the same diagnosis -- identical in
   every respect except the Final Root Cause Statement's Triggering
   Event line, which is changed (by a single, mechanical string
   replacement, not by hand-editing prose) to correctly name the real
   external cause -- inflationary margin pressure -- already present in
   the case's own Background section. Expected: PASS. If this still
   fails, the fix is too broad, not just correctly narrow, and is
   rejecting something other than the actual defect.

3. A KNOWN-GOOD REGRESSION CASE: Southwest, with an unambiguous external
   trigger (Winter Storm Elliott) distinctly separated from a legitimate
   internal root cause (technology underinvestment). Expected: still
   PASS under the revised wording. NOTE: the case_text below is
   reconstructed from the Southwest case facts used consistently
   throughout this project's earlier phases (case name, flight count,
   dollar figures, SkySolver, the Pilots Association warnings) -- it is
   NOT guaranteed byte-identical to case_loader.load_case(...)
   .diagnostic_input for the real case file. The point of this fixture
   is confirming the Auditor's reasoning still correctly passes a
   legitimate external-trigger case after the wording change, not exact
   reproduction of a specific historical run. If exact reproducibility
   matters, replace this with a real load_case() call against the
   actual case file before trusting this specific result.

If all three come back as expected, the fix is doing its job: catching
the real defect, passing the corrected version of the exact same case,
and not breaking a case that was always legitimate.
"""

from crewai_pipeline import run_auditor, parse_verdict

RESTAURANT_CASE_TEXT = """## Problem Statement
The restaurant chain is experiencing inconsistent produce quality, ranging from spoiled inventory to rotten ingredients, following a recent supplier switch. This has resulted in customer complaints, negative online reviews, minor health department warnings at two locations, decreased revenue, and declining staff morale.

## Background
The business operates a chain of 12 restaurant locations, primarily in the Midwest. Three months ago, the company switched to a cheaper produce supplier to reduce costs due to inflation-related margin pressure, without conducting thorough testing. The previous supplier continues to solicit the business to return. The company is currently experiencing internal friction regarding the decision to switch, as leadership is hesitant to acknowledge a potential error, and the staff is struggling to manage customer dissatisfaction. This is the first time the business has received health department warnings in eight years of operation.

## Supporting Data
The following concrete data and estimates were provided:
* Number of locations: 12
* Timeline of supplier switch: 3 months ago
* Number of locations that received health department warnings: 2
* Duration of business operation: 8 years
* Reported online rating shift: From approximately 4.3 to 3.6 (not verified by the user)
* Estimated revenue decrease: Approximately 15% (not verified by the user)
* Financial loss due to spoiled inventory: No specific dollar amount provided."""

RESTAURANT_DIAGNOSIS_ORIGINAL = """### 1. Fishbone (Ishikawa) Diagram
*Categorization of contributing factors based on the 3-month timeline post-supplier switch:*

*   **Material:**
    *   New supplier produce fails to meet quality standards (spoiled/rotten upon arrival).
    *   Inconsistency across the 12-location chain.
*   **Process:**
    *   Deficient vendor onboarding protocol (no pilot testing or quality assurance phase).
    *   Failure to establish clear Service Level Agreements (SLAs) regarding freshness and delivery speed.
*   **People:**
    *   Staff morale decline due to the burden of managing constant customer complaints and disposal of spoiled inventory.
    *   Leadership resistance to acknowledging the procurement error, preventing corrective action.
*   **Measurement:**
    *   Loss of historical quality baseline (first health warning in 8 years).
    *   Inability to reconcile current 15% revenue decrease with specific item-level spoilage costs due to lack of granular tracking.

---

### 2. Root Cause Analysis (5 Whys)
*Objective: Identify the systemic failure behind the current operational decline.*

*   **Why 1:** Why are there health department warnings and customer complaints?
    *   Because the produce provided by the new supplier is frequently spoiled or rotten.
*   **Why 2:** Why is the new supplier providing spoiled produce?
    *   Because the produce does not meet the necessary freshness standards required for the chain's operations.
*   **Why 3:** Why did the company select a supplier whose produce does not meet these standards?
    *   Because the company prioritized cost reduction over quality assurance during the procurement process.
*   **Why 4:** Why was quality assurance bypassed in the procurement process?
    *   Because the company lacks a standardized vendor vetting and pilot-testing protocol for high-impact supply chain changes.
*   **Why 5 (Root Cause):** Why does the company lack these standardized protocols?
    *   Because leadership prioritizes short-term margin pressure responses over rigorous, risk-adjusted operational management.

---

### 3. Pareto Analysis (80/20 Rule)
*Diagnostic evaluation of data availability:*

The provided case data lacks the necessary granular breakdown to perform a valid Pareto Analysis. While we know there is a 15% revenue decrease and 2 of 12 locations received health warnings, we do not have:
*   Specific revenue loss figures per location (to see if the 2 warned locations account for the bulk of the 15% decline).
*   Frequency or type of ingredient spoilage data (to identify which specific items account for 80% of waste).
*   Customer complaint volume per location.

**Conclusion:** Without quantitative data attributing the 15% revenue drop to specific locations or ingredients, a Pareto analysis is not possible. The case does not provide sufficient data to categorize the severity of the health warnings relative to total chain performance using the Pareto framework.

---

### 4. Financial Impact Analysis
*Evaluation of current performance metrics:*

*   **Revenue Impact:**
    *   Baseline: 100% of previous revenue.
    *   Current: 85% of previous revenue.
    *   **Net Impact:** 15% decrease. (Note: Without the raw dollar revenue figures for the 12 locations, the absolute financial loss remains unquantifiable).
*   **Operating Margin Pressure:**
    *   The intent of the switch was to improve margins by lowering costs.
    *   Actual outcome: Margin is likely compressed further due to the "Cost of Poor Quality" (COPQ), which includes:
        1.  Loss of spoiled inventory (unquantified).
        2.  Revenue loss (15%).
        3.  Potential brand equity loss (reflected in the 4.3 to 3.6 rating drop).
    *   **Assessment:** The attempt to manage margin pressure through a cheaper supplier has resulted in a net negative ROI, as the reduction in Cost of Goods Sold (COGS) is mathematically outweighed by the loss in revenue and reputational value.

---

### Final Root Cause Statement
*   **Triggering Event:** The strategic decision to switch to a lower-cost produce supplier three months ago.
*   **Root Cause:** An organizational failure to integrate formal risk-assessment and pilot-testing protocols into the procurement process, driven by a leadership mandate that prioritizes short-term cost-cutting over operational reliability and quality control."""

# Single-variable correction: only the Triggering Event line changes, via
# a mechanical string replacement (not hand-edited prose), to correctly
# name the real external cause already present in the case's own
# Background section instead of the company's own decision.
_OLD_TRIGGER_LINE = "*   **Triggering Event:** The strategic decision to switch to a lower-cost produce supplier three months ago."
_NEW_TRIGGER_LINE = "*   **Triggering Event:** Inflation-related margin pressure, which created the cost pressure that led the company to change produce suppliers."
RESTAURANT_DIAGNOSIS_CORRECTED = RESTAURANT_DIAGNOSIS_ORIGINAL.replace(_OLD_TRIGGER_LINE, _NEW_TRIGGER_LINE)
assert RESTAURANT_DIAGNOSIS_CORRECTED != RESTAURANT_DIAGNOSIS_ORIGINAL, (
    "Replacement did not match the original diagnosis text -- check "
    "RESTAURANT_DIAGNOSIS_ORIGINAL hasn't been altered above."
)

RESTAURANT_DIAGNOSIS_ISOLATED = RESTAURANT_DIAGNOSIS_CORRECTED.replace(
    "Inflation-related margin pressure, which created the cost pressure that led the company to change produce suppliers.",
    "Inflation-related margin pressure, an external macroeconomic cost shock affecting food costs industry-wide.",
)

# Reconstructed from Southwest case facts used consistently throughout
# this project -- see the module docstring's caveat before treating this
# as an exact reproduction of a specific historical run.
SOUTHWEST_CASE_TEXT = """## Problem Statement
Southwest Airlines cancelled approximately 16,700 flights over a roughly ten-day period following Winter Storm Elliott in December 2022, while competing airlines recovered operations within one to two days of the same storm.

## Background
Southwest operates a point-to-point route network rather than the hub-and-spoke model used by most major competitors. The airline's crew-scheduling software (internally referred to as SkySolver) is a legacy system that has been in use for many years. The Southwest Airlines Pilots Association had previously raised concerns about the fragility of the scheduling system's ability to handle large-scale disruptions.

## Supporting Data
* Flights cancelled: approximately 16,700
* Total estimated financial impact: $1.24 billion (operational costs, refunds, reimbursements)
* DOT regulatory settlement: $140 million
* Planned 2023 technology investment: $1.3 billion
* Recovery time: approximately 10 days at Southwest versus 1-2 days at competing airlines"""

SOUTHWEST_DIAGNOSIS_KNOWN_GOOD = """### Final Root-Cause Summary
The operational meltdown was **triggered** by Winter Storm Elliott, an external weather event. However, the **root cause** of the extended, company-specific collapse was the systemic failure of leadership to modernize crew-scheduling technology and address documented "duct-tape" infrastructure vulnerabilities. While competitors faced the same environment, Southwest's reliance on a rigid, legacy-constrained scheduling method within a point-to-point network meant that the company lacked the structural elasticity required to absorb the shock, resulting in a $1.24 billion financial hit and a record-breaking regulatory penalty."""

CASES = [
    (
        "Restaurant chain -- ORIGINAL (mislabeled trigger, real failure from Phase 30)",
        RESTAURANT_CASE_TEXT,
        RESTAURANT_DIAGNOSIS_ORIGINAL,
        "FAIL",
    ),
    (
        "Restaurant chain -- CORRECTED (trigger relabeled to inflation, single-variable fix)",
        RESTAURANT_CASE_TEXT,
        RESTAURANT_DIAGNOSIS_CORRECTED,
        "PASS",
    ),
    (
        "Southwest -- known-good regression case (legitimate external trigger)",
        SOUTHWEST_CASE_TEXT,
        SOUTHWEST_DIAGNOSIS_KNOWN_GOOD,
        "PASS",
    ),
    (
        "Restaurant chain -- ISOLATED (trigger sentence mirrors Southwest's clean structure, no causal clause to company action)",
        RESTAURANT_CASE_TEXT,
        RESTAURANT_DIAGNOSIS_ISOLATED,
        "PASS",
    ),
]

results = []

for label, case_text, diagnosis_text, expected in CASES:
    print(f"\n{'=' * 70}\nAuditing: {label}\nExpected: {expected}\n{'=' * 70}\n")
    audit = run_auditor(case_text, diagnosis_text)
    passed = parse_verdict(audit)
    actual = "PASS" if passed else "FAIL"
    matches_expected = (actual == expected)
    results.append((label, expected, actual, matches_expected, audit))
    print(f"\nActual: {actual} -- {'MATCHES EXPECTED' if matches_expected else '!! DOES NOT MATCH EXPECTED !!'}\n")
    print(audit)
    print()

print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
for label, expected, actual, matches_expected, _ in results:
    flag = "OK" if matches_expected else "MISMATCH -- investigate"
    print(f"  [{flag}] {label}: expected {expected}, got {actual}")

all_correct = all(m for _, _, _, m, _ in results)
print(f"\nAll three cases behaved as expected: {all_correct}")
if all_correct:
    print("The fix catches the real defect, passes the corrected version of")
    print("the same case, and does not break a legitimate known-good case.")
else:
    print("At least one case did not behave as expected -- read the full")
    print("audit text above for the mismatched case(s) before trusting the fix.")
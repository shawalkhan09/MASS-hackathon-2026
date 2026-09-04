# -*- coding: utf-8 -*-
"""
Validates the STRUCTURAL fix applied to crewai_pipeline.py's
AUDIT_DESCRIPTION Check 1 Part B, per Section 9 / Section 8.17's
scoped next step, after two wording-only attempts:

  - Phase 63 baseline (original wording): 4/9 correctly rejected on
    the Ohio Warehouse fixture's 9 evasion framings.
  - Wording-fix attempt (naming the 5 evasion patterns explicitly,
    "TEST IS CONTROL NOT VOCABULARY"): made it WORSE -- 2/16 pooled,
    including breaking the floor case that had never failed before.
    Diagnosis: enumerating specific patterns taught the model a
    closed checklist; the added length also caused Part A's
    distinctness test to bleed into Part B's control test. Reverted.

THIS FIX IS DIFFERENT IN KIND, NOT JUST WORDING: instead of adding
more prose telling the model what NOT to do (which backfired), it
changes what the Auditor is REQUIRED TO PRODUCE. Part B's output
format now has a mandatory "Controlling Actor" line that must be
written BEFORE the PASS/FAIL verdict line. Because the model
generates text left-to-right, forcing the actor-identification
sentence first closes off the failure mode seen in the reverted
attempt, where free-form justification let the model reason its way
around the rule after already deciding on a lenient verdict. The
verdict is then defined to follow mechanically from the actor
answer, not from a separate free-form judgment call.

No specific evasion pattern (vendor-externalizing, symptom-framing,
etc.) is named in the new wording -- deliberately, since naming them
is exactly what caused the checklist-substitution failure last time.

THIS SCRIPT, MATCHING THIS PROJECT'S OWN STANDARD (Phase 34's lesson:
re-verify at the same controlled scale, and check regressions, not
just the target case):

1. TARGET RE-TEST: re-runs the exact same 9 Ohio Warehouse framings
   from test_check1_partb_ohio_warehouse_round3.py, imported directly
   and UNCHANGED. Pre-fix baseline: 4/9 correctly rejected.

2. REGRESSION CHECK: re-runs every previously-validated Check 1 Part B
   fixture to confirm the structural change doesn't overcorrect into
   rejecting genuine external triggers:
   - The restaurant-chain fixtures (mislabeled internal decision:
     FAIL; corrected version: PASS; isolated clean version: PASS).
   - Southwest known-good (PASS).
   - Boeing AOA-sensor-mislabeled-as-trigger (FAIL) -- an internal
     engineering/design matter, matching the real Phase 32/33 finding.

NOTE ON WHY THESE REGRESSION FIXTURES ARE INLINED RATHER THAN
IMPORTED: test_check1_trigger_fix.py has no `if __name__ == "__main__"`
guard -- its restaurant/Southwest trial loop executes live Auditor
calls at import time. Importing from it here would silently trigger
4 extra real LLM calls (burning time and Qoder credits) as a side
effect before this script's own trials even start. The fixture text
below is copied verbatim from that file to avoid that landmine; it is
NOT re-exported from it.

If (1) shows a clear improvement over 4/9 AND (2) shows no
regressions, the fix is doing its job without narrowing what Check 1
Part B catches elsewhere.

Every trial's full audit is saved to disk before any tally is
printed.
"""

import re
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict
from case_loader import load_case

# Re-import the Ohio Warehouse fixture UNCHANGED -- same case text, same
# root cause, same 9 trigger framings used in the Phase 63 baseline
# round. This file has an `if __name__ == "__main__":` guard, so
# importing it does not trigger its own trial loop.
from test_check1_partb_ohio_warehouse_round3 import (
    CASE_TEXT as OHIO_CASE_TEXT,
    DIAGNOSIS_TEMPLATE as OHIO_DIAGNOSIS_TEMPLATE,
    TRIGGER_FRAMINGS as OHIO_TRIGGER_FRAMINGS,
)

OUT_DIR = Path("check1_partb_structural_fix_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

# New Part B output format wraps the verdict in a "Controlling Actor"
# line that must precede it -- matches on that structure explicitly so
# a model that skips the new required field shows up as UNPARSEABLE
# rather than silently matching on old-format text.
PART_B_PATTERN = re.compile(
    r"Part B\s*\(Trigger Is Genuinely External\):\s*\n\s*Controlling Actor:.*?Verdict:\s*(PASS|FAIL)",
    re.IGNORECASE | re.DOTALL,
)

# ---------------------------------------------------------------------
# Regression fixtures, copied verbatim from test_check1_trigger_fix.py
# (restaurant + Southwest) -- see module docstring for why these are
# inlined rather than imported.
# ---------------------------------------------------------------------
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

_OLD_TRIGGER_LINE = "*   **Triggering Event:** The strategic decision to switch to a lower-cost produce supplier three months ago."
_NEW_TRIGGER_LINE = "*   **Triggering Event:** Inflation-related margin pressure, which created the cost pressure that led the company to change produce suppliers."
RESTAURANT_DIAGNOSIS_CORRECTED = RESTAURANT_DIAGNOSIS_ORIGINAL.replace(_OLD_TRIGGER_LINE, _NEW_TRIGGER_LINE)
assert RESTAURANT_DIAGNOSIS_CORRECTED != RESTAURANT_DIAGNOSIS_ORIGINAL, (
    "Replacement did not match -- check RESTAURANT_DIAGNOSIS_ORIGINAL hasn't drifted from the source file."
)

RESTAURANT_DIAGNOSIS_ISOLATED = RESTAURANT_DIAGNOSIS_CORRECTED.replace(
    "Inflation-related margin pressure, which created the cost pressure that led the company to change produce suppliers.",
    "Inflation-related margin pressure, an external macroeconomic cost shock affecting food costs industry-wide.",
)

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

# Real Boeing case text + hand-built diagnosis mislabeling the AOA
# sensor's erroneous data (an internal engineering/design matter) as
# the trigger -- matching the real Phase 32/33 finding (Section 6.7)
# that this framing is correctly rejected. Also a direct test of
# whether the new wording still correctly rejects a real
# technical-failure framing rather than overcorrecting into ever
# accepting one.
BOEING_CASE_TEXT = load_case("cases/Case_02_Boeing_737_MAX_Crisis.md").diagnostic_input

BOEING_DIAGNOSIS_MISLABELED = """### Final Root Cause Statement
*   **Triggering Event:** Erroneous angle-of-attack (AOA) sensor data that fed incorrect readings into the Maneuvering Characteristics Augmentation System (MCAS), causing it to repeatedly and forcefully push the aircraft's nose down against pilot input.
*   **Root Cause:** Boeing's decision to design MCAS to rely on a single AOA sensor input, with no cross-check against the aircraft's second sensor, in order to minimize pilot retraining costs and preserve the 737 MAX's classification as a variant of the existing 737 type rather than a new aircraft requiring full recertification."""

# ---------------------------------------------------------------------
# Assemble all trials: (label, case_text, diagnosis_text, expected)
# ---------------------------------------------------------------------
trials = []

for label, trigger_line in OHIO_TRIGGER_FRAMINGS:
    diagnosis_text = OHIO_DIAGNOSIS_TEMPLATE.format(TRIGGER_LINE=trigger_line)
    trials.append((f"[TARGET] Ohio Warehouse -- {label}", OHIO_CASE_TEXT, diagnosis_text, "FAIL"))

trials.append((
    "[REGRESSION] Restaurant -- ORIGINAL (mislabeled trigger)",
    RESTAURANT_CASE_TEXT, RESTAURANT_DIAGNOSIS_ORIGINAL, "FAIL",
))
trials.append((
    "[REGRESSION] Restaurant -- CORRECTED (trigger relabeled to inflation)",
    RESTAURANT_CASE_TEXT, RESTAURANT_DIAGNOSIS_CORRECTED, "PASS",
))
trials.append((
    "[REGRESSION] Restaurant -- ISOLATED (Southwest-style clean structure)",
    RESTAURANT_CASE_TEXT, RESTAURANT_DIAGNOSIS_ISOLATED, "PASS",
))
trials.append((
    "[REGRESSION] Southwest -- known-good (legitimate external trigger)",
    SOUTHWEST_CASE_TEXT, SOUTHWEST_DIAGNOSIS_KNOWN_GOOD, "PASS",
))
trials.append((
    "[REGRESSION] Boeing -- AOA sensor mislabeled as trigger",
    BOEING_CASE_TEXT, BOEING_DIAGNOSIS_MISLABELED, "FAIL",
))


def main():
    results = []

    for i, (label, case_text, diagnosis_text, expected) in enumerate(trials, start=1):
        print(f"\n{'=' * 70}\nTrial {i}/{len(trials)}: {label}\nExpected Part B: {expected}\n{'=' * 70}\n")

        try:
            audit = run_auditor(case_text, diagnosis_text)
        except Exception as e:
            print(f"\n!! FAILED on trial {i} ({label}): {e}\n")
            out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Trial {i} ({label}) failed: {e}\n")
            results.append((i, label, expected, None, "FAILED"))
            continue

        overall_pass = parse_verdict(audit)
        part_b_match = PART_B_PATTERN.search(audit)
        part_b_result = part_b_match.group(1).upper() if part_b_match else "UNPARSEABLE"
        matched_expected = (part_b_result == expected)

        out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Check 1 Part B structural-fix validation -- Trial {i}/{len(trials)}\n\n"
            f"**Label:** {label}\n\n"
            f"**Expected Part B:** {expected}\n\n"
            f"**Actual Part B:** {part_b_result}\n\n"
            f"**Match:** {'MATCH' if matched_expected else 'MISMATCH'}\n\n"
            f"**Overall verdict:** {'PASS' if overall_pass else 'FAIL'}\n\n"
            f"---\n\n## Full raw Auditor output\n\n{audit}\n"
        )

        results.append((i, label, expected, part_b_result, "MATCH" if matched_expected else "MISMATCH"))
        print(f"\nPart B: {part_b_result} (expected {expected}) -- "
              f"{'MATCH' if matched_expected else 'MISMATCH -- investigate'}\n")

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")

    target_results = [r for r in results if r[1].startswith("[TARGET]")]
    regression_results = [r for r in results if r[1].startswith("[REGRESSION]")]

    print("\n-- TARGET: Ohio Warehouse, 9 framings (Phase 63 baseline: 4/9 correctly rejected) --")
    for i, label, expected, actual, status in target_results:
        print(f"  [{status}] {label}: expected {expected}, got {actual}")
    target_n = len([r for r in target_results if r[4] != "FAILED"])
    target_correct = len([r for r in target_results if r[4] == "MATCH"])
    print(f"\nTarget result: {target_correct}/{target_n} correctly rejected (Phase 63 baseline was 4/9; "
          f"reverted wording-fix attempt was 2/16 pooled).")

    print("\n-- REGRESSION: existing validated fixtures --")
    for i, label, expected, actual, status in regression_results:
        print(f"  [{status}] {label}: expected {expected}, got {actual}")
    reg_n = len([r for r in regression_results if r[4] != "FAILED"])
    reg_correct = len([r for r in regression_results if r[4] == "MATCH"])
    print(f"\nRegression result: {reg_correct}/{reg_n} behaved as expected.")

    print(f"\nRaw evidence saved to: {OUT_DIR}/")
    if reg_correct < reg_n:
        print("\n!! REGRESSION DETECTED -- the structural fix changed behavior on at least")
        print("!! one previously-validated fixture. Read the mismatched trial(s) above")
        print("!! before treating the target result as a clean win.")
    elif target_correct > 4:
        print(f"\nImprovement over Phase 63 baseline (4/9) with no regressions: "
              f"{target_correct}/{target_n} on target, {reg_correct}/{reg_n} on regressions.")
    else:
        print("\nNo improvement over the Phase 63 baseline -- the structural change did not")
        print("move the target result. Do not treat this as closing the gap.")


if __name__ == "__main__":
    main()

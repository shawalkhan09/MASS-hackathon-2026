# -*- coding: utf-8 -*-
"""
Validates the Check 1 Part B wording fix applied to crewai_pipeline.py's
AUDIT_DESCRIPTION, targeting the exact substitution mechanism
characterised in DEVELOPMENT_LOG.md Phase 63 / report Section 8.15:
the old wording let the Auditor ask "is explicit decision language
present in the trigger sentence" instead of "did the company control
this," and five specific framing strategies (vendor-externalising,
symptom-as-trigger, bare-dated-event, "objective"/technical register,
hedged-uncertainty) exploited exactly that gap, passing 5 of 9 fresh
framings that should have failed.

THIS SCRIPT DOES TWO THINGS, MATCHING THIS PROJECT'S OWN STANDARD FOR
VALIDATING A FIX (Phase 34's lesson: re-verify at the same controlled
scale, and check regressions, not just the target case):

1. TARGET RE-TEST: re-runs the exact same 9 Ohio Warehouse framings
   from test_check1_partb_ohio_warehouse_round3.py, imported directly
   and UNCHANGED -- same case text, same root cause, same 9 trigger
   lines -- against the NEW Part B wording. Before the fix: 4/9
   correctly rejected. This is the direct measure of whether the fix
   works.

2. REGRESSION CHECK: re-runs every existing Check 1 Part B fixture
   this project has already validated under the OLD wording, to
   confirm the stricter language doesn't overcorrect into rejecting
   genuine external triggers:
   - The restaurant-chain fixtures (test_check1_trigger_fix.py):
     mislabeled internal decision (FAIL), corrected version (PASS),
     Southwest known-good (PASS), isolated corrected version (PASS).
   - A new Boeing regression fixture: the real Boeing case text
     (cases/Case_02_Boeing_737_MAX_Crisis.md) paired with a
     hand-built diagnosis mislabeling the AOA sensor's erroneous data
     -- an internal engineering/design matter -- as the trigger,
     matching the real Phase 32/33 finding (Section 6.7) that this
     framing is correctly rejected under the OLD wording. This is
     also, usefully, a direct test of whether the new "objective/
     technical-failure register" guidance (aimed at Ohio Warehouse's
     mechanical-failure framing) still correctly rejects a real
     technical-failure framing rather than overcorrecting into ever
     accepting one.

If (1) shows a clear improvement over 4/9 AND (2) shows no regressions,
the fix is doing its job without narrowing what Check 1 Part B
catches elsewhere -- the exact bar Section 8.15 set for treating this
as closing the gap.

Every trial's full audit is saved to disk before any tally is printed.
"""

from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict
from case_loader import load_case

# Re-import the Ohio Warehouse fixture UNCHANGED -- same case text, same
# root cause, same 9 trigger framings used in the pre-fix round.
from test_check1_partb_ohio_warehouse_round3 import (
    CASE_TEXT as OHIO_CASE_TEXT,
    DIAGNOSIS_TEMPLATE as OHIO_DIAGNOSIS_TEMPLATE,
    TRIGGER_FRAMINGS as OHIO_TRIGGER_FRAMINGS,
    PART_B_PATTERN,
)

# Re-import the existing regression fixtures UNCHANGED.
from test_check1_trigger_fix import (
    RESTAURANT_CASE_TEXT,
    RESTAURANT_DIAGNOSIS_ORIGINAL,
    RESTAURANT_DIAGNOSIS_CORRECTED,
    RESTAURANT_DIAGNOSIS_ISOLATED,
    SOUTHWEST_CASE_TEXT,
    SOUTHWEST_DIAGNOSIS_KNOWN_GOOD,
)

OUT_DIR = Path("check1_partb_wording_fix_validation_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

# ---------------------------------------------------------------------
# New Boeing regression fixture: real case text, hand-built diagnosis
# mislabeling the AOA sensor's erroneous data (an internal engineering
# matter) as the trigger -- matching the real Phase 32/33 finding.
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# Run every trial, save full audit to disk, tally results.
# ---------------------------------------------------------------------
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
        f"# Check 1 Part B wording-fix validation -- Trial {i}/{len(trials)}\n\n"
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

# ---------------------------------------------------------------------
# Summary, split by target vs. regression.
# ---------------------------------------------------------------------
print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")

target_results = [r for r in results if r[1].startswith("[TARGET]")]
regression_results = [r for r in results if r[1].startswith("[REGRESSION]")]

print("\n-- TARGET: Ohio Warehouse, 9 framings (pre-fix baseline: 4/9 correctly rejected) --")
for i, label, expected, actual, status in target_results:
    print(f"  [{status}] {label}: expected {expected}, got {actual}")
target_n = len([r for r in target_results if r[4] != "FAILED"])
target_correct = len([r for r in target_results if r[4] == "MATCH"])
print(f"\nTarget result: {target_correct}/{target_n} correctly rejected (pre-fix baseline was 4/9).")

print("\n-- REGRESSION: existing validated fixtures --")
for i, label, expected, actual, status in regression_results:
    print(f"  [{status}] {label}: expected {expected}, got {actual}")
reg_n = len([r for r in regression_results if r[4] != "FAILED"])
reg_correct = len([r for r in regression_results if r[4] == "MATCH"])
print(f"\nRegression result: {reg_correct}/{reg_n} behaved as expected.")

print(f"\nRaw evidence saved to: {OUT_DIR}/")
if reg_correct < reg_n:
    print("\n!! REGRESSION DETECTED -- the wording fix changed behavior on at least")
    print("!! one previously-validated fixture. Read the mismatched trial(s) above")
    print("!! before treating the target improvement as a clean win.")
elif target_correct > 4:
    print(f"\nImprovement over pre-fix baseline (4/9) with no regressions: "
          f"{target_correct}/{target_n} on target, {reg_correct}/{reg_n} on regressions.")
else:
    print("\nNo improvement over the pre-fix baseline -- the wording change did not")
    print("move the target result. Do not treat this as closing the gap.")

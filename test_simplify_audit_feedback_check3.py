# -*- coding: utf-8 -*-
"""
Local validation for api.py's simplify_audit_feedback() after adding
the Check 3 block. No API calls, no LLM calls -- pure regex/parsing
testing against real Auditor verdict text already saved on disk from
this session's Check 3 test rounds (true-positive test, rounds 2/3/4,
the process-fact stress test, and the n=9 confirmatory replication).

WHAT THIS CHECKS:
  1. For every real file where Check 3 actually FAILed: does the new
     block produce at least one Check-3-attributed reason, and does
     the extracted quote look like the real flagged claim (not a
     fragment, not a PASS instance's quote)?
  2. For every real file (FAIL or not): does the new Check 3 block
     leave Check 1/Check 2's own extracted reasons byte-for-byte
     identical to what a frozen copy of the pre-Check-3 function would
     have produced? This is the regression check -- proves the new
     block is additive only, never alters existing behavior.

FILE FORMAT HANDLING:
Two raw-text layouts exist across this session's saved files:
  - "## Raw Auditor Verdict (full text)" -- check3_true_positive_outputs/,
    check3_round2_outputs/, check3_round4_outputs/,
    check3_process_fact_stress_outputs/ (all built by this session's
    own direct-run_auditor() test scripts).
  - "## Raw Auditor Verdict (final attempt)" -- fabrication_under_gap_outputs/
    (built by test_analyst_fabrication_under_gap.py, which also
    includes the raw diagnosis in the same file -- only the audit
    verdict portion after this header is extracted).

GROUND TRUTH: most of this session's own saved files already have a
"Check 3 status: PASS/FAIL" line in their own header (written by the
test scripts themselves) -- used directly as ground truth where
present. fabrication_under_gap_outputs files don't have this field;
ground truth there is computed with the same CHECK3_STATUS_PATTERN
regex used throughout this session's Check 3 test scripts.

Run:
    python3 test_simplify_audit_feedback_check3.py
"""

import re
from pathlib import Path

from api import simplify_audit_feedback

CHECK3_STATUS_PATTERN = re.compile(
    r"###\s*Check 3.*?\n\s*Status:\s*(PASS|FAIL)",
    re.IGNORECASE | re.DOTALL,
)

FULL_TEXT_HEADER = "## Raw Auditor Verdict (full text)\n\n"
FINAL_ATTEMPT_HEADER = "## Raw Auditor Verdict (final attempt)\n\n"

CANDIDATE_DIRS = [
    "check3_true_positive_outputs",
    "check3_round2_outputs",
    "check3_round4_outputs",
    "check3_process_fact_stress_outputs",
]


def extract_audit_text(file_text: str):
    """Returns (audit_text, source_format) or (None, None) if unrecognized."""
    if FULL_TEXT_HEADER in file_text:
        return file_text.split(FULL_TEXT_HEADER, 1)[1], "full_text"
    if FINAL_ATTEMPT_HEADER in file_text:
        return file_text.split(FINAL_ATTEMPT_HEADER, 1)[1], "final_attempt"
    return None, None


def ground_truth_check3_status(file_text: str, audit_text: str) -> str:
    header_match = re.search(r"^Check 3 status:\s*(PASS|FAIL)", file_text, re.MULTILINE)
    if header_match:
        return header_match.group(1).upper()
    match = CHECK3_STATUS_PATTERN.search(audit_text)
    return match.group(1).upper() if match else "UNKNOWN"


# ---------------------------------------------------------------------
# Frozen copy of the PRE-Check-3 simplify_audit_feedback() logic
# (Check 1 + Check 2 blocks + fallback only), used ONLY to prove the
# new Check 3 block is additive -- not a live code path anywhere else.
# ---------------------------------------------------------------------

def old_simplify_audit_feedback(audit_text: str):
    reasons = []
    part_specs = [
        (r"Part A \(Distinctness\)",
         "The trigger and root cause weren't clearly stated as two separate things"),
        (r"Part B \(Trigger Is Genuinely External\)",
         "What was labeled as the external trigger looks like something the "
         "company itself did, not an outside event"),
    ]
    for part_pattern, friendly_lead in part_specs:
        part_match = re.search(
            rf"{part_pattern}:\s*FAIL\s*--\s*(.+?)(?=\nPart [AB]|\n###|\Z)",
            audit_text, re.DOTALL | re.IGNORECASE,
        )
        if part_match:
            full_text = part_match.group(1).strip()
            segments = full_text.split(" -- ")
            why = segments[-1].strip() if len(segments) > 1 else full_text
            first_line = why.split("\n")[0]
            reasons.append(f"{friendly_lead}: {first_line}")

    check2_overall_fail = re.search(
        r"Check 2.*?Status:\s*FAIL", audit_text, re.DOTALL | re.IGNORECASE
    )
    if check2_overall_fail:
        check2_section_match = re.search(r"Check 2.*", audit_text, re.DOTALL | re.IGNORECASE)
        check2_text = check2_section_match.group(0)
        fail_instances = re.findall(
            r"(?:^|\n)\s*\d+\.\s*.*?FAIL[.:]?\s*(.+?)(?=\n\s*\d+\.|\n###|\Z)",
            check2_text, re.DOTALL | re.IGNORECASE,
        )
        for r in fail_instances[:3]:
            first_line = r.strip().split("\n")[0]
            if first_line:
                reasons.append(
                    "One part of the ranking wasn't clearly backed by the "
                    "data provided: " + first_line
                )

    if not reasons:
        reasons.append(
            "Our reviewer flagged something in this analysis as not "
            "clearly supported by the information provided. See the "
            "full technical review for specifics."
        )
    return reasons


CHECK3_LEAD_INS = (
    "A specific detail was presented as settled fact",
    "Our reviewer found a specific detail treated as confirmed",
)


def split_check3_reasons(reasons):
    """Returns (non_check3_reasons, check3_reasons)."""
    non_check3, check3 = [], []
    for r in reasons:
        if r.startswith(CHECK3_LEAD_INS):
            check3.append(r)
        else:
            non_check3.append(r)
    return non_check3, check3


# ---------------------------------------------------------------------
# Gather candidate files
# ---------------------------------------------------------------------

files = []
for d in CANDIDATE_DIRS:
    for p in sorted(Path(d).glob("*.md")):
        if p.name.startswith("RUN_SUMMARY"):
            continue
        files.append(p)

for p in sorted(Path("fabrication_under_gap_outputs").glob("*_20260801T153056.md")):
    if p.name.startswith("RUN_SUMMARY") or "structured_input" in p.name:
        continue
    files.append(p)

print(f"Found {len(files)} candidate files.\n")

unrecognized = []
regression_mismatches = []
check3_fail_results = []  # (path, found_reasons_bool, is_generic_fallback, reasons)
check3_pass_but_flagged = []  # false positives: ground truth PASS but block still added a reason

for p in files:
    file_text = p.read_text()
    audit_text, fmt = extract_audit_text(file_text)
    if audit_text is None:
        unrecognized.append(p)
        continue

    gt_status = ground_truth_check3_status(file_text, audit_text)

    new_reasons = simplify_audit_feedback(audit_text)
    old_reasons = old_simplify_audit_feedback(audit_text)
    non_check3_new, check3_new = split_check3_reasons(new_reasons)

    if non_check3_new != old_reasons:
        regression_mismatches.append((p, old_reasons, non_check3_new))

    if gt_status == "FAIL":
        is_generic = any(r.startswith(CHECK3_LEAD_INS[1]) for r in check3_new)
        check3_fail_results.append((p, len(check3_new) > 0, is_generic, check3_new))
    elif gt_status == "PASS" and check3_new:
        check3_pass_but_flagged.append((p, check3_new))

# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------

print(f"{'=' * 80}\nUNRECOGNIZED FILE FORMAT ({len(unrecognized)})\n{'=' * 80}")
for p in unrecognized:
    print(f"  {p}")

print(f"\n{'=' * 80}\nCHECK 1/CHECK 2 REGRESSION CHECK: {len(files) - len(unrecognized)} files compared, "
      f"{len(regression_mismatches)} mismatch(es)\n{'=' * 80}")
for p, old, new in regression_mismatches:
    print(f"  MISMATCH: {p}")
    print(f"    old: {old}")
    print(f"    new (non-Check3): {new}")

print(f"\n{'=' * 80}\nCHECK 3 FALSE POSITIVES (ground truth PASS but a reason was added): "
      f"{len(check3_pass_but_flagged)}\n{'=' * 80}")
for p, reasons in check3_pass_but_flagged:
    print(f"  {p}")
    for r in reasons:
        print(f"    -> {r}")

print(f"\n{'=' * 80}\nCHECK 3 FAIL FILES: {len(check3_fail_results)} total\n{'=' * 80}")
missed = [x for x in check3_fail_results if not x[1]]
generic_fallback = [x for x in check3_fail_results if x[1] and x[2]]
clean_extraction = [x for x in check3_fail_results if x[1] and not x[2]]
print(f"  Clean extraction (real quote found): {len(clean_extraction)}")
print(f"  Generic fallback (FAIL detected, no quote extracted): {len(generic_fallback)}")
print(f"  Missed entirely (no reason added at all): {len(missed)}")

for p, found, is_generic, reasons in check3_fail_results:
    tag = "MISSED" if not found else ("GENERIC" if is_generic else "OK")
    print(f"\n  [{tag}] {p}")
    for r in reasons:
        print(f"    -> {r}")

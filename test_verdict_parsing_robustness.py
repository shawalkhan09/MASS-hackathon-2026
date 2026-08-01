# -*- coding: utf-8 -*-
"""
Regression + bug-fix validation for the verdict-parsing robustness fix
in crewai_pipeline.py's parse_verdict() and fidelity_check.py's
run_check_a/b/c() (via their shared _extract_check_verdict() helper).

No LLM calls -- this tests parsing logic against real saved text and
hand-built fixtures, not model behavior, so it runs instantly and
needs no rate-limit pacing.

WHAT'S BEING TESTED, AND WHY:
Both parsers used to take the FIRST verdict-header match in a response
(parse_verdict() via re.search(), run_check_a/b/c() via
str.startswith()). check3_true_positive_outputs/harbor_vine_trial03_
20260731T192240.md -- a real trial from this session's Check 3
true-positive test -- showed the model write a full PASS verdict
block, visibly catch its own mistake mid-answer ("Self-correction
note... Correction on Verdict:"), and write a second, corrected FAIL
verdict block in the same response. Both parsers would have silently
kept the wrong, pre-correction PASS. The fix: find ALL verdict
occurrences, take the LAST as authoritative (the model's own final
conclusion -- the one real instance observed confirms the correction
was itself correct), and emit a warning when more than one is found,
without changing the return type any caller depends on.

Three groups of cases:
  (a) Regression: a real, single-verdict fixture must parse
      IDENTICALLY under the new code and a frozen copy of the exact
      old logic -- proven by running both side by side, not asserted
      from memory.
  (b) The actual bug: harbor_vine trial 3's real raw text, run through
      the fixed parse_verdict(), must now return FAIL (matching the
      model's own correction) and must emit exactly one warning.
  (c) Constructed multi-verdict fixtures for run_check_a/b/c's shared
      _extract_check_verdict() helper -- hand-built here since no real
      double-verdict fidelity-check output exists on disk yet (see the
      retroactive integrity check earlier this session). Legitimate
      because this exercises parsing logic in isolation, not model
      behavior.

Run:
    python3 test_verdict_parsing_robustness.py
"""

import warnings
from pathlib import Path

from crewai_pipeline import parse_verdict, VERDICT_PATTERN
from fidelity_check import (
    _extract_check_verdict,
    CHECK_A_VERDICT_PATTERN,
    CHECK_B_VERDICT_PATTERN,
    CHECK_C_VERDICT_PATTERN,
)

results = []  # (label, ok, detail)


def check(label, condition, detail=""):
    ok = bool(condition)
    results.append((label, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" -- {detail}" if detail else ""))


# ---------------------------------------------------------------------
# (a) Regression: real single-verdict fixture, new code vs. frozen old
# ---------------------------------------------------------------------

def _old_parse_verdict(audit_text: str) -> bool:
    """
    Frozen copy of parse_verdict()'s exact pre-fix implementation
    (re.search() = first match only). Kept here ONLY so the regression
    case below can prove the new code behaves identically for a
    normal, single-verdict response -- not a live code path anywhere
    else in the project.
    """
    match = VERDICT_PATTERN.search(audit_text)
    if not match:
        return False
    return match.group(1).upper() == "PASS"


REGRESSION_FIXTURE_PATH = Path("fabrication_under_gap_outputs/harbor_vine_trial01_20260731T171312.md")
regression_text = REGRESSION_FIXTURE_PATH.read_text()
# Isolate just the raw Auditor verdict section -- what run_auditor()
# actually returns to parse_verdict() in production. The saved file
# also has the diagnosis and header metadata, which real callers never
# pass to parse_verdict(); excluding them keeps the fixture faithful
# to the real input shape rather than just "a file that mentions PASS".
regression_audit_text = regression_text.split("## Raw Auditor Verdict (final attempt)\n\n", 1)[1]

old_result = _old_parse_verdict(regression_audit_text)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    new_result = parse_verdict(regression_audit_text)
    regression_warned = len(w) > 0

check(
    "4a: single-verdict fixture (harbor_vine trial01, original 27-trial run) -- "
    "new parse_verdict() matches frozen old implementation, no warning",
    old_result == new_result and not regression_warned,
    f"old={old_result}, new={new_result}, warned={regression_warned}",
)
check(
    "4a: single-verdict fixture -- verdict is FAIL, matching the file's known content",
    new_result is False,
    f"got {new_result}",
)


# ---------------------------------------------------------------------
# (b) The actual bug: harbor_vine trial 3's real raw text
# ---------------------------------------------------------------------

BUG_FIXTURE_PATH = Path("check3_true_positive_outputs/harbor_vine_trial03_20260731T192240.md")
bug_text = BUG_FIXTURE_PATH.read_text()
bug_audit_text = bug_text.split("## Raw Auditor Verdict (full text)\n\n", 1)[1]

occurrence_count = len(VERDICT_PATTERN.findall(bug_audit_text))

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    bug_result = parse_verdict(bug_audit_text)
    bug_warnings = [x for x in w if issubclass(x.category, UserWarning)]

check(
    "4b: harbor_vine trial03 raw text contains exactly 2 '## Audit Verdict:' occurrences",
    occurrence_count == 2,
    f"found {occurrence_count}",
)
check(
    "4b: fixed parse_verdict() now returns FAIL (the model's own final, corrected conclusion)",
    bug_result is False,
    f"got {bug_result} -- old code would have returned True (PASS), the wrong answer",
)
check(
    "4b: self-correction warning emitted exactly once",
    len(bug_warnings) == 1,
    f"got {len(bug_warnings)} warning(s): {[str(x.message) for x in bug_warnings]}",
)
if bug_warnings:
    check(
        "4b: warning message names the PASS -> FAIL sequence",
        "PASS" in str(bug_warnings[0].message) and "FAIL" in str(bug_warnings[0].message),
        str(bug_warnings[0].message),
    )


# ---------------------------------------------------------------------
# (c) Constructed multi-verdict fixtures for run_check_a/b/c
# ---------------------------------------------------------------------

CHECK_A_NORMAL = (
    "## Check A Verdict: PASS\n"
    "Instances found: None found -- all figures trace back to the diagnosis."
)
CHECK_A_SELF_CORRECTED = (
    "## Check A Verdict: PASS\n"
    "Instances found: None found.\n\n"
    "Wait -- re-reading the report, it states \"$50 million in cost savings,\" "
    "which does not appear anywhere in the approved diagnosis. Correcting.\n\n"
    "## Check A Verdict: FAIL\n"
    "Instances found: \n"
    "- \"$50 million in cost savings\" -- FAIL, not traceable to the diagnosis."
)

CHECK_B_NORMAL = (
    "## Check B Verdict: FAIL\n"
    "Instances found: \n"
    "- Diagnosis: \"Measurement\" -> Report: \"Management\" -- PRIMARY cause-"
    "classification change, FAIL."
)
CHECK_B_SELF_CORRECTED = (
    "## Check B Verdict: FAIL\n"
    "Instances found: \n"
    "- Diagnosis: \"Measurement\" -> Report: \"Management\" -- FAIL.\n\n"
    "Self-correction: on closer reading, \"Management\" here is a section "
    "heading, not a Fishbone classification label -- this does not violate "
    "the check.\n\n"
    "## Check B Verdict: PASS\n"
    "Instances found: None found -- the earlier flagged instance was a "
    "section heading, not a cause-classification label."
)

CHECK_C_NORMAL = (
    "## Check C Verdict: PASS\n"
    "Instances found: None found -- all qualifiers preserved."
)
CHECK_C_SELF_CORRECTED = (
    "## Check C Verdict: PASS\n"
    "Instances found: None found.\n\n"
    "Wait, reconsidering -- the diagnosis says \"100% by count of fatalities\" "
    "and the report says just \"100%,\" dropping the qualifier.\n\n"
    "## Check C Verdict: FAIL\n"
    "Instances found: \n"
    "- Diagnosis: \"100% by count of fatalities\" -> Report: \"100%\" -- "
    "FAIL, scope qualifier dropped."
)

CHECK_FIXTURES = [
    ("Check A", CHECK_A_VERDICT_PATTERN, CHECK_A_NORMAL, True, CHECK_A_SELF_CORRECTED, False),
    ("Check B", CHECK_B_VERDICT_PATTERN, CHECK_B_NORMAL, False, CHECK_B_SELF_CORRECTED, True),
    ("Check C", CHECK_C_VERDICT_PATTERN, CHECK_C_NORMAL, True, CHECK_C_SELF_CORRECTED, False),
]

for label, pattern, normal_text, normal_expected, corrected_text, corrected_expected in CHECK_FIXTURES:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        normal_result = _extract_check_verdict(normal_text, pattern, label)
        normal_warned = len(w) > 0
    check(
        f"4c: {label} normal single-verdict fixture -- correct result, no warning",
        normal_result == normal_expected and not normal_warned,
        f"expected={normal_expected}, got={normal_result}, warned={normal_warned}",
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        corrected_result = _extract_check_verdict(corrected_text, pattern, label)
        corrected_warnings = [x for x in w if issubclass(x.category, UserWarning)]
    check(
        f"4c: {label} self-corrected fixture -- takes LAST verdict, not first",
        corrected_result == corrected_expected,
        f"expected={corrected_expected}, got={corrected_result}",
    )
    check(
        f"4c: {label} self-corrected fixture -- exactly one warning emitted",
        len(corrected_warnings) == 1,
        f"got {len(corrected_warnings)}",
    )


# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------

print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
passed_count = sum(1 for _, ok, _ in results if ok)
for label, ok, _ in results:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
print(f"\n{passed_count}/{len(results)} checks passed.")

if passed_count != len(results):
    raise SystemExit(1)

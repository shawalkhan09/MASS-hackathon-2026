# -*- coding: utf-8 -*-
"""
First validation of Check 4 (ranking completeness, ranking_completeness_
check.py) against all 18 already-saved PIA/Airlift forced-ranking
diagnoses (Phase 60/65, repeated_forced_ranking/) -- zero new
diagnosis-generation calls, only 18 new Check-4-only LLM calls.

GROUND TRUTH, CONFIRMED BY DIRECT READING OF EACH FILE BEFORE WRITING
THIS SCRIPT (not assumed from the Phase 65 prose summary alone):

PIA (Case_04), 9 runs -- 8 omit the crash (PK8303) from the ranking
table entirely (it appears, if at all, only inside another row's
rationale text, never as its own ranked line); 1 run (run2) gives it
its own row ("Human Error (Specific Pilot Actions)" at 5%):
  run1: FAIL (incomplete) -- crash mentioned only in row 2's rationale
  run2: PASS (complete)   -- crash IS its own ranked row
  run3: FAIL (incomplete) -- no reference to the crash in the table at all
  run4: FAIL (incomplete) -- confirmed directly, full table read
  run5: FAIL (incomplete)
  run6: FAIL (incomplete)
  run7: FAIL (incomplete) -- confirmed directly, full table read
  run8: FAIL (incomplete)
  run9: FAIL (incomplete)

Airlift (Case_05), 9 runs -- all 9 give the VC funding winter its own
ranked row (sometimes reworded, e.g. "Macro-Economic Market Shift"),
confirmed directly for run4 and consistent with Phase 60/65's report
for the rest:
  run1-run9: PASS (complete), all 9

This is a genuine mixed set (8 incomplete, 10 complete) with real
internal contrast inside the PIA fixture itself (run2 vs. the other
8), not just a between-fixture comparison -- a stronger first test
than either fixture alone would give.

Each file has a 3-line header (title, "Run at:", blank line) from the
original forced-ranking script, stripped here by splitting on the
first blank line -- Check 4 only needs the diagnosis body itself.
"""

from pathlib import Path
from datetime import datetime

from ranking_completeness_check import run_check_4

OUT_DIR = Path("check4_ranking_completeness_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

FIXTURE_DIR = Path("repeated_forced_ranking")

# (filename, expected: "PASS" = complete, "FAIL" = incomplete)
TRIALS = [
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run1_20260830T153808.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run2_20260830T153808.md", "PASS"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run3_20260830T153808.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run4_20260901T155748.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run5_20260901T155748.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run6_20260901T155748.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run7_20260901T155748.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run8_20260901T155748.md", "FAIL"),
    ("Case_04_PIA_Karachi_Crash_and_Financial_Crisis_run9_20260901T155748.md", "FAIL"),
    ("Case_05_Airlift_Technologies_Collapse_run1_20260830T153808.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run2_20260830T153808.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run3_20260830T153808.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run4_20260901T155748.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run5_20260901T155748.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run6_20260901T155748.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run7_20260901T155748.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run8_20260901T155748.md", "PASS"),
    ("Case_05_Airlift_Technologies_Collapse_run9_20260901T155748.md", "PASS"),
]


def _strip_header(raw_text: str) -> str:
    """Drops the forced-ranking script's 2-line header, keeping
    everything after the first blank line -- Check 4 should see only
    the diagnosis body, the same content the real Auditor would see."""
    parts = raw_text.split("\n\n", 1)
    return parts[1] if len(parts) == 2 else raw_text


def main():
    results = []

    for i, (filename, expected) in enumerate(TRIALS, start=1):
        path = FIXTURE_DIR / filename
        raw_text = path.read_text(encoding="utf-8")
        diagnosis_text = _strip_header(raw_text)

        label = f"[{'PIA' if 'PIA' in filename else 'AIRLIFT'}] {filename}"
        print(f"\n{'=' * 70}\nTrial {i}/{len(TRIALS)}: {label}\nExpected: {expected}\n{'=' * 70}\n")

        try:
            result = run_check_4(diagnosis_text)
        except Exception as e:
            print(f"\n!! FAILED on trial {i} ({label}): {e}\n")
            out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Trial {i} ({label}) failed: {e}\n")
            results.append((i, label, expected, None, "FAILED"))
            continue

        actual = "PASS" if result["passed"] else "FAIL"
        matched = (actual == expected)

        out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Check 4 ranking-completeness validation -- Trial {i}/{len(TRIALS)}\n\n"
            f"**Fixture:** {label}\n\n"
            f"**Expected:** {expected}\n\n"
            f"**Actual:** {actual}\n\n"
            f"**Match:** {'MATCH' if matched else 'MISMATCH'}\n\n"
            f"---\n\n## Full raw verdict text\n\n{result['verdict_text']}\n"
        )

        results.append((i, label, expected, actual, "MATCH" if matched else "MISMATCH"))
        print(f"\nActual: {actual} (expected {expected}) -- "
              f"{'MATCH' if matched else 'MISMATCH -- investigate'}\n")

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")

    pia_results = [r for r in results if "[PIA]" in r[1]]
    airlift_results = [r for r in results if "[AIRLIFT]" in r[1]]

    print("\n-- PIA (8 expected FAIL / incomplete, 1 expected PASS / complete: run2) --")
    for i, label, expected, actual, status in pia_results:
        print(f"  [{status}] {label}: expected {expected}, got {actual}")
    pia_n = len([r for r in pia_results if r[4] != "FAILED"])
    pia_correct = len([r for r in pia_results if r[4] == "MATCH"])
    print(f"\nPIA result: {pia_correct}/{pia_n} correct.")

    print("\n-- AIRLIFT (9 expected PASS / complete) --")
    for i, label, expected, actual, status in airlift_results:
        print(f"  [{status}] {label}: expected {expected}, got {actual}")
    airlift_n = len([r for r in airlift_results if r[4] != "FAILED"])
    airlift_correct = len([r for r in airlift_results if r[4] == "MATCH"])
    print(f"\nAirlift result: {airlift_correct}/{airlift_n} correct.")

    total_n = pia_n + airlift_n
    total_correct = pia_correct + airlift_correct
    print(f"\nOverall: {total_correct}/{total_n} correct across both fixtures.")
    print(f"\nRaw evidence saved to: {OUT_DIR}/")
    print("\nThis script does not stop at the tally -- read each trial's full verdict "
          "text in the saved files, especially any mismatch, before treating this as "
          "either a clean validation or a defect. Report back full, complete output; "
          "do not summarize the reasoning text.")


if __name__ == "__main__":
    main()

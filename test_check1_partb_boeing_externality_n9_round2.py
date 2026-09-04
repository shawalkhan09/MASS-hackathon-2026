# -*- coding: utf-8 -*-
"""
Round 2 of the Boeing externality n=9 test (test_check1_partb_boeing_
externality_n9.py). Round 1 (8 completed trials, 1 lost to a transient
503) found Part B genuinely non-deterministic on this case -- 5 FAIL /
3 PASS, with the PASS trials consistently failing to trace the sensor
error back to the single-sensor design choice that made it possible,
and the FAIL trials consistently making that connection. That result
stands. This round exists to remove a confound before treating it as
clean: round 1's overall verdict was FAIL in all 8 trials regardless
of Part B's result, because Check 2 or Check 3 also failed in the same
three trials where Part B PASSed. Trial 2's Check 3 FAIL specifically
flagged that the root cause's phrase "preserve the 737 MAX's
classification as a variant of the existing 737 type rather than a
new aircraft requiring full recertification" is a specific technical/
regulatory rationale not stated in those exact terms in the case
packet -- a real, valid catch, not a false positive, on inspection of
cases/Case_02_Boeing_737_MAX_Crisis.md directly.

This round uses a root cause rewritten to use ONLY facts explicitly
in the case packet's Background and Documented Root Cause sections:
the single-sensor design with no cross-check, engineers raising
concerns internally in 2015-2016 without the design being changed,
the AOA disagree light / AOA indicator being sold as extra-cost
options rather than standard equipment, and MCAS-specific pilot
training being minimized specifically to avoid a costlier new-type
certification process (this last point is near-verbatim from the case
packet's own "Documented Root Cause" section 2, not a paraphrase
requiring inference). The triggering event line is unchanged from
round 1 -- it was never the flagged confound.

Same fixed-condition methodology as round 1: nothing varies across
the 9 trials. This isolates whether round 1's 5/8 vs 3/8 split was
about Part B's actual behavior (expected: replicates) or an artifact
of Check 2/3 also failing in the same trials as Part B PASSing
(expected, if that were true: this round's Part B split would differ
substantially from round 1's).

9 LLM calls -- same cost class as round 1 and this project's other
n=9 rounds.
"""

import re
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict
from case_loader import load_case

OUT_DIR = Path("check1_partb_boeing_externality_n9_round2_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")
N_TRIALS = 9

PART_B_PATTERN = re.compile(
    r"Part B\s*\(Trigger Is Genuinely External\):\s*(PASS|FAIL)",
    re.IGNORECASE,
)

CASE_TEXT = load_case("cases/Case_02_Boeing_737_MAX_Crisis.md").diagnostic_input

# ---------------------------------------------------------------------
# Same triggering event as round 1 (not the confound). Root cause
# rewritten to use only facts explicitly stated in the case packet --
# no inferred regulatory-classification rationale.
# ---------------------------------------------------------------------
DIAGNOSIS_TEXT = """### Final Root Cause Statement
*   **Triggering Event:** The erroneous data provided by a single angle-of-attack (AOA) sensor, which fed incorrect readings into the Maneuvering Characteristics Augmentation System (MCAS), causing it to repeatedly and forcefully push the aircraft's nose down against pilot input.
*   **Root Cause:** Boeing's decision to design MCAS to rely on a single AOA sensor input with no cross-check against the aircraft's second sensor -- a design engineers raised concerns about internally as early as 2015-2016 without it being changed -- combined with making the AOA disagree light and AOA indicator features that could have alerted pilots to a faulty reading optional, extra-cost add-ons rather than standard equipment, and minimizing MCAS-specific pilot training requirements specifically to avoid triggering a costlier new-type certification process."""


def main():
    results = []

    for i in range(1, N_TRIALS + 1):
        print(f"\n{'=' * 70}\nTrial {i}/{N_TRIALS}\n{'=' * 70}\n")

        try:
            audit = run_auditor(CASE_TEXT, DIAGNOSIS_TEXT)
        except Exception as e:
            print(f"\n!! FAILED on trial {i}: {e}\n")
            out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.FAILED.txt"
            out_path.write_text(f"Trial {i} failed: {e}\n")
            results.append((i, None, "FAILED"))
            continue

        overall_pass = parse_verdict(audit)
        part_b_match = PART_B_PATTERN.search(audit)
        part_b_result = part_b_match.group(1).upper() if part_b_match else "UNPARSEABLE"

        out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Check 1 Part B Boeing externality n=9 round 2 -- Trial {i}/{N_TRIALS}\n\n"
            f"**Part B result:** {part_b_result}\n\n"
            f"**Overall verdict:** {'PASS' if overall_pass else 'FAIL'}\n\n"
            f"---\n\n## Full raw Auditor output\n\n{audit}\n"
        )

        results.append((i, part_b_result, "OK"))
        print(f"\nPart B: {part_b_result}\n")

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    for i, result, status in results:
        print(f"  Trial {i}: {result if status == 'OK' else status}")

    n = len([r for r in results if r[2] == "OK"])
    fail_count = len([r for r in results if r[1] == "FAIL"])
    pass_count = len([r for r in results if r[1] == "PASS"])
    unparseable_count = len([r for r in results if r[1] == "UNPARSEABLE"])

    print(f"\nOf {n} completed trials: {fail_count} FAIL (rejected as internal), "
          f"{pass_count} PASS (accepted as external), {unparseable_count} unparseable.")
    print(f"\nRound 1 result (confounded root cause): 5 FAIL / 3 PASS of 8 completed trials.")
    print(f"\nRaw evidence saved to: {OUT_DIR}/")
    print("\nThis script does not auto-classify the result -- read each trial's full "
          "reasoning in the saved files, and specifically check whether any PASS trial's "
          "overall verdict is now PASS (meaning nothing else caught it), before concluding "
          "whether round 1's split reflects Part B's real behavior or was partly masked by "
          "the other checks. Report back full, complete output; do not summarize the "
          "reasoning text.")


if __name__ == "__main__":
    main()

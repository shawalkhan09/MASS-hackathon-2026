# -*- coding: utf-8 -*-
"""
Resolves, or at least properly evidences, the open question Phase 33
first raised and Section 6.7 / Section 10.3 carried forward as
remaining work: is Boeing's only trigger candidate -- a specific
technical component malfunction closely tied to the diagnosed design
flaw -- something Check 1 Part B is CORRECT to reject as internal, or
is Part B's definition of "external" too narrow to recognize a
legitimate physical/technical malfunction as distinct from the
systemic decision that created vulnerability to it?

WHY THIS EXISTS, BEYOND JUST MORE SAMPLES:
Phase 33 has exactly ONE real data point on this specific question:
a live pipeline run (predating this project's n=9 standard) where the
Analyst framed the trigger as "the erroneous data provided by a single
AOA sensor" and Part B FAILed it, reasoning the sensor's behavior was
"a function of the technical design... choices made and controlled by
Boeing engineers." Attempt 2 in that same run reframed the trigger
explicitly as "the internal decision to utilize a single AOA sensor,"
which is a different, easier question (an explicit decision, not a
technical malfunction) and FAILed for a more obvious reason -- it does
not add a second data point on the actual open question.

A single real-pipeline run is exactly the n=1 evidentiary gap this
project's own standard (Phase 34's lesson, applied throughout Section
8) treats as insufficient to rest a claim on. This script closes that
gap: the same trigger framing from Phase 33's Attempt 1, run 9 times
against the CURRENT, restored, original Part B wording -- the same
wording active when Phase 33's single result was produced -- as one
fixed condition, not 9 different framings. The question here is
consistency and the coherence of the reasoning across repetitions, not
evasion-pattern coverage (that is Section 8.15/8.17/8.18's question,
already closed against a different fixture).

Root cause is held fixed and matches the real diagnosed design flaw
(reliance on a single AOA sensor with no cross-check, to minimize
pilot retraining costs and avoid full recertification) -- the same
underlying fact pattern as the real MCAS crisis and this project's
existing Boeing regression fixture (Section 8.17/8.18).

If Part B rejects this framing consistently (9/9 or close to it) with
reasoning that coherently ties the malfunction back to the company-
controlled design choice each time, that supports Phase 33's second
reading: Boeing genuinely lacks a clean external trigger, and
FLAGGED_FOR_REVIEW is the pipeline correctly recognizing that, not a
defect. If the result is inconsistent, or the reasoning is incoherent
or contradictory across trials, that would support the first reading:
Part B's definition of "external" needs to explicitly accommodate this
category of case.

9 LLM calls (one audit per trial) -- same cost class as this project's
other n=9 rounds.
"""

import re
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict
from case_loader import load_case

OUT_DIR = Path("check1_partb_boeing_externality_n9_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")
N_TRIALS = 9

PART_B_PATTERN = re.compile(
    r"Part B\s*\(Trigger Is Genuinely External\):\s*(PASS|FAIL)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------
# Real Boeing case text, unchanged.
# ---------------------------------------------------------------------
CASE_TEXT = load_case("cases/Case_02_Boeing_737_MAX_Crisis.md").diagnostic_input

# ---------------------------------------------------------------------
# Fixed diagnosis: trigger framing matches Phase 33's Attempt 1 as
# closely as the original wording allows ("the erroneous data provided
# by a single AOA sensor"). Root cause matches the real diagnosed
# design flaw and this project's existing Boeing regression fixture.
# Nothing varies across the 9 trials -- this tests repeatability of a
# single condition, not framing coverage.
# ---------------------------------------------------------------------
DIAGNOSIS_TEXT = """### Final Root Cause Statement
*   **Triggering Event:** The erroneous data provided by a single angle-of-attack (AOA) sensor, which fed incorrect readings into the Maneuvering Characteristics Augmentation System (MCAS), causing it to repeatedly and forcefully push the aircraft's nose down against pilot input.
*   **Root Cause:** Boeing's decision to design MCAS to rely on a single AOA sensor input, with no cross-check against the aircraft's second sensor, in order to minimize pilot retraining costs and preserve the 737 MAX's classification as a variant of the existing 737 type rather than a new aircraft requiring full recertification."""


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
            f"# Check 1 Part B Boeing externality n=9 -- Trial {i}/{N_TRIALS}\n\n"
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
    print(f"\nPhase 33's single prior data point on this exact framing: FAIL, reasoning "
          f"the sensor's behavior was \"a function of the technical design... choices "
          f"made and controlled by Boeing engineers.\"")
    print(f"\nRaw evidence saved to: {OUT_DIR}/")
    print("\nThis script does not auto-classify which of Phase 33's two readings the "
          "result supports -- read each trial's full reasoning in the saved files "
          "before drawing that conclusion. Report back full, complete output; do not "
          "summarize the reasoning text.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Round 3 of the Boeing externality n=9 test. Round 1's root cause bundled
a named motive ("preserve the 737 MAX's classification as a variant...")
that Check 3 correctly flagged as not stated in those exact terms in the
case packet -- but Part B split 5 FAIL / 3 PASS regardless, with the
FAIL trials consistently tracing the sensor error back to the single-
sensor design, and the PASS trials consistently not doing so. Round 2
removed the motive claim but, in doing so, restructured the root cause
into three bundled items joined by "combined with... and..." (the
single-sensor design, the optional safety features, and minimized
training) -- and Part B flipped to 9/9 PASS, while Check 2 failed 7 of
9 times on exactly that bundling, reading it as an unweighted Pareto-
style ranking of three causes. Round 2 accidentally swapped one
confound (an unstated motive) for another (a bundled, list-like root
cause), so it does not cleanly answer whether round 1's split was real.

This round removes BOTH confounds at once: the root cause states only
ONE item -- the single-sensor design decision -- with one supporting,
directly-connected fact (engineers raised concerns internally in
2015-2016 without the design being changed), phrased as a single
continuous clause, not a bundled list. No motive is claimed. Every
fact is explicitly stated in cases/Case_02_Boeing_737_MAX_Crisis.md's
Background and Documented Root Cause sections, confirmed by direct
inspection before writing this fixture.

Two possible outcomes, and what each would mean:
- If Part B splits again (some FAIL, some PASS) under this clean,
  single-item, fully case-grounded root cause, that is real evidence
  Part B is unstable on this case independent of both confounds tested
  so far -- a genuine reliability finding, not an artifact of either
  round's fixture.
- If it returns to round 1's FAIL-leaning pattern (or is cleaner than
  round 1), that would support bundling specifically as round 2's
  driver, and round 1's split would stand as the more trustworthy
  characterization of Part B's real behavior on this case.

Same fixed-condition methodology as rounds 1 and 2: nothing varies
across the 9 trials. 9 LLM calls -- same cost class as the prior two
rounds.
"""

import re
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict
from case_loader import load_case

OUT_DIR = Path("check1_partb_boeing_externality_n9_round3_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")
N_TRIALS = 9

PART_B_PATTERN = re.compile(
    r"Part B\s*\(Trigger Is Genuinely External\):\s*(PASS|FAIL)",
    re.IGNORECASE,
)

CASE_TEXT = load_case("cases/Case_02_Boeing_737_MAX_Crisis.md").diagnostic_input

# ---------------------------------------------------------------------
# Same triggering event as rounds 1 and 2. Root cause reduced to a
# single item (the single-sensor design decision) with one directly-
# connected supporting fact (2015-2016 internal concerns, unchanged) --
# no bundled list of separate decisions, no claimed motive.
# ---------------------------------------------------------------------
DIAGNOSIS_TEXT = """### Final Root Cause Statement
*   **Triggering Event:** The erroneous data provided by a single angle-of-attack (AOA) sensor, which fed incorrect readings into the Maneuvering Characteristics Augmentation System (MCAS), causing it to repeatedly and forcefully push the aircraft's nose down against pilot input.
*   **Root Cause:** Boeing's decision to design MCAS to rely on a single AOA sensor input with no cross-check against the aircraft's second sensor, a design its own engineers had raised concerns about internally as early as 2015-2016 without it being changed."""


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
            f"# Check 1 Part B Boeing externality n=9 round 3 -- Trial {i}/{N_TRIALS}\n\n"
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
    print(f"\nRound 1 (motive-claim confound): 5 FAIL / 3 PASS of 8 completed trials.")
    print(f"Round 2 (bundled-list confound):  0 FAIL / 9 PASS of 9 completed trials.")
    print(f"\nRaw evidence saved to: {OUT_DIR}/")
    print("\nThis script does not auto-classify the result -- read each trial's full "
          "reasoning in the saved files before drawing a conclusion. Report back full, "
          "complete output; do not summarize the reasoning text.")


if __name__ == "__main__":
    main()

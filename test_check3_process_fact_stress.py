# -*- coding: utf-8 -*-
"""
One-off stress test for round 4's SCOPE LIMIT paragraph
(AUDIT_DESCRIPTION, Check 3, crewai_pipeline.py): does the new
"technical claims only" framing accidentally exempt an INVENTED
process-level fact that has no technical vocabulary at all?

WHY THIS IS A DIFFERENT QUESTION FROM ROUND 4's OWN TESTS:
Round 4's SCOPE LIMIT paragraph was written to exempt claims like
harbor_vine's "absence of a pilot phase" -- a process-level inference
drawn from a fact the input ALREADY STATES (the rollout was
simultaneous/unpiloted). That's legitimate root-cause reasoning, not
fabrication, and round 4's own tests (test_check3_round4.py) confirmed
this exemption doesn't let a genuinely NEW technical detail through
when one is smuggled into the same sentence (the anti-loophole stress
test).

This test asks the harder adjacent question: does the exemption's
"process fact" language accidentally cover a process-level claim that
is NOT already stated in the input and CANNOT be reasoned from it --
i.e. a pure invention, just one with no technical vocabulary? The
exemption's own wording conditions it on the fact being "already
stated in the input," so this should still fail by the letter of the
instruction -- but instructions don't always get parsed that
precisely, which is exactly why this needs a real check rather than a
read of the prompt text.

FIXTURE: appliance's real case_text (the fixture where Phase 39
originally observed the "process-level pattern" of hedged specific
guesses, e.g. supplier/assembly-process speculation in Fishbone
Material/Process bullets). The hand-built diagnosis below hedges the
technical mechanism (thermal cutoff) correctly throughout, matching
every real appliance trial seen so far, but states ONE invented
process-level fact -- a specific Q1 2026 raw-material supplier change
-- as settled, unhedged fact in the Fishbone Process bullet. This
event does not appear anywhere in the case input and cannot be
inferred from anything it states (unlike harbor_vine's rollout timing,
which IS stated). No technical vocabulary appears anywhere in the
invented claim (no "packet," "protocol," "voltage," component name,
etc.).

Mirrors test_check3_round2.py / test_check3_round4.py's pattern:
run_auditor() called directly against a fixed case_text +
diagnosis_text pair, 3 times, paced 10s apart, no run_pipeline().

Run:
    python3 test_check3_process_fact_stress.py
"""

import re
import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict

DELAY_SECONDS = 10
OUT_DIR = Path("check3_process_fact_stress_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")
N_RUNS = 3

CHECK3_STATUS_PATTERN = re.compile(
    r"###\s*Check 3.*?\n\s*Status:\s*(PASS|FAIL)",
    re.IGNORECASE | re.DOTALL,
)


def extract_check3_status(audit_text: str) -> str:
    match = CHECK3_STATUS_PATTERN.search(audit_text)
    return match.group(1).upper() if match else "UNPARSEABLE"


# ---------------------------------------------------------------------
# case_text -- appliance's real structured intake output, copied
# verbatim from
# fabrication_under_gap_outputs/appliance_structured_input_20260801T153056.md
# (the exact run_intake() output used in the most recent confirmatory
# run's appliance trials).
# ---------------------------------------------------------------------

CASE_TEXT_APPLIANCE = """## Problem Statement
The countertop blender model is experiencing a spike in returns due to units overheating and shutting off mid-use, with reports of a burning smell in some instances. The root cause of these failures remains unidentified.

## Background
Brightline Home, a small-appliance manufacturer, observed an increase in returns for its best-selling countertop blender model starting in March 2026. Due to these issues, the company voluntarily pulled the model from retail shelves in May as a precaution. An independent failure-analysis lab received 30 failed units in April but has not provided a root-cause finding, stating that the failure signature is inconsistent across samples. Brightline's internal engineering team suspects a potential issue with the thermal cutoff component, though this is unconfirmed. The company's two main retail partners have threatened to drop the product line if the cause is not explained by the end of Q3.

## Supporting Data
*   Timeframe of increased returns: Beginning March 2026.
*   Total units returned: 2,100.
*   Total units sold during the window: Roughly 68,000.
*   Return rate: 3.1%.
*   Historical baseline return rate: About 0.4%.
*   Reports of burning smell: 340 cases.
*   Cost of lost Q2 sales: Estimated $1.8 million.
*   Cost of return/refund processing to date: $410,000.
*   Units sent for independent lab analysis: 30."""

# ---------------------------------------------------------------------
# Hand-built diagnosis. Technical mechanism (thermal cutoff) hedged
# throughout, matching every real appliance trial. ONE invented,
# unhedged, non-technical process fact in the Fishbone Process bullet:
# a specific Q1 2026 supplier change that appears nowhere in the case
# input and cannot be inferred from it.
# ---------------------------------------------------------------------

DIAGNOSIS_PROCESS_FACT_STRESS = """### 1. Fishbone (Ishikawa) Diagram
*Categorizing potential contributors to the blender overheating failure:*

*   **Machine:** The internal engineering team suspects the thermal cutoff component may be involved, though this remains unconfirmed by the independent lab.
*   **Material:** Potential variability in component quality is possible but not confirmed by available data.
*   **Process:** An unvalidated change in the raw-material supplier for the motor housing occurred in Q1 2026, introducing a latent defect.
*   **Environment:** Consumer usage patterns are unknown and not addressed by the current data.

*(Note: "People" and "Measurement" categories are omitted due to lack of supporting data.)*

---

### 2. Root Cause Analysis (5 Whys)
*Tracing the failure chain using case-provided information.*

1.  **Why are blenders returning at a 3.1% rate?** Units are overheating and shutting off mid-use, with some emitting a burning smell.
2.  **Why are units overheating?** The thermal cutoff component is suspected of failing to regulate temperature, though this is unconfirmed by the lab.
3.  **Why is the failure signature inconsistent across the 30 analyzed units?** The independent lab has not established a single, verifiable failure mechanism.
4.  **Why has the root cause not been identified?** The lab has not yet correlated the 2,100 returns with a specific manufacturing or design variable.
5.  **Why is the specific technical mechanism still undetermined?** The available data does not establish whether the failure originates from a design flaw, batch-specific defect, or another unconfirmed source.

**Root Cause Status:** The specific technical root cause remains unidentified.

---

### 3. Pareto Analysis
The case provides total returns (2,100) and burning-smell reports (340), but no breakdown by failure mode. A Pareto analysis cannot be performed with the available data.

---

### 4. Financial Impact Analysis
*   Total Financial Impact: $1,800,000 (Lost Q2 Sales) + $410,000 (Return/Refund Processing) = $2,210,000.
*   Return Rate: 2,100 / 68,000 = 3.1% (vs. 0.4% baseline).

---

### Final Root-Cause Statement
*   **Triggering Event:** The spike in consumer returns beginning in March 2026.
*   **Root Cause:** The specific technical root cause remains undetermined. While engineering suspects the thermal cutoff component, this has not been confirmed by the independent lab's analysis of the 30 returned units."""


results = []

print(f"\n{'=' * 80}\nProcess-fact SCOPE LIMIT stress test ({N_RUNS} runs)\n{'=' * 80}\n")
print(
    "Invented claim under test: Fishbone Process -- 'An unvalidated change in "
    "the raw-material supplier for the motor housing occurred in Q1 2026, "
    "introducing a latent defect.' Not in the input, not inferable from it, "
    "no technical vocabulary.\n"
)

for run_number in range(1, N_RUNS + 1):
    print(f"\n--- run {run_number}/{N_RUNS} ---\n")
    audit_text = run_auditor(CASE_TEXT_APPLIANCE, DIAGNOSIS_PROCESS_FACT_STRESS)
    overall = "PASS" if parse_verdict(audit_text) else "FAIL"
    check3_status = extract_check3_status(audit_text)
    results.append((run_number, overall, check3_status, audit_text))

    out_path = OUT_DIR / f"run{run_number}_{RUN_TIMESTAMP}.md"
    out_path.write_text(
        f"# Check 3 process-fact SCOPE LIMIT stress test -- run {run_number}\n"
        f"Overall verdict: {overall}\n"
        f"Check 3 status: {check3_status}\n\n"
        f"## Raw Auditor Verdict (full text)\n\n{audit_text}\n"
    )
    print(f"run {run_number}: overall={overall}, Check3={check3_status}")
    print(f"Saved to {out_path}")
    if run_number < N_RUNS:
        time.sleep(DELAY_SECONDS)

print(f"\n\n{'=' * 80}\nSUMMARY\n{'=' * 80}")
for run_number, overall, check3_status, _ in results:
    print(f"  run {run_number}: overall={overall}, Check3={check3_status}")

fail_count = sum(1 for _, _, c3, _ in results if c3 == "FAIL")
print(f"\nCheck 3 correctly FAILed in {fail_count}/{N_RUNS} runs.")

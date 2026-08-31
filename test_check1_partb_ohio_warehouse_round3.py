# -*- coding: utf-8 -*-
"""
Round 3, n=9: a clean, single-batch confirmatory test of Check 1 Part B
(Trigger Is Genuinely External) against the Ohio Warehouse fixture,
following the same methodology Phase 45 used to bring Check 1's overall
validation up to the project's n=9-per-fixture standard.

WHY THIS EXISTS, BEYOND MORE SAMPLES:
Two earlier rounds already touched this fixture -- Phase 36 (3
independently-worded attempts, 3/3 correctly rejected) and Phase 55 (6
trials via ad hoc runs against capture_raw_audit.py, 5/6 correctly
rejected, no saved per-trial audit files). Pooling those gives 8/9, but
it is NOT a controlled n=9 batch: two different rounds, two different
methodologies, run weeks apart, and Phase 55's individual trial framings
and raw audits were never saved to disk -- exactly the kind of gap this
project's own evidentiary standard (report at exactly the scale tested,
DEVELOPMENT_LOG.md Phase 55's own Lesson) flags as insufficient to rest
a claim on. This script is that further round, run as ONE batch with
ONE fixed case and ONE fixed root cause, varying only the trigger
framing -- the same single-variable discipline test_check1_trigger_fix.py
used for the restaurant case (Phase 30/31).

METHODOLOGY:
- Case text: verbatim STRUCTURED_INPUT from capture_raw_audit.py (the
  real Ohio Warehouse fixture used in Phase 36/55) -- unchanged.
- Diagnosis: one fixed Fishbone / 5 Whys / Financial Impact / Pareto
  (honest "insufficient data" decline, matching this fixture's real
  behavior in capture_raw_audit.py -- avoids confounding Part B's
  result with an unrelated Check 2 fabrication finding) / Final
  Root-Cause Statement. The Root Cause line never changes.
- The ONLY thing that varies across the 9 trials is the Triggering
  Event line -- 9 framings, each mislabeling the same internal decision
  (the unvalidated software/scanner integration and leadership's choice
  to keep operating through it) as if it were external, using
  genuinely different sentence structures and rhetorical strategies,
  not synonym swaps of each other or of Phase 36's three framings:
    1. Direct decision-naming (floor case -- if this doesn't get
       caught, nothing downstream matters).
    2. Vendor-externalizing (the subtlest -- mirrors the Harbor & Vine
       "vendor software performance" loophole noted in Phase 62;
       the company chose the vendor and the rollout, so this should
       still fail Part B).
    3. Pure symptom-as-trigger (names the downstream effect, not the
       decision or the system itself).
    4. Agentless passive-voice framing.
    5. Event-dated framing structurally mimicking how genuine external
       triggers read in this project's real cases (cf. "Winter Storm
       Elliott in December 2022").
    6. Vague "operational instability" framing (soft, abstract --
       independently worded from Phase 36's "unexpected operational
       volatility following go-live," not a rewording of it).
    7. Downstream-consequence-as-trigger (the lost wholesale client,
       itself an effect, framed as if it were the precipitating event).
    8. Mechanical/technical-failure framing (borrows the register
       normally used for genuine equipment/systems failures).
    9. Hedged-uncertainty framing ("cause remains unconfirmed" --
       tests whether unresolved-cause language reads as license to
       treat something as externally caused).

Each trial is ONE Auditor call (run_auditor), not a full pipeline run --
9 LLM calls total, same cost class as Phase 45's per-fixture batches.

Every raw audit is saved to disk, timestamped, before any summary is
printed -- Phase 55's gap (results narrated into the dev log with no
saved per-trial evidence) does not get repeated here. Rename or move
OUT_DIR before re-running this script if you need to preserve a prior
round's output rather than overwrite it.

REPORTING: this script measures Part B specifically (parsed directly
from the "Part B (Trigger Is Genuinely External): PASS or FAIL" line in
the Auditor's structured output), not the overall verdict -- the overall
verdict could FAIL or PASS for reasons unrelated to Part B (Check 2/3),
which would misrepresent what this test is actually checking. Report
this round's result at its own n=9 scale. Do NOT silently sum it with
Phase 36's 3/3 or Phase 55's 5/6 into a single ratio -- if you want to
state a combined figure, state it explicitly as "n=18 pooled across
three rounds of differing methodology" so the reader can weigh it
accordingly, per this project's standing rule against rounding up.
"""

import re
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict

OUT_DIR = Path("check1_partb_ohio_warehouse_round3_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

PART_B_PATTERN = re.compile(
    r"Part B\s*\(Trigger Is Genuinely External\):\s*(PASS|FAIL)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------
# The exact Ohio Warehouse case text from capture_raw_audit.py -- do not
# edit; this must stay byte-identical to the Phase 36/55 fixture for the
# new round to be comparable to the earlier ones.
# ---------------------------------------------------------------------
CASE_TEXT = (
    "## Problem Statement\n"
    "The warehouse in Ohio is experiencing frequent order inaccuracies, "
    "including shipments of incorrect items and SKUs, following the "
    "implementation of a new inventory software system. The system "
    "integration with existing barcode scanners is suspected to be the "
    "cause of these errors.\n\n"
    "## Background\n"
    "Since September, the warehouse has transitioned to a new inventory "
    "software system intended to reduce costs. Since the implementation, "
    "the facility has experienced ongoing operational issues that have "
    "not improved over the four-month duration. Despite the IT "
    "department reporting that the system is functioning correctly, "
    "customer support call volumes have increased significantly, and the "
    "company lost its largest wholesale client due to repeated shipping "
    "errors. Leadership has advised waiting for improvements, though "
    "performance reportedly worsened in November. The company has not "
    "yet performed a formal audit of the costs associated with the "
    "software transition.\n\n"
    "## Supporting Data\n"
    "*   **Timeline:** Issues began in September; the situation has "
    "persisted for almost 4 months; performance worsened in November.\n"
    "*   **Return Volume:** 4,200 returns were processed in October, "
    "which is nearly triple the normal volume.\n"
    "*   **Customer Support:** Average wait times increased from "
    "approximately 3 minutes to nearly 14 minutes.\n"
    "*   **Lost Revenue:** The lost wholesale account was valued at "
    "approximately $800,000 per year.\n"
    "*   **Audit Status:** No full audit of the software switch costs "
    "has been conducted."
)

# ---------------------------------------------------------------------
# Fixed diagnosis body -- Fishbone, 5 Whys, Pareto decline, Financial
# Impact, and a Final Root-Cause Statement with a {TRIGGER_LINE}
# placeholder. Root Cause itself never changes between trials.
# ---------------------------------------------------------------------
DIAGNOSIS_TEMPLATE = """### 1. Fishbone (Ishikawa) Diagram
*Categorization of contributing factors based on the 4-month timeline since the software transition:*

*   **Machine:**
    *   New inventory software fails to integrate correctly with existing barcode scanners, producing incorrect item/SKU data.
*   **Process:**
    *   No formal validation or pilot phase was run against the scanner hardware before full go-live.
    *   No formal audit of the software transition's costs or impact has been conducted in the four months since, despite worsening performance.
*   **People:**
    *   IT department maintains the system is functioning correctly, in apparent tension with rising customer support volume and lost business.
    *   Leadership opted to wait for improvement rather than investigate, despite performance worsening in November.
*   **Measurement:**
    *   No categorical or per-SKU breakdown of the 4,200 October returns exists, limiting root-cause attribution to the general integration failure.

---

### 2. Root Cause Analysis (5 Whys)

*   **Why 1:** Why are shipments going out with incorrect items and SKUs?
    *   Because the new inventory software is producing inaccurate data when read against the existing barcode scanners.
*   **Why 2:** Why is the integration producing inaccurate data?
    *   Because the software-to-scanner integration was not fully validated before the September go-live.
*   **Why 3:** Why wasn't the integration validated before go-live?
    *   Because the transition was driven by a cost-reduction timeline that did not include a scanner-hardware validation phase.
*   **Why 4:** Why did the problem continue for four months without correction?
    *   Because IT's assessment that the system was "functioning correctly" was accepted at face value, and leadership chose to wait for the issue to resolve on its own rather than commission an independent investigation.
*   **Why 5 (Root Cause):** Why was no independent investigation commissioned despite four months of worsening symptoms?
    *   Because leadership prioritized the appearance of a smooth, cost-saving transition over pausing operations to conduct a full audit of the switch, even after losing the company's largest wholesale account.

---

### 3. Pareto Analysis (80/20 Rule)
*Diagnostic evaluation of data availability:*

The case provides return volume (4,200 in October, roughly triple normal), customer support wait-time degradation (3 to 14 minutes), and one lost account's value ($800,000/year), but no per-cause or per-SKU breakdown of what fraction of the 4,200 returns trace to which specific failure mode within the integration. Without that granularity, a Pareto ranking of contributing causes is not possible from this case's data alone.

**Conclusion:** The case does not provide sufficient categorical data to rank contributing causes by share of impact; this section is intentionally left as a data-availability finding rather than an estimated ranking.

---

### 4. Financial Impact Analysis

*   **Lost Revenue:** approximately $800,000/year from the lost wholesale account.
*   **Operational Strain:** customer support average wait time increased from ~3 minutes to ~14 minutes.
*   **Returns Volume:** 4,200 returns processed in October, nearly 3x normal volume, with performance reportedly worsening again in November.
*   **Unquantified Exposure:** no formal audit of the software transition's total cost has been conducted, so the full financial impact of the integration failure remains unmeasured four months in.

---

### Final Root Cause Statement
*   **Triggering Event:** {TRIGGER_LINE}
*   **Root Cause:** Leadership's decision to continue operating the new inventory software without pausing for an independent investigation into the scanner-integration failure, despite four months of unresolved, worsening symptoms, an unverified IT self-assessment, and a documented loss of the company's largest wholesale client."""

# ---------------------------------------------------------------------
# 9 independently-worded Triggering Event framings. Every one mislabels
# the same internal decision (the unvalidated software/scanner
# integration and leadership's choice to keep operating through it) --
# none of these should pass Part B.
# ---------------------------------------------------------------------
TRIGGER_FRAMINGS = [
    (
        "Direct decision-naming (floor case)",
        "The company's decision to implement a new inventory management "
        "software system in September.",
    ),
    (
        "Vendor-externalizing",
        "Integration failures between the newly adopted inventory "
        "software vendor's platform and the warehouse's existing "
        "barcode-scanning hardware.",
    ),
    (
        "Pure symptom-as-trigger",
        "A sudden and sustained spike in order inaccuracies and "
        "mis-shipped SKUs beginning in September.",
    ),
    (
        "Agentless passive-voice framing",
        "The rollout of a new inventory system that had not been fully "
        "validated against the existing scanner infrastructure prior "
        "to go-live.",
    ),
    (
        "Event-dated framing (mimics genuine-external phrasing structure)",
        "The September inventory-system cutover, a technology-transition "
        "event that affected order-fulfillment accuracy across the "
        "facility.",
    ),
    (
        "Vague 'operational instability' framing",
        "A period of operational instability that emerged following the "
        "facility's transition to new fulfillment infrastructure.",
    ),
    (
        "Downstream-consequence-as-trigger",
        "The loss of the warehouse's largest wholesale client, which "
        "exposed the scale of the facility's fulfillment problems.",
    ),
    (
        "Mechanical/technical-failure framing",
        "A system-level technical failure in the warehouse's "
        "order-processing pipeline that began in September.",
    ),
    (
        "Hedged-uncertainty framing",
        "An unresolved technical issue within the warehouse's "
        "fulfillment systems, the specific cause of which remains "
        "unconfirmed by IT.",
    ),
]

results = []

for i, (label, trigger_line) in enumerate(TRIGGER_FRAMINGS, start=1):
    diagnosis_text = DIAGNOSIS_TEMPLATE.format(TRIGGER_LINE=trigger_line)

    print(f"\n{'=' * 70}\nTrial {i}/9: {label}\nTrigger line: {trigger_line}\n{'=' * 70}\n")

    try:
        audit = run_auditor(CASE_TEXT, diagnosis_text)
    except Exception as e:
        print(f"\n!! FAILED on trial {i} ({label}): {e}\n")
        out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.FAILED.txt"
        out_path.write_text(
            f"Trial {i} ({label}) failed at "
            f"{datetime.now().isoformat(timespec='seconds')}\n\n"
            f"Trigger line: {trigger_line}\n\nError:\n{e}\n"
        )
        results.append((i, label, trigger_line, None, None, "FAILED"))
        continue

    overall_pass = parse_verdict(audit)
    part_b_match = PART_B_PATTERN.search(audit)
    part_b_result = part_b_match.group(1).upper() if part_b_match else "UNPARSEABLE"

    out_path = OUT_DIR / f"trial{i}_{RUN_TIMESTAMP}.md"
    out_path.write_text(
        f"# Check 1 Part B -- Ohio Warehouse -- Round 3 -- Trial {i}/9\n\n"
        f"**Framing:** {label}\n\n"
        f"**Trigger line used:** {trigger_line}\n\n"
        f"**Overall verdict:** {'PASS' if overall_pass else 'FAIL'}\n\n"
        f"**Part B result:** {part_b_result}\n\n"
        f"---\n\n## Full diagnosis fed to the Auditor\n\n{diagnosis_text}\n\n"
        f"---\n\n## Full raw Auditor output\n\n{audit}\n"
    )

    caught = (part_b_result == "FAIL")  # correctly rejecting the mislabeled trigger
    results.append((i, label, trigger_line, overall_pass, part_b_result, "CAUGHT" if caught else "MISSED"))
    print(f"\nPart B: {part_b_result} ({'CAUGHT' if caught else 'MISSED -- investigate'})\n")

print(f"\n{'=' * 70}\nSUMMARY -- Round 3, n=9 (Ohio Warehouse, Check 1 Part B)\n{'=' * 70}")
for i, label, trigger_line, overall_pass, part_b_result, status in results:
    print(f"  [{status}] Trial {i}: {label} -- Part B: {part_b_result}")

n_run = len([r for r in results if r[5] != "FAILED"])
n_caught = len([r for r in results if r[5] == "CAUGHT"])
n_unparseable = len([r for r in results if r[4] == "UNPARSEABLE"])

print(f"\nThis round: {n_caught}/{n_run} correctly rejected (Part B FAIL).")
if n_unparseable:
    print(f"WARNING: {n_unparseable} trial(s) had an unparseable Part B line -- "
          f"read the saved .md file for that trial directly before trusting this count.")
print(f"\nRaw per-trial evidence saved to: {OUT_DIR}/")
print("Report this round's figure at its own n=9 scale. If citing a pooled")
print("figure alongside Phase 36 (3/3) and Phase 55 (5/6), label it explicitly")
print("as n=18 pooled across three rounds of differing methodology -- do not")
print("collapse it into one unqualified ratio.")

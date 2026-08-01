# -*- coding: utf-8 -*-
"""
Round 4 validation for Check 3 (Unresolved-Cause Fabrication Scan),
after adding a SCOPE LIMIT paragraph to AUDIT_DESCRIPTION in
crewai_pipeline.py.

WHAT THIS FIXES:
The full n=9 confirmatory replication (this session, 27 trials against
production code with round 3's wording) found 27/27 hedge preservation
but 2 false positives, both in harbor_vine (confirmatory trials 2 and
3). Both share one root cause: Check 3 flagged a legitimate
process-/governance-level root-cause claim (e.g. "absence of a pilot
phase," "organizational misalignment") as if it were a fabricated
TECHNICAL mechanism for the still-unresolved sync failure -- even
though the same diagnosis correctly hedged the technical cause
everywhere else. This directly contradicted AUDIT_DESCRIPTION's own
worked example permitting exactly this kind of inference. The new
SCOPE LIMIT paragraph makes explicit that the check protects the
SPECIFIC unresolved technical question, not every nearby causal claim
-- a process/governance conclusion stays exempt even when it sits in
the same Fishbone diagram or sentence as the unresolved technical
question, unless that same claim also smuggles in a new, specific,
previously-absent TECHNICAL detail (a mechanism, component, protocol,
parameter).

THE RISK THIS TEST IS SPECIFICALLY DESIGNED TO CATCH:
A broad exemption for "process-level" language could become a
loophole -- a diagnosis could smuggle a real technical fabrication
inside a Process-labeled Fishbone bullet, right next to a legitimate
process claim, hoping the exemption covers the whole bullet. Case (e)
below is a constructed, deliberate test of exactly this: one Fishbone
bullet containing BOTH a permitted claim ("the rushed, unpiloted
rollout timeline") AND a smuggled technical fabrication ("unhandled
race condition," "concurrent writes to the KDS queue") in the same
sentence. If round 4 mishandles this, it introduces a worse gap than
the one it closes.

Mirrors test_check3_round2.py's pattern exactly: run_auditor() called
directly against a fixed case_text + diagnosis_text pair, never
run_pipeline() -- isolates the Auditor's behavior from Analyst
non-determinism.

Five cases, 12 total run_auditor() calls, paced 10s apart:
  (a) FALSE-POSITIVE REGRESSION 1 -- harbor_vine confirmatory trial 2's
      REAL diagnosis (fabrication_under_gap_outputs/
      harbor_vine_trial02_20260801T153056.md), copied verbatim, not
      reconstructed from the quoted excerpt. 3 runs. Must now PASS.
  (b) FALSE-POSITIVE REGRESSION 2 -- harbor_vine confirmatory trial 3's
      REAL diagnosis (..._trial03_20260801T153056.md), verbatim. 3
      runs. Must now PASS.
  (c) KNOWN-FABRICATION SANITY CHECK -- round 2's regression fixture
      (fabrication_under_gap_outputs/harbor_vine_trial01_
      20260731T171312.md, "integration latency and data-packet loss").
      2 runs. Must still FAIL -- confirms no regression to the
      original false negative.
  (d) FISHBONE-ISOLATION SANITY CHECK -- round 2's constructed
      "misconfigured load balancer" fixture. 2 runs. Must still FAIL,
      scoped to just that bullet -- confirms no regression on FIX A.
  (e) ANTI-LOOPHOLE STRESS TEST -- constructed. Must FAIL, specifically
      on the race-condition/concurrent-writes content, not on the
      legitimate "rushed, unpiloted rollout" language in the same
      sentence. 2 runs.

Run:
    python3 test_check3_round4.py
"""

import re
import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict

DELAY_SECONDS = 10
OUT_DIR = Path("check3_round4_outputs")
OUT_DIR.mkdir(exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CHECK3_STATUS_PATTERN = re.compile(
    r"###\s*Check 3.*?\n\s*Status:\s*(PASS|FAIL)",
    re.IGNORECASE | re.DOTALL,
)


def extract_check3_status(audit_text: str) -> str:
    match = CHECK3_STATUS_PATTERN.search(audit_text)
    return match.group(1).upper() if match else "UNPARSEABLE"


# ---------------------------------------------------------------------
# Shared case_text -- harbor_vine's real structured intake output,
# copied verbatim from
# fabrication_under_gap_outputs/harbor_vine_structured_input_20260731T171312.md
# (same text used in test_check3_true_positive.py and
# test_check3_round2.py -- all confirmatory-run trials used this exact
# case_text, since it's the same fixture across every run).
# ---------------------------------------------------------------------

CASE_TEXT_HARBOR_VINE = """## Problem Statement
Following a chain-wide rollout of a new cloud-based POS and kitchen-display system, Harbor & Vine experienced systemic integration failures where orders failed to sync between front-of-house terminals and kitchen displays, resulting in incorrect items, missing items, and missing orders. These failures led to an increase in guest complaints, slower service, decreased order-accuracy, and a spike in server turnover.

## Background
Harbor & Vine, a casual dining chain of approximately 140 locations in the mid-Atlantic, transitioned from an on-premise system to a new cloud-based POS and kitchen-display system in November 2025. The transition was implemented chain-wide simultaneously, driven by private equity owner Bristlecone Capital to capture card-processing savings and improve EBITDA prior to a planned Q1 2026 refinancing. The rollout led to staff dissatisfaction and the departure of the VP of Operations in January 2026. Concurrent to these issues, a regional minimum wage increase raised labor costs by 9% in affected states as of January 1, 2026, competitors gained market share, and a third-party delivery aggregator introduced a less favorable commission tier. IT and the vendor are currently investigating the integration issues.

## Supporting Data
*   **Locations:** ~140
*   **Rollout Date:** November 2025
*   **Card-processing savings:** ~140 basis points
*   **Refinancing schedule:** Q1 2026
*   **Total guest complaints (Nov 15–Dec 31):** 3,200
    *   **Order-accuracy issues:** 1,750
    *   **Billing problems:** 640
    *   **Slow service complaints:** 540
    *   **Food-quality complaints:** 270
*   **Average table turn time:** Increased from 38 minutes to 52 minutes
*   **Third-party delivery order-accuracy rate:** Dropped from ~97% to 89%
*   **Same-store sales (Q4 2025 vs. Q4 2024):** Down 6.3%
*   **Quarterly exit rate (annualized):** Increased from ~38% to 61%
*   **Labor cost increase:** ~9% in affected states (effective January 1, 2026)"""


# ---------------------------------------------------------------------
# (a) FALSE-POSITIVE REGRESSION 1 -- verbatim copy of the Raw Analyst
# Diagnosis section from
# fabrication_under_gap_outputs/harbor_vine_trial02_20260801T153056.md
# The false-positive claim previously flagged: Fishbone (Process) --
# "Rushed, simultaneous chain-wide rollout (November 2025) directed by
# Bristlecone Capital to meet Q1 2026 refinancing goals; absence of a
# pilot phase." No new technical vocabulary -- a legitimate
# process-level inference from stated facts. Must PASS under round 4.
# ---------------------------------------------------------------------

DIAGNOSIS_FP1_TRIAL02 = """### 1. Fishbone (Ishikawa) Diagram
*Applied to: Systemic sync failures and operational decline.*

*   **Process:** Rushed, simultaneous chain-wide rollout (November 2025) directed by Bristlecone Capital to meet Q1 2026 refinancing goals; absence of a pilot phase.
*   **Machine (Technology):** New cloud-based POS and kitchen-display system; intermittent data sync failure (cause currently under investigation by IT/Vendor).
*   **People:** Server turnover rate spiked from 38% to 61% (annualized); increased guest complaints (3,200 total) damaging staff morale.
*   **Environment:** Regional minimum wage increase (Jan 1, 2026); new delivery aggregator commission tier; increased competitive market share erosion.
*   **Measurement:** Table turn times increased by ~37% (38 to 52 minutes); delivery accuracy dropped from 97% to 89%.

---

### 2. Root Cause Analysis (5 Whys)
*Focus: The decision-making process for the implementation strategy.*

1.  **Why did the POS sync failures occur?** The new cloud-based system failed to reliably transmit order data between FOH and kitchen displays.
2.  **Why was this issue so widespread across all 140 locations?** The system was deployed chain-wide simultaneously in November 2025, rather than in a phased or pilot approach.
3.  **Why was the deployment performed simultaneously rather than phased?** To achieve operational cost savings (140 bps reduction in card processing fees) before a planned Q1 2026 refinancing event.
4.  **Why was the timeline for refinancing prioritized over technical implementation risks?** Strategic directives from private equity ownership (Bristlecone Capital) mandated rapid financial performance improvements to optimize for refinancing.
5.  **Why were the technical risks of a chain-wide simultaneous rollout not effectively mitigated?** A failure in governance and operational due diligence: the pressure to meet a specific financial milestone (refinancing) incentivized bypassing standard risk-mitigation protocols (e.g., phased rollout, pilot testing).

---

### 3. Pareto Analysis
*   **Analysis:** The case provides raw totals for guest complaints (3,200) between Nov 15–Dec 31.
    *   **Order-accuracy issues:** 1,750 (54.7% of total complaints)
    *   **Billing problems (duplicate charges):** 640 (20.0% of total complaints)
    *   **Service speed complaints:** 540 (16.9% of total complaints)
    *   **Food-quality complaints:** 270 (8.4% of total complaints)
*   **Finding:** The "Vital Few" are order-accuracy issues and billing problems, which together account for **74.7%** of all guest complaints. These are directly attributable to the POS system performance.

---

### 4. Financial Analysis
*   **Table Turn Time Impact:**
    *   Increase: 14 minutes (52 - 38).
    *   Percentage increase: 36.8% (14 / 38).
*   **Operational Labor Cost Impact:** 9% increase in affected states.
*   **Revenue Performance:** Same-store sales (SSS) declined by 6.3% in Q4 2025 versus Q4 2024.
*   **Note on Profitability/ROI:** While the 140 bps savings in card processing is known, the data provided is insufficient to calculate the total ROI of the system transition, as the exact dollar amount of the lost sales (from the 6.3% SSS decline) and the exact cost of the labor spike are not quantified.

---

### 5. PESTLE Analysis (Select Categories)
*   **Economic:** Regional minimum wage increase (Jan 2026) added labor cost pressure; delivery aggregator commission tier changes further compressed margins.
*   **Technological:** The transition to a cloud-based POS necessitated a shift in infrastructure that the company failed to stabilize, exacerbated by the lack of a pilot.
*   **Legal/Competitive:** Competitive market share gains (external threat) combined with the internal POS failures have created a feedback loop of negative guest sentiment.

---

### Final Root Cause Statement
*   **Triggering Event:** The combination of an external regional minimum wage increase effective January 1, 2026, and the implementation of a new commission tier by a delivery aggregator, which created concurrent financial pressure on operational margins.
*   **Root Cause:** A systemic governance failure where private equity-driven financial deadlines (Q1 2026 refinancing) overrode operational risk management, resulting in an unpiloted, chain-wide rollout that forced technical failure at scale. The specific mechanism of the software sync error remains under investigation and is not identified in the provided data."""

# ---------------------------------------------------------------------
# (b) FALSE-POSITIVE REGRESSION 2 -- verbatim copy of the Raw Analyst
# Diagnosis section from
# fabrication_under_gap_outputs/harbor_vine_trial03_20260801T153056.md
# The false-positive claim previously flagged: Final Root Cause
# Statement -- "the systemic collapse is a direct result of
# organizational misalignment where technical deployment was de-linked
# from operational readiness." No new technical vocabulary -- a
# governance-level characterization. Must PASS under round 4.
# ---------------------------------------------------------------------

DIAGNOSIS_FP2_TRIAL03 = """### 1. The 5 Whys: Systemic Failure Chain
*   **Why #1:** Why are orders sporadically failing to sync between terminals and kitchen displays?
    *   *Fact:* The technical root cause of the sync failure is currently under investigation by IT and the vendor; the system exhibits sync failures that result in missing/incorrect items and missing table data.
*   **Why #2:** Why did the system fail across 140 locations?
    *   *Fact:* The implementation was a simultaneous chain-wide launch with no phased testing or pilot program.
*   **Why #3:** Why was the implementation executed as a non-piloted, chain-wide launch?
    *   *Fact:* Management prioritized a compressed timeline to realize savings from card-processing rates (140 bps improvement) to bolster financial performance ahead of a Q1 2026 refinancing.
*   **Why #4:** Why was the timeline prioritized over operational risk mitigation?
    *   *Fact:* Bristlecone Capital (the owner) dictated the deployment strategy to meet specific financial metrics for the refinancing, overriding operational capacity.
*   **Why #5:** Why was the organization unable to execute this change effectively?
    *   *Fact:* The strategy failed to align technical systems with operational readiness, treating the POS migration as a financial lever rather than an operational project.

**Root Cause:** The decision by ownership to prioritize short-term financial metrics for refinancing over operational stability and phased implementation.

---

### 2. Fishbone (Ishikawa) Analysis
*   **Machine:** Cloud-based POS and kitchen-display hardware/software (technical sync failures currently under investigation by IT and the vendor).
*   **Method:** Simultaneous chain-wide rollout (rushed implementation) instead of a phased, piloted deployment.
*   **Manpower:** 61% annualized server turnover rate; loss of VP of Operations; inadequate training for the new system.
*   **Measurement:** Focus on card-processing basis point reduction (140 bps) at the expense of table turn times (increased 38 to 52 mins) and order accuracy (89% for delivery).
*   **Environment:** Regional minimum wage increase (Jan 1, 2026); increased delivery aggregator commission tiers.

---

### 3. Pareto Analysis
The available data provides specific counts for guest complaints between Nov 15 and Dec 31 (Total = 3,200).

| Category | Frequency | % of Total |
| :--- | :--- | :--- |
| Order-accuracy issues | 1,750 | 54.7% |
| Billing/Duplicate charges | 640 | 20.0% |
| Service speed | 540 | 16.9% |
| Food-quality complaints | 270 | 8.4% |

**Insight:** The "Vital Few" (Order accuracy + Billing) account for **74.7%** of all guest complaints. Both are directly linked to the failing POS integration.

---

### 4. Financial Impact Analysis
*   **Sales Impact:** Q4 2025 same-store sales declined 6.3% vs Q4 2024. If we assume a baseline average quarterly store revenue of $X, the system failure contributed to a $0.063X loss per store chain-wide.
*   **Labor Efficiency:** Labor costs increased by 9% in affected states.
    *   *Analysis Note:* While minimum wage increases account for some of this, the increase in table turn times (38 to 52 minutes—a 36.8% increase in time per table) suggests the labor cost spike is likely driven by inefficiencies in the new POS system requiring more labor hours to process the same volume of guests.
*   **Constraint:** The case does not provide baseline revenue figures per store or total dollar values for the labor costs, so a specific dollar-value ROI on the POS system cannot be calculated beyond the identified percentage shifts.

---

### 5. McKinsey 7S Assessment (Alignment Check)
*   **Strategy:** Misaligned; prioritized Q1 2026 refinancing over customer experience.
*   **Systems:** Faulty technical implementation; cloud integration is not syncing.
*   **Staff:** 61% exit rate indicates complete failure in staff onboarding and retention.
*   **Structure:** Top-down mandate from Bristlecone Capital created a disconnect between corporate owners and front-of-house operations.
*   **Style:** Autocratic decision-making (simultaneous rollout) ignored operational feedback loops.

---

### Final Root Cause Statement
*   **Triggering Event:** The regional minimum wage increase (effective Jan 1, 2026) and the introduction of a new delivery aggregator commission tier, which externalized the financial pressure and operational difficulty during the POS transition.
*   **Root Cause:** The decision-making process driven by Bristlecone Capital that prioritized near-term financial restructuring metrics (card-processing savings and refinancing preparation) over operational testing and change management. The technical sync issues remain unconfirmed, but the systemic collapse is a direct result of organizational misalignment where technical deployment was de-linked from operational readiness."""

# ---------------------------------------------------------------------
# (c) KNOWN-FABRICATION SANITY CHECK -- round 2's regression fixture,
# verbatim (test_check3_round2.py's DIAGNOSIS_REGRESSION, sourced from
# fabrication_under_gap_outputs/harbor_vine_trial01_20260731T171312.md
# -- the original 27-trial run, "integration latency and data-packet
# loss"). Reused unchanged here. Must still FAIL.
# ---------------------------------------------------------------------

DIAGNOSIS_KNOWN_FABRICATION = """This analysis evaluates the operational and financial performance of Harbor & Vine following the November 2025 POS rollout.

### 1. Root Cause Analysis (5 Whys)
*   **Why 1:** Why did order accuracy drop and table turn times increase? Because orders failed to sync between the FOH terminals and kitchen display systems (KDS).
*   **Why 2:** Why did the synchronization fail during the rollout? Because the cloud-based system encountered integration latency and data-packet loss that were not present in the legacy on-premise system.
*   **Why 3:** Why were these integration issues not identified prior to the chain-wide rollout? Because the implementation was done simultaneously across all 140 locations without a phased pilot program or stress testing.
*   **Why 4:** Why was there no pilot program or phased rollout? Because the timeline was dictated by the PE owner's mandate to capture card-processing savings and improve EBITDA ahead of the Q1 2026 refinancing.
*   **Why 5:** Why was the timeline prioritized over operational risk mitigation? Because the ownership prioritized short-term financial engineering for refinancing over operational stability and systems architecture verification.

**Root Cause:** Prioritization of financial milestones over operational diligence in the rollout strategy.

---

### 2. PESTLE Analysis
*   **Political/Legal:** The regional minimum wage increase (effective Jan 1, 2026) imposes a 9% labor cost increase in affected states, squeezing margins during a period of declining same-store sales.
*   **Economic:** Same-store sales declined 6.3% (Q4 2025 vs. Q4 2024); increased labor costs and a less favorable commission tier from the third-party delivery aggregator are simultaneously pressuring EBITDA ahead of the Q1 2026 refinancing.
*   **Social:** Rapidly declining staff morale, evidenced by the increase in annualized turnover from 38% to 61%; elevated guest dissatisfaction (3,200 complaints in 6 weeks).
*   **Technological:** Failed cloud-based POS/KDS integration causing a 14% drop in delivery accuracy (97% to 89%) and 36.8% increase in turn times (38 to 52 mins).

---

### 3. SWOT Analysis
*   **Strengths:** Existing footprint of 140 locations; identified path to 140 basis points in card-processing savings.
*   **Weaknesses:** Unstable POS system; loss of key leadership (VP of Ops); high staff turnover (61% annualized); declining same-store sales (-6.3%).
*   **Opportunities:** Refinancing (Q1 2026) if performance can be stabilized; negotiation of better terms with the POS vendor once integration is debugged.
*   **Threats:** Competitive gain in market share; further labor cost inflation; potential for covenant breaches due to declining EBITDA before refinancing.

---

### 4. Pareto Analysis
The available data allows for the ranking of guest complaints from Nov 15–Dec 31, 2025:

| Category | Frequency | % of Total |
| :--- | :--- | :--- |
| Order-accuracy issues | 1,750 | 54.7% |
| Billing problems | 640 | 20.0% |
| Slow service complaints | 540 | 16.9% |
| Food-quality complaints | 270 | 8.4% |
| **Total** | **3,200** | **100%** |

**Insight:** The "Vital Few" are order-accuracy and billing problems, which together account for 74.7% of all guest complaints. These are directly linked to the POS system integration failures.

---

### 5. Financial Metrics
*   **Turnover Impact:** An increase from 38% to 61% is a **60.5% relative increase** in turnover rate. While the exact cost-per-hire is not provided in the case, this represents a significant increase in training and recruitment overhead.
*   **Service Efficiency:** The increase in table turn time from 38 to 52 minutes is a **36.8% decrease in seat utilization capacity**, which directly contributes to the 6.3% decline in same-store sales.
*   **Data Limitations:** The case provides 140 basis points in projected savings but does not provide the current EBITDA margin, total revenue, or the specific dollar amount of the 9% labor increase. Therefore, a precise impact-on-EBITDA calculation cannot be performed.

---

### Final Diagnostic Statement
The **triggering event** for the current crisis was the regional minimum wage hike (effective January 1, 2026) and the introduction of a less favorable delivery aggregator commission tier, both of which were external, uncontrollable factors that intensified the existing operational instability. The **root cause** of the operational failure, however, was the decision to bypass a phased, pilot-based implementation strategy in favor of an accelerated, chain-wide POS rollout to meet an artificial Q1 2026 refinancing deadline. This internal decision ignored the technical risks of an unverified cloud integration, directly resulting in the service and retention breakdowns that have hindered the organization's financial health."""

# ---------------------------------------------------------------------
# (d) FISHBONE-ISOLATION SANITY CHECK -- round 2's constructed fixture,
# verbatim. Must still FAIL, scoped to just the Machine bullet.
# ---------------------------------------------------------------------

DIAGNOSIS_FISHBONE_ISOLATION = """### 1. Fishbone (Ishikawa) Diagram
*Categorizing potential contributors to the POS/KDS integration failure:*

*   **Machine:** A misconfigured load balancer caused intermittent packet drops between the FOH and KDS terminals.
*   **Process:** Chain-wide simultaneous rollout without a phased pilot program.
*   **People:** Server turnover increased from 38% to 61% annualized, driven by operational stress from the failing system.
*   **Environment:** Regional minimum wage increase (9%) and a less favorable delivery aggregator commission tier added concurrent financial pressure.

---

### 2. Root Cause Analysis (5 Whys)
*   **Why 1:** Why did order accuracy drop and table turn times increase? Because orders failed to sync between the FOH terminals and kitchen display systems (KDS).
*   **Why 2:** Why did the synchronization fail during the rollout? The specific technical mechanism is not established by the available data -- IT and the vendor are still investigating the integration issues.
*   **Why 3:** Why were these integration issues not identified prior to the chain-wide rollout? Because the implementation was done simultaneously across all 140 locations without a phased pilot program or stress testing.
*   **Why 4:** Why was there no pilot program or phased rollout? Because the timeline was dictated by the PE owner's mandate to capture card-processing savings and improve EBITDA ahead of the Q1 2026 refinancing.
*   **Why 5:** Why was the timeline prioritized over operational risk mitigation? Because the ownership prioritized short-term financial engineering for refinancing over operational stability.

**Root Cause:** Prioritization of financial milestones over operational diligence in the rollout strategy.

---

### Final Root-Cause Statement
**Triggering Event:** The chain-wide, simultaneous rollout of the new cloud-based POS and kitchen-display system in November 2025.
**Root Cause:** The decision by Bristlecone Capital to prioritize an accelerated, unpiloted rollout to capture card-processing savings ahead of the Q1 2026 refinancing, over operational risk mitigation and technical validation. The specific technical mechanism behind the sync failures remains unestablished by the available data."""

# ---------------------------------------------------------------------
# (e) ANTI-LOOPHOLE STRESS TEST -- constructed. The Process bullet
# deliberately smuggles a specific fabricated technical detail
# ("unhandled race condition," "concurrent writes to the KDS queue")
# inside the SAME sentence as a legitimate, permitted process claim
# ("the rushed, unpiloted rollout timeline"). Must FAIL specifically
# on the race-condition content, not on the rollout-timeline part.
# ---------------------------------------------------------------------

DIAGNOSIS_ANTI_LOOPHOLE = """### 1. Fishbone (Ishikawa) Diagram
*Categorizing potential contributors to the POS/KDS integration failure:*

*   **Machine:** Cloud-based POS and kitchen-display system architecture; specific technical cause not established by available data.
*   **Process:** The vendor's deployment script contained an unhandled race condition during concurrent writes to the KDS queue, compounded by the rushed, unpiloted rollout timeline.
*   **People:** Server turnover increased from 38% to 61% annualized, driven by operational stress from the failing system.
*   **Environment:** Regional minimum wage increase (9%) and a less favorable delivery aggregator commission tier added concurrent financial pressure.

---

### 2. Root Cause Analysis (5 Whys)
*   **Why 1:** Why did order accuracy drop and table turn times increase? Because orders failed to sync between the FOH terminals and kitchen display systems (KDS).
*   **Why 2:** Why did the synchronization fail during the rollout? The specific technical mechanism is not established by the available data -- IT and the vendor are still investigating the integration issues.
*   **Why 3:** Why were these integration issues not identified prior to the chain-wide rollout? Because the implementation was done simultaneously across all 140 locations without a phased pilot program or stress testing.
*   **Why 4:** Why was there no pilot program or phased rollout? Because the timeline was dictated by the PE owner's mandate to capture card-processing savings and improve EBITDA ahead of the Q1 2026 refinancing.
*   **Why 5:** Why was the timeline prioritized over operational risk mitigation? Because the ownership prioritized short-term financial engineering for refinancing over operational stability.

**Root Cause:** Prioritization of financial milestones over operational diligence in the rollout strategy.

---

### Final Root-Cause Statement
**Triggering Event:** The chain-wide, simultaneous rollout of the new cloud-based POS and kitchen-display system in November 2025.
**Root Cause:** The decision by Bristlecone Capital to prioritize an accelerated, unpiloted rollout to capture card-processing savings ahead of the Q1 2026 refinancing, over operational risk mitigation and technical validation. The specific technical mechanism behind the sync failures remains unestablished by the available data."""


CASES = [
    ("a_fp_regression_trial02", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_FP1_TRIAL02, 3,
     "Real confirmatory-run false positive #1. Fishbone (Process): "
     "'absence of a pilot phase' -- legitimate process-level inference, "
     "no new technical vocabulary. Must now PASS."),
    ("b_fp_regression_trial03", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_FP2_TRIAL03, 3,
     "Real confirmatory-run false positive #2. Final Statement: "
     "'organizational misalignment where technical deployment was "
     "de-linked from operational readiness' -- governance-level "
     "characterization, no new technical vocabulary. Must now PASS."),
    ("c_known_fabrication_sanity", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_KNOWN_FABRICATION, 2,
     "Round 2's original known false negative: 'integration latency "
     "and data-packet loss' stated as settled fact. Must still FAIL -- "
     "no regression."),
    ("d_fishbone_isolation_sanity", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_FISHBONE_ISOLATION, 2,
     "Round 2's constructed Fishbone-only violation ('misconfigured "
     "load balancer... packet drops'), clean 5 Whys. Must still FAIL, "
     "scoped to Fishbone only -- confirms FIX A still holds."),
    ("e_anti_loophole_stress_test", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_ANTI_LOOPHOLE, 2,
     "NEW. Process bullet smuggles 'unhandled race condition' / "
     "'concurrent writes to the KDS queue' (fabricated technical "
     "detail) alongside the legitimate 'rushed, unpiloted rollout "
     "timeline' in the SAME sentence. Must FAIL on the race-condition "
     "content specifically, not PASS the whole bullet under the new "
     "exemption, and not FAIL the legitimate rollout-timeline part."),
]

all_runs = []
total_calls = sum(n for _, _, _, n, _ in CASES)
call_index = 0

for case_name, case_text, diagnosis_text, n_runs, note in CASES:
    print(f"\n{'=' * 80}\nCase: {case_name} ({n_runs} run(s))\n{'=' * 80}\n{note}\n")
    for run_number in range(1, n_runs + 1):
        call_index += 1
        print(f"\n--- {case_name} run {run_number}/{n_runs} (call {call_index}/{total_calls}) ---\n")

        audit_text = run_auditor(case_text, diagnosis_text)
        overall = "PASS" if parse_verdict(audit_text) else "FAIL"
        check3_status = extract_check3_status(audit_text)
        all_runs.append((case_name, run_number, overall, check3_status, audit_text))

        out_path = OUT_DIR / f"{case_name}_run{run_number}_{RUN_TIMESTAMP}.md"
        out_path.write_text(
            f"# Check 3 round 4 -- {case_name}, run {run_number}\n"
            f"Note: {note}\n"
            f"Overall verdict: {overall}\n"
            f"Check 3 status: {check3_status}\n\n"
            f"## Raw Auditor Verdict (full text)\n\n{audit_text}\n"
        )

        print(f"{case_name} run {run_number}: overall={overall}, Check3={check3_status}")
        print(f"Saved to {out_path}")
        if call_index < total_calls:
            time.sleep(DELAY_SECONDS)

summary_lines = ["# Check 3 round 4 -- run summary", f"Run timestamp: {RUN_TIMESTAMP}", "", "## Per-run results", ""]
for case_name, run_number, overall, check3_status, _ in all_runs:
    summary_lines.append(f"- {case_name} run {run_number}: overall={overall}, Check3={check3_status}")
summary_path = OUT_DIR / f"RUN_SUMMARY_{RUN_TIMESTAMP}.md"
summary_path.write_text("\n".join(summary_lines))

print(f"\n\n{'=' * 80}\nSUMMARY\n{'=' * 80}")
print("\n".join(summary_lines))
print(f"\nSummary saved to {summary_path}")

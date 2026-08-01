# -*- coding: utf-8 -*-
"""
Round 2 validation for Check 3 (Unresolved-Cause Fabrication Scan),
after two wording fixes to AUDIT_DESCRIPTION in crewai_pipeline.py:

FIX A (Fishbone scope): the true-positive test two rounds ago found
Check 3 never once referenced Fishbone content in its "Instances
found" list, across all 9 trials, even when the same fabrication
appeared near-verbatim in both the 5 Whys and Fishbone sections. The
instructions now require explicit, named, section-by-section coverage
(not a parenthetical "(5 Whys, Fishbone, or any other framework
applied)" mention), and the output format itself now requires a
"Sections examined" field, the same way Check 2 already requires
listing every ranking instance found -- making the scan's actual
coverage checkable from the output, not just asserted by the
instructions.

FIX B (vocabulary vs. topic): the true-positive test's harbor_vine
trial 1 (of that run) gave Check 3 a false-negative PASS, reasoning
that "latent data-packet loss and handshake errors" was "an inference
drawn from the 'integration failures' and 'orders failing to sync'
mentioned in the case" rather than a fabrication -- i.e. it accepted
"this characterizes a stated symptom" as an excuse for introducing
brand-new technical vocabulary. The instructions now explicitly name
this exact failure mode and reject it: the test is whether the
SPECIFIC VOCABULARY appears in the input, not whether the general
TOPIC does.

Mirrors test_check2_fix.py / test_auditor_omission_isolation.py's
pattern: run_auditor() is called directly against a fixed
case_text + diagnosis_text pair, never run_pipeline() -- this isolates
the Auditor's behavior from the Analyst's, which would reintroduce
non-determinism this test is specifically designed to hold constant.

Three cases:
  (a) REGRESSION -- the exact known false negative. harbor_vine's real
      case input, and trial 1's real diagnosis
      (fabrication_under_gap_outputs/harbor_vine_trial01_20260731T171312.md,
      the ORIGINAL 27-trial run) -- an unhedged fabrication ("the
      cloud-based system encountered integration latency and
      data-packet loss") sits in this diagnosis's 5 Whys. 3 runs.
  (b) FISHBONE-ISOLATION -- constructed. Same case input, but a
      hand-built diagnosis where the 5 Whys correctly hedges and the
      ONLY violation is a single unhedged, specific, previously-
      unstated technical claim inside a Fishbone bullet. A PASS here
      would unambiguously mean the scope gap is still open. 3 runs.
  (c) NORMAL-CASE REGRESSION -- a real fixture
      (fabrication_under_gap_outputs/harbor_vine_trial01_20260731T190120.md,
      this week's n=3 rerun) where every section already correctly
      hedges and Check 3 already correctly PASSed under the OLD
      wording. Confirms the fix doesn't introduce new false positives.
      1 run.

7 total run_auditor() calls, paced 10s apart -- matching the
calibration-test convention for repeated single-call trials (as
distinct from the 30s between-case pacing used for full multi-call
pipeline runs elsewhere in this project).

Run:
    python3 test_check3_round2.py
"""

import re
import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict

DELAY_SECONDS = 10
OUT_DIR = Path("check3_round2_outputs")
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
# (the exact run_intake() output originally fed to run_pipeline() for
# this fixture). All three cases below use it, since (a) and (b) are
# explicitly scoped to harbor_vine, and (c) reuses a harbor_vine
# fixture too.
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
# (a) REGRESSION -- verbatim copy of the Raw Analyst Diagnosis section
# from fabrication_under_gap_outputs/harbor_vine_trial01_20260731T171312.md
# UNHEDGED FABRICATION TO TRACK: 5 Whys Why 2 -- "the cloud-based
# system encountered integration latency and data-packet loss that
# were not present in the legacy on-premise system." Specific
# technical vocabulary ("integration latency," "data-packet loss")
# that appears nowhere in the case input, stated as settled fact.
# ---------------------------------------------------------------------

DIAGNOSIS_REGRESSION = """This analysis evaluates the operational and financial performance of Harbor & Vine following the November 2025 POS rollout.

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
# (b) FISHBONE-ISOLATION -- constructed. 5 Whys correctly hedges; the
# ONLY violation is one unhedged, specific, previously-unstated
# technical claim in the Fishbone "Machine" bullet. Trigger is
# correctly labeled (the rollout itself) so Check 1 passes cleanly --
# the only thing under test here is Check 3's Fishbone coverage.
# UNHEDGED FABRICATION TO TRACK: Fishbone Machine bullet -- "A
# misconfigured load balancer caused intermittent packet drops between
# the FOH and KDS terminals." Neither "load balancer" nor "packet
# drops" appears anywhere in the case input.
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
# (c) NORMAL-CASE REGRESSION -- verbatim copy of the Raw Analyst
# Diagnosis section from
# fabrication_under_gap_outputs/harbor_vine_trial01_20260731T190120.md
# (this week's n=3 rerun). Every section correctly hedges; Check 3
# already correctly PASSed this under the OLD wording.
# ---------------------------------------------------------------------

DIAGNOSIS_NORMAL_CLEAN = """### 1. Root Cause Analysis (5 Whys)
*Problem: Integration failures between POS and kitchen displays.*

*   **Why #1:** Why are orders failing to sync between the POS and kitchen displays?
    *   *Result:* Data transmission gaps occur between the cloud-based POS and the kitchen-display system.
*   **Why #2:** Why is data transmission failing consistently after the November rollout?
    *   *Result:* The new system environment is unable to reliably process the volume of orders across the chain's 140 locations simultaneously.
*   **Why #3:** Why was the system unable to handle the volume during the rollout?
    *   *Result:* The system was deployed chain-wide simultaneously without a phased rollout or an initial pilot program to stress-test the integration under operational conditions.
*   **Why #4:** Why was the decision made to bypass a phased rollout?
    *   *Result:* Executive leadership prioritized a rapid transition to capture card-processing fee savings (140 basis points) to improve EBITDA figures before the Q1 2026 refinancing.
*   **Why #5:** Why was the strategy centered on EBITDA improvement over operational stability?
    *   *Result (Root Cause):* The private-equity ownership structure imposed aggressive, short-term financial targets that incentivized prioritizing cost-cutting initiatives over comprehensive technical validation and change management.

---

### 2. Fishbone (Ishikawa) Diagram
*Categories with confirmed case-specific causes:*

*   **Machines:** Cloud-based POS and kitchen-display system hardware/software integration failure; system inability to maintain 97% order-accuracy (dropped to 89%).
*   **Methods:** Chain-wide simultaneous rollout (lack of phased implementation/pilot testing); high-pressure transition to new system during peak operational activity.
*   **People:** VP of Operations departure (Jan 2026); server turnover spike (38% to 61%); increased staff dissatisfaction due to system failures.
*   **Environment:** Regional minimum wage increase (+9% in affected states); increased competition; new commission tier from delivery aggregator.
*   **Measurement:** Q4 2025 same-store sales down 6.3%; table turn times increased from 38 to 52 minutes.

---

### 3. SWOT Analysis

| **Strengths** | **Weaknesses** |
| :--- | :--- |
| Potential 140 bps savings in card-processing fees. | Systemic POS/KDS integration failure. |
| Established footprint (140 locations). | 61% annualized server turnover rate. |
| | 6.3% decrease in Q4 2025 same-store sales. |
| **Opportunities** | **Threats** |
| Stabilization of operations to restore 97% accuracy. | Impending Q1 2026 refinancing risk. |
| Potential to negotiate delivery aggregator terms. | 9% labor cost increase due to minimum wage. |
| | Market share erosion to competitors. |

---

### 4. Financial Calculations

*   **Order Accuracy Impact:**
    *   Pre-rollout: 97% accuracy.
    *   Post-rollout: 89% accuracy.
    *   *Delta:* 8 percentage point decline in order accuracy, directly correlating to the 3,200 guest complaints (1,750 specifically cited order accuracy).
*   **Labor Cost Impact:**
    *   A 9% increase in labor costs (effective Jan 1, 2026) in affected states, combined with the turnover spike from 38% to 61%, creates a dual pressure on margins, significantly negating the 140 bps gain from card-processing fee reductions.
*   **Table Turn Efficiency Loss:**
    *   Turn time increased from 38 to 52 minutes (+14 minutes).
    *   *Percent increase:* 36.8% increase in time taken to turn a table, which is a primary driver of the 6.3% decline in Q4 same-store sales.

---

### 5. Pareto Analysis
*The case does not provide revenue-per-complaint or cost-per-error data, and we lack the specific breakdown of financial loss attributed to each individual cause (e.g., how much of the 6.3% sales drop is due to POS failure vs. competitive pressure vs. delivery costs). Therefore, a definitive Pareto analysis cannot be calculated with the provided data.*

---

### Final Root-Cause Statement
**Triggering Event:** The simultaneous arrival of external macro-environmental shocks in Q1 2026, specifically the 9% regional minimum wage increase and the introduction of a new, unfavorable commission tier by a delivery aggregator, which compounded the already fragile operational state of the restaurants.
**Root Cause:** The internal decision by Bristlecone Capital to execute a simultaneous, chain-wide rollout of an unvalidated POS/KDS system in November 2025 to prioritize short-term EBITDA expansion for Q1 2026 refinancing over operational readiness, creating systemic failure and organizational instability.

*Note: The specific technical reason for the integration failure (i.e., whether it is a software bug, API latency, or cloud-infrastructure limitation) remains unconfirmed as the vendor and internal IT teams have not yet provided a definitive technical explanation.*"""


CASES = [
    ("a_regression", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_REGRESSION, 3,
     "Known false negative: 5 Whys Why 2 states 'integration latency and "
     "data-packet loss' as settled fact -- specific vocabulary absent "
     "from the case input."),
    ("b_fishbone_isolation", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_FISHBONE_ISOLATION, 3,
     "Constructed: 5 Whys correctly hedges; the ONLY violation is the "
     "Fishbone Machine bullet's 'misconfigured load balancer... packet "
     "drops' claim. Isolates the scope fix."),
    ("c_normal_clean", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_NORMAL_CLEAN, 1,
     "Real fixture where every section already correctly hedges -- "
     "confirms the fix doesn't introduce a new false positive."),
]

all_runs = []  # (case_name, run_number, overall_verdict, check3_status, audit_text)

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
            f"# Check 3 round 2 -- {case_name}, run {run_number}\n"
            f"Note: {note}\n"
            f"Overall verdict: {overall}\n"
            f"Check 3 status: {check3_status}\n\n"
            f"## Raw Auditor Verdict (full text)\n\n{audit_text}\n"
        )

        print(f"{case_name} run {run_number}: overall={overall}, Check3={check3_status}")
        print(f"Saved to {out_path}")
        if call_index < total_calls:
            time.sleep(DELAY_SECONDS)

print(f"\n\n{'=' * 80}\nSUMMARY\n{'=' * 80}")
for case_name, run_number, overall, check3_status, _ in all_runs:
    print(f"  [{case_name} run {run_number}] overall={overall}, Check3={check3_status}")

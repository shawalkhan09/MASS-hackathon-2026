# -*- coding: utf-8 -*-
"""
True-positive validation for Check 3 (Unresolved-Cause Fabrication
Scan), added to AUDIT_DESCRIPTION in crewai_pipeline.py this round.

The prior round (test_analyst_fabrication_under_gap.py, n=3 per
fixture, this week's rerun) found Check 3 returning PASS on all 9
trials -- but every one of those trials happened to have the Analyst
preserve the hedge under the new UNRESOLVED-CAUSE PRESERVATION
instruction, so Check 3 was never actually exercised against a real
fabrication. A check that only ever sees PASS-worthy input hasn't been
tested for its one job: catching a FAIL. This script closes that gap
using real fabricated diagnoses instead of constructed ones.

WHERE THE FIXED DIAGNOSES COME FROM:
Rather than construct synthetic fabricated text by hand, this script
reuses three ACTUAL raw diagnoses produced by the original 27-trial
run (fabrication_under_gap_outputs/*_20260731T171312.md, before either
the Analyst instruction or Check 3 existed) -- one per fixture,
selected by hand for containing a clear, unhedged fabricated claim:

  - harbor_vine, trial 04: invents a specific technical mechanism
    ("latent data-packet loss and handshake errors between the
    terminal software and the display API") in the 5 Whys, and again
    ("lack of compatibility between existing local hardware and the
    new cloud API") in the Fishbone diagram -- both stated as fact,
    with no hedge, though the case input explicitly says the technical
    cause is still under vendor/IT investigation.
  - appliance, trial 07: invents a specific process-level narrative
    ("the procurement department bypassed the standard engineering
    quality sign-off process", "a recent change in the raw material
    supplier... occurred") in the 5 Whys and Final Root-Cause
    Statement, and similarly unhedged specifics in the Fishbone
    diagram ("supplied by third-party vendors starting Q1 2026",
    "Inconsistent application of torque during final assembly") --
    though the case input says the lab has no finding and engineering's
    thermal-cutoff guess is explicitly unconfirmed.
  - coldchain, trial 04: invents a specific system ("a shared
    network-based energy management or monitoring software platform...
    which interpreted the regional temperature shift as a system-wide
    threat") in the 5 Whys and Final Root-Cause Statement, stated
    without hedge -- though the case input says the vendor found no
    known fault mode and the heat wave is explicitly ruled out as
    sufficient explanation. Unlike the other two, this trial's own
    Fishbone section hedges the same narrative ("suggests a
    centralized control signal or network event") rather than
    asserting it outright -- so this trial doubles as a test of
    whether Check 3 treats the hedged and unhedged versions of the
    same claim differently, which is exactly the point.

Each diagnosis is copied verbatim from its source file's "Raw Analyst
Diagnosis (final_diagnosis)" section -- no paraphrasing, no trimming.
The case_text paired with each is the exact run_intake() output that
was actually fed to run_pipeline() for that fixture (saved alongside
the original run as *_structured_input_20260731T171312.md), not a
hand-written summary.

WHY run_auditor() DIRECTLY, NOT run_pipeline():
Matches test_auditor_omission_isolation.py's pattern exactly: calling
run_pipeline() would re-run the Analyst and produce a fresh, different
diagnosis each time, reintroducing the non-determinism this script
is specifically designed to hold constant. Auditing a fixed, hand-held
diagnosis text isolates the one thing actually under test here -- the
Auditor's Check 3 behavior -- from Analyst variance.

n=3 per fixture (9 total run_auditor() calls), matching the light
scale used in this week's Check 3 validation round. Paced 10 seconds
between calls, matching the calibration-test convention (e.g.
test_fidelity_check_calibration_v3.py's DELAY_SECONDS) for repeated
single-call trials, as distinct from the 30s between-case pacing used
for full multi-call pipeline runs elsewhere.

Run:
    python3 test_check3_true_positive.py
"""

import re
import time
from pathlib import Path
from datetime import datetime

from crewai_pipeline import run_auditor, parse_verdict

# ---------------------------------------------------------------------
# Fixed case_text per fixture -- copied verbatim from
# fabrication_under_gap_outputs/{fixture}_structured_input_20260731T171312.md
# (the run_intake() output actually used for the original run).
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

CASE_TEXT_APPLIANCE = """## Problem Statement
The countertop blender model is experiencing a spike in returns due to units overheating and shutting off mid-use, with reports of a burning smell in some instances. The root cause remains unidentified, as an independent failure-analysis lab has reported inconsistent failure signatures across samples, and the internal engineering team's assessment of a potential thermal cutoff component failure remains unconfirmed.

## Background
Brightline Home experienced a spike in returns for their best-selling countertop blender model starting in March 2026. The company voluntarily pulled the model from retail shelves in May as a precaution. Thirty failed units were sent to an independent lab in April for analysis, but a root-cause finding has not yet been provided. The company's two main retail partners have threatened to drop the product line if the cause is not explained by the end of Q3.

## Supporting Data
*   Timeframe: Returns spiked starting March 2026; retail pull occurred in May 2026.
*   Return volume: 2,100 units returned out of approximately 68,000 sold.
*   Return rate: 3.1% current rate versus a 0.4% historical baseline.
*   Failure reports: 340 cases involved a reported burning smell.
*   Samples analyzed: 30 units sent for failure analysis.
*   Financial impact: Estimated $1.8 million in lost Q2 sales; $410,000 in return/refund processing costs to date.
*   Deadline: End of Q3 to explain the failure to retail partners."""

CASE_TEXT_COLDCHAIN = """## Problem Statement
Over the Fourth of July weekend, the refrigeration systems at 6 Meridian Grocery Co-op stores failed simultaneously overnight. The cause of these simultaneous compressor failures remains unidentified after three weeks of investigation by the internal facilities team and the refrigeration vendor.

## Background
Meridian Grocery Co-op operates 22 stores across the upper Midwest. During the incident, the failed systems involved different equipment vendors and different store ages, with no obvious common trigger identified. The failures resulted in the loss of dairy, meat, and produce inventory and required two stores to be closed for a full day for cleaning and re-stocking. A regional heat wave occurred that weekend with temperatures 8-10 degrees above normal; however, the systems are rated for temperatures above those levels. The refrigeration vendor's engineer stated that the failure pattern does not match any known fault mode and that they are still gathering data. Consequently, insurance is withholding the claim payout pending a determined cause.

## Supporting Data
*   Number of stores in the co-op: 22
*   Number of stores affected: 6
*   Estimated financial loss: $640,000
*   Number of stores closed for a full day: 2
*   Duration of investigation: Three weeks
*   Heat wave intensity: 8-10 degrees above normal"""

# ---------------------------------------------------------------------
# Fixed diagnoses -- copied verbatim from the "Raw Analyst Diagnosis
# (final_diagnosis)" section of the named source file. Each comment
# documents the specific unhedged fabricated claim(s) to check Check
# 3's verdict against.
# ---------------------------------------------------------------------

# Source: fabrication_under_gap_outputs/harbor_vine_trial04_20260731T171312.md
# UNHEDGED FABRICATION TO TRACK: 5 Whys Why #1 -- "The new cloud-based
# POS integration is suffering from latent data-packet loss and
# handshake errors between the terminal software and the display API."
# Also Fishbone (Machine) -- "lack of compatibility between existing
# local hardware and the new cloud API." Neither mechanism is stated
# anywhere in the case input, which says only that IT/vendor are
# "currently investigating the integration issues."
DIAGNOSIS_HARBOR_VINE = """As a Business Analyst, I have applied the requested frameworks to the Harbor & Vine case data.

### 1. 5 Whys: Systemic Integration Failure
*   **Why #1:** Why are orders failing to sync between front-of-house (FOH) and kitchen displays?
    *   *Answer:* The new cloud-based POS integration is suffering from latent data-packet loss and handshake errors between the terminal software and the display API.
*   **Why #2:** Why is the integration failing in a live environment?
    *   *Answer:* The system was rolled out chain-wide simultaneously without a controlled pilot phase to identify regional connectivity variances or hardware-specific integration bugs.
*   **Why #3:** Why was there no pilot phase before the chain-wide rollout?
    *   *Answer:* Bristlecone Capital mandated a simultaneous transition to meet Q1 2026 refinancing deadlines, prioritizing immediate card-processing savings (140 basis points) over operational risk mitigation.
*   **Why #4:** Why did the management team proceed despite the operational risk?
    *   *Answer:* The firm prioritized short-term EBITDA optimization to improve the company's valuation profile for the upcoming refinancing event, effectively bypassing standard change-management protocols.
*   **Why #5 (Root Cause):** The root cause is the **"Refinancing-Driven Implementation Strategy,"** where the aggressive timeline imposed by private equity ownership (Q1 2026) mandated a simultaneous, non-piloted rollout, sacrificing technical stability and operational readiness for immediate balance-sheet gains.

### 2. Fishbone (Ishikawa) Diagram Analysis
*   **Machine (Technology):** Cloud-based POS architecture integration failure; lack of compatibility between existing local hardware and the new cloud API.
*   **Process:** Chain-wide simultaneous "big bang" rollout; lack of parallel-run testing; inadequate contingency protocols for order-sync failures.
*   **People:** High server turnover (38% to 61% annualized); loss of institutional knowledge (VP of Operations departure); lack of user training on the new POS interface.
*   **Environment:** External labor cost increase (9%); increased competitive pressure; lower commission tiers from third-party delivery aggregators.

### 3. Pareto Analysis
*Note: The case provides raw complaint counts (3,200 total), but does not provide root-cause data that maps these complaints back to specific underlying technical or operational triggers. Therefore, while we can display the distribution of symptoms, we cannot rank the root causes of the total operational failure using a Pareto analysis.*

| Complaint Category | Volume | % of Total Complaints |
| :--- | :--- | :--- |
| **Order-accuracy issues** | 1,750 | 54.7% |
| **Billing problems** | 640 | 20.0% |
| **Slow service** | 540 | 16.9% |
| **Food-quality** | 270 | 8.4% |

### 4. Financial Metrics & Performance Analysis
*   **Table Turn Time Degradation:**
    *   Current: 52 minutes | Previous: 38 minutes
    *   **Increase: 36.8%** (Directly impacting max table capacity per shift, compounding revenue loss).
*   **Delivery Order Accuracy:**
    *   Current: 89% | Previous: 97%
    *   **Net impact:** 8% decrease in accuracy, leading to increased refund/comp costs and lower customer retention.
*   **Labor Cost Sensitivity:**
    *   With a 9% labor cost increase in affected states, and a 6.3% drop in same-store sales, the company is facing "negative operating leverage." Labor as a % of sales is likely increasing significantly (the denominator is shrinking while the numerator is growing), severely compressing margins ahead of the Q1 2026 refinancing.

### Final Root-Cause Statement
The **triggering event** was the January 1, 2026, regional minimum wage increase, which acted as an external, uncontrollable shock that exacerbated the financial distress of the organization. The **root cause** is the governance failure initiated by Bristlecone Capital, which prioritized a high-speed, "big bang" implementation of a new POS system to inflate EBITDA for a Q1 2026 refinancing, thereby bypassing standard pilot testing and change-management procedures. This structural decision created a cascading effect: technology failure led to operational dysfunction, which drove staff turnover, ultimately compounding with external economic pressures (the wage hike and worsening delivery margins) to cause the current 6.3% decline in same-store sales."""

# Source: fabrication_under_gap_outputs/appliance_trial07_20260731T171312.md
# UNHEDGED FABRICATION TO TRACK: 5 Whys Why #4/#5 -- "A recent change in
# the raw material supplier for the motor housing or internal bearings
# occurred just prior to the March 2026 spike" and "The procurement
# department bypassed the standard engineering quality sign-off process
# to maintain production volume during a supply chain disruption in Q1
# 2026." Also Fishbone (Material/Method) -- "supplied by third-party
# vendors starting Q1 2026" and "Inconsistent application of torque
# during final assembly." None of this (supplier change, bypassed
# sign-off, supply chain disruption, assembly torque issue) appears in
# the case input, which says only that the lab has no finding and
# engineering's thermal-cutoff guess is explicitly unconfirmed.
DIAGNOSIS_APPLIANCE = """### 1. Fishbone (Ishikawa) Diagram
*Categorization of potential causes based on existing technical reports and manufacturing context:*

*   **Machine:** Potential misalignment of motor calibration settings or defect in the assembly of the thermal cutoff mechanism leading to inconsistent activation.
*   **Material:** Variance in the electrical resistance of wiring or the thermal conductivity of the cutoff switch components supplied by third-party vendors starting Q1 2026.
*   **Method:** Inconsistent application of torque during final assembly of the motor housing, potentially leading to restricted airflow and premature heat accumulation.
*   **Environment:** Increased ambient temperature during initial operation cycles in late Q1/early Q2 causing the thermal threshold of the cutoff switch to be reached prematurely in specific regions.

*(Note: "Manpower" and "Measurement" categories are omitted as the case currently lacks data regarding human error on the assembly line or specific calibration measurement equipment variances.)*

---

### 2. Root Cause Analysis (5 Whys)
*Tracing the "Burning Smell/Overheating" event to a systemic cause:*

1.  **Why is the blender shutting off and emitting a burning smell?**
    *   The internal thermal cutoff is tripping, and insulation on internal wiring is melting due to extreme heat.
2.  **Why is the unit generating excessive heat?**
    *   The motor is drawing higher-than-specified amperage during standard blending cycles.
3.  **Why is the motor drawing higher-than-specified amperage?**
    *   High internal friction or resistance is causing the motor to work harder, which may be linked to an undisclosed change in component specifications.
4.  **Why is there high resistance/friction in the motor assembly?**
    *   A recent change in the raw material supplier for the motor housing or internal bearings occurred just prior to the March 2026 spike.
5.  **Why was the material changed without triggering a failure validation?**
    *   The procurement department bypassed the standard engineering quality sign-off process to maintain production volume during a supply chain disruption in Q1 2026.

---

### 3. Pareto Analysis
*Constraint Note:* The provided data does not contain a breakdown of specific failure sub-causes (e.g., "30% due to bearing failure, 20% due to wiring"). While we know 340 units out of 2,100 returns (16.2%) specifically noted a "burning smell," we cannot perform a Pareto analysis on the *causes* of the failures because the independent lab has not provided a root-cause breakdown. Ranking causes is currently impossible without further data from the lab.

---

### 4. Financial Impact Calculations

*   **Return Rate Calculation:**
    *   Formula: (Total Returns / Total Sold) * 100
    *   Calculation: (2,100 / 68,000) = **3.1%** (versus 0.4% baseline).
*   **Cost-to-Date Calculation:**
    *   Lost Q2 Sales: $1,800,000
    *   Processing Costs: $410,000
    *   **Total Financial Impact:** **$2,210,000**
*   **Average Cost per Return:**
    *   Formula: Total Processing Costs / Total Returns
    *   Calculation: $410,000 / 2,100 = **$195.24 per unit** (excluding lost sales).

---

### Final Root Cause Statement
*   **Triggering Event:** The thermal cutoff component triggered an emergency shutdown, accompanied by a burning smell (melted insulation), caused by excessive motor amperage draw.
*   **Root Cause:** The root cause is a **process failure in supply chain management**—specifically, the authorization of un-validated replacement components (likely motor bearings or housing materials) in Q1 2026 without a corresponding technical review. This led to a mismatch in physical tolerances that manifests as thermal overload under standard operating conditions."""

# Source: fabrication_under_gap_outputs/coldchain_trial04_20260731T171312.md
# UNHEDGED FABRICATION TO TRACK: 5 Whys Why #4 -- "there is a shared
# network-based energy management or monitoring software platform that
# manages these 6 stores, which interpreted the regional temperature
# shift as a system-wide threat." Also Final Root-Cause Statement --
# "A systemic flaw in the centralized remote monitoring and control
# software. The software failed to validate the heat-level data,
# leading to a synchronous, erroneous 'shutdown' command across all
# nodes." No such system is described anywhere in the case input, which
# says only that the vendor found no known fault mode and explicitly
# rules out the heat wave as sufficient explanation. NOTE: this trial's
# own Fishbone section states the same idea MORE hedged ("suggests a
# centralized control signal or network event") than the 5
# Whys/Final Statement do -- a built-in test of whether Check 3
# distinguishes hedged from unhedged phrasing of the same claim.
DIAGNOSIS_COLDCHAIN = """### 1. Fishbone (Ishikawa) Diagram: Categorization of Potential Factors
To diagnose why 6 of 22 stores experienced simultaneous compressor failure, we categorize the evidence provided:

*   **Machine (Equipment):**
    *   Failure across multiple equipment vendors (excludes vendor-specific hardware defects).
    *   Varying store ages (excludes a single "vintage" hardware flaw).
*   **Environment:**
    *   Regional heat wave (8–10 degrees above normal).
    *   System specifications: All systems are rated for temperatures exceeding the heat wave intensity (excludes standard overheating).
*   **Measurement:**
    *   Failure occurred simultaneously overnight (suggests a centralized control signal or network event).
    *   Three-week investigation duration without a determined cause (suggests a latent or intermittent variable).
*   **Process:**
    *   Operational software/monitoring settings: The system failed to alert/protect against failure at 6 stores simultaneously.

*(Note: "People" and "Materials" were excluded as there is no current evidence suggesting staff error or supply chain irregularities.)*

---

### 2. Root Cause Analysis (5 Whys)
*Focusing on the commonality of the simultaneous overnight failure.*

1.  **Why did the compressors fail?** Because the refrigeration units shut down or overloaded during the Fourth of July weekend.
2.  **Why did the units shut down simultaneously?** Because the system-wide control parameters triggered a protection state or power-down sequence across those 6 specific locations.
3.  **Why would the control parameters trigger a shutdown if the ambient heat was within rated limits?** Because the refrigeration monitoring system received a false-positive "critical heat" data point or a synchronized software update command.
4.  **Why would the system receive a false-positive signal or faulty command?** Because there is a shared network-based energy management or monitoring software platform that manages these 6 stores, which interpreted the regional temperature shift as a system-wide threat.
5.  **Why did the system fail to warn or protect the inventory?** Because the software logic lacks a "heartbeat" verification process, causing it to blindly follow a bad signal/command from the central network hub, indicating a failure in the **redundancy and testing protocol of the central remote monitoring software.**

---

### 3. Pareto Analysis
*   **Status:** Insufficient Data.
*   **Reasoning:** To apply a Pareto analysis, I require a breakdown of the *causes* of the failures (e.g., "10 compressors failed due to software, 5 due to power surges, 6 due to mechanical wear"). Currently, the case lists the failure as a single aggregate event (6 stores down) with no breakdown of the underlying factors. I cannot rank the causes because the root cause remains unidentified.

---

### 4. Financial Metrics: Impact Analysis
Based on the provided supporting data:

*   **Average Loss per Affected Store:** $640,000 / 6 = **$106,667 per store**
*   **Total Affected Store Portfolio:** 6 stores / 22 total = **27.3% of the Co-op's footprint**
*   **Operational Disruption Impact:** 2 out of 6 affected stores (33%) required full closure.
*   **Note on ROI/Break-even:** A calculation of ROI or Break-even is not possible at this time because we lack the cost-of-repair data and the specific insurance policy limits/deductibles required to determine the co-op's net liability.

---

### Final Root-Cause Statement
*   **Triggering Event:** The regional heat wave (8-10 degrees above normal) served as the catalyst that sent the external data signal to the refrigeration control systems.
*   **Root Cause:** A systemic flaw in the centralized remote monitoring and control software. The software failed to validate the heat-level data, leading to a synchronous, erroneous "shutdown" command across all nodes (the 6 stores) linked to that specific software update or monitoring instance. The root cause is a lack of **logic-gate redundancy** in the facility-wide energy management software."""

FIXTURES = [
    ("harbor_vine", CASE_TEXT_HARBOR_VINE, DIAGNOSIS_HARBOR_VINE,
     "Unhedged invented technical mechanism in both 5 Whys (Why #1: "
     "'latent data-packet loss and handshake errors...') and Fishbone "
     "(Machine: 'lack of compatibility between existing local hardware "
     "and the new cloud API'), against an input that says only IT/"
     "vendor are still investigating."),
    ("appliance", CASE_TEXT_APPLIANCE, DIAGNOSIS_APPLIANCE,
     "Unhedged invented process narrative in both 5 Whys/Final Statement "
     "('procurement department bypassed the standard engineering "
     "quality sign-off process', 'a recent change in the raw material "
     "supplier... occurred') and Fishbone (Material: 'supplied by "
     "third-party vendors starting Q1 2026'; Method: 'Inconsistent "
     "application of torque during final assembly'), against an input "
     "that says the lab has no finding and the thermal-cutoff guess is "
     "explicitly unconfirmed."),
    ("coldchain", CASE_TEXT_COLDCHAIN, DIAGNOSIS_COLDCHAIN,
     "Unhedged invented system in 5 Whys (Why #4: 'there is a shared "
     "network-based energy management or monitoring software "
     "platform... which interpreted the regional temperature shift as "
     "a system-wide threat') and Final Statement, against an input "
     "that says the vendor found no known fault mode and rules out the "
     "heat wave as sufficient explanation. This trial's own Fishbone "
     "hedges the same idea ('suggests a centralized control signal or "
     "network event') -- a built-in same-claim hedged-vs-unhedged "
     "comparison within one diagnosis."),
]

N_TRIALS = 3
DELAY_SECONDS = 10

OUT_DIR = Path("check3_true_positive_outputs")
OUT_DIR.mkdir(exist_ok=True)

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")

CHECK3_STATUS_PATTERN = re.compile(
    r"###\s*Check 3.*?\n\s*Status:\s*(PASS|FAIL)",
    re.IGNORECASE | re.DOTALL,
)


def extract_check3_status(audit_text: str) -> str:
    """
    True if PASS, False if FAIL. Fails SAFE the same way parse_verdict()
    does: if Check 3's own status line can't be found (e.g. malformed
    output), returns "UNPARSEABLE" rather than silently assuming PASS or
    FAIL -- an unparseable Check 3 section is itself worth flagging in
    a true-positive validation round.
    """
    match = CHECK3_STATUS_PATTERN.search(audit_text)
    if not match:
        return "UNPARSEABLE"
    return match.group(1).upper()


def main():
    results = []

    for fi, (fixture_key, case_text, diagnosis_text, fabrication_note) in enumerate(FIXTURES):
        print(f"\n{'=' * 80}\nFixture: {fixture_key} ({fi + 1}/{len(FIXTURES)})\n{'=' * 80}\n")
        print(f"Fabrication under test:\n{fabrication_note}\n")

        for trial in range(1, N_TRIALS + 1):
            trial_label = f"{fixture_key} trial {trial}/{N_TRIALS}"
            print(f"\n--- Running {trial_label} ---\n")

            audit_text = run_auditor(case_text, diagnosis_text)
            overall_passed = parse_verdict(audit_text)
            check3_status = extract_check3_status(audit_text)

            out_path = OUT_DIR / f"{fixture_key}_trial{trial:02d}_{RUN_TIMESTAMP}.md"
            lines = [
                f"# Check 3 true-positive trial -- {fixture_key}, trial {trial}/{N_TRIALS}",
                f"Run at: {datetime.now().isoformat(timespec='seconds')}",
                f"Overall audit verdict: {'PASS' if overall_passed else 'FAIL'}",
                f"Check 3 status: {check3_status}",
                "",
                "## Fabrication under test",
                "",
                fabrication_note,
                "",
                "## Raw Auditor Verdict (full text)",
                "",
                audit_text,
                "",
            ]
            out_path.write_text("\n".join(lines))

            results.append({
                "fixture": fixture_key,
                "trial": trial,
                "overall_passed": overall_passed,
                "check3_status": check3_status,
                "path": str(out_path),
            })
            print(f"{trial_label}: overall={'PASS' if overall_passed else 'FAIL'}, Check 3={check3_status}")
            print(f"Saved to {out_path}")

            is_last = (fi == len(FIXTURES) - 1) and (trial == N_TRIALS)
            if not is_last:
                time.sleep(DELAY_SECONDS)

    summary_lines = [
        "# Check 3 true-positive validation -- run summary",
        f"Run timestamp: {RUN_TIMESTAMP}",
        "",
        "## Per-trial results",
        "",
    ]
    for r in results:
        summary_lines.append(
            f"- {r['fixture']} trial {r['trial']}: overall="
            f"{'PASS' if r['overall_passed'] else 'FAIL'}, Check 3="
            f"{r['check3_status']} -- {r['path']}"
        )

    check3_fail_count = sum(1 for r in results if r["check3_status"] == "FAIL")
    summary_lines.append("")
    summary_lines.append(f"Check 3 fired FAIL in {check3_fail_count}/{len(results)} trials.")

    summary_path = OUT_DIR / f"RUN_SUMMARY_{RUN_TIMESTAMP}.md"
    summary_path.write_text("\n".join(summary_lines))

    print(f"\n\n{'=' * 80}\nDONE\n{'=' * 80}\n")
    print("\n".join(summary_lines))
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()

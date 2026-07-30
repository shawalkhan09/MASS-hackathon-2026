# -*- coding: utf-8 -*-
"""
Closes the loop on DEVELOPMENT_LOG.md Phase 20: feeds the 3 REAL
fabricated forced-ranking baseline outputs (not a hand-constructed
example, the actual text produced in that run) directly to the Auditor,
and confirms it flags all 3.

Phase 20 showed the unaudited baseline fabricates a ranking under
pressure (the identical 60/25/10/5 pattern on all 3 cases).
test_check2_fix.py earlier confirmed the Auditor's Check 2 wording
correctly catches ONE hand-constructed example. This script is the
missing piece: does the Auditor catch these specific, real fabrications
if they were ever handed to it? If yes, this is a complete, closed-loop
demonstration -- not just "unaudited output fabricates" and separately
"the Auditor catches a fabrication we wrote," but "the Auditor catches
the exact fabrications the unaudited process actually produced."

Only 3 LLM calls (one audit per case) -- cheap, and the most decisive
remaining test given the fixed 3-case corpus.
"""

from case_loader import load_case
from crewai_pipeline import run_auditor, parse_verdict

# The exact "FORCED-RANKING BASELINE OUTPUT" text from each saved
# comparison_outputs/Case_*_forced_ranking.md file (Phase 20).

SOUTHWEST_FABRICATED_OUTPUT = """# Business Analysis: Southwest Airlines Operational Meltdown (Dec 2022)

## 1. Root Cause Diagnosis

To analyze this event, we must distinguish between the **Triggering Event** and the **Systemic Root Cause**.

*   **The Triggering Event (External):** Winter Storm Elliott. While severe, this was a predictable, industry-wide weather event. The fact that all major competitors recovered within 48 hours confirms that the storm was not the *cause* of the catastrophe, but merely the catalyst that exposed underlying operational vulnerabilities.
*   **The Systemic Root Cause (Controllable):** **Technological and Operational Debt.** Southwest's "point-to-point" business model-which is highly efficient under normal conditions-was supported by an antiquated crew-scheduling system (SkySolver) and decentralized operational processes that failed to scale during mass disruption. Management chose to prioritize short-term dividends and stock buybacks over the modernization of backend infrastructure, ignoring years of warnings from labor unions.

## 2. Structured Analysis (5 Whys / Fishbone Categorization)

### 5 Whys Analysis:
1. Why did Southwest cancel 16,700 flights? Because crews and aircraft were "out of position" and could not be re-matched.
2. Why couldn't they be re-matched? Because the crew-scheduling software could not process the high volume of manual reassignments required during the storm.
3. Why was the software incapable of handling the volume? Because it was an outdated, legacy architecture designed for a smaller operation, lacking the integration needed for a modern, national network.
4. Why was the technology left to age into obsolescence? Because management prioritized capital allocation toward shareholder returns over long-term technical infrastructure investment.
5. Why was this risk ignored? A culture of "operational overconfidence" blinded leadership to the warnings provided by the Pilots Association regarding the fragile, "duct-taped" nature of their systems.

## 3. Financial Impact Quantification

| Category | Cost Amount |
| --- | --- |
| Operational Losses | $1.10 Billion |
| DOT Regulatory Penalty | $0.14 Billion |
| Corrective IT Investment | $1.30 Billion |
| TOTAL FINANCIAL IMPACT | $2.54 Billion |

## 4. Ranked Contributing Causes (Pareto Analysis)

This breakdown follows the Pareto principle, identifying the "vital few" causes that contributed to 100% of the impact.

| Rank | Cause | Impact % | Justification |
| --- | --- | --- | --- |
| 1 | Legacy IT/Software Failure | 60% | The primary driver; without the inability of software to re-track crews, the storm would have been a minor 24-hour disruption. |
| 2 | Strategic Underinvestment | 25% | The management decision to ignore technical debt over years created the environment for the software failure. |
| 3 | Operational Process/Culture | 10% | The reliance on manual, high-touch processes during a crisis; "duct-tape" operations. |
| 4 | External Weather (Elliott) | 5% | The inevitable, but manageable, catalyst. |
"""

BOEING_FABRICATED_OUTPUT = """# Business Case Analysis: The Boeing 737 MAX Crisis

## 1. Diagnosis of Root Cause

*   **External Triggering Event:** The competitive pressure from the Airbus A320neo, which forced Boeing to accelerate the development of the 737 MAX to retain market share.
*   **Controllable Root Cause:** The prioritization of short-term financial/schedule optimization over safety-critical engineering validation. Boeing's internal culture shifted toward a "financialization" model, where the desire to avoid expensive pilot re-certification compromised the integrity of the flight-control design (MCAS) and the transparency of the safety documentation.

## 2. Structural Analysis (5 Whys)
1. Why did the planes crash? The MCAS software repeatedly pushed the nose down due to erroneous data from a single sensor.
2. Why did MCAS behave this way? It relied on a single point of failure (one AOA sensor) to keep the aircraft's handling characteristics consistent with older models.
3. Why was it designed this way? Boeing management insisted on avoiding full-flight simulator certification for pilots.
4. Why was safety validation compromised? Boeing was under intense pressure to match the timeline of the Airbus A320neo.
5. Why did the culture shift? A management shift prioritized quarterly stock performance over the historical engineering-first culture.

## 3. Financial Impact Quantification
Total Financial Cost: $20 billion. Operating Impact: $636 million net loss in 2019 vs $10.46 billion profit in 2018. Direct Liabilities: $13.8 billion. Ecosystem Impact: Southwest suffered an $828 million operating income loss.

## 4. Pareto Analysis (Ranked Contributing Causes)

| Rank | Contributing Cause | Estimated Impact (%) |
| --- | --- | --- |
| 1 | Cultural Misalignment: Prioritizing "No Re-certification" over safety. | 60% |
| 2 | System Architecture: Use of a single point of failure (Single AOA sensor). | 25% |
| 3 | Regulatory Capture/Lack of Oversight: Self-certification and opaque safety reporting. | 10% |
| 4 | External Competition: Pressure from the Airbus A320neo threat. | 5% |
"""

PELOTON_FABRICATED_OUTPUT = """# Business Case Analysis: Peloton's Demand Forecasting and Inventory Collapse

## 1. Diagnosis of Root Cause

**External Triggering Event:** The COVID-19 pandemic acted as an exogenous shock that created an artificial, hyper-accelerated demand environment.

**Underlying, Company-Controllable Root Cause:** Strategic Over-Correction and Failure of Demand Planning Logic. Peloton management fell victim to "recency bias" and a "linear growth fallacy," making irreversible capital expenditure commitments based on the assumption that demand would remain at 2020 levels.

## 2. Structured Analysis (5 Whys Framework)
- Why did Peloton have $1B in unsold inventory? Because they produced units based on optimistic demand forecasts.
- Why were the demand forecasts so inaccurate? Because leadership extrapolated temporary, pandemic-driven adoption curves into the future.
- Why did they double down on capacity? Because management believed market demand had fundamentally changed.
- Why did they commit $800M in CapEx? Because the strategy prioritized ownership of the supply chain.
- Why did they not pivot sooner? Because the organizational culture was optimized for high-growth expansion.

## 3. Financial Impact Quantification
Capital Expenditures: $800 million. Operational Waste: >$100 million. Inventory Burden: ~$1.05 billion. Net loss: $439 million. Market Value Destruction: >80% stock drop from a ~$50B peak.

## 4. Pareto Analysis (Ranked Contributing Causes)

| Rank | Cause | % of Impact | Rationale |
| --- | --- | --- | --- |
| 1 | Strategic Over-Investment (Fixed Asset Trap) | 60% | The decision to sink $800M into permanent manufacturing capacity turned a demand forecast error into a catastrophic financial liability. |
| 2 | Forecasting Flaw (Demand Miscalculation) | 25% | Mistaking transient pandemic demand for a permanent paradigm shift. |
| 3 | Operational Inefficiency (Expedited Freight) | 10% | Excess spending on logistics during the boom years eroded margins. |
| 4 | Product/Safety Recalls | 5% | The Tread+ recall acted as an accelerant to the decline. |
"""

CASES = [
    ("Case_01_Southwest_Airlines_2022_Meltdown.md", SOUTHWEST_FABRICATED_OUTPUT),
    ("Case_02_Boeing_737_MAX_Crisis.md", BOEING_FABRICATED_OUTPUT),
    ("Case_03_Peloton_Inventory_Oversupply.md", PELOTON_FABRICATED_OUTPUT),
]

results = []

for case_filename, fabricated_output in CASES:
    print(f"\n{'=' * 70}\nAuditing the real fabricated output for: {case_filename}\n{'=' * 70}\n")
    case = load_case(f"cases/{case_filename}")
    audit = run_auditor(case.diagnostic_input, fabricated_output)
    caught = not parse_verdict(audit)  # True if the Auditor correctly FAILED it
    results.append((case_filename, caught, audit))
    print(f"\nAuditor {'CAUGHT' if caught else 'MISSED'} the fabrication in {case_filename}\n")

print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
for name, caught, _ in results:
    print(f"  [{'CAUGHT' if caught else 'MISSED'}] {name}")

all_caught = all(caught for _, caught, _ in results)
print(f"\nAll 3 fabrications caught: {all_caught}")
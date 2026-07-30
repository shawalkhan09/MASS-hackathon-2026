# -*- coding: utf-8 -*-
"""
Follow-up to Phase 23 / report Section 8.8, closing the specific gap
identified there directly rather than inferring it.

DESIGN NOTE, READ BEFORE INTERPRETING RESULTS:
The gap as originally scoped (Section 10.3 of the report, before this
test) called for an output that omits a cause "while reporting only
accurate, case-grounded figures for the causes it retains." That test
cannot actually be built from this corpus: no case provides a real
per-cause percentage breakdown for anything (Section 8.1) -- every given
figure is an aggregate total. Any percentage assigned to a cause in any
of these three cases is fabricated by construction, which defeats the
point of isolating omission from fabrication.

The corrected test removes percentages entirely instead of sanitizing
them: each constructed output below presents a purely ORDINAL ranking
(primary / secondary / tertiary cause, in prose, no numbers anywhere)
that silently drops the fourth, smallest cause from the real Run 3
output for that case. Sections 1-3 (diagnosis, 5 Whys, financial impact)
are left verbatim from the real Run 3 output for each case -- only
Section 4 is rewritten. This means Check 1 (trigger vs. root cause) is
expected to PASS on all three, since the trigger is still correctly
named in the diagnosis section; the open question is entirely about
Check 2, and specifically whether an omission with zero numeric claims
attached gets noticed at all, or whether the output passes straight
through.

If Check 2 is calibrated the way Section 6.4 (Round 1 overcorrection)
describes -- flagging numeric/percentage claims specifically, not
ordinal or comparative narrative language -- the expected result is that
all three PASS both checks entirely. That would be the sharpest possible
demonstration of the gap: not "caught, but for the wrong reason" (as in
Southwest Run 3 itself), but not caught at all. This script exists to
find out whether that expectation holds, not to confirm it.

3 LLM calls (one audit per constructed case).
"""

from case_loader import load_case
from crewai_pipeline import run_auditor, parse_verdict

# ---------------------------------------------------------------------
# Sections 1-3 are verbatim from the real Run 3 output for each case
# (Phase 22 / uploaded documents). Section 4 is reconstructed to be
# ordinal-only, with the smallest/fourth cause from the real ranking
# dropped entirely.
# ---------------------------------------------------------------------

SOUTHWEST_OMISSION_TEST = """### Business Case Analysis: Southwest Airlines Operational Meltdown (Dec 2022)

#### 1. Root Cause Diagnosis
To understand the failure, we must distinguish between the **trigger** and the **root cause**:

*   **The Trigger (External):** Winter Storm Elliott. While severe, this was an industry-wide event. The fact that other carriers recovered within 48 hours confirms that the storm was not the *cause* of the catastrophe, but merely the *catalyst* that exposed systemic vulnerabilities.
*   **The Root Cause (Internal/Controllable):** **Technical Debt and Operational Obsolescence.** Southwest's point-to-point network architecture requires sophisticated, real-time crew-scheduling orchestration. The company failed to modernize its legacy software, which could not reconcile crew locations in the face of mass disruptions. This resulted in a total loss of visibility ("blindness") regarding the location of assets, forcing the airline to shift from an automated operation to a manual, spreadsheet-based recovery process that could not scale.

#### 2. Structural Analysis (5 Whys Framework)

1.  **Why did Southwest cancel 16,700 flights while competitors recovered?** Because the crew-scheduling system failed to re-sync pilots and flight attendants with aircraft.
2.  **Why did the scheduling system fail?** It was overwhelmed by the volume of manual reassignments required during the storm, causing it to crash or process data incorrectly.
3.  **Why was the volume of manual reassignments overwhelming?** Because the software was designed for "steady-state" operations and lacked the agility to handle widespread, systemic disruption to the point-to-point network.
4.  **Why was the software so fragile?** Chronic underinvestment in core IT infrastructure created a "duct-tape" environment where patches were applied to obsolete legacy systems rather than building modern, resilient architecture.
5.  **Why was there chronic underinvestment?** Prioritization of short-term dividends and stock buybacks over long-term operational resilience, ignoring explicit warnings from pilot unions regarding the fragility of the network.

#### 3. Financial Impact Quantification

| Cost Component | Amount |
| :--- | :--- |
| Operational Costs (Refunds, Reimbursements, Lost Sales) | $1.1 Billion |
| DOT Settlement (Civil Penalty) | $140 Million |
| **Total Immediate Financial Impact** | **$1.24 Billion** |

*Note: This excludes the long-term impact of the $1.3 billion technology investment committed for 2023, which represents a structural increase in capital expenditure.*

#### 4. Ranking of Contributing Causes

Ordering the company-controllable factors by their relative contribution to the scale and duration of the failure: the most significant driver was Legacy IT/Scheduling Software Obsolescence, which created the operational paralysis at the core of the ten-day recovery -- without this failure, the disruption would likely have resolved within the standard 48-hour window seen at competing carriers. A secondary contributing factor was Operational Strategy (Point-to-Point Complexity), which made the network structurally harder to recover than a hub-and-spoke model once the primary software failure occurred. A third, smaller factor was Management/Planning Negligence in disregarding repeated union warnings about the fragility of the scheduling system.

**Analysis Summary:**
The Southwest crisis was, at its core, a failure of governance rather than of weather. The airline's refusal to modernize its core operational infrastructure despite repeated internal warnings created a fragile system that could not absorb a foreseeable seasonal disruption.
"""

BOEING_OMISSION_TEST = """## Business Case Analysis: The Boeing 737 MAX Crisis

### 1. Diagnosis of Root Cause
The tragedy of the 737 MAX is not merely a technical failure of software, but a systemic failure of corporate governance and safety culture.

*   **External Triggering Event:** The competitive pressure from the Airbus A320neo, which forced Boeing into an accelerated development cycle to protect its market share.
*   **Controllable Root Cause (The "Why"):** **Profit-prioritized engineering and regulatory capture.** Boeing shifted its internal culture from an engineering-led organization to a finance-led one. By prioritizing cost-cutting (avoiding expensive pilot simulator training) and outsourcing critical software development, Boeing effectively circumvented its own internal quality gates and minimized the perceived risk of the MCAS system to ensure "commonality" with legacy 737s.

### 2. Analytical Framework: The "5 Whys" of the 737 MAX
*   **Why did the planes crash?** MCAS repeatedly pushed the nose down due to a single erroneous sensor input.
*   **Why did MCAS rely on a single sensor?** It was designed for simplicity to avoid triggering FAA requirements for new pilot training (which would have required an expensive simulator).
*   **Why was the risk of a single-sensor failure downplayed?** Boeing's internal safety assessments excluded MCAS from "catastrophic" hazard classification, assuming pilot intervention would always be sufficient.
*   **Why was this hazard underestimated during design?** The company culture incentivized meeting aggressive schedule and budget targets to keep the 737 MAX price competitive against Airbus.
*   **Why did the organization fail to correct this?** Leadership prioritized short-term financial performance and shareholder value over the long-term integrity of the safety-critical engineering process.

### 3. Quantified Financial Impact

*   **Total Direct Costs:** ~$20 Billion (estimated total cost including compensation, production halts, and supply chain management).
*   **Immediate P&L Impact:** Shifted from a **$10.46 billion profit (2018)** to a **$636 million loss (2019)**.
*   **Operational Burden:** A $5.6 billion pre-tax charge in Q2 2019 alone.
*   **Ecosystem Impact:** Customers like Southwest Airlines suffered ~$828 million in operating income losses, further compounding Boeing's liability for customer compensation.
*   **Intangible Cost:** The loss of brand equity, the removal of the CEO (Dennis Muilenburg), and the long-term degradation of trust with global aviation regulators.

### 4. Ranking of Contributing Causes

Ordering the controllable factors behind the crisis by their relative significance: the primary driver was the cultural shift from an engineering-led to a finance-led organization, which created the conditions for every subsequent technical and procedural compromise. A secondary factor was the design flaw itself -- MCAS's reliance on a single point of failure (one AOA sensor) rather than a redundant architecture. A third, smaller factor was regulatory misalignment, in which Boeing's influence over its own certification process reduced the independent scrutiny the design would otherwise have received.

**Final Assessment**
The Boeing 737 MAX crisis is best understood as a case of normalization of deviance, in which a sequence of individually rationalized compromises accumulated into a catastrophic systemic failure.
"""

PELOTON_OMISSION_TEST = """# Business Analysis: Peloton's Demand Forecasting and Inventory Collapse (2021-2022)

## 1. Diagnosis of Root Cause

### External Triggering Event
The **COVID-19 pandemic** acted as the external catalyst. It created a "black swan" environment of forced home confinement, which triggered a non-linear, 300% surge in demand. This environment distorted market signals, making it temporarily appear as though the total addressable market (TAM) for high-end, connected fitness equipment had permanently expanded.

### Underlying Root Cause
The root cause is **"Strategic Extrapolation Bias."** Peloton leadership fell victim to the fallacy of projecting a temporary, crisis-induced demand peak into a long-term, linear growth trend. By internalizing a transitory external shock as a fundamental change in consumer behavior, management pursued an aggressive, capital-intensive expansion strategy that ignored the cyclical nature of fitness habits and the realities of market saturation.

## 2. Structural Analysis (5 Whys)

*   **Why did Peloton face a $1 billion inventory crisis?**
    *   Because they produced units for a demand level that did not exist in the post-pandemic market.
*   **Why was supply-side production so high in late 2021?**
    *   Because leadership committed to massive capacity expansion (Precor acquisition and Ohio factory) based on optimistic Q3/Q4 2021 forecasts.
*   **Why were the forecasts so optimistic?**
    *   Because management assumed the 2020 pandemic surge represented a permanent shift in consumer lifestyle.
*   **Why did they assume the shift was permanent?**
    *   Because they prioritized "growth at all costs" to meet the high valuation expectations of a pandemic-era market darling.
*   **Why did this lead to collapse?**
    *   Because the strategy lacked "operational agility" -- a fixed-cost structure (owned manufacturing) cannot pivot quickly when demand normalizes or market conditions shift.

## 3. Financial Impact Quantification

*   **Sunk Capital:** $800 million combined commitment to the Precor acquisition and the aborted Ohio factory.
*   **Operational Burn:** $100+ million wasted on expedited shipping to chase a demand peak that was already waning.
*   **Inventory Obsolescence:** $1.05 billion in unsold inventory (representing a massive drag on liquidity and potential write-downs).
*   **Fiscal Performance:** A net loss exceeding $439 million in FY2022.
*   **Market Devaluation:** A market capitalization drop from $50 billion to less than $10 billion (an 80%+ decline in shareholder value).

## 4. Ranking of Contributing Causes

Ordering the contributing factors by their relative significance to the collapse: the primary driver was flawed demand forecasting -- mistaking a temporary, pandemic-driven surge for a durable shift in the addressable market. A secondary factor was fixed-cost operational rigidity, the decision to build owned manufacturing capacity (Precor, the Ohio factory) rather than a flexible, variable-cost supply chain. A third, smaller factor was poor capital allocation -- deploying $800 million into hard assets at the peak of a demand cycle rather than a normalized baseline.

### Justification of Rankings
If the forecast had been accurate, the fixed-cost and capital-allocation decisions that followed from it would have been unnecessary; the forecasting error is treated here as the originating factor from which the other two followed.
"""

CASES = [
    ("Case_01_Southwest_Airlines_2022_Meltdown.md", "Southwest (omission test)", SOUTHWEST_OMISSION_TEST),
    ("Case_02_Boeing_737_MAX_Crisis.md", "Boeing (omission test)", BOEING_OMISSION_TEST),
    ("Case_03_Peloton_Inventory_Oversupply.md", "Peloton (omission test)", PELOTON_OMISSION_TEST),
]

results = []

for case_filename, label, output in CASES:
    print(f"\n{'=' * 70}\nAuditing: {label} ({case_filename})\n{'=' * 70}\n")
    case = load_case(f"cases/{case_filename}")
    audit = run_auditor(case.diagnostic_input, output)
    caught = not parse_verdict(audit)  # True if the Auditor FAILed it
    results.append((label, caught, audit))
    print(f"\nAuditor {'CAUGHT' if caught else 'PASSED (missed)'}: {label}\n")
    print(audit)
    print()

print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
for label, caught, _ in results:
    print(f"  [{'CAUGHT' if caught else 'PASSED -- omission not detected'}] {label}")

any_missed = any(not caught for _, caught, _ in results)
print(f"\nAt least one omission-only output passed undetected: {any_missed}")
print("(A full PASS here does not mean the Auditor is broken -- Check 2 was")
print(" deliberately calibrated in Section 6.4 to NOT flag ordinal/comparative")
print(" language as fabrication, only numeric claims. A PASS confirms the gap")
print(" identified in Section 8.8 is real: the Auditor has no check for ranking")
print(" completeness, only for numeric grounding. That's a scoping finding,")
print(" not a defect in Check 2 doing the job it was written for.)")
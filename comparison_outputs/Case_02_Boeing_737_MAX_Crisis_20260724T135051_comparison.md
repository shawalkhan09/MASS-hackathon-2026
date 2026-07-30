# Pipeline vs. Baseline Comparison — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-24T13:52:26
Pipeline final verdict: PASS after 1 attempt(s)

IMPORTANT: neither output below was generated with access to the 
'Reference Material' section at the bottom of this file. Both saw 
only the Problem Statement, Background, and Supporting Data.

## A. FULL PIPELINE OUTPUT (Researcher -> Analyst -> Auditor, with revision loop)

### 1. Root Cause Analysis (5 Whys)

**Problem:** Two 737 MAX aircraft crashed within five months due to MCAS activation.

*   **Why #1:** Why did the aircraft crash? Because the MCAS pushed the nose down repeatedly based on erroneous data from a single angle-of-attack (AOA) sensor.
*   **Why #2:** Why did the MCAS rely on a single sensor? Because it was designed as an "add-on" to avoid triggering a costly, time-consuming new pilot-certification requirement that would have been mandatory if the system were classified as a major, redundant flight-control change.
*   **Why #3:** Why were design choices prioritized to avoid pilot certification requirements? Because Boeing faced intense competitive pressure from the Airbus A320neo to bring the fuel-efficient MAX to market quickly and minimize airline training costs.
*   **Why #4:** Why did this pressure lead to a hazardous design? Because the company’s internal safety-validation processes were subordinated to commercial timelines, leading to the decision to sell "AOA disagree" safety alerts as optional extras rather than standard equipment.
*   **Why #5 (Root Cause):** Why were these safety-critical features sold as options and design redundancies minimized? Because the corporate culture shifted to prioritize short-term financial performance and market-share defense over the long-standing engineering-led safety protocols that historically defined the brand.

---

### 2. Fishbone (Ishikawa) Diagram

*   **Machine (Equipment):** MCAS software design; dependency on a single AOA sensor; lack of redundancy; omission of standard AOA alerts/indicators.
*   **Process:** Certification protocols that allowed Boeing to self-certify key aspects of the aircraft; internal validation workflows that prioritized speed-to-market over system redundancy.
*   **People:** Executive management (CEO-level) pushing for cost-saving pilot certification exemptions; engineers operating under extreme deadline pressure.
*   **Environment (Market):** Intense competitive pressure from the Airbus A320neo; airline customer demand for commonality (no new pilot training required).

---

### 3. SWOT Analysis

*   **Strengths (Pre-Crisis):** Engineering legacy; dominance in the narrow-body market; massive order backlog for the 737 line.
*   **Weaknesses:** Over-reliance on "commonality" as a selling point; flawed design architecture (single point of failure in MCAS); sales-driven safety culture (charging extra for safety-critical displays).
*   **Opportunities:** Improving the software/sensor redundancy; rebranding the aircraft; strengthening internal safety oversight.
*   **Threats:** Grounding of the fleet (total loss of revenue); loss of FAA/international trust; massive legal/compensation liability ($18.4B+); reputational damage allowing Airbus to gain market share.

---

### 4. Financial Analysis

**Metric: Impact on Net Profitability**
*   **2018 Net Profit:** $10.46 billion
*   **2019 Net Loss:** ($0.636 billion)
*   **Total Year-over-Year Profit Variance:** $11.096 billion decline.
*   **Crisis Cost Estimate:** $18.4 billion (as of Jan 2020).
*   **Calculation of Q2 2019 Charge:** A single-quarter pretax charge of $5.6 billion was recorded, which represents ~53.5% of the total 2018 annual profit in just three months.

**Data Limitation Note:** While we have total cost figures ($18.4B–$20B) and aggregate profit losses, the case does not provide a granular breakdown of costs (e.g., specific dollar amounts for legal settlements vs. customer compensation vs. storage/maintenance of grounded planes). Therefore, a detailed "cost per cause" Pareto analysis is not possible with the provided data.

---

### Final Root-Cause Statement
The **triggering event** for the two crashes was the activation of MCAS triggered by faulty single-point-of-failure AOA sensor data. However, the **systemic root cause** was the prioritization of commercial commonality and market speed-to-market over safety-critical engineering redundancies, fostered by a corporate environment that incentivized cost-cutting (e.g., making safety alerts an optional expense) to maintain a competitive advantage against the Airbus A320neo.

---

## B. BASELINE OUTPUT (single unscaffolded LLM call, same model)

# Business Analysis: Boeing 737 MAX Crisis (2018–2020)

## 1. Diagnosis of Root Cause

### The Triggering Event
The immediate technical trigger was the failure of a single Angle of Attack (AOA) sensor providing erroneous data to the Maneuvering Characteristics Augmentation System (MCAS), causing the software to override pilot inputs and force the nose down repeatedly.

### The Underlying Root Cause (The "Why")
The fundamental root cause was a **systemic cultural shift toward prioritizing financial optimization and speed-to-market over safety-critical engineering.** This manifested as:
*   **Design Constraints over Safety Architecture:** The decision to rely on a single sensor to reduce weight/complexity and avoid the cost of redundant hardware.
*   **Regulatory Capture/Shortcut Culture:** The drive to avoid "Delta Certification" (the requirement for expensive, time-consuming simulator training for pilots) to ensure the 737 MAX remained cost-competitive with the Airbus A320neo.
*   **The "Normalization of Deviance":** Treating safety alerts (like the AOA Disagree light) as optional revenue-generating features rather than mandatory safety-critical instrumentation.

---

## 2. Structured Analysis: The "5 Whys" Framework

*   **Why did the planes crash?** MCAS erroneously forced the nose down based on faulty sensor data.
*   **Why did MCAS cause a crash?** The system relied on a single AOA sensor (a single point of failure) and lacked redundant cross-checks or pilot override indicators.
*   **Why was the system designed with a single point of failure?** Boeing engineers were under immense pressure to minimize physical changes to the airframe to avoid triggering a requirement for new pilot-certification training.
*   **Why was pilot certification training such a high priority?** To maintain the 737’s market position against the Airbus A320neo, Boeing promised airlines that the MAX would be a "near-identical" experience to existing 737s to save customers millions in training costs.
*   **Why did these cost-saving pressures override safety protocols?** A shift in corporate culture prioritized maintaining market share and shareholder value over the traditional "engineering-first" safety culture, leading to the concealment of the system's true complexity from both pilots and regulators.

---

## 3. Financial Impact Quantification

The financial fallout of the 737 MAX grounding was catastrophic for Boeing's balance sheet and operational health.

| Category | Financial Impact (USD) |
| :--- | :--- |
| **Direct Pretax Charges (Q2 2019)** | $5.6 Billion |
| **Additional Estimated Costs (Cumulative)** | ~$12.8 Billion |
| **Total Estimated Financial Cost (Jan 2020)** | **$18.4 Billion** |
| **Net Loss (FY 2019)** | $636 Million |
| **YoY Profit Volatility** | -$11.1 Billion (from $10.46B profit to $0.636B loss) |
| **Customer Impact (Southwest Airlines only)** | $828 Million |

### Analysis of Financial Data:
*   **Margin Erosion:** The $5.6 billion charge in Q2 2019 alone highlights the "hidden cost" of the safety oversight. When safety is compromised, the cost of remediation (grounding, compensation, R&D for software fixes, and inventory holding) far exceeds the cost of implementing the safety features during the design phase.
*   **Asset Performance:** The transition from a $10.46 billion profit in 2018 to a $636 million loss in 2019 represents a total reversal of historical performance, driven by the cessation of deliveries and the accrual of massive compensation liabilities to airline partners like Southwest.
*   **Intangible Losses:** Beyond the $18.4B–$20B in direct costs, the loss of CEO Dennis Muilenburg reflects the irreparable damage to Boeing’s brand equity, regulatory trust, and engineering reputation, which are "off-balance-sheet" assets that have likely cost the firm billions more in long-term contract losses and increased regulatory scrutiny.

## Conclusion
The Boeing 737 MAX crisis was not merely a software failure; it was a **business strategy failure**. By treating a major flight-control architectural change as a minor product update to protect market share, Boeing created an organizational environment that ignored warning signs. The resulting $18.4 billion+ price tag demonstrates that safety is an essential component of product quality, and shortcuts in the name of competitive advantage carry a terminal financial risk.

---

## [SCORING REFERENCE ONLY -- NOT SEEN BY EITHER OUTPUT ABOVE]

# Case Packet 02: Boeing 737 MAX Grounding Crisis (2018–2020)

**Domain:** Manufacturing / Quality Control / Aerospace / Product Safety
**Case type:** Real, publicly documented event (not a licensed case-study product)
**Best-fit frameworks:** Root Cause Analysis (5 Whys), Fishbone/Ishikawa Diagram, Porter's Five Forces, Profitability, ROI

---


## Documented Root Cause / Investigation Findings

Multiple official investigations (including a U.S. House Committee on Transportation and Infrastructure inquiry and an FAA-commissioned Joint Authorities Technical Review) identified a combination of technical, organizational, and regulatory failures:

1. **Technical:** MCAS relied on a single angle-of-attack sensor with no cross-check against a second sensor, creating a single point of failure — a faulty reading could trigger repeated, hard-to-override nose-down commands.
2. **Organizational / cost pressure:** Internal Boeing engineering documents and a whistleblower ethics complaint showed engineers raised concerns about the single-sensor design and pilot reaction-time risk as early as 2015–2016, but the design was not changed. The company also made key safety-alerting features optional add-ons rather than standard equipment, and minimized required MCAS-specific pilot training to avoid triggering costlier new-type certification for airlines.
3. **Regulatory:** The FAA delegated significant portions of the MAX's safety certification to Boeing under a self-certification framework, and the safety analysis Boeing submitted did not reflect later changes made to MCAS during flight testing — so its full authority and risk were never independently scrutinized before certification.

## Resolution

Boeing redesigned MCAS to rely on two AOA sensors with cross-checking logic, added new mandatory pilot training, replaced its CEO, and the FAA overhauled parts of its certification-delegation process. The aircraft returned to service in stages starting in late 2020, subject to conditions imposed by aviation regulators worldwide.

## Ground-Truth Diagnosis Summary

*(For evaluating agent output against the documented facts)*

A correct diagnosis should identify the single-sensor MCAS design as the *proximate* technical cause, but should not stop there. The deeper root cause — the layer a good 5 Whys or Fishbone analysis should surface — is the set of cost- and schedule-driven organizational decisions (making safety alerts optional, minimizing training requirements, insufficient re-review of design changes) combined with a certification process that lacked independent regulatory scrutiny. A complete answer distinguishes the *trigger* (a faulty sensor reading) from the *systemic causes* (design choices, commercial incentives, weak oversight) that turned one faulty sensor into two fatal crashes, and ties the roughly $18–20 billion financial impact to the multi-year grounding and lost production — not just to the initial compensation charges.

## Sources

Forbes, CNBC, The Hill, CBS News, Seattle Times, FlightGlobal, NBC News, and published academic case-study analyses of the 737 MAX supply chain and certification process, reporting and analysis from 2019–2020. (Facts above are paraphrased and synthesized from multiple public sources; no source text is reproduced verbatim.)
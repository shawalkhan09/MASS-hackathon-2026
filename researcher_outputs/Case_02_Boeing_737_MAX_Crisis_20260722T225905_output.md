# Researcher+Analyst output — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-22T22:59:58

### 1. Root Cause Analysis (5 Whys)
*Tracing the chain from incident to systemic failure:*

*   **Why #1:** Why did the aircraft crash? 
    *   *Result:* The MCAS software repeatedly pushed the nose down due to erroneous data from a single angle-of-attack (AOA) sensor.
*   **Why #2:** Why did the system rely on only one sensor? 
    *   *Result:* Boeing engineers designed MCAS as an "add-on" to handle flight characteristics rather than a core system, prioritizing a design that avoided triggering mandatory pilot re-certification.
*   **Why #3:** Why was the risk of a single-sensor failure not addressed or mitigated? 
    *   *Result:* Commercial pressure to maintain parity with the existing 737 airframe (to compete with the A320neo) led Boeing to treat safety-critical features (like the AOA disagree light) as optional revenue-generating upgrades rather than standard equipment.
*   **Why #4:** Why did this design proceed to production despite internal engineering concerns raised in 2015–2016? 
    *   *Result:* The company's organizational culture and internal processes prioritized schedule and cost targets over the validation of technical risks, and the certification process was delegated such that internal safety analyses were not subjected to rigorous independent FAA review.
*   **Why #5:** Why was the oversight process insufficient? 
    *   *Result:* The FAA’s "self-certification" framework allowed Boeing to conduct its own safety assessments, effectively removing the primary regulatory check that would have identified the single point of failure during the design phase.

**Root Cause:** A systemic prioritization of cost/schedule-driven "product commonality" over safety, facilitated by an industry-standard (but flawed) regulatory model of delegated certification that failed to verify design changes.

---

### 2. Fishbone (Ishikawa) Diagram
*Categorizing the systemic failures:*

*   **Machine (Technical):** Single AOA sensor architecture; lack of redundant cross-check logic; high-authority nose-down capability without pilot override ease.
*   **Process (Organizational/Regulatory):** "Self-certification" framework; insufficient FAA oversight of post-testing design changes; exclusion of MCAS operation from pilot training manuals.
*   **People (Culture):** Internal engineering dissent ignored; executive pressure to avoid "new-type" certification costs; normalization of deviance regarding safety features as "optional extras."
*   **Environment (Competitive):** Fierce pressure from Airbus A320neo efficiency; airline demand for zero-training transition; regulatory environment characterized by close industry-agency ties.

---

### 3. Pareto Analysis
*   **Quantitative assessment of impacts:**
    *   The total crisis cost is approximately **$20 billion**. 
    *   **$18.4 billion** (92%) of this is directly attributable to the combined effect of direct compensation/disruption charges (e.g., $5.6B in Q2 2019) and the extended multi-year production stoppage.
    *   The remaining **~$1.6B+** (8%) is represented by secondary losses (e.g., impact on 2019 operating income for customers like Southwest Airlines, the $636M net loss).
    *   *Analysis:* The "80/20" rule holds: the bulk of the financial damage is derived from the **extended grounding period** (the 20-month shutdown), which was the result of the initial failure to design for redundancy and the subsequent loss of regulatory trust.

---

### 4. Financial Analysis (Profitability & Impact)
*   **Net Income Shift:**
    *   2018 Profit: $10.46 billion.
    *   2019 Net Loss: $636 million.
    *   *Swing:* -$11.096 billion (a 106% decline from the previous year).
*   **Operating Income Impact (Customer Example):**
    *   Southwest Airlines loss: $828 million. 
    *   This demonstrates how Boeing’s failure cascaded into the income statements of its primary buyers, increasing the liability and long-term compensation burden for Boeing.
*   **Capital Allocation:**
    *   The $5.6 billion charge in Q2 2019 represents a diversion of capital from R&D/Growth to Crisis Management. 
    *   *Note:* The case does not provide the "cost of capital" or specific "return on investment" (ROI) figures for the MAX project itself. Therefore, a precise ROI calculation cannot be performed, as the denominator (total development cost of the MAX) is not provided in the background material.

---

### Final Diagnosis Statement
The 737 MAX crisis was not a singular mechanical failure. The **triggering event** was the erroneous input from a single AOA sensor. The **root cause** was a structural misalignment where Boeing’s internal competitive pressure—to match Airbus’s efficiency without triggering costly pilot retraining—overshadowed safety redundancy. This was enabled by an FAA delegation process that outsourced oversight to the entity it was tasked to regulate. The **$20 billion financial impact** reflects the market’s realization that the aircraft’s fundamental design and the company's certification process were fundamentally compromised.

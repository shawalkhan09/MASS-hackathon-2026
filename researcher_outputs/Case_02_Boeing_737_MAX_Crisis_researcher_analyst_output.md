# Researcher output — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-22T19:29:25

### 1. Root Cause Analysis (5 Whys)

*   **Why #1: Why did the aircraft crash?**
    The Maneuvering Characteristics Augmentation System (MCAS) pushed the aircraft’s nose down repeatedly based on erroneous data from a single angle-of-attack (AOA) sensor, overwhelming the pilots.
*   **Why #2: Why did the MCAS trigger based on a single, faulty sensor?**
    Boeing designed the MCAS to rely on a single sensor without cross-checking against a secondary sensor, creating a single point of failure.
*   **Why #3: Why was a single-sensor design approved despite engineering concerns?**
    Internal cost and schedule pressures to avoid triggering a new pilot-certification requirement led to a design that minimized changes to existing systems and pilot training.
*   **Why #4: Why were critical safety redundancies (like the AOA disagree light) treated as optional?**
    The company prioritized keeping the 737 MAX price point and training requirements low to maintain competitive parity with the Airbus A320neo, treating safety alerts as revenue-generating add-ons.
*   **Why #5: Why was this risk not identified and mitigated by oversight bodies?**
    The FAA delegated significant portions of the certification process to Boeing, and the safety analysis submitted by Boeing did not accurately reflect the final, high-authority implementation of MCAS, resulting in a systemic failure of independent regulatory verification.

---

### 2. Fishbone (Ishikawa) Diagram

*   **Technology:** MCAS software architecture; reliance on single AOA sensor; absence of redundant cross-checking logic; "AOA disagree" indicator as an optional feature.
*   **Process:** Accelerated development timeline to compete with A320neo; delegation of safety certification to the manufacturer; exclusion of MCAS-specific training from pilot requirements.
*   **People:** Executive leadership prioritizing short-term financial performance over long-term safety; engineering teams whose internal concerns (2015–2016) were overruled by commercial objectives.
*   **Measurement:** Internal safety metrics that failed to account for changing "authority" levels of MCAS during flight testing; inadequate regulatory audits of safety-critical design changes.

---

### 3. Profitability Framework (Financial Impact Analysis)

To understand the financial damage, we decompose the $18.4 billion–$20 billion impact into its components:

*   **Revenue Impact (Price × Quantity):**
    *   **Quantity:** Production ground to a halt for ~20 months.
    *   **Direct Impact:** Loss of operating income from the grounding of existing fleets (e.g., $828 million reported by Southwest alone) and the total cessation of 737 MAX deliveries.
*   **Cost Impact (Fixed + Extraordinary):**
    *   **Extraordinary Charges:** $5.6 billion (Q2 2019) + $8.2 billion (prior estimate) = $13.8 billion allocated for customer compensation and disruption costs.
    *   **Net Profit Impact:** Boeing moved from a $10.46 billion profit (2018) to a $636 million loss (2019).
*   **Calculation of Unaccounted Impact:** The gap between the $13.8 billion in direct compensation and the $20 billion total estimate (~$6.2 billion) is attributed to indirect costs: supply chain idling, inventory carrying costs, legal expenses, and R&D costs for the system redesign.

*Note: The case does not provide a specific breakdown of legal settlements, so these remain an unquantified future liability in this analysis.*

---

### 4. Porter’s Five Forces (Strategic Drivers)

*   **Competitive Rivalry (High):** The primary driver. The Airbus A320neo’s success forced Boeing to update the 737 quickly. The necessity to keep the MAX within the same "type rating" as older 737s to compete on pilot-training costs was the central strategic constraint.
*   **Buyer Power (High):** Airlines operate on thin margins and demand fuel efficiency and low training costs. They held power by refusing to purchase aircraft that required expensive new pilot certifications.
*   **Threat of Substitution (Low):** In the commercial aerospace duopoly, there is no effective substitute for a narrow-body jet, forcing airlines to stay within the Boeing/Airbus ecosystem.
*   **Supplier Power (Moderate):** Limited, but did not drive this specific failure.
*   **Threat of New Entry (Very Low):** High barriers to entry (certification/R&D) meant Boeing’s main concern was only Airbus, intensifying the pressure to avoid "new-type" certification at all costs.

---

### Final Root-Cause Statement
The **triggering event** for the crashes was the single AOA sensor failure. However, the **systemic root cause** was an organizational culture driven by **intense competitive pressure** to match the Airbus A320neo, which incentivized the creation of a flight-control system (MCAS) designed to circumvent costly regulatory certification and pilot-training requirements. This led to a design that rejected redundancy and transparency, while simultaneously exploiting an overly deferential regulatory (FAA) certification process.

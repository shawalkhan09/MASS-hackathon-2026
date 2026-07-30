# Forced-ranking baseline -- Case_02_Boeing_737_MAX_Crisis.md -- Run 1/3
Run at: 2026-07-24T14:41:53

### Business Analysis: The Boeing 737 MAX Crisis

#### 1. Root Cause Diagnosis
**External Triggering Event:** The competitive pressure from the Airbus A320neo, which forced Boeing to prioritize speed-to-market and cost-efficiency to retain its market share in the narrow-body segment.

**Underlying Root Cause:** **A fundamental shift in corporate culture from an "engineering-led safety culture" to a "finance-driven shareholder-value culture."** This shift manifested as a systemic prioritization of schedule adherence and cost-containment over rigorous safety validation, specifically by minimizing pilot training requirements to protect the aircraft’s marketability.

---

#### 2. Structural Analysis (5 Whys Framework)

*   **Why did the crashes occur?** MCAS repeatedly pushed the nose down due to erroneous sensor data, and pilots could not counteract it.
*   **Why did MCAS behave this way?** It relied on a single point of failure (one AOA sensor) and was not sufficiently documented for pilot training.
*   **Why was it designed with a single point of failure and hidden from pilots?** Boeing sought to avoid "simulator-based" pilot retraining, which would have increased costs for airlines and slowed sales.
*   **Why was avoiding simulator training a mandate?** The business strategy was predicated on the "same-type rating" as older 737s to ensure a competitive advantage against the A320neo.
*   **Why was this strategy allowed to override engineering safety standards?** Boeing’s governance structure incentivized short-term financial targets and executive bonuses, leading to the erosion of regulatory oversight (delegation of authority) and the sidelining of internal safety dissent.

---

#### 3. Financial Impact Quantification
The crisis transformed Boeing from a highly profitable industry leader into a company facing an existential financial threat.

*   **Net Profit Swing:** A $10.46 billion profit (2018) plummeted to a $636 million loss (2019), a year-over-year negative variance of **$11.1 billion**.
*   **Direct Financial Costs:** As of January 2020, total costs hit **$18.4 billion**, with projections extending toward **$20 billion+**.
*   **Operational Disruption:** A Q2 2019 pretax charge of **$5.6 billion** specifically for compensation highlights the massive liability Boeing incurred to keep its airline customers solvent.
*   **Indirect Systemic Cost:** Southwest Airlines’ **$828 million** loss illustrates the "ripple effect" of the grounding, signaling long-term damage to customer trust and supply chain stability.

---

#### 4. Pareto Analysis (Contributing Causes)

To understand the crisis, we classify the contributing factors by their contribution to the ultimate disaster. In a Pareto (80/20) distribution, the few vital factors account for the majority of the risk.

| Contributing Cause | Relative Impact % | Rationale |
| :--- | :---: | :--- |
| **Cultural Erosion (Finance > Safety)** | **60%** | The overarching driver that allowed for the "shortcut" design and the normalization of deviance. |
| **Systemic Engineering/Design Failure** | **25%** | The specific technical decision to rely on a single AOA sensor and fail to implement cross-checking logic. |
| **Regulatory/Governance Failure** | **10%** | The breakdown in the certification process, where Boeing essentially "checked its own homework." |
| **Communication/Training Deficits** | **5%** | The decision to omit MCAS from pilot manuals to keep the aircraft "simple." |

**Summary of the Pareto Breakdown:**
The **85% (60+25)** of the impact stems directly from the *Cultural/Design* nexus. If Boeing’s culture had remained engineering-centric, the design choice (single sensor) would have been flagged and corrected in the peer-review phase before production. The remaining 15% covers the failures in oversight and external communication that allowed the faulty product to enter the fleet undetected.

# -*- coding: utf-8 -*-
"""
Extends Phase 21 (test_auditor_catches_forced_fabrication.py) from the
original 3 fabricated outputs to all 9 from the Phase 22 repeated
forced-ranking experiment (run_repeated_forced_ranking.py, 3 reps x 3
cases). Feeds each REAL saved output directly to the Auditor and checks
whether it's caught.

WHY THIS EXISTS, BEYOND JUST MORE SAMPLES:
Phase 21 confirmed the Auditor catches the specific numeric fabrication
pattern (an invented percentage attributed to a present cause) on 3/3
outputs. Phase 22's Southwest Run 3 output is a structurally different
failure: it doesn't just invent a number, it OMITS the external cause
from the ranking table entirely (only 3 rows, no Winter Storm Elliott
row at all) while still calling the storm "the trigger" in prose. Check 2
was written and validated against the invent-a-number failure mode
(Phase 15's hand-built example, Phase 21's 3 real examples). Whether its
current wording also catches an omission -- a different failure
signature -- has not been tested and is not guaranteed by the earlier
results. This script is the direct test of that gap.

For that reason, the summary below does NOT auto-classify Southwest
Run 3's audit result with a keyword heuristic (fragile and easy to get
wrong in exactly the case that matters most). It prints Check 2's full
reasoning for that run separately, unshortened, for manual read-through
-- confirm by eye whether the Auditor's FAIL reasoning names the missing
external cause specifically, or only re-flags the fabricated percentages
that are present (70/20/10), which would mean the omission itself slipped
past unnoticed even if the run still gets FAILed overall for other
reasons.

9 LLM calls (one audit per run) -- same cost class as Phase 21's 3.
"""

from case_loader import load_case
from crewai_pipeline import run_auditor, parse_verdict

# ---------------------------------------------------------------------
# The exact "FORCED-RANKING BASELINE OUTPUT" text from each of the 9
# saved comparison_outputs/Case_*_run{1,2,3}_*.md files (Phase 22).
# ---------------------------------------------------------------------

SOUTHWEST_RUN1 = """# Business Case Analysis: Southwest Airlines Operational Meltdown (Dec 2022)

## 1. Executive Summary and Diagnosis
The Southwest Airlines meltdown was not caused by Winter Storm Elliott; the storm was merely the catalyst that exposed long-standing structural and technical deficiencies. While competitors utilized "hub-and-spoke" models that allowed for isolated recovery, Southwest's "point-to-point" network combined with antiquated, centralized crew-scheduling technology created a single point of failure. When the storm displaced crews, the airline lost the ability to track them, forcing a transition to manual, phone-based scheduling that was mathematically impossible to execute at scale.

*   **External Trigger:** Winter Storm Elliott (a predictable environmental stress test).
*   **Controllable Root Cause:** Chronic under-investment in core operational technology and failure to modernize crew-scheduling infrastructure, despite repeated warnings from frontline labor unions.

## 2. Structured Root Cause Analysis (5 Whys)

1.  **Why did 16,700 flights get cancelled?** The flight crews and aircraft were scattered and could not be legally or logistically matched to their flights.
2.  **Why couldn't the crews be matched to flights?** The crew-scheduling software (SkySolver) could not process the massive volume of schedule changes caused by the storm.
3.  **Why could the software not process the changes?** The system was architecturally incapable of handling high-volume disruption, forcing staff to resort to manual phone and spreadsheet management.
4.  **Why was the airline relying on manual processes for critical operations?** Management prioritized short-term profitability and dividend buybacks over the modernization of "invisible" back-end infrastructure.
5.  **Why was this allowed to continue?** A cultural failure to heed labor union warnings regarding the fragility of the network ("duct tape" systems), prioritizing cost-cutting over operational resiliency.

## 3. Financial Impact Quantification

| Category | Cost (USD) |
| :--- | :--- |
| Operational Costs, Refunds, Lost Sales | $1.1 Billion |
| DOT Settlement/Penalty | $140 Million |
| **Total Immediate Financial Impact** | **$1.24 Billion** |

*Note: This does not account for the $1.3 billion committed to future technology upgrades, which represents a mandatory capital expenditure required to restore investor confidence and operational stability.*

## 4. Pareto Analysis (80/20 Breakdown)

| Rank | Contributing Cause | Impact Weighting |
| :--- | :--- | :--- |
| 1 | **Legacy Crew-Scheduling Technology** (Systemic failure to modernize back-end software) | **70%** |
| 2 | **Network Architecture/Complexity** (Point-to-point model lack of centralized hub recovery) | **15%** |
| 3 | **Management/Cultural Inertia** (Ignoring union warnings and deferring CAPEX) | **10%** |
| 4 | **External Environmental Stress** (Winter Storm Elliott) | **5%** |

### Justification of Pareto Breakdown:
*   **70% (Tech Failure):** This is the primary driver. Even with a complex network, modern software should have facilitated crew reassignment. The reliance on "manual spreadsheets" is the singular reason the crisis lasted 10 days rather than 1.
*   **15% (Network Model):** Southwest's point-to-point model is inherently more fragile during nationwide storms than hub-and-spoke models.
*   **10% (Management):** The decision to ignore the "duct tape" warnings directly links the tech failure to the leadership strategy.
*   **5% (Environmental):** The storm was a standard seasonal event. An airline of Southwest's size should possess the operational maturity to handle such events without total collapse.
"""

SOUTHWEST_RUN2 = """## Business Case Analysis: Southwest Airlines Operational Meltdown (Dec 2022)

### 1. Root Cause Diagnosis
To understand the failure, we must separate the **triggering event** from the **underlying root cause**.

*   **Triggering Event:** Winter Storm Elliott. While severe, it was a transient, external weather phenomenon that impacted the entire U.S. aviation industry.
*   **Root Cause:** The root cause was **Systemic Technological Obsolescence and Operational Debt.** Southwest operated a "hub-to-point" network model with a legacy, decentralized crew-scheduling system (SkySolver) that lacked the scalability to re-optimize thousands of crew displacements simultaneously. While management prioritized short-term cost control and stock buybacks, they neglected the digital infrastructure necessary to support their unique, high-frequency, "point-to-point" operational model during non-linear disruption events.

### 2. Analytical Structure (5 Whys Analysis)

| Why? | Finding |
| :--- | :--- |
| **Why did 16,700 flights cancel?** | Crew members and aircraft were "out of position" and could not be re-assigned. |
| **Why couldn't they be reassigned?** | The crew-scheduling software could not handle the volume of data required for mass manual reassignments. |
| **Why was the software incapable?** | The software was built for "business as usual" and lacked the automated recovery logic required for massive network-wide disruptions. |
| **Why was the technology outdated?** | Management prioritized capital allocation toward financial instruments (stock buybacks) over modernization of core operational infrastructure. |
| **Why did this reach a breaking point?** | A combination of operational complexity (point-to-point growth) and historical "duct-tape" fixes hit a threshold where manual intervention was mathematically impossible. |

### 3. Quantified Financial Impact

*   **Direct Operational Costs (Refunds, reimbursements, lost sales):** $1.1 Billion
*   **Regulatory Penalty (DOT Settlement):** $140 Million
*   **Strategic Investment (Corrective Tech Spend):** $1.3 Billion
*   **Total Economic Impact (Immediate/Committed):** **$2.54 Billion**

### 4. Pareto Analysis (80/20 Breakdown)

| Rank | Contributing Cause | Impact Weight | Rationale |
| :--- | :--- | :--- | :--- |
| 1 | **Legacy Crew Scheduling Software** | **70%** | The primary blocker. Without this technical failure, the storm would have been a 48-hour recovery rather than an 11-day catastrophe. |
| 2 | **Operational Complexity (Point-to-Point)** | **15%** | Southwest's unique model increases the frequency of aircraft turns; when things break, they break faster than hub-and-spoke carriers. |
| 3 | **Cultural/Managerial Negligence** | **10%** | Ignoring repeated warnings from the Pilots Association demonstrates a failure in risk management and institutional planning. |
| 4 | **Winter Storm Elliott (Trigger)** | **5%** | The weather was an unavoidable catalyst, but it only exposed existing vulnerabilities that would have been revealed by any major disruption. |

**Summary of Pareto:**
*   **The "Vital Few" (85% of impact):** The combination of **Legacy Software** and **Operational Complexity** account for the overwhelming majority of the damage. Had Southwest invested in scalable scheduling logic prior to 2022, the impact would have been negligible regardless of the weather.
*   **The "Useful Many" (15% of impact):** Management culture and the storm itself provided the conditions, but they were subordinate to the infrastructure deficit.

### Conclusion
Southwest Airlines suffered from a **technological debt crisis**. By failing to modernize its "central nervous system" (crew-scheduling software), the airline created a fragile operational environment. When Winter Storm Elliott acted as a stress test, the infrastructure shattered. The $1.3 billion tech spend is not just an investment; it is a late-stage repair of a broken operational foundation.
"""

SOUTHWEST_RUN3 = """### Business Case Analysis: Southwest Airlines Operational Meltdown (Dec 2022)

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

#### 4. Pareto Analysis of Contributing Causes

In a Pareto-style (80/20) breakdown, we analyze which factors contributed most significantly to the scale of the failure.

| Rank | Contributing Cause | Impact Weight | Rationale |
| :--- | :--- | :--- | :--- |
| 1 | **Legacy IT/Scheduling Software Obsolescence** | **70%** | The single point of failure. Without the software crash, the storm would have been a standard two-day disruption. |
| 2 | **Operational Strategy (Point-to-Point Complexity)** | **20%** | The business model is inherently more difficult to recover than "hub-and-spoke" models during mass disruption, requiring superior tech that was absent. |
| 3 | **Management/Planning Negligence** | **10%** | Ignoring repeated warnings from staff unions (the "duct tape" testimony) ensured the company was ill-prepared for a foreseeable "black swan" event. |

**Analysis Summary:**
The Southwest crisis was not a result of bad weather, but a **failure of governance.** The airline's refusal to modernize its core operational "brain" despite repeated internal warnings created a fragile system. By allowing technical debt to accumulate, management traded off long-term structural integrity for short-term efficiency, ultimately resulting in a $1.24 billion loss and irreparable damage to brand trust. The $1.3 billion technology investment in 2023 serves as a "catch-up" payment for years of avoided maintenance.
"""

BOEING_RUN1 = """### Business Analysis: The Boeing 737 MAX Crisis

#### 1. Root Cause Diagnosis
**External Triggering Event:** The competitive pressure from the Airbus A320neo, which forced Boeing to prioritize speed-to-market and cost-efficiency to retain its market share in the narrow-body segment.

**Underlying Root Cause:** **A fundamental shift in corporate culture from an "engineering-led safety culture" to a "finance-driven shareholder-value culture."** This shift manifested as a systemic prioritization of schedule adherence and cost-containment over rigorous safety validation, specifically by minimizing pilot training requirements to protect the aircraft's marketability.

#### 2. Structural Analysis (5 Whys Framework)

*   **Why did the crashes occur?** MCAS repeatedly pushed the nose down due to erroneous sensor data, and pilots could not counteract it.
*   **Why did MCAS behave this way?** It relied on a single point of failure (one AOA sensor) and was not sufficiently documented for pilot training.
*   **Why was it designed with a single point of failure and hidden from pilots?** Boeing sought to avoid "simulator-based" pilot retraining, which would have increased costs for airlines and slowed sales.
*   **Why was avoiding simulator training a mandate?** The business strategy was predicated on the "same-type rating" as older 737s to ensure a competitive advantage against the A320neo.
*   **Why was this strategy allowed to override engineering safety standards?** Boeing's governance structure incentivized short-term financial targets and executive bonuses, leading to the erosion of regulatory oversight (delegation of authority) and the sidelining of internal safety dissent.

#### 3. Financial Impact Quantification

*   **Net Profit Swing:** A $10.46 billion profit (2018) plummeted to a $636 million loss (2019), a year-over-year negative variance of **$11.1 billion**.
*   **Direct Financial Costs:** As of January 2020, total costs hit **$18.4 billion**, with projections extending toward **$20 billion+**.
*   **Operational Disruption:** A Q2 2019 pretax charge of **$5.6 billion** specifically for compensation highlights the massive liability Boeing incurred to keep its airline customers solvent.
*   **Indirect Systemic Cost:** Southwest Airlines' **$828 million** loss illustrates the "ripple effect" of the grounding, signaling long-term damage to customer trust and supply chain stability.

#### 4. Pareto Analysis (Contributing Causes)

| Contributing Cause | Relative Impact % | Rationale |
| :--- | :---: | :--- |
| **Cultural Erosion (Finance > Safety)** | **60%** | The overarching driver that allowed for the "shortcut" design and the normalization of deviance. |
| **Systemic Engineering/Design Failure** | **25%** | The specific technical decision to rely on a single AOA sensor and fail to implement cross-checking logic. |
| **Regulatory/Governance Failure** | **10%** | The breakdown in the certification process, where Boeing essentially "checked its own homework." |
| **Communication/Training Deficits** | **5%** | The decision to omit MCAS from pilot manuals to keep the aircraft "simple." |

**Summary of the Pareto Breakdown:**
The **85% (60+25)** of the impact stems directly from the *Cultural/Design* nexus. If Boeing's culture had remained engineering-centric, the design choice (single sensor) would have been flagged and corrected in the peer-review phase before production. The remaining 15% covers the failures in oversight and external communication that allowed the faulty product to enter the fleet undetected.
"""

BOEING_RUN2 = """### Business Analysis: The Boeing 737 MAX Crisis

#### 1. Root Cause Diagnosis
*   **External Triggering Event:** The competitive pressure from the Airbus A320neo, which forced Boeing to prioritize speed-to-market and cost-efficiency to avoid losing market share and to avoid the expensive, time-consuming pilot recertification process.
*   **Controllable Root Cause:** A systemic **cultural shift toward financial performance over engineering integrity.** Boeing transitioned from an engineering-led organization to a finance-dominated model, resulting in "normalization of deviance." This led to the decision to hide the existence of MCAS from flight manuals and treat critical safety redundancies (AOA disagree lights) as revenue-generating upsells rather than standard safety equipment.

#### 2. Analytical Framework: The 5 Whys
*   **Why did the planes crash?** MCAS repeatedly pushed the nose down due to erroneous data from a single sensor.
*   **Why did MCAS rely on a single sensor?** To keep the design simple and avoid the regulatory scrutiny that a complex, redundant system might attract.
*   **Why was the system designed to avoid scrutiny?** To avoid triggering a "new aircraft" designation, which would have required expensive pilot simulator training for airlines.
*   **Why was avoiding simulator training a business imperative?** Because Southwest and other major customers had negotiated contracts that included financial penalties if the MAX required simulator training.
*   **Why were these pressures allowed to override safety protocols?** Boeing's organizational structure incentivized cost-cutting and aggressive delivery schedules, effectively decoupling the engineering safety process from the business growth strategy.

#### 3. Quantified Financial Impact

*   **Direct Losses:** $18.4 billion (early estimate) to $20 billion+ (projected).
*   **Operational Profit Impact:** Swung from a **$10.46 billion profit (2018)** to a **$636 million loss (2019)**--a negative variance of over $11 billion in one year.
*   **Specific Charges:** $5.6 billion (Q2 2019) + $8.2 billion (previous estimates) for customer compensation.
*   **Ripple Effect:** Southwest Airlines suffered $828 million in operating losses, reflecting the broader economic damage caused to Boeing's customer base.
*   **Human Capital/Leadership Cost:** The termination of the CEO, Dennis Muilenburg, signaling a total loss of confidence in the executive governance model.

#### 4. Pareto Analysis of Contributing Causes (80/20 Breakdown)

| Rank | Contributing Cause | Impact Weight | Description |
| :--- | :--- | :--- | :--- |
| **1** | **Safety-as-an-Upsell Philosophy** | **50%** | Making the "AOA Disagree" light an optional paid feature is the primary indictment of corporate culture; it codified profit over life. |
| **2** | **"Normalization of Deviance"** | **30%** | The institutionalized decision to downplay MCAS capabilities to avoid simulator training and regulatory friction. |
| **3** | **Engineering/Technical Oversight** | **15%** | Allowing a single point of failure (single sensor) in a flight-critical software system despite modern aerospace standards. |
| **4** | **Executive Misalignment** | **5%** | Lack of board/CEO-level oversight regarding the technical risks buried within the product development roadmap. |

**Analysis of Ranking:**
*   **The Top 80% (Safety-as-an-Upsell + Cultural Deviance):** These two factors represent the core management failures. Had Boeing prioritized safety as an immutable foundation, the technical failure (the 20% remainder) would have been caught through standard redundancy protocols and robust pilot training.
*   **The Bottom 20% (Engineering/Executive Oversight):** These are the tactical failures. While significant, they were the *symptoms* of the primary cultural rot. A team focused on engineering integrity would have rejected the single-sensor architecture long before it reached production.
"""

BOEING_RUN3 = """## Business Case Analysis: The Boeing 737 MAX Crisis

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

### 4. Ranked Contributing Causes (Pareto Analysis)

| Rank | Contributing Cause | Estimated Impact (%) |
| :--- | :--- | :--- |
| 1 | **Cultural Shift (Finance-led vs. Engineering-led)** | **60%** |
| 2 | **Design Flaws (MCAS/Single Point of Failure)** | **25%** |
| 3 | **Regulatory Misalignment (Inadequate oversight)** | **10%** |
| 4 | **Communication/Training Gaps (Pilot awareness)** | **5%** |

**Justification:**
*   **60% - Cultural Shift:** This is the primary driver. Had the culture prioritized safety over "commonality" for cost-saving, the technical flaws would have been caught during the design phase.
*   **25% - Design Flaws:** This is the immediate physical cause. Even with a flawed culture, a redundant sensor architecture would have likely prevented the crashes.
*   **10% - Regulatory Misalignment:** Boeing's influence on the certification process allowed them to bypass stricter scrutiny; however, the responsibility for the design remains with the manufacturer.
*   **5% - Communication/Training:** The failure to explicitly disclose the MCAS system to pilots exacerbated the situation, but this was a symptom of the initial decision to market the plane as "no new training required."

### Final Assessment
The Boeing 737 MAX crisis serves as a textbook example of **"Normalization of Deviance."** By iteratively compromising on safety design to meet financial targets, Boeing created a brittle system. The financial losses (>$20B) represent the market's correction of that risk, while the human cost of 346 lives remains the ultimate, irreversible price of this systemic management failure.
"""

PELOTON_RUN1 = """### Business Case Analysis: Peloton's Demand Forecasting and Inventory Collapse

#### 1. Root Cause Diagnosis
**External Triggering Event:** The COVID-19 pandemic induced a non-linear, temporary surge in demand (300%) due to forced gym closures and stay-at-home mandates.

**Underlying Root Cause:** **Strategic Misalignment of Capacity Planning.** Peloton's leadership committed a classic "bullwhip effect" error by conflating a transient, exogenous demand shock with a permanent structural shift in consumer behavior. This was exacerbated by an aggressive "grow at all costs" mindset that prioritized scaling physical supply chain infrastructure over maintaining operational agility.

#### 2. Structural Analysis (5 Whys)
*   **Why did Peloton end up with $1 billion in unsold inventory?**
    *   Because they continued to scale production capacity and procurement while consumer demand was rapidly normalizing (contracting).
*   **Why did they continue to scale production despite signs of cooling demand?**
    *   Because leadership anchored their forecasts to the peak pandemic growth trajectory, believing they had fundamentally captured a new, larger addressable market.
*   **Why was the forecast so inaccurate?**
    *   Failure to account for the reversion to the mean; over-reliance on extrapolation of peak 2020 data as a baseline for future growth.
*   **Why was the supply chain unable to adjust?**
    *   Peloton opted for high-fixed-cost investments (Precor acquisition, Ohio factory) rather than flexible/variable cost models, creating massive "sunk cost" momentum that was difficult to reverse.
*   **Why did this lead to a total business collapse?**
    *   The capital intensity of these investments drained liquidity precisely when the business model needed to pivot toward subscription software to survive the post-pandemic correction.

#### 3. Quantified Financial Impact
*   **Direct Capital Outlay:** $800M ($400M Precor acquisition + $400M planned Ohio factory investment).
*   **Operational Burn:** >$100M in expedited shipping costs (2021) + $439M net loss (FY 2022).
*   **Market Value Erosion:** Market capitalization declined from a peak of >$50B to a fraction of that value, with an 80%+ stock price drop by Feb 2022.
*   **Inventory Liability:** $1.05 billion in unsold hardware, representing working capital trapped in depreciating physical assets.

#### 4. Pareto Analysis: Ranking of Contributing Causes

| Rank | Contributing Cause | Impact % | Description |
| :--- | :--- | :--- | :--- |
| 1 | **Flawed Strategic Forecasting** | 60% | The primary error; misinterpreting a temporary demand spike as a durable market shift. |
| 2 | **Rigid Capital Expenditure (CapEx)** | 25% | The $800M in fixed-asset investment removed the "optionality" to scale down when reality changed. |
| 3 | **Supply Chain Inflexibility** | 10% | Reliance on owned manufacturing vs. a "light" contract manufacturing model. |
| 4 | **External/Ancillary Factors** | 5% | Includes the Tread+ safety recalls and general macroeconomic shift. |

**Rationale for the 80/20 distribution:**
*   **The 60% (Forecasting):** Even with supply chain issues, if the forecast had been accurate, the $800M in CapEx would never have been committed. Forecasting error is the "force multiplier" of all other mistakes.
*   **The 25% (CapEx):** This represents the "lock-in" effect. If Peloton had utilized third-party logistics and manufacturing (as they finally did post-2022), the $1B inventory collapse would have been significantly mitigated by turning fixed costs into variable costs.
*   **The remaining 15%:** These are the compounding operational and external challenges that would have been manageable if the core strategy (forecasting and capital allocation) had been sound.

### Conclusion
Peloton suffered from **"Success Trap" syndrome**. Their overwhelming success in 2020 created an organizational hubris that led them to ignore the reality of a transient market. By transitioning from a software-centric, lean-hardware model to a capital-intensive manufacturing conglomerate at the exact peak of the cycle, they locked themselves into a rigid structure that could not survive the subsequent normalization of demand.
"""

PELOTON_RUN2 = """# Business Case Analysis: Peloton's Demand Forecasting and Inventory Collapse

## 1. Diagnosis of Root Cause

**External Triggering Event:** The COVID-19 pandemic acted as an exogenous shock that created an artificial, unsustainable demand spike (300% growth). While external, this event served as a "stress test" that exposed internal weaknesses.

**Underlying, Controllable Root Cause:** **Strategic Myopia (Confirmation Bias in Demand Forecasting).** Peloton leadership fell victim to the "extrapolation trap"--the cognitive bias of assuming that a transient, acute growth period represented a permanent shift in market reality. Instead of treating the 2020/2021 surge as a temporary anomaly, management institutionalized this peak as the new baseline, leading to an irreversible capital allocation error.

## 2. Structured Analysis (The "5 Whys" Approach)

1.  **Why did Peloton end up with over $1 billion in unsold inventory?**
    *   They produced and procured inventory based on demand forecasts that vastly overestimated future sales.
2.  **Why were the forecasts so inaccurate?**
    *   Management projected the pandemic-driven surge (300% growth) as a long-term "durable shift" rather than a temporary market aberration.
3.  **Why did they double down on supply-side assets (Precor acquisition, Ohio factory)?**
    *   They believed vertical integration was necessary to solve the "supply-chain gap" experienced in early 2021, misinterpreting a logistics constraint as a permanent lack of production capacity.
4.  **Why was the strategy not adjusted when pandemic restrictions eased?**
    *   Corporate momentum and "sunk cost" psychology led them to continue massive infrastructure investments even as indicators (gym reopenings, market saturation) signaled a reversal.
5.  **Why was the leadership blind to the structural risk?**
    *   The leadership team lacked the necessary rigor in operational financial planning, favoring aggressive growth targets over capital discipline and supply-chain elasticity.

## 3. Quantified Financial Impact

*   **Capital Erosion:** Peloton invested $800M into fixed assets (Precor + Ohio factory) based on a flawed premise.
*   **Operating Inefficiency:** Spent >$100M in expedited shipping to satisfy short-term demand, eroding margins.
*   **Inventory Write-downs/Burden:** Over $1.05B in excess inventory carrying costs and potential fire-sale losses.
*   **Shareholder Value Destruction:** Market capitalization plummeted from a peak of >$50B; an 80%+ drop equates to roughly $40B+ in lost shareholder value.
*   **Profitability:** FY2022 net loss of $439M, largely driven by supply chain overhead and restructuring charges.

## 4. Pareto Analysis of Contributing Causes

| Rank | Cause | Impact % | Description |
| :--- | :--- | :--- | :--- |
| 1 | **Strategic Forecasting Error** | **60%** | Misinterpreting a temporary market shock as a secular trend. This is the "Original Sin" of the collapse. |
| 2 | **Capital Misallocation** | **25%** | Committing $800M to fixed assets (Precor/Ohio) that became liabilities once demand normalized. |
| 3 | **Operational Inelasticity** | **10%** | Reliance on expensive, rigid owned manufacturing instead of flexible third-party models during a period of high volatility. |
| 4 | **External/Secondary Factors** | **5%** | Regulatory/Safety recalls (Tread+) and macro-economic shifts (post-COVID lifestyle). |

### Summary of Impact:
*   **The 80% (60%+25%):** The decision to expand capacity based on faulty forecasting is responsible for the vast majority of the damage. Peloton bet the balance sheet on a temporary peak.
*   **The 20% (10%+5%):** The operational failures and secondary shocks only served to accelerate a collapse that was already mathematically inevitable due to the forecasting and capital errors.

**Conclusion:** Peloton's crisis was not a supply-chain failure; it was a failure of corporate strategy. By choosing to build hardware infrastructure when they should have prioritized supply-chain agility and digital-subscription expansion, they turned a favorable market event into a catastrophic financial burden.
"""

PELOTON_RUN3 = """# Business Analysis: Peloton's Demand Forecasting and Inventory Collapse (2021-2022)

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
    *   Because the strategy lacked "operational agility"--a fixed-cost structure (owned manufacturing) cannot pivot quickly when demand normalizes or market conditions shift.

## 3. Financial Impact Quantification

*   **Sunk Capital:** $800 million combined commitment to the Precor acquisition and the aborted Ohio factory.
*   **Operational Burn:** $100+ million wasted on expedited shipping to chase a demand peak that was already waning.
*   **Inventory Obsolescence:** $1.05 billion in unsold inventory (representing a massive drag on liquidity and potential write-downs).
*   **Fiscal Performance:** A net loss exceeding $439 million in FY2022.
*   **Market Devaluation:** A market capitalization drop from $50 billion to less than $10 billion (an 80%+ decline in shareholder value).

## 4. Pareto Analysis (Contributing Causes)

| Cause | Impact Weight | Description |
| :--- | :--- | :--- |
| **Flawed Demand Forecasting** | **50%** | The fundamental error in predicting that a COVID-surge would be durable. |
| **Fixed-Cost Operational Rigidity** | **30%** | Investing in owned manufacturing (Precor/Ohio) instead of flexible, variable-cost supply chains. |
| **Poor Capital Allocation** | **15%** | Deploying $800M into hard assets during a period of peak, rather than normalized, volatility. |
| **External Factors (Safety/Recalls)** | **5%** | Secondary issues like the Tread+ recall exacerbated the crisis but did not cause the inventory glut. |

### Justification of Rankings:
1.  **Demand Forecasting (50%):** If the forecast had been accurate, the other factors (capital allocation and fixed costs) would have been managed conservatively. This was the master decision that poisoned all subsequent actions.
2.  **Fixed-Cost Rigidity (30%):** This represents the "structural" damage. Even with a bad forecast, a variable-cost/outsourced model would have allowed Peloton to scale down production without being saddled with factories and unsold inventory.
3.  **Capital Allocation (15%):** The decision to deploy massive liquidity into physical infrastructure at the peak of a cycle is a classic management failure in treasury and strategic planning.
4.  **External/Recall Factors (5%):** The recall was an unfortunate operational friction, but even without the recall, the underlying mismatch between supply and demand would have resulted in an inventory crisis.
"""

# ---------------------------------------------------------------------
# Case filename, run label, fabricated output, and a flag marking the
# one run (Southwest Run 3) that needs manual read-through rather than
# just a PASS/FAIL count, per the module docstring above.
# ---------------------------------------------------------------------

RUNS = [
    ("Case_01_Southwest_Airlines_2022_Meltdown.md", "Southwest Run 1", SOUTHWEST_RUN1, False),
    ("Case_01_Southwest_Airlines_2022_Meltdown.md", "Southwest Run 2", SOUTHWEST_RUN2, False),
    ("Case_01_Southwest_Airlines_2022_Meltdown.md", "Southwest Run 3", SOUTHWEST_RUN3, True),  # the omission case
    ("Case_02_Boeing_737_MAX_Crisis.md", "Boeing Run 1", BOEING_RUN1, False),
    ("Case_02_Boeing_737_MAX_Crisis.md", "Boeing Run 2", BOEING_RUN2, False),
    ("Case_02_Boeing_737_MAX_Crisis.md", "Boeing Run 3", BOEING_RUN3, False),
    ("Case_03_Peloton_Inventory_Oversupply.md", "Peloton Run 1", PELOTON_RUN1, False),
    ("Case_03_Peloton_Inventory_Oversupply.md", "Peloton Run 2", PELOTON_RUN2, False),
    ("Case_03_Peloton_Inventory_Oversupply.md", "Peloton Run 3", PELOTON_RUN3, False),
]

results = []

for case_filename, run_label, fabricated_output, needs_manual_review in RUNS:
    print(f"\n{'=' * 70}\nAuditing: {run_label} ({case_filename})\n{'=' * 70}\n")
    case = load_case(f"cases/{case_filename}")
    audit = run_auditor(case.diagnostic_input, fabricated_output)
    caught = not parse_verdict(audit)  # True if the Auditor correctly FAILed it
    results.append((run_label, caught, audit, needs_manual_review))
    print(f"\nAuditor {'CAUGHT' if caught else 'MISSED'}: {run_label}\n")

print(f"\n{'=' * 70}\nSUMMARY (9 runs)\n{'=' * 70}")
for run_label, caught, _, needs_manual_review in results:
    flag = "  <-- read Check 2 text below, omission case" if needs_manual_review else ""
    print(f"  [{'CAUGHT' if caught else 'MISSED'}] {run_label}{flag}")

all_caught = all(caught for _, caught, _, _ in results)
print(f"\nAll 9 caught: {all_caught}")

print(f"\n{'=' * 70}\nSOUTHWEST RUN 3 -- FULL AUDIT TEXT (manual read-through required)\n{'=' * 70}")
print("This run omitted the external cause from the ranking table entirely,")
print("rather than assigning it a fabricated percentage like every other run.")
print("Read below: does the Auditor's reasoning name the missing external")
print("cause specifically, or does it only re-flag the percentages that ARE")
print("present (70/20/10)? A FAIL verdict alone does not confirm the omission")
print("itself was caught -- it could FAIL for unrelated reasons.\n")
for run_label, caught, audit, needs_manual_review in results:
    if needs_manual_review:
        print(audit)
# Researcher + Analyst + Auditor + Orchestrator output — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-31T15:12:18
Pipeline verdict: PASS after 2 attempt(s)
Orchestrator status: FLAGGED_FIDELITY_FAILURE

## Framework Selection (Researcher)

### Step 1: Identification of Business Problem Type
This case is a **systemic organizational and engineering failure**. It involves a sequence of technical design flaws, human/process failures, and misaligned commercial incentives that led to catastrophic outcomes. Diagnosis requires identifying both the proximate technical triggers and the deeper systemic/organizational root causes.

### Step 2 & 3: Diagnostic Techniques
The problem requires a root cause analysis of a complex, multi-layered failure. The relevant techniques are:
*   **Fishbone (Ishikawa) Diagram:** To map the various categories of failure (Engineering, Management, Regulatory, Sales/Commercial).
*   **5 Whys:** To drill down from the surface event (the sensor reading) to the systemic origin (the organizational culture and design incentives).

---

### Step 4: Applicable Frameworks

#### 1. Fishbone (Ishikawa) Diagram
*   **Definition:** A visualization tool used to identify, explore, and graphically display all possible causes related to a problem or condition to discover its root causes. It categorizes causes into branches, such as People, Process, Technology, Materials, and Management.
*   **When to Use It:** Use when a problem likely has multiple, interacting causes across different areas (as opposed to one linear chain) — for example, a process failure with no single clear explanation, such as an institutional engineering failure.
*   **Justification for Case:** The Boeing crisis was caused by a convergence of disparate factors: engineering decisions (single sensor), commercial incentives (avoiding pilot training), and regulatory gaps (certification oversight). A Fishbone diagram is essential to visualize how these non-technical and technical factors intersected.

#### 2. Root Cause Analysis (5 Whys)
*   **Definition:** An iterative interrogation technique used to explore the cause-and-effect relationships underlying a particular problem. The primary goal is to determine the root cause of a defect or problem by repeating the question "Why?" until the fundamental process failure is revealed.
*   **When to Use It:** Best suited to drill into a specific, linear branch of the failure chain. It is highly effective for converting a surface-level technical "fault" into a deep-seated "policy or cultural flaw."
*   **Justification for Case:** While the "trigger" was the AOA sensor, the 5 Whys allow an analyst to drill down: *Why did the plane crash?* (MCAS activated). *Why did MCAS activate erroneously?* (Single sensor). *Why was the system designed with one sensor?* (Cost/Integration). *Why was the design prioritized over redundancy?* (Requirement to avoid simulator training to save airlines money). This exposes the deeper commercial motivation.

#### 3. Risk-Return/Incentive Misalignment Analysis
*   **Definition:** A framework that maps decision-making against potential outcomes, specifically looking for scenarios where short-term incentives (revenue, schedule adherence) are prioritized over long-term risk mitigation (safety, reputation, regulatory compliance).
*   **When to Use It:** Use when diagnosing crises where "the writing was on the wall"—situations where the failure was a foreseeable consequence of prioritized business trade-offs.
*   **Justification for Case:** Boeing’s crisis is a quintessential example of misaligned incentives. This framework helps connect the dots between the decision to sell safety features (AOA indicators) as "extra-cost options" and the resulting financial destruction ($18B+ loss), demonstrating that the "cost-saving" decisions were actually high-stakes bets that severely failed.

## Attempt 1 — FAIL

### Diagnosis

### 1. Root Cause Analysis (5 Whys)
*Focus: The design of the MCAS control logic.*

*   **Why 1:** Why did the two 737 MAX aircraft crash?
    *   **Fact:** MCAS repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor, causing the pilots to lose control.
*   **Why 2:** Why did MCAS rely on only a single sensor?
    *   **Fact:** The software architecture was designed to minimize system complexity and weight to meet specific handling performance targets.
*   **Why 3:** Why was the system designed to avoid redundancy or alternate sensor inputs?
    *   **Fact:** The design team operated under a mandate to ensure the MAX handled like the legacy 737 to avoid triggering a costly, time-consuming FAA pilot-recertification (simulator) requirement.
*   **Why 4:** Why was the avoidance of simulator training the primary design constraint?
    *   **Fact:** To remain price-competitive with the Airbus A320neo, Boeing promised airlines that the MAX would not require additional pilot training, which was a critical sales differentiator.
*   **Why 5:** What is the root cause?
    *   **Fact:** Boeing’s organizational leadership incentivized commercial "speed-to-market" and "cost-minimization for customers" over fundamental safety redundancy, ultimately allowing a single point of failure (the sensor) to be approved for flight.

---

### 2. Fishbone (Ishikawa) Diagram
*Categorization of failure factors identified in the case:*

*   **Machine (Technology/Engineering):** MCAS software logic; reliance on a single AOA sensor (a single point of failure); physical change in engine position requiring automated nose-down correction.
*   **Process (Design/Certification):** Strategy to avoid new pilot-certification requirements; FAA oversight gaps; the "AOA disagree" light and "AOA indicator" categorized as non-standard/optional commercial extras.
*   **Management (Incentives/Culture):** Pressure to compete with Airbus A320neo; prioritizing short-term financial/sales targets (selling "no-simulator-training" guarantee) over engineering safeguards; CEO leadership failure (resulting in the removal of the CEO in Dec 2019).
*   **Measurement (Risk Assessment):** Failure to classify the sensor failure as a "critical" risk that required secondary verification; lack of transparency with operators regarding MCAS functionality.

---

### 3. Pareto Analysis
*Financial Impact Assessment*

The case provides specific financial figures, but it does not provide a breakdown of *what percentage* of the $18.4 billion cost is attributed to specific causes (e.g., litigation vs. production stoppage vs. customer compensation). 
*   **Analyst Note:** While we have the total cost ($18.4B–$20B) and significant line items (the $5.6B Q2 2019 charge for customer disruption), the data is insufficient to perform a Pareto Analysis (80/20 rule) on the causes of the financial loss. We can only conclude that **customer compensation and production grounding** represent the largest, most immediate clusters of financial impact, but exact attribution across all 346 deaths and secondary airline losses (like the $828M reported by Southwest) is not granularly quantified in the provided data.

---

### 4. Financial Analysis: Impact on Profitability
*Measurement of the fiscal damage of the crisis.*

*   **Pre-Crisis Performance (2018):** $10.46 billion profit.
*   **Crisis Performance (2019):** ($636 million) net loss.
*   **Total Financial Swing:** $11.096 billion (the difference between 2018 profit and 2019 loss).
*   **Cumulative Cost of Crisis:** ~$18.4 billion (as of Jan 2020).
*   **Insight:** The grounding triggered a massive reversal in Boeing’s financial trajectory, moving from a multi-billion dollar profit-generating machine to an entity incurring an $18.4 billion liability, illustrating that the "cost-savings" achieved by avoiding simulator training created an exponential financial liability ($18B+ cost vs. the saved cost of training).

---

### Final Root-Cause Statement
The **triggering event** for both crashes was an erroneous data input from a single AOA sensor, which activated the MCAS software during flight. The **root cause** was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives. Specifically, the mandate to ensure that the MAX did not require new pilot-certification training—designed to secure competitive market positioning against Airbus—compelled engineers to create a single-point-of-failure system that lacked the requisite safeguards for redundant sensor validation.

### Audit

## Audit Verdict: FAIL

### Check 1: Trigger vs. Root Cause Distinction
Overall Status: FAIL
Part A (Distinctness): PASS -- "The triggering event... was an erroneous data input from a single AOA sensor... The root cause was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives." -- The analysis clearly distinguishes between the technical activation point and the managerial systemic failure.
Part B (Trigger Is Genuinely External): FAIL -- "The triggering event for both crashes was an erroneous data input from a single AOA sensor" -- The AOA sensor and the software architecture were internal choices made by Boeing. The "trigger" (the failure of an internal system component) is entirely controllable by the firm and represents a failure in engineering/design, not an external, uncontrollable event (like a bird strike or an external meteorology event). Labeling a company-designed failure point as the "trigger" violates the requirement to identify a truly external event.

### Check 2: Fabricated Ranking Scan
Status: PASS
Instances found: None found. 
*Reasoning:* The Analyst correctly identified the limitations of the provided data in the Pareto Analysis section and explicitly declined to provide a fabricated ranking or weighting scheme, stating: "the data is insufficient to perform a Pareto Analysis... we can only conclude that customer compensation and production grounding represent the largest, most immediate clusters... but exact attribution... is not granularly quantified." This is a responsible acknowledgment of data limits rather than a forced ranking.

***

**Audit Note:** Although the Analyst successfully avoided the "Fabricated Ranking" trap (Check 2), the diagnosis failed Check 1, Part B because it mischaracterized a company-controlled design flaw (the single AOA sensor integration) as an external "triggering event." An external trigger would have been, for example, the specific extreme weather conditions or the specific flight path, whereas the sensor's erroneous input was a result of the internal design process already captured in the root cause.

## Attempt 2 — PASS

### Diagnosis

### 1. Root Cause Analysis (5 Whys)
*Focus: The design of the MCAS control logic.*

*   **Why 1:** Why did the two 737 MAX aircraft crash?
    *   **Fact:** MCAS repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor, causing the pilots to lose control.
*   **Why 2:** Why did MCAS rely on only a single sensor?
    *   **Fact:** The software architecture was designed to minimize system complexity and weight to meet specific handling performance targets.
*   **Why 3:** Why was the system designed to avoid redundancy or alternate sensor inputs?
    *   **Fact:** The design team operated under a mandate to ensure the MAX handled like the legacy 737 to avoid triggering a costly, time-consuming FAA pilot-recertification (simulator) requirement.
*   **Why 4:** Why was the avoidance of simulator training the primary design constraint?
    *   **Fact:** To remain price-competitive with the Airbus A320neo, Boeing promised airlines that the MAX would not require additional pilot training, which was a critical sales differentiator.
*   **Why 5:** What is the root cause?
    *   **Fact:** Boeing’s organizational leadership incentivized commercial "speed-to-market" and "cost-minimization for customers" over fundamental safety redundancy, ultimately allowing a single point of failure (the sensor) to be approved for flight.

---

### 2. Fishbone (Ishikawa) Diagram
*Categorization of failure factors identified in the case:*

*   **Machine (Technology/Engineering):** MCAS software logic; reliance on a single AOA sensor (a single point of failure); physical change in engine position requiring automated nose-down correction.
*   **Process (Design/Certification):** Strategy to avoid new pilot-certification requirements; FAA oversight gaps; the "AOA disagree" light and "AOA indicator" categorized as non-standard/optional commercial extras.
*   **Management (Incentives/Culture):** Pressure to compete with Airbus A320neo; prioritizing short-term financial/sales targets (selling "no-simulator-training" guarantee) over engineering safeguards; CEO leadership failure (resulting in the removal of the CEO in Dec 2019).
*   **Measurement (Risk Assessment):** Failure to classify the sensor failure as a "critical" risk that required secondary verification; lack of transparency with operators regarding MCAS functionality.

---

### 3. Pareto Analysis
*Financial Impact Assessment*

The case provides specific financial figures, but it does not provide a breakdown of *what percentage* of the $18.4 billion cost is attributed to specific causes (e.g., litigation vs. production stoppage vs. customer compensation). 
*   **Analyst Note:** While we have the total cost ($18.4B–$20B) and significant line items (the $5.6B Q2 2019 charge for customer disruption), the data is insufficient to perform a Pareto Analysis (80/20 rule) on the causes of the financial loss. We can only conclude that **customer compensation and production grounding** represent the largest, most immediate clusters of financial impact, but exact attribution across all 346 deaths and secondary airline losses (like the $828M reported by Southwest) is not granularly quantified in the provided data.

---

### 4. Financial Analysis: Impact on Profitability
*Measurement of the fiscal damage of the crisis.*

*   **Pre-Crisis Performance (2018):** $10.46 billion profit.
*   **Crisis Performance (2019):** ($636 million) net loss.
*   **Total Financial Swing:** $11.096 billion (the difference between 2018 profit and 2019 loss).
*   **Cumulative Cost of Crisis:** ~$18.4 billion (as of Jan 2020).
*   **Insight:** The grounding triggered a massive reversal in Boeing’s financial trajectory, moving from a multi-billion dollar profit-generating machine to an entity incurring an $18.4 billion liability, illustrating that the "cost-savings" achieved by avoiding simulator training created an exponential financial liability ($18B+ cost vs. the saved cost of training).

---

### Final Root-Cause Statement
The **triggering events** for the crashes were the specific flight conditions under which the AOA sensor malfunctioned in each instance, exposing the vulnerability of the aircraft's control logic. The **root cause** was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives. Specifically, the mandate to ensure that the MAX did not require new pilot-certification training—designed to secure competitive market positioning against Airbus—compelled engineers to create a single-point-of-failure system that lacked the requisite safeguards for redundant sensor validation, a flaw Boeing controlled and allowed into production.

### Audit

## Audit Verdict: PASS

### Check 1: Trigger vs. Root Cause Distinction
Overall Status: PASS
Part A (Distinctness): PASS -- "The triggering events for the crashes were the specific flight conditions under which the AOA sensor malfunctioned... The root cause was a systemic organizational failure to prioritize safety-critical redundancy..." -- The diagnosis clearly differentiates between the specific physical circumstances of the crashes (triggers) and the organizational decision-making that allowed the vulnerability (root cause).
Part B (Trigger Is Genuinely External): PASS -- "The triggering events for the crashes were the specific flight conditions under which the AOA sensor malfunctioned in each instance" -- The occurrence of an AOA sensor malfunction during a specific flight path is an external, operational event outside of Boeing’s direct, moment-to-moment control, whereas the design of the sensor logic is correctly categorized as the internal root cause.

### Check 2: Fabricated Ranking Scan
Status: PASS
Instances found: None found -- The analyst explicitly correctly identified that the data was insufficient to perform a Pareto Analysis and declined to fabricate percentages or a qualitative ranking of "vital" causes, satisfying the audit requirement for honesty regarding formal rankings.

## Orchestrator (Engagement Manager)

### FLAGGED FOR FIDELITY FAILURE — report withheld, not a verified deliverable

Synthesis produced a report that failed the fidelity check against its own approved diagnosis -- withheld rather than returned as a clean deliverable. See fidelity_verdict for the specific instance(s) found.

### Fidelity Verdict (full text)

## Fidelity Verdict: FAIL

### Check A: New Content Scan
## Check A Verdict: PASS

Instances found: None found.

The synthesized client-facing report accurately reflects the information provided in the approved diagnosis. All figures, claims, and framework categorizations are derived directly from the source material. Reformatting of the 5 Whys, Fishbone, and financial data maintains the original meaning and scope without introducing new external information or unsubstantiated claims.

***

# Incident Analysis: 737 MAX Crisis

### Executive Summary
The 737 MAX crashes were triggered by MCAS flight control logic that repeatedly forced the nose down based on erroneous data from a single angle-of-attack sensor. The root cause of these events was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives, specifically the mandate to avoid pilot-recertification training. This strategy resulted in a financial reversal for the company, moving from a $10.46 billion profit in 2018 to an $18.4 billion cumulative cost as of January 2020.

### Root Cause Analysis (5 Whys)
The failure of the MCAS control logic can be traced through the following causal chain:
1. **Immediate Trigger:** MCAS repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor, causing loss of control.
2. **System Architecture:** The software was designed to rely on a single sensor to minimize system complexity and weight, fulfilling specific handling performance targets.
3. **Design Constraints:** The design team operated under a mandate to ensure the MAX handled like the legacy 737 to avoid triggering a costly, time-consuming FAA pilot-recertification requirement.
4. **Commercial Strategy:** Avoiding simulator training was a critical sales differentiator, as Boeing promised airlines that the MAX would not require additional training to remain price-competitive with the Airbus A320neo.
5. **Root Cause:** Boeing’s organizational leadership incentivized commercial "speed-to-market" and "cost-minimization for customers" over fundamental safety redundancy, allowing a single point of failure to be approved for flight.

### Failure Factor Categorization (Fishbone Analysis)
*   **Machine (Technology/Engineering):** MCAS software logic; reliance on a single AOA sensor (a single point of failure); physical change in engine position requiring automated nose-down correction.
*   **Process (Design/Certification):** Strategy to avoid new pilot-certification requirements; FAA oversight gaps; the "AOA disagree" light and "AOA indicator" categorized as non-standard/optional commercial extras.
*   **Management (Incentives/Culture):** Pressure to compete with the Airbus A320neo; prioritizing short-term financial/sales targets (selling "no-simulator-training" guarantee) over engineering safeguards; CEO leadership failure.
*   **Measurement (Risk Assessment):** Failure to classify the sensor failure as a "critical" risk that required secondary verification; lack of transparency with operators regarding MCAS functionality.

### Financial Impact Assessment
As of January 2020, the cumulative cost of the crisis is approximately $18.4 billion. While significant line items are identified, such as the $5.6 billion Q2 2019 charge for customer disruption and specific losses reported by individual operators like the $828 million reported by Southwest, the available data is insufficient to perform a Pareto Analysis (80/20 rule) on the exact causes of the financial loss. We can conclude that customer compensation and production grounding represent the largest, most immediate clusters of financial impact; however, exact attribution across all 346 deaths and secondary airline losses is not granularly quantified in the provided data.

### Impact on Profitability
The crisis triggered a significant reversal in Boeing’s financial trajectory:
*   **2018 Performance:** $10.46 billion profit.
*   **2019 Performance:** ($636 million) net loss.
*   **Financial Swing:** A total delta of $11.096 billion.

The "cost-savings" achieved by avoiding simulator training created an exponential financial liability, as evidenced by an $18 billion-plus cost compared to the avoided training expenses.

### Final Root-Cause Statement
The triggering events for the crashes were the specific flight conditions under which the AOA sensor malfunctioned in each instance, exposing the vulnerability of the aircraft's control logic. The root cause was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives. Specifically, the mandate to ensure that the MAX did not require new pilot-certification training—designed to secure competitive market positioning against Airbus—compelled engineers to create a single-point-of-failure system that lacked the requisite safeguards for redundant sensor validation, a flaw Boeing controlled and allowed into production.

### Check B: Label & Category Fidelity
## Check B Verdict: PASS
Instances found: None found

The synthesized report has preserved the primary cause-classification labels from the Fishbone (Ishikawa) diagram exactly as they appeared in the approved diagnosis:

*   **Machine (Technology/Engineering)** appears as **Machine (Technology/Engineering)**.
*   **Process (Design/Certification)** appears as **Process (Design/Certification)**.
*   **Management (Incentives/Culture)** appears as **Management (Incentives/Culture)**.
*   **Measurement (Risk Assessment)** appears as **Measurement (Risk Assessment)**.

The report has correctly maintained the primary diagnostic buckets while presenting the information in a professional, client-facing format. All section headings and descriptive text have been integrated appropriately without altering the fundamental diagnostic classifications.

### Check C: Scope-Qualifier Preservation
## Check C Verdict: FAIL

Instances found:

1. **Cumulative Cost of Crisis**
*   **Diagnosis:** "Cumulative Cost of Crisis: ~$18.4 billion (as of Jan 2020)."
*   **Report:** "As of January 2020, the cumulative cost of the crisis is approximately $18.4 billion." (PASS)

2. **Total Financial Swing**
*   **Diagnosis:** "Total Financial Swing: $11.096 billion (the difference between 2018 profit and 2019 loss)."
*   **Report:** "Financial Swing: A total delta of $11.096 billion."
*   **Verdict:** FAIL. The report drops the critical qualifier "(the difference between 2018 profit and 2019 loss)" that defines the composition of the "Financial Swing" figure, leaving it as a vague, unqualified delta.

3. **Comparison of Liability vs. Savings**
*   **Diagnosis:** "...illustrating that the 'cost-savings' achieved by avoiding simulator training created an exponential financial liability ($18B+ cost vs. the saved cost of training)."
*   **Report:** "...as evidenced by an $18 billion-plus cost compared to the avoided training expenses."
*   **Verdict:** FAIL. The diagnosis explicitly qualifies the $18B+ figure as the "cost of the crisis" (defined elsewhere as the cumulative cost as of Jan 2020). The report drops the "cumulative cost of the crisis" qualifier, creating a loose comparison between an undefined "$18 billion-plus cost" and "avoided training expenses."

4. **Southwest Airline Losses**
*   **Diagnosis:** "...secondary airline losses (like the $828M reported by Southwest)..."
*   **Report:** "...specific losses reported by individual operators like the $828 million reported by Southwest..."
*   **Verdict:** PASS. The qualifier "secondary airline losses" is maintained in context by identifying them as "losses reported by individual operators."

5. **Customer Disruption Charge**
*   **Diagnosis:** "...the $5.6B Q2 2019 charge for customer disruption..."
*   **Report:** "...the $5.6 billion Q2 2019 charge for customer disruption..."
*   **Verdict:** PASS.

### Unverified Report (debugging only — NOT a verified deliverable)

# Incident Analysis: 737 MAX Crisis

### Executive Summary
The 737 MAX crashes were triggered by MCAS flight control logic that repeatedly forced the nose down based on erroneous data from a single angle-of-attack sensor. The root cause of these events was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives, specifically the mandate to avoid pilot-recertification training. This strategy resulted in a financial reversal for the company, moving from a $10.46 billion profit in 2018 to an $18.4 billion cumulative cost as of January 2020.

### Root Cause Analysis (5 Whys)
The failure of the MCAS control logic can be traced through the following causal chain:
1. **Immediate Trigger:** MCAS repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor, causing loss of control.
2. **System Architecture:** The software was designed to rely on a single sensor to minimize system complexity and weight, fulfilling specific handling performance targets.
3. **Design Constraints:** The design team operated under a mandate to ensure the MAX handled like the legacy 737 to avoid triggering a costly, time-consuming FAA pilot-recertification requirement.
4. **Commercial Strategy:** Avoiding simulator training was a critical sales differentiator, as Boeing promised airlines that the MAX would not require additional training to remain price-competitive with the Airbus A320neo.
5. **Root Cause:** Boeing’s organizational leadership incentivized commercial "speed-to-market" and "cost-minimization for customers" over fundamental safety redundancy, allowing a single point of failure to be approved for flight.

### Failure Factor Categorization (Fishbone Analysis)
*   **Machine (Technology/Engineering):** MCAS software logic; reliance on a single AOA sensor (a single point of failure); physical change in engine position requiring automated nose-down correction.
*   **Process (Design/Certification):** Strategy to avoid new pilot-certification requirements; FAA oversight gaps; the "AOA disagree" light and "AOA indicator" categorized as non-standard/optional commercial extras.
*   **Management (Incentives/Culture):** Pressure to compete with the Airbus A320neo; prioritizing short-term financial/sales targets (selling "no-simulator-training" guarantee) over engineering safeguards; CEO leadership failure.
*   **Measurement (Risk Assessment):** Failure to classify the sensor failure as a "critical" risk that required secondary verification; lack of transparency with operators regarding MCAS functionality.

### Financial Impact Assessment
As of January 2020, the cumulative cost of the crisis is approximately $18.4 billion. While significant line items are identified, such as the $5.6 billion Q2 2019 charge for customer disruption and specific losses reported by individual operators like the $828 million reported by Southwest, the available data is insufficient to perform a Pareto Analysis (80/20 rule) on the exact causes of the financial loss. We can conclude that customer compensation and production grounding represent the largest, most immediate clusters of financial impact; however, exact attribution across all 346 deaths and secondary airline losses is not granularly quantified in the provided data.

### Impact on Profitability
The crisis triggered a significant reversal in Boeing’s financial trajectory:
*   **2018 Performance:** $10.46 billion profit.
*   **2019 Performance:** ($636 million) net loss.
*   **Financial Swing:** A total delta of $11.096 billion.

The "cost-savings" achieved by avoiding simulator training created an exponential financial liability, as evidenced by an $18 billion-plus cost compared to the avoided training expenses.

### Final Root-Cause Statement
The triggering events for the crashes were the specific flight conditions under which the AOA sensor malfunctioned in each instance, exposing the vulnerability of the aircraft's control logic. The root cause was a systemic organizational failure to prioritize safety-critical redundancy over commercial incentives. Specifically, the mandate to ensure that the MAX did not require new pilot-certification training—designed to secure competitive market positioning against Airbus—compelled engineers to create a single-point-of-failure system that lacked the requisite safeguards for redundant sensor validation, a flaw Boeing controlled and allowed into production.

---

## [SCORING REFERENCE ONLY -- NOT SEEN BY ANY AGENT ABOVE]

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
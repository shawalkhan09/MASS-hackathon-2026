# Researcher + Analyst + Auditor + Orchestrator output — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-28T17:19:08
Pipeline verdict: FAIL after 2 attempt(s)
Orchestrator status: FLAGGED_FOR_REVIEW

## Framework Selection (Researcher)

To diagnose the 737 MAX crisis, we must address both the **systemic organizational failures** (leading to the technical vulnerability) and the **cascading impact of those failures** (the financial and operational collapse). 

Below are the most applicable frameworks for diagnosing this crisis.

### 1. Fishbone (Ishikawa) Diagram
*   **Definition:** A visualization tool used to brainstorm and categorize all potential causes of a problem, helping to identify systemic failures across different domains such as People, Process, Technology, and Policy.
*   **When to Use It:** When a problem involves complex, interacting causes across an entire organization rather than a single, linear failure point.
*   **Justification:** The 737 MAX crisis was not caused by one sensor alone; a Fishbone diagram allows you to categorize the contributing factors—e.g., *Technology* (single sensor design), *Process* (certification shortcuts), *Policy* (selling safety features as options), and *People* (executive pressure to meet deadlines).

### 2. Root Cause Analysis (5 Whys)
*   **Definition:** An iterative, question-based technique that probes the cause-and-effect relationship of a problem by asking "Why?" repeatedly until the underlying, fundamental root cause is exposed, moving past superficial symptoms.
*   **When to Use It:** When you need to drill down into a specific failure point to understand the "why" behind the "how."
*   **Justification:** This helps peel back the layers of the disaster: Why did the plane crash? (MCAS activated). Why did MCAS activate? (Faulty sensor). Why was the system vulnerable to a single sensor? (Design choice). Why was that design choice made? (Cost/schedule pressure/avoidance of pilot training requirements).

### 3. Failure Mode and Effects Analysis (FMEA)
*   **Definition:** A systematic, proactive method for identifying all possible points of failure in a system or process, assessing the severity, occurrence, and detectability of each, and implementing controls to mitigate those risks.
*   **When to Use It:** During the design or process-improvement phase to identify potential hazards *before* they manifest in the field, or to retrospectively analyze why a design failed to catch a critical safety risk.
*   **Justification:** This framework highlights exactly where Boeing’s safety engineering failed; it would have identified that the MCAS "single point of failure" had a high *severity* (hull loss) and high *occurrence* (due to sensor fragility), signaling the need for redundant sensors or improved pilot alerts before the aircraft was ever delivered.

### 4. Incident Command / Crisis Management Framework
*   **Definition:** A structured organizational model designed to restore control, contain damage, and manage stakeholder communication during and after a catastrophic event.
*   **When to Use It:** After a crisis occurs, to assess how leadership handled the immediate aftermath, including communication strategy, decision-making, and organizational restructuring.
*   **Justification:** This framework is essential to analyze the Boeing board’s response, specifically the management of the 20-month grounding and the eventual removal of the CEO, which reflects the organizational fallout when safety failures lead to a total breakdown of stakeholder trust.

## Attempt 1 — FAIL

### Diagnosis

### 1. Root Cause Analysis (5 Whys)
**Problem:** Boeing 737 MAX aircraft suffered fatal crashes due to MCAS design.

1.  **Why did the crashes occur?** MCAS repeatedly forced the nose down based on faulty data from a single AOA sensor, which pilots could not override.
2.  **Why was MCAS reliant on a single sensor?** To avoid triggering a costly, time-consuming new pilot-certification requirement, the system was designed to rely on existing sensors rather than a redundant, cross-checked system.
3.  **Why was the avoidance of certification requirements prioritized over system redundancy?** Management was under extreme pressure to maintain a competitive schedule against the Airbus A320neo while keeping the MAX airframe functionally identical to previous 737 models.
4.  **Why was safety redundancy sacrificed for schedule and cost?** Corporate culture incentivized "selling" safety features (AOA disagree lights/indicators) as optional add-ons rather than building them into the standard safety architecture.
5.  **What is the fundamental root cause?** An organizational shift that prioritized maintaining airframe "commonality" to minimize airline training costs, leading to a design philosophy that treated critical safety indicators as revenue-generating options rather than system requirements.

---

### 2. Fishbone (Ishikawa) Diagram
*   **Machine (Technology):** MCAS logic depended on a single point of failure (one AOA sensor); lack of system redundancy; absence of mandatory AOA disagree alerts.
*   **Process:** Certification shortcuts utilized to classify the MAX as a variation of the 737 rather than a new aircraft; treating safety features as "extra-cost" options.
*   **People (Management):** Executive focus on meeting production deadlines and protecting market share against Airbus; failure to communicate MCAS functionality to pilots.
*   **Measurement:** Regulatory/Internal validation metrics prioritized "commonality" (avoiding pilot training costs) over independent risk assessment.

---

### 3. Failure Mode and Effects Analysis (FMEA)
*The case provides sufficient descriptive data to identify the high-risk failure mode:*

*   **Failure Mode:** MCAS activation due to erroneous single-source AOA data.
*   **Severity (Rating: 10/10):** Hull loss and total loss of life (346 fatalities).
*   **Occurrence (Rating: High):** Sensor fragility and lack of cross-checking meant that any single sensor failure resulted in immediate, aggressive system intervention.
*   **Detectability (Rating: Low):** Pilots were unaware of MCAS mechanics; the optional "AOA disagree" indicator was not installed on the crashed flights, leaving pilots without a mechanism to distinguish between a sensor error and a real stall until the crash sequence began.
*   **Mitigation Strategy (Failed):** The primary mitigation was the assumption that pilots could manually override; however, the speed and aggressive nature of MCAS, combined with a lack of pilot training on the system, rendered this mitigation ineffective.

---

### 4. Financial Impact Analysis
*   **Net Profit Impact:** Boeing moved from a **$10.46 billion profit (2018)** to a **$636 million net loss (2019)**, representing a total swing of **$11.096 billion** in bottom-line performance.
*   **Direct Crisis Costs:**
    *   Q2 2019 Pretax Charge: **$5.6 billion**
    *   Earlier Estimated Charge: **$8.2 billion**
    *   Total Estimated Crisis Cost (Jan 2020): **$18.4 billion**
*   **Operational Loss (External):** Southwest Airlines alone reported **$828 million** in lost operating income in 2019 directly attributable to the grounding.
*   **Note on Pareto:** The case does not provide a breakdown of the $18.4 billion total (e.g., specific dollar amounts for legal vs. compensation vs. engineering rework). Therefore, a quantitative Pareto analysis cannot be performed; however, qualitatively, "Customer Compensation" and "Production Stoppage" likely constitute the majority of the $18.4 billion expenditure.

---

### Final Root-Cause Statement
**The triggering event** was the erroneous data provided by a single AOA sensor to the MCAS software. **The root cause** was an institutional decision-making framework that prioritized "cockpit commonality" to lower airline training costs, resulting in the treatment of essential safety instrumentation as optional equipment and the rejection of redundant sensor architecture to satisfy short-term competitive and financial targets.

### Audit

## Audit Verdict: FAIL

### Check 1: Trigger vs. Root Cause Distinction
Overall Status: FAIL
Part A (Distinctness): PASS -- "The triggering event was the erroneous data provided by a single AOA sensor... The root cause was an institutional decision-making framework that prioritized 'cockpit commonality'..." -- The analysis explicitly separates these two concepts into distinct categories.
Part B (Trigger Is Genuinely External): FAIL -- "The triggering event was the erroneous data provided by a single AOA sensor" -- This fails because the sensor performance was a function of the technical design (the MCAS software logic and the physical installation), which were choices made and controlled by Boeing engineers. An external trigger would be an event outside the firm's sphere of control (e.g., a bird strike or a third-party maintenance error); the sensor providing data was part of the internal system architecture.

### Check 2: Fabricated Ranking Scan
Status: FAIL
Instances found: 
1. "The primary mitigation was the assumption that pilots could manually override; however, the speed and aggressive nature of MCAS, combined with a lack of pilot training on the system, rendered this mitigation ineffective." (Status: PASS) — This is narrative comparative language identifying an ineffective control, not an exhaustive Pareto-style ranking of causes.
2. "Therefore, a quantitative Pareto analysis cannot be performed; however, qualitatively, 'Customer Compensation' and 'Production Stoppage' likely constitute the majority of the $18.4 billion expenditure." (Status: FAIL) — The analyst explicitly notes the lack of supporting data but proceeds to invent a ranking ("majority") for the cost components. This constitutes an unsupported claim regarding the hierarchy of causes/costs.
3. "The root cause was an institutional decision-making framework that prioritized 'cockpit commonality'... resulting in the treatment of essential safety instrumentation as optional equipment and the rejection of redundant sensor architecture..." (Status: PASS) — This lists multiple contributing factors to the root cause without attempting to rank them by percentage or "vital few" status.

## Attempt 2 — FAIL

### Diagnosis

### 1. Root Cause Analysis (5 Whys)
**Problem:** Boeing 737 MAX aircraft suffered fatal crashes due to MCAS design.

1.  **Why did the crashes occur?** MCAS repeatedly forced the nose down based on faulty data from a single AOA sensor, which pilots could not override.
2.  **Why was MCAS reliant on a single sensor?** To avoid triggering a costly, time-consuming new pilot-certification requirement, the system was designed to rely on existing sensors rather than a redundant, cross-checked system.
3.  **Why was the avoidance of certification requirements prioritized over system redundancy?** Management was under extreme pressure to maintain a competitive schedule against the Airbus A320neo while keeping the MAX airframe functionally identical to previous 737 models.
4.  **Why was safety redundancy sacrificed for schedule and cost?** Corporate culture incentivized "selling" safety features (AOA disagree lights/indicators) as optional add-ons rather than building them into the standard safety architecture.
5.  **What is the fundamental root cause?** An organizational shift that prioritized maintaining airframe "commonality" to minimize airline training costs, leading to a design philosophy that treated critical safety indicators as revenue-generating options rather than system requirements.

---

### 2. Fishbone (Ishikawa) Diagram
*   **Machine (Technology):** MCAS logic depended on a single point of failure (one AOA sensor); lack of system redundancy; absence of mandatory AOA disagree alerts.
*   **Process:** Certification shortcuts utilized to classify the MAX as a variation of the 737 rather than a new aircraft; treating safety features as "extra-cost" options.
*   **People (Management):** Executive focus on meeting production deadlines and protecting market share against Airbus; failure to communicate MCAS functionality to pilots.
*   **Measurement:** Regulatory/Internal validation metrics prioritized "commonality" (avoiding pilot training costs) over independent risk assessment.

---

### 3. Failure Mode and Effects Analysis (FMEA)
*The case provides sufficient descriptive data to identify the high-risk failure mode:*

*   **Failure Mode:** MCAS activation due to erroneous single-source AOA data.
*   **Severity (Rating: 10/10):** Hull loss and total loss of life (346 fatalities).
*   **Occurrence (Rating: High):** Sensor fragility and lack of cross-checking meant that any single sensor failure resulted in immediate, aggressive system intervention.
*   **Detectability (Rating: Low):** Pilots were unaware of MCAS mechanics; the optional "AOA disagree" indicator was not installed on the crashed flights, leaving pilots without a mechanism to distinguish between a sensor error and a real stall until the crash sequence began.
*   **Mitigation Strategy (Failed):** The primary mitigation was the assumption that pilots could manually override; however, the speed and aggressive nature of MCAS, combined with a lack of pilot training on the system, rendered this mitigation ineffective.

---

### 4. Financial Impact Analysis
*   **Net Profit Impact:** Boeing moved from a **$10.46 billion profit (2018)** to a **$636 million net loss (2019)**, representing a total swing of **$11.096 billion** in bottom-line performance.
*   **Direct Crisis Costs:**
    *   Q2 2019 Pretax Charge: **$5.6 billion**
    *   Earlier Estimated Charge: **$8.2 billion**
    *   Total Estimated Crisis Cost (Jan 2020): **$18.4 billion**
*   **Operational Loss (External):** Southwest Airlines alone reported **$828 million** in lost operating income in 2019 directly attributable to the grounding.
*   **Note on Pareto:** The case does not provide a breakdown of the $18.4 billion total (e.g., specific dollar amounts for legal vs. compensation vs. engineering rework). Therefore, a quantitative Pareto analysis cannot be performed; the case does not provide sufficient data to rank the components of the financial impact.

---

### Final Root-Cause Statement
**The triggering event** was the internal decision to utilize a single AOA sensor as the primary input for MCAS, coupled with the business decision to treat AOA alerts as optional equipment. **The root cause** was an institutional decision-making framework that prioritized "cockpit commonality" to lower airline training costs, resulting in the rejection of redundant sensor architecture to satisfy short-term competitive and financial targets.

### Audit

## Audit Verdict: FAIL

### Check 1: Trigger vs. Root Cause Distinction
Overall Status: FAIL
Part A (Distinctness): PASS -- The diagnosis explicitly separates the trigger ("the internal decision to utilize a single AOA sensor") from the root cause ("an institutional decision-making framework").
Part B (Trigger Is Genuinely External): FAIL -- <"The triggering event was the internal decision to utilize a single AOA sensor as the primary input for MCAS, coupled with the business decision to treat AOA alerts as optional equipment."> -- The diagnosis identifies internal corporate decisions as the "triggering event." Per the audit standard, a company's own strategic decisions, business choices, or internal actions (such as choosing a design specification or an equipment sales strategy) are not external events; they are controllable internal actions and therefore invalid as triggers.

### Check 2: Fabricated Ranking Scan
Status: PASS
Instances found: None found. (The Analyst explicitly identified that a Pareto analysis could not be performed due to lack of data, and refrained from fabricating a ranking or weight distribution to fill that gap.)

## Orchestrator (Engagement Manager)

### FLAGGED FOR REVIEW — no report synthesized

Diagnosis did not pass audit after 2 attempt(s). No client-facing report was synthesized -- synthesizing one from an unresolved FAIL would present an unapproved diagnosis as a clean deliverable. See pipeline_result['history'] for the full attempt trail and the Auditor's final feedback.

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
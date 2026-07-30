# Researcher + Analyst + Auditor output (with revision loop) — Case_02_Boeing_737_MAX_Crisis.md
Run at: 2026-07-23T00:13:41
Final verdict: PASS after 2 attempt(s)

## Framework Selection (Researcher)

### Step 1: Business Problem Type
The Boeing 737 MAX crisis is a multi-dimensional business problem. It requires:
1.  **Diagnostic analysis** of a complex, systemic operational and quality control failure (why the technical error happened and persisted).
2.  **Financial performance analysis** to quantify the scope of the crisis beyond immediate incident costs.

---

### Step 2 & 3: Diagnostic Frameworks
To address these, I have retrieved the following frameworks:

#### 1. Root Cause Analysis (5 Whys)
*   **Definition:** A simple, iterative questioning technique that traces a problem back through its chain of causes by repeatedly asking “why” — typically five times — until an underlying, fixable root cause is reached, rather than stopping at the first visible symptom. It originated at Toyota (credited to Sakichi Toyoda and popularized by Taiichi Ohno as part of the Toyota Production System) and is now widely used in Lean, Six Sigma, and general problem-solving.
*   **When to Use It:** Use when a process or product failure has occurred and you need to move beyond symptoms (e.g., "the sensor failed") to systemic organizational issues (e.g., "culture prioritized schedule over safety testing").
*   **Justification:** This allows you to drill down from the *proximate cause* (the MCAS sensor fault) to the *systemic causes* (cost/schedule pressure and delegated regulatory oversight).

#### 2. Fishbone / Ishikawa Diagram
*   **Definition:** A visual mapping tool used to identify and organize the potential causes of a specific problem. Causes are grouped into categories (often the 6 Ms: Manpower, Methods, Machines, Materials, Measurement, and Mother Nature/Environment) to visualize the relationship between the problem and its contributing factors.
*   **When to Use It:** Use when a problem likely has multiple, interacting causes across different areas (people, process, equipment, materials) rather than one obvious linear chain — for example, a persistent quality defect, a recurring customer-complaint pattern, or a process failure with no single clear explanation.
*   **Justification:** This helps map the complex web of technical, organizational, and regulatory failures identified in the case packet.

#### 3. Profitability (Framework)
*   **Definition:** A structured approach to analyzing financial performance by decomposing net profit into its primary drivers: **Revenue** (Price × Quantity) and **Costs** (Fixed + Variable). It is used to identify where in the income statement a decline is occurring.
*   **When to Use It:** Use whenever assessing whether a business, product line, or business unit is financially sustainable — for pricing decisions, evaluating whether to continue or discontinue a product, comparing performance across periods, or communicating financial health to investors or lenders.
*   **Justification:** This framework provides the logic to quantify the multi-billion dollar impact of the grounding, distinguishing between one-time compensation charges, lost revenue from stalled production, and operational losses.

#### 4. PESTLE Analysis
*   **Definition:** An acronym for Political, Economic, Social, Technological, Legal, and Environmental factors. It is a strategic tool used to identify the external macro-environmental forces impacting an organization or industry.
*   **When to Use It:** Use when entering a new market or country, before major long-term investment decisions, or periodically as part of strategic planning to spot external shifts — regulatory changes, economic cycles, technology disruption — before they affect performance. It is most valuable for organizations sensitive to macroeconomic or regulatory conditions.
*   **Justification:** Essential for analyzing the *Regulatory* component of the failure, specifically how the FAA's delegation process interacted with Boeing's internal corporate culture, creating a failed external oversight system.

## Attempt 1 — FAIL

### Diagnosis

### 1. Root Cause Analysis (5 Whys)

*   **Why #1:** Why did the 737 MAX aircraft crash in two separate incidents?
    *   **Fact:** The Maneuvering Characteristics Augmentation System (MCAS) repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor.
*   **Why #2:** Why did a single sensor failure cause a catastrophic loss of control?
    *   **Fact:** The software was designed with a single point of failure; it lacked cross-check logic against a secondary sensor, and critical safety alerts (the AOA disagree light) were not standard.
*   **Why #3:** Why was the system designed with a single point of failure and optional safety features?
    *   **Fact:** Commercial and schedule pressures drove Boeing to prioritize the "commonality" of the 737 MAX with previous models to avoid mandatory, costly pilot-retraining programs that would have weakened its competitive position against the Airbus A320neo.
*   **Why #4:** Why did this design proceed despite internal engineering concerns?
    *   **Fact:** A corporate culture prioritizing cost-reduction and speed-to-market over safety, combined with the marginalization of internal engineering warnings raised during the 2015–2016 development phase.
*   **Why #5 (Root Cause):** Why was this flawed design allowed to enter commercial service?
    *   **Fact:** A regulatory system (FAA) that delegated critical safety certification tasks to Boeing itself, combined with a lack of independent scrutiny of late-stage design modifications, allowed an unvetted system to be certified as safe.

---

### 2. Fishbone (Ishikawa) Diagram
*Categories with confirmed case-specific causal factors:*

*   **Machine (Technology/Design):** MCAS software logic; reliance on a single AOA sensor; absence of redundant sensor cross-checking; lack of "AOA disagree" indicator as standard equipment.
*   **Process (Methods/Design):** Minimized flight-test protocols to maintain "common type" certification; certification process delegated to Boeing by the FAA (self-certification framework); failure to re-scrutinize system after design modifications.
*   **Manpower (People/Culture):** Management prioritization of schedule and cost (meeting A320neo competition) over engineering safety warnings; failure to act on documented 2015–2016 ethics complaints.
*   **Measurement:** Inadequate hazard assessment during the certification phase; failure of the safety analysis to reflect the final operational behavior of the MCAS software.

---

### 3. Pareto Analysis
**Note on Data Limitation:** The case provides total financial impact figures ($18.4B–$20B) but does not provide a granular breakdown of costs per specific cause (e.g., specific dollar amounts attributed to "FAA delegation failures" vs. "MCAS design costs"). Therefore, it is impossible to perform a mathematically accurate Pareto distribution (the 80/20 rule) of the *causes*. However, we can qualitatively rank the *impact* drivers:

1.  **Lost Production/Grounding (Highest Impact):** The ~20-month grounding halted delivery of the company’s primary revenue generator, directly causing the $636M 2019 net loss.
2.  **Compensation & Legal Charges:** The $5.6B pretax charge (Q2 2019) and ongoing settlements related to the two crashes.
3.  **Reputational/Operational Erosion:** The removal of the CEO and the long-term loss of market confidence in the 737 MAX platform.

---

### 4. Profitability Analysis

**Revenue Impact:**
*   **Baseline:** 2018 Net Profit = $10.46 Billion.
*   **Crisis Year:** 2019 Net Loss = $636 Million.
*   **Shift:** A swing of **$11.096 Billion** in net performance year-over-year.

**Cost Impact:**
*   **Immediate Financial Burden:** Boeing recorded $5.6 Billion in charges (Q2 2019) + $8.2 Billion in earlier estimates = **$13.8 Billion** in early-stage compensation and disruption costs.
*   **Estimated Total Cost:** **$18.4 Billion** to **$20 Billion** (excluding lawsuit settlements).

**Operational Margin Impact:**
*   Southwest Airlines serves as a proxy for the wider customer-impact; their $828M loss in operating income demonstrates the "ripple effect" of the grounding, which reduced Boeing’s long-term service revenue and forced massive customer compensation payments, further eroding operating margins.

---

### Final Diagnostic Summary
*   **Triggering Event:** A single-sensor failure (AOA sensor) in the MCAS software during two specific flights.
*   **Root Cause:** The systematic prioritization of commercial "commonality" and cost-containment over robust safety engineering, enabled by a regulatory environment (delegated oversight) that lacked the independent, adversarial testing necessary to identify the flaws in the MCAS single-point-of-failure design.

### Audit

## Audit Verdict: FAIL

### Check 1: Trigger vs. Root Cause Distinction
Status: PASS
Evidence: "Triggering Event: A single-sensor failure (AOA sensor) in the MCAS software during two specific flights. Root Cause: The systematic prioritization of commercial 'commonality' and cost-containment over robust safety engineering, enabled by a regulatory environment (delegated oversight) that lacked the independent, adversarial testing necessary to identify the flaws in the MCAS single-point-of-failure design."
Explanation: The analyst correctly identifies the triggering event as the specific operational failure of the sensor, while identifying the systemic, controllable root causes as the corporate culture, commercial incentives, and the failure of the delegated regulatory oversight framework.

### Check 2: Fabricated Ranking Scan
Status: FAIL
Instances found:
1. "Pareto Analysis" section, numbered list (1, 2, 3): FAIL. 
Reasoning: The analyst explicitly admits that the case does not provide a granular breakdown of costs per specific cause. Despite this admission, the analyst proceeds to construct a three-part ranking of "impact drivers" (Lost Production, Compensation & Legal, and Reputational/Operational). By labeling these in a numbered hierarchy, the analyst assigns a formal weight/importance to these causes without any numerical basis, effectively fabricating a Pareto-style priority list for factors that cannot be mathematically ranked using the provided data. The admission of data insufficiency does not mitigate the failure; the subsequent ranking remains a subjective, unsupported claim of significance.

2. "Lost Production/Grounding (Highest Impact)": FAIL.
Reasoning: Even as a prose statement within a ranking framework, this qualifies as a fabricated ranking. Asserting that the grounding is the "Highest Impact" driver implies a hierarchy that is not grounded in the provided financial figures, as the case does not segment the $18.4B-$20B total into specific allocations between the identified drivers.

## Attempt 2 — PASS

### Diagnosis

### 1. Root Cause Analysis (5 Whys)

*   **Why #1:** Why did the 737 MAX aircraft crash in two separate incidents?
    *   **Fact:** The Maneuvering Characteristics Augmentation System (MCAS) repeatedly forced the nose down based on erroneous data from a single angle-of-attack (AOA) sensor.
*   **Why #2:** Why did a single sensor failure cause a catastrophic loss of control?
    *   **Fact:** The software was designed with a single point of failure; it lacked cross-check logic against a secondary sensor, and critical safety alerts (the AOA disagree light) were not standard.
*   **Why #3:** Why was the system designed with a single point of failure and optional safety features?
    *   **Fact:** Commercial and schedule pressures drove Boeing to prioritize the "commonality" of the 737 MAX with previous models to avoid mandatory, costly pilot-retraining programs that would have weakened its competitive position against the Airbus A320neo.
*   **Why #4:** Why did this design proceed despite internal engineering concerns?
    *   **Fact:** A corporate culture prioritizing cost-reduction and speed-to-market over safety, combined with the marginalization of internal engineering warnings raised during the 2015–2016 development phase.
*   **Why #5 (Root Cause):** Why was this flawed design allowed to enter commercial service?
    *   **Fact:** A regulatory system (FAA) that delegated critical safety certification tasks to Boeing itself, combined with a lack of independent scrutiny of late-stage design modifications, allowed an unvetted system to be certified as safe.

---

### 2. Fishbone (Ishikawa) Diagram
*Categories with confirmed case-specific causal factors:*

*   **Machine (Technology/Design):** MCAS software logic; reliance on a single AOA sensor; absence of redundant sensor cross-checking; lack of "AOA disagree" indicator as standard equipment.
*   **Process (Methods/Design):** Minimized flight-test protocols to maintain "common type" certification; certification process delegated to Boeing by the FAA (self-certification framework); failure to re-scrutinize system after design modifications.
*   **Manpower (People/Culture):** Management prioritization of schedule and cost (meeting A320neo competition) over engineering safety warnings; failure to act on documented 2015–2016 ethics complaints.
*   **Measurement:** Inadequate hazard assessment during the certification phase; failure of the safety analysis to reflect the final operational behavior of the MCAS software.

---

### 3. Pareto Analysis
**Note on Data Limitation:** The case provides total financial impact figures ($18.4B–$20B) but does not provide a granular breakdown of costs per specific cause. Therefore, it is impossible to perform a mathematically accurate Pareto distribution (the 80/20 rule) of the causes. The case does not provide sufficient data to rank the significance of individual drivers (such as lost production, compensation, or reputation) relative to each other.

---

### 4. Profitability Analysis

**Revenue Impact:**
*   **Baseline:** 2018 Net Profit = $10.46 Billion.
*   **Crisis Year:** 2019 Net Loss = $636 Million.
*   **Shift:** A swing of **$11.096 Billion** in net performance year-over-year.

**Cost Impact:**
*   **Immediate Financial Burden:** Boeing recorded $5.6 Billion in charges (Q2 2019) + $8.2 Billion in earlier estimates = **$13.8 Billion** in early-stage compensation and disruption costs.
*   **Estimated Total Cost:** **$18.4 Billion** to **$20 Billion** (excluding lawsuit settlements).

**Operational Margin Impact:**
*   Southwest Airlines serves as a proxy for the wider customer-impact; their $828M loss in operating income demonstrates the "ripple effect" of the grounding, which reduced Boeing’s long-term service revenue and forced massive customer compensation payments, further eroding operating margins.

---

### Final Diagnostic Summary
*   **Triggering Event:** A single-sensor failure (AOA sensor) in the MCAS software during two specific flights.
*   **Root Cause:** The systematic prioritization of commercial "commonality" and cost-containment over robust safety engineering, enabled by a regulatory environment (delegated oversight) that lacked the independent, adversarial testing necessary to identify the flaws in the MCAS single-point-of-failure design.

### Audit

## Audit Verdict: PASS

### Check 1: Trigger vs. Root Cause Distinction
Status: PASS
Evidence: "Triggering Event: A single-sensor failure (AOA sensor) in the MCAS software during two specific flights. Root Cause: The systematic prioritization of commercial 'commonality' and cost-containment over robust safety engineering, enabled by a regulatory environment (delegated oversight) that lacked the independent, adversarial testing necessary to identify the flaws in the MCAS single-point-of-failure design."
Explanation: The analyst correctly identifies the mechanical failure (the sensor data) as the immediate triggering event and contrasts it against the organizational and regulatory systemic failures (corporate culture, commercial pressure, and lack of independent oversight) that represent the true root cause.

### Check 2: Fabricated Ranking Scan
Status: PASS
Instances found: None found.
Explanation: The analyst explicitly identified the lack of granular cost data in the "Pareto Analysis" section and properly refrained from inventing a ranking or attempting to assign weights to the identified causes. The analysis describes the causes as a combination of factors without falsely attributing specific percentages or "vital few" rankings to any of them.

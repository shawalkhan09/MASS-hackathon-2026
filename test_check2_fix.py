# -*- coding: utf-8 -*-
"""
Direct test of the Check 2 fix, using a KNOWN-BAD diagnosis as input
instead of running the full pipeline and hoping an LLM spontaneously
reproduces the same violation. LLM output isn't deterministic -- two
single-case runs in a row happened not to reproduce the "Vital Few"
prose-ranking bug, which tells us nothing about whether the fix works,
only that we got unlucky/lucky twice. Feeding the exact bad diagnosis
directly answers three concrete questions:

  1. Does the updated Check 2 wording now correctly FAIL this input?
  2. Does the revision step produce a corrected diagnosis?
  3. Does re-auditing the revision now PASS?

Uses 2-3 LLM calls total (vs. a full pipeline run's 3+), and targets
exactly the thing that needs verifying.
"""

from pathlib import Path

from crewai_pipeline import run_auditor, run_analyst_revision, parse_verdict

case_text = Path("cases/Case_01_Southwest_Airlines_2022_Meltdown.md").read_text()

# The exact diagnosis that the OLD Check 2 wording incorrectly passed --
# includes the Pareto section with the "Vital Few" prose-ranking claim.
KNOWN_BAD_DIAGNOSIS = """### 1. Root Cause Analysis (5 Whys)
*   **Why 1:** Why did Southwest cancel 16,700 flights over 10 days?
    *   *Result:* Because the airline's crew-scheduling software could not automatically reassign pilots and flight attendants to recover from the disruptions caused by Winter Storm Elliott.
*   **Why 2:** Why could the scheduling software not handle the reassignments?
    *   *Result:* Because the system was outdated and struggled to process the scale of manual re-optimizations required for the airline's dispersed crew and aircraft positions.
*   **Why 3:** Why was the system outdated and unable to scale?
    *   *Result:* Because of chronic underinvestment in technology compared to modern systems used by competitors, despite documented, recurring warnings from the pilots' union.
*   **Why 4:** Why did management persist with this technology despite warnings?
    *   *Result:* Because of a strategic prioritization of short-term efficiency and operational costs over the long-term resilience required to support their unique, high-velocity network.
*   **Why 5 (Root Cause):** Why was the risk ignored?
    *   *Result:* A failure in corporate governance to treat "operational debt" as a critical financial risk, allowing known, fragile legacy systems to remain the backbone of the operation despite evidence that they were failing with increasing frequency.

---

### 2. Fishbone (Ishikawa) Diagram
*   **Machine (Technology):** Legacy crew-scheduling software failed to scale; lack of modern automated re-optimization tools.
*   **Method (Process):** Point-to-point network model caused cascading failures; reliance on manual phone/spreadsheet rebooking processes during disruptions.
*   **Material (Infrastructure):** Inadequate winter-weather equipment and supplies at key stations.
*   **Environment:** Winter Storm Elliott (the triggering event).
*   **Measurement:** Failure to act on internal/union reports regarding "duct tape" operations; failure to address escalating frequency of previous minor tech glitches.

---

### 3. Pareto Analysis
*   **Data Availability:** The case provides the *total* financial impact ($1.1B in operational costs) and the *result* (16,700 cancellations). However, the case does **not** provide a granular breakdown of which specific cause contributed what percentage to the $1.1B loss (e.g., we do not know how much of the $1.1B was strictly "scheduling software failure" vs. "lack of de-icing crews").
*   **Analysis:** Because the data is not segmented by cause, a traditional Pareto chart cannot be accurately constructed. However, based on the DOT's conclusion that the event "crossed the line from uncontrollable weather to company responsibility," we can qualitatively deduce that **Technology Failure (Scheduling Software)** and **Network Design (Point-to-Point)** represent the "Vital Few" causes that transformed a common weather event into an unprecedented, industry-outlier catastrophe.

---

### 4. Financial Impact Analysis
*   **Total Operational Cost (Dec 2022 Meltdown):** $1.1 Billion
    *   Includes: Refunds, reimbursements, extra operating costs, and lost ticket sales.
*   **Regulatory Penalty (DOT Settlement):** $140 Million
    *   Composition: $35M cash fine; $105M in travel-voucher compensation.
*   **Corrective Investment (2023):** $1.3 Billion
    *   Context: This represents a 25% increase over 2019 technology spend, effectively acting as the "cost of compliance/remediation" to fix the system that failed.
*   **Summary Calculation:**
    *   Total Immediate Financial Impact = $1.1B (Operational) + $140M (Regulatory) = **$1.24 Billion.**
    *   Total Financial Exposure (Loss + Remediation) = **$2.54 Billion.**

---

### Final Root-Cause Summary
The Southwest Airlines meltdown was triggered by **Winter Storm Elliott**, an uncontrollable environmental factor that all major airlines faced. However, the root cause—which prevented recovery and turned a manageable disruption into a 16,700-flight cancellation crisis—was **systemic operational fragility driven by a failure to invest in mission-critical technology.**

While the point-to-point network structure and inadequate winter staffing were contributing factors, the lack of automated, scalable scheduling software acted as the single point of failure that forced the company into manual, spreadsheet-based recovery. This was not an unpredictable "black swan" event, but the result of institutional neglect regarding known, documented technology risks, ultimately costing the company $1.24 billion in immediate losses and necessitating a $1.3 billion capital commitment to modernize infrastructure."""

FRAMEWORK_CONTEXT = (
    "1. Root Cause Analysis (5 Whys) -- iterative questioning to trace a "
    "problem back through its chain of causes to a fixable root cause.\n"
    "2. Fishbone/Ishikawa Diagram -- maps causes into categories "
    "(Machine, Method, Material, Environment, Measurement, People).\n"
    "3. Pareto Analysis -- ranks causes by measured contribution to "
    "identify the 'vital few' driving most of the impact; requires "
    "quantifiable, case-provided data to rank causes.\n"
    "4. Profitability / Financial Impact Analysis -- decomposes financial "
    "impact into components using case-provided figures."
)

print("=" * 70)
print("STEP 1: Auditing the known-bad diagnosis with the UPDATED Check 2")
print("=" * 70)
audit_1 = run_auditor(case_text, KNOWN_BAD_DIAGNOSIS)
print(audit_1)
passed_1 = parse_verdict(audit_1)
print(f"\nParsed verdict: {'PASS' if passed_1 else 'FAIL'}")

if passed_1:
    print("\n!! STILL PASSING -- the fix did not catch it. Needs more work.")
else:
    print("\nCorrectly FAILED -- proceeding to test the revision step.")

    print("\n" + "=" * 70)
    print("STEP 2: Analyst revision based on this audit feedback")
    print("=" * 70)
    revised = run_analyst_revision(case_text, FRAMEWORK_CONTEXT, KNOWN_BAD_DIAGNOSIS, audit_1)
    print(revised)

    print("\n" + "=" * 70)
    print("STEP 3: Re-auditing the revision")
    print("=" * 70)
    audit_2 = run_auditor(case_text, revised)
    print(audit_2)
    passed_2 = parse_verdict(audit_2)
    print(f"\nParsed verdict: {'PASS' if passed_2 else 'FAIL'}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Original diagnosis:  FAIL (confirmed)")
    print(f"Revised diagnosis:   {'PASS' if passed_2 else 'FAIL'}")
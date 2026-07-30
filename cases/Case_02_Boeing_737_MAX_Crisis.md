# Case Packet 02: Boeing 737 MAX Grounding Crisis (2018–2020)

**Domain:** Manufacturing / Quality Control / Aerospace / Product Safety
**Case type:** Real, publicly documented event (not a licensed case-study product)
**Best-fit frameworks:** Root Cause Analysis (5 Whys), Fishbone/Ishikawa Diagram, Porter's Five Forces, Profitability, ROI

---

## Problem Statement

Two crashes of the same new aircraft model, five months apart, killed 346 people combined and led to a worldwide grounding lasting nearly two years. Diagnose the chain of causes that allowed a known technical vulnerability to reach production twice, and quantify the resulting business impact.

## Background

Boeing developed the 737 MAX as a fuel-efficient update to its best-selling 737 line, competing against Airbus's new A320neo. To fit larger, more efficient engines under the existing 737 airframe, engineers moved the engines forward and higher on the wing, which changed the aircraft's handling characteristics at high angles of attack. To make the MAX handle like older 737 models — and avoid triggering a costly new pilot-certification requirement for airlines — Boeing introduced a new flight-control software system, the Maneuvering Characteristics Augmentation System (MCAS), which automatically pushed the aircraft's nose down if a sensor indicated a stall risk.

Lion Air Flight 610 crashed in Indonesia on October 29, 2018, killing all 189 aboard, after MCAS repeatedly forced the nose down based on erroneous sensor data. The aircraft continued flying after this crash. Ethiopian Airlines Flight 302 crashed on March 10, 2019, in a nearly identical failure pattern, killing all 157 aboard. The aircraft was grounded worldwide days later and did not return to service until late 2020.

## Supporting Data

- **2 crashes, 346 total deaths** (189 + 157)
- Aircraft grounded worldwide from March 2019 to November/December 2020 (~20 months)
- Boeing's estimated total financial cost of the crisis reached approximately **$18.4 billion** by January 2020; some Wall Street analysts estimated the ultimate total could reach roughly **$20 billion**, excluding crash-related lawsuit settlements
- A **$5.6 billion** pretax charge was recorded in Q2 2019 alone for customer compensation and disruption costs, on top of an earlier $8.2 billion estimate
- Boeing posted a **net loss of $636 million for full-year 2019** — its first annual loss in more than 20 years, versus a $10.46 billion profit in 2018
- Southwest Airlines alone reported losing approximately **$828 million** in 2019 operating income due to the grounding of its MAX fleet
- Boeing's CEO, Dennis Muilenburg, was removed by the board in December 2019
- MCAS took input from only a **single angle-of-attack sensor** per flight — a documented single point of failure; the optional "AOA disagree light" and "AOA indicator" features that could have alerted pilots to a faulty sensor reading were sold as extra-cost options, and neither crashed aircraft had them installed

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

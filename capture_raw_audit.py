# -*- coding: utf-8 -*-
"""
Diagnostic re-run of the exact structured input from the live UI test
(the Ohio warehouse / inventory software case), to answer two specific
questions the UI's simplified reason couldn't answer on its own:

1. Is api.py's simplify_audit_feedback() actually conflating a PASSING
   Check 2 instance's reasoning with FAIL framing -- the displayed
   reason ("wasn't clearly backed by the data") was followed by
   explanation text that describes the Analyst correctly DECLINING to
   fabricate a ranking, which reads like a PASS description wearing a
   FAIL label.

2. What did Check 1 actually say about the "Triggering Event" framing?
   The diagnosis's Final Root-Cause Statement called "the external
   onset of systemic shipment inaccuracies... in September" the
   trigger -- but that's the case's own internal software switch and
   its symptoms, not anything external. This case was deliberately
   built with no genuine external trigger candidate at all. Did Check
   1 Part B catch this, or did something let it through -- and if it
   did catch it, why didn't its reason show up in the UI?

This does not modify api.py, orchestrator.py, or crewai_pipeline.py --
it only imports and calls existing functions to inspect their real
behavior on real input.
"""

from crewai_pipeline import run_pipeline
from api import simplify_audit_feedback

STRUCTURED_INPUT = (
    "## Problem Statement\n"
    "The warehouse in Ohio is experiencing frequent order inaccuracies, "
    "including shipments of incorrect items and SKUs, following the "
    "implementation of a new inventory software system. The system "
    "integration with existing barcode scanners is suspected to be the "
    "cause of these errors.\n\n"
    "## Background\n"
    "Since September, the warehouse has transitioned to a new inventory "
    "software system intended to reduce costs. Since the implementation, "
    "the facility has experienced ongoing operational issues that have "
    "not improved over the four-month duration. Despite the IT "
    "department reporting that the system is functioning correctly, "
    "customer support call volumes have increased significantly, and the "
    "company lost its largest wholesale client due to repeated shipping "
    "errors. Leadership has advised waiting for improvements, though "
    "performance reportedly worsened in November. The company has not "
    "yet performed a formal audit of the costs associated with the "
    "software transition.\n\n"
    "## Supporting Data\n"
    "*   **Timeline:** Issues began in September; the situation has "
    "persisted for almost 4 months; performance worsened in November.\n"
    "*   **Return Volume:** 4,200 returns were processed in October, "
    "which is nearly triple the normal volume.\n"
    "*   **Customer Support:** Average wait times increased from "
    "approximately 3 minutes to nearly 14 minutes.\n"
    "*   **Lost Revenue:** The lost wholesale account was valued at "
    "approximately $800,000 per year.\n"
    "*   **Audit Status:** No full audit of the software switch costs "
    "has been conducted."
)


def main():
    pipeline_result = run_pipeline(STRUCTURED_INPUT, max_revisions=1)

    print("=" * 70)
    print(f"PIPELINE VERDICT: {'PASS' if pipeline_result['final_passed'] else 'FAIL'} "
          f"after {pipeline_result['total_attempts']} attempt(s)")
    print("=" * 70)

    for h in pipeline_result["history"]:
        print(f"\n{'#' * 70}")
        print(f"ATTEMPT {h['attempt']} — {'PASS' if h['passed'] else 'FAIL'}")
        print(f"{'#' * 70}")
        print("\n--- FULL RAW DIAGNOSIS ---")
        print(h["diagnosis"])
        print("\n--- FULL RAW AUDIT (unfiltered by api.py) ---")
        print(h["audit"])

    last_audit = pipeline_result["history"][-1]["audit"]

    print("\n" + "=" * 70)
    print("WHAT api.py's simplify_audit_feedback() PRODUCES FROM THE ABOVE")
    print("=" * 70)
    reasons = simplify_audit_feedback(last_audit)
    for r in reasons:
        print(f"- {r}")


if __name__ == "__main__":
    main()
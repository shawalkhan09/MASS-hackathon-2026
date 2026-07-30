# -*- coding: utf-8 -*-
"""
First validation pass for intake.py -- the one component in this
project that has never been through the build-test-find-a-real-defect
cycle every other agent (Researcher, Analyst, Auditor, Orchestrator,
fidelity check) went through before being trusted.

WHAT THIS TESTS, AND WHY THIS SHAPE OF TEST: intake.py's own docstring
identifies the specific risk -- "turning something vague into something
that reads as complete and specific is precisely what fabrication under
pressure means" (Section 8 of the report). That's a claim about
BEHAVIOR ON VAGUE INPUT specifically, not a general "is this agent any
good" question. So the fixtures below deliberately span a spectrum of
how much concrete data is actually present -- from none, to exactly
one figure, to several -- with the EXACT ground truth documented in
each fixture's own comment. That makes it possible to check, for any
given output, whether every number/date/figure it contains actually
traces back to the input, and whether an absence of data is reported
as an absence (as the task instructions require) rather than quietly
filled in.

WHAT THIS DOESN'T AUTOMATE, AND WHY: unlike the fidelity check or the
Auditor, this agent's output is free text being checked against another
piece of free text, not a structured diagnosis being checked against a
Pareto-style ranking claim. Building an automated fabrication-detector
for this shape of comparison would itself be a second unvalidated
component sitting on top of the one being tested. This first pass
prints full output for manual review against each fixture's documented
ground truth instead -- the same way Check 2's ORIGINAL failure mode
was first found by manual review before any automated check existed
for it (Section 6.4). Automating this comparison, if it's judged worth
doing after this pass, is future work, not a substitute for actually
looking at what came out this time.

N_TRIALS = 5 per fixture (15 total calls), paced 10 seconds apart given
the confirmed 15 RPM free-tier ceiling.
"""

import time

from intake import run_intake

N_TRIALS = 5
DELAY_SECONDS = 10

# ---------------------------------------------------------------------------
# FIXTURE_SPARSE -- ground truth: ZERO concrete numbers, dates, or figures
# anywhere in the input. Every claim is qualitative ("a few months,"
# "probably costing us in some way"). A correct output's Supporting Data
# section should say explicitly that no concrete data was provided --
# per the task's own instruction -- not invent a percentage, dollar
# figure, or count to make the section look complete.
# ---------------------------------------------------------------------------
FIXTURE_SPARSE = (
    "We've been having a really rough time with returns lately. Customers "
    "keep sending things back, and it's been going on for a few months "
    "now. Our team thinks it might be because the sizing on our clothing "
    "line is inconsistent, but we honestly haven't dug into it properly. "
    "It's definitely hurting morale in the warehouse and probably costing "
    "us in some way, though nobody's pulled the actual numbers together "
    "yet."
)

# ---------------------------------------------------------------------------
# FIXTURE_ONE_NUMBER -- ground truth: exactly ONE concrete figure exists
# in the entire input -- "340%" (the late-delivery complaint increase).
# "March" and "same period last year" are the only date-like references,
# neither a specific date. No dollar figures, no other percentages, no
# counts anywhere. A correct output surfaces the 340% figure and stops --
# it should not add a plausible-sounding dollar impact, a specific date,
# or an additional percentage the input never gave.
# ---------------------------------------------------------------------------
FIXTURE_ONE_NUMBER = (
    "Since March, we've noticed a big uptick in customer support tickets "
    "about late deliveries. We switched to a new regional shipping "
    "carrier around that time to cut costs, and it seems related, though "
    "we haven't confirmed it. Customer complaints have gone up a lot. The "
    "only real number we have is that late-delivery complaints are up "
    "340% compared to the same period last year."
)

# ---------------------------------------------------------------------------
# FIXTURE_DETAILED -- ground truth: exactly these figures and nothing
# else -- Q2 this year; $49/month new tier; $19/month existing tier;
# projected 5,000 signups; actual 612 signups; 22% monthly churn (new
# tier); 4% monthly churn (standard tier); cancellations mentioning
# confusion about what's included. A correct output includes exactly
# these numbers and this one stated reason for cancellation -- not an
# invented total-revenue-impact figure, not an invented percentage of
# total users affected, not an additional cancellation reason the input
# never mentioned.
# ---------------------------------------------------------------------------
FIXTURE_DETAILED = (
    "In Q2 this year, we launched a new subscription tier priced at "
    "$49/month, positioned above our existing $19/month plan. We "
    "projected 5,000 signups in the first quarter based on our marketing "
    "team's estimate, but only got 612 actual signups by the end of that "
    "quarter. Churn on the new tier has been running at about 22% "
    "monthly, way higher than our standard tier's 4% monthly churn. "
    "Support has flagged that a lot of new-tier cancellations mention "
    "confusion about what's actually included at the higher price point."
)

FIXTURES = [
    ("FIXTURE_SPARSE", FIXTURE_SPARSE,
     "no concrete numbers/dates anywhere -- Supporting Data should say so explicitly"),
    ("FIXTURE_ONE_NUMBER", FIXTURE_ONE_NUMBER,
     "exactly one figure (340%) -- nothing else numeric should appear"),
    ("FIXTURE_DETAILED", FIXTURE_DETAILED,
     "exactly these figures: Q2, $49, $19, 5000, 612, 22%, 4% -- nothing more"),
]


def main():
    for name, raw_input, ground_truth_note in FIXTURES:
        print("=" * 70)
        print(f"FIXTURE: {name}")
        print(f"GROUND TRUTH: {ground_truth_note}")
        print("=" * 70)
        for trial in range(1, N_TRIALS + 1):
            result = run_intake(raw_input)
            print(f"\n--- {name} trial {trial}/{N_TRIALS} ---")
            print(result)
            print(f"--- end {name} trial {trial}/{N_TRIALS} ---\n")
            if trial < N_TRIALS or name != FIXTURES[-1][0]:
                time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
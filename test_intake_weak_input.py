# -*- coding: utf-8 -*-
"""
Second validation pass for intake.py, extending Phase 35
(test_intake_validation.py) along the axis that file's own docstring
flags as untested: input QUALITY, not just input COMPLETENESS.

WHAT PHASE 35 TESTED, AND WHAT IT DIDN'T: Phase 35 ran three fixtures
of clean, fluent English that varied only in how much concrete data
was present (zero, one, several figures). It never tried weak grammar,
code-switched Roman Urdu/English -- this project's actual target
market -- vague quantifiers, long rambling multi-topic input, or an
extremely sparse one-liner. intake.py's own docstring names exactly
these as untested: "long, rambling, multi-topic input; genuine
section-boundary ambiguity; and vague quantifiers that might get
mistakenly promoted into concrete figures (e.g. 'about half our
customers' becoming a stated percentage)". This pass is the first
real test of that named risk, plus the weak-grammar and code-switched
shapes that come with the market the tool is actually for.

SAME SHAPE OF TEST AS PHASE 35: each fixture documents its EXACT
ground truth in the comment above it, so every number/date/figure in
any given output can be traced back to the input, every hedge the
user stated can be checked for preservation rather than promotion,
and every vague quantifier can be checked against being turned into a
specific percentage or count.

WHAT THIS DOESN'T AUTOMATE, AND WHY: same reasoning as Phase 35's own
docstring -- this agent's output is free text being checked against
another piece of free text, and building an automated fabrication-
detector for this shape of comparison would itself be a second
unvalidated component sitting on top of the one being tested. Full
output is printed for manual review AND saved to disk, one file per
trial in intake_weak_input_outputs/, rather than print-only --
DEVELOPMENT_LOG.md Phase 60 documents a real terminal-truncation bug
from skipping exactly that step.

N_TRIALS = 5 per fixture (25 total calls), paced 10 seconds apart
given the confirmed 15 RPM free-tier ceiling (same pacing as
test_intake_validation.py).
"""

import time
from pathlib import Path
from datetime import datetime

from intake import run_intake

N_TRIALS = 5
DELAY_SECONDS = 10

OUT_DIR = Path("intake_weak_input_outputs")
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# FIXTURE_WEAK_ENGLISH -- ground truth: duration "3 month"; delivery time
# changed from "2 day" to "6 day, sometime more"; new courier company used
# since "January"; "almost 40 customer" lost; loss "around 500000
# rupees," explicitly hedged as not exactly calculated; the courier being
# the cause is explicitly hedged ("not 100% sure"). A correct output
# preserves BOTH hedges as hedges, not as stated certainties, and does
# not smooth the grammar into a cleaner-sounding invented specific.
# ---------------------------------------------------------------------------
FIXTURE_WEAK_ENGLISH = (
    "we have big problem since 3 month. Our customer very angry because "
    "delivery always late. Before covid we deliver in 2 day now taking 6 "
    "day sometime more. We use new courier company from january this "
    "cause the problem I think but not 100% sure. We lose almost 40 "
    "customer already they stop order from us. Money loss maybe around "
    "500000 rupees but I not calculate exact."
)

# ---------------------------------------------------------------------------
# FIXTURE_ROMAN_URDU_ENGLISH -- ground truth: return rate went from "5%"
# to "18%"; supplier changed in "July"; revenue down "almost 200000 per
# month," explicitly hedged as not exactly calculated; the supplier
# change being the cause is explicitly hedged ("shayad," "confirm nahi
# hai" -- Roman Urdu for "maybe" and "not confirmed"). A correct output
# should extract the English business facts correctly despite the
# code-switching, and preserve both hedges exactly as it would for an
# all-English input with the same hedges.
# ---------------------------------------------------------------------------
FIXTURE_ROMAN_URDU_ENGLISH = (
    "Humari dukaan mein last 2 mahine se bohat problem hai. Grahak "
    "complaints bahut zyada ho gaye hain quality issue pe. We changed "
    "our supplier in July, shayad that's the wajah lekin confirm nahi "
    "hai. Return rate pehle 5% tha ab 18% ho gaya hai. Revenue down "
    "almost 200000 per month but exact hisaab nahi kiya abhi tak."
)

# ---------------------------------------------------------------------------
# FIXTURE_VAGUE_QUANTIFIERS -- ground truth: ZERO concrete numbers
# anywhere except the month "September" and the vague timeframe "last
# quarter." "About half," "most of," and "a handful" are all vague
# qualifiers stated by the user and must NOT be promoted into specific
# percentages or counts (e.g. must not become "50% of customers
# churned" or "a majority of staff"). This is the literal risk named in
# intake.py's own docstring as untested -- the first real test of it.
# ---------------------------------------------------------------------------
FIXTURE_VAGUE_QUANTIFIERS = (
    "About half our repeat customers seem to have stopped ordering in "
    "the last quarter. Most of our staff think it's because we raised "
    "prices in September, though we haven't surveyed anyone properly. A "
    "handful of customers have complained directly about cost. We "
    "haven't pulled any real numbers yet."
)

# ---------------------------------------------------------------------------
# FIXTURE_LONG_RAMBLING_MULTITOPIC -- ground truth: the ONLY figure
# anywhere is "27% more support tickets about shipping delays" since
# "the new warehouse system went live in April." Everything else (the
# hiring freeze, the website redesign, the parking lot complaints) is
# scene-setting the user included but is not the stated problem and has
# no numbers attached. A correct output identifies shipping-delay
# tickets as the actual Problem Statement, keeps the tangents in
# Background at most if anywhere, and does not fabricate a connection
# between the parking lot or the hiring freeze and the shipping
# problem, since the input never draws that connection itself.
# ---------------------------------------------------------------------------
FIXTURE_LONG_RAMBLING_MULTITOPIC = (
    "So it's been a weird year honestly. We had a hiring freeze back in "
    "February which nobody was happy about, and then in March we redid "
    "the whole website which took way longer than expected and cost "
    "more than the agency quoted us originally. Then in April we "
    "switched over to a new warehouse management system, and I guess "
    "since then support has been getting a lot more tickets about "
    "shipping delays, like 27% more than before, which is a lot. Also "
    "separately people keep complaining there's not enough parking at "
    "the warehouse but that's probably unrelated. Anyway the shipping "
    "thing is what's actually worrying me."
)

# ---------------------------------------------------------------------------
# FIXTURE_MINIMAL_ONE_LINER -- ground truth: zero concrete data of any
# kind, not even a vague timeframe -- shorter and sparser than
# test_intake_validation.py's existing FIXTURE_SPARSE. A correct output
# states plainly that no supporting data exists and does not invent a
# percentage, timeframe, or cause of any kind to make the sections look
# more complete than the input actually supports.
# ---------------------------------------------------------------------------
FIXTURE_MINIMAL_ONE_LINER = "Sales are down and I don't know why."

FIXTURES = [
    ("FIXTURE_WEAK_ENGLISH", FIXTURE_WEAK_ENGLISH,
     "weak grammar; figures: 3 month, 2 day -> 6 day, January, ~40 customers, "
     "~500000 rupees (hedged); courier-causation hedged ('not 100% sure')"),
    ("FIXTURE_ROMAN_URDU_ENGLISH", FIXTURE_ROMAN_URDU_ENGLISH,
     "Roman Urdu/English code-switch; figures: 5% -> 18%, July, ~200000/month "
     "(hedged); supplier-causation hedged ('shayad', 'confirm nahi hai')"),
    ("FIXTURE_VAGUE_QUANTIFIERS", FIXTURE_VAGUE_QUANTIFIERS,
     "ZERO numbers except September and 'last quarter'; 'about half'/'most "
     "of'/'a handful' must not become percentages or counts"),
    ("FIXTURE_LONG_RAMBLING_MULTITOPIC", FIXTURE_LONG_RAMBLING_MULTITOPIC,
     "only figure is 27% more shipping-delay tickets since April; hiring "
     "freeze/website/parking are tangents with no numbers and no drawn connection"),
    ("FIXTURE_MINIMAL_ONE_LINER", FIXTURE_MINIMAL_ONE_LINER,
     "zero concrete data of any kind, not even a timeframe -- Supporting Data "
     "should say so explicitly, nothing invented"),
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
            # Save-to-disk, not print-only: Phase 60's terminal-truncation
            # lesson. One file per trial, self-contained (input + output).
            out_path = OUT_DIR / f"{name}_trial{trial}.txt"
            out_path.write_text(
                f"# Intake weak-input test -- {name} -- trial {trial}/{N_TRIALS}\n"
                f"Run at: {datetime.now().isoformat(timespec='seconds')}\n"
                f"GROUND TRUTH: {ground_truth_note}\n\n"
                f"## RAW INPUT\n{raw_input}\n\n"
                f"## INTAKE OUTPUT\n{result}\n"
            )
            print(f"Saved to {out_path}")
            if trial < N_TRIALS or name != FIXTURES[-1][0]:
                time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()

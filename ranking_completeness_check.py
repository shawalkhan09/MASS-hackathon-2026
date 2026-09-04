# -*- coding: utf-8 -*-
"""
Check 4 -- Ranking Completeness. A candidate fourth Auditor check,
addressing the omission-blindness gap documented across Sections
8.8/8.9 (synthetic fixtures) and Section 8.14/Phase 65 (PIA/Airlift,
real cases): the Auditor's existing Check 2 verifies that a ranking's
PERCENTAGES aren't fabricated, but never checks whether the ranking is
COMPLETE -- whether a cause the diagnosis itself already names
elsewhere (the labeled Triggering Event, the labeled Root Cause) has
simply been left out of the ranking table, substituted by a generic
catch-all category instead.

WHY THIS DOES NOT REQUIRE ANY CHANGE TO THE ANALYST'S OUTPUT:
every diagnosis this project generates already labels its Triggering
Event and Root Cause explicitly, in the same Final Root-Cause
Statement structure Check 1 already parses reliably. This check reads
two sections of the SAME diagnosis against each other -- it needs no
new field, no case text, and no second document.

WHY THIS IS ITS OWN ISOLATED MODULE, NOT A FOURTH CHECK BOLTED ONTO
crewai_pipeline.py's SHARED AUDIT_DESCRIPTION: Section 10.3 already
flags an open, untested question -- whether the Auditor's own Check
1/2/3 share the same cross-check bleed the fidelity check's Check
A/B/C had before their Section 6.7 architectural isolation (see that
module's docstring for the two independent, confirmed regressions
this exact failure mode caused there). Adding a fourth check to
Check 1/2/3's shared prompt would introduce a new instance of a risk
that is already open and unresolved, rather than staying clear of it.
This module follows fidelity_check.py's proven pattern instead: its
own isolated Agent + Task + Crew, seeing only this check's own
instructions.

SCOPE, DELIBERATELY NARROW: this checks only the diagnosis's own
labeled Triggering Event and Root Cause against its own ranking table,
if one is present. It does NOT require every minor Fishbone factor to
appear in the ranking, and it does NOT flag anything if the diagnosis
provides no ranking at all (many diagnoses correctly decline to rank
due to insufficient data -- e.g. the Ohio Warehouse fixture -- and
that is not incompleteness). It also does not enumerate named evasion
patterns or example substitute phrases in its wording -- Phase 66/67's
lesson (naming specific patterns teaches a closed checklist rather
than the general principle) is deliberately not repeated here.

VALIDATION: see test_check4_ranking_completeness.py, which runs this
check against all 18 already-saved PIA/Airlift forced-ranking
diagnoses (Phase 60/65) -- zero new diagnosis-generation calls, since
those fixtures already exist on disk with a known, real ground truth
(8 PIA runs omit their trigger from the ranking, 1 retains it; all 9
Airlift runs retain theirs).
"""

import re
import warnings

from crewai import Agent, Task, Crew

from crewai_pipeline import MODEL

# ---------------------------------------------------------------------------
# Same find-all-take-last-plus-warn verdict parsing as fidelity_check.py's
# _extract_check_verdict() -- duplicated here rather than imported, to keep
# this module's only dependency on crewai_pipeline.py being MODEL itself,
# consistent with fidelity_check.py's own import footprint.
# ---------------------------------------------------------------------------


def _extract_verdict(verdict_text: str, pattern: "re.Pattern") -> bool:
    """True if PASS, False if FAIL or unparseable (fails SAFE)."""
    matches = pattern.findall(verdict_text)
    if not matches:
        return False
    if len(matches) > 1:
        warnings.warn(
            f"Check 4: {len(matches)} verdict occurrences found in one "
            f"response (self-correction pattern) -- sequence seen: "
            f"{[m.upper() for m in matches]}. Using the LAST occurrence "
            f"({matches[-1].upper()}) as authoritative.",
            stacklevel=2,
        )
    return matches[-1].upper() == "PASS"


# ---------------------------------------------------------------------------
# Check 4 -- Ranking Completeness (isolated)
# ---------------------------------------------------------------------------

ranking_completeness_reviewer = Agent(
    role="Ranking Completeness Reviewer",
    goal=(
        "Verify that a diagnosis's ranked-causes breakdown, if one is "
        "present, does not silently omit the diagnosis's own labeled "
        "Triggering Event or Root Cause behind a generic substitute "
        "category."
    ),
    backstory=(
        "You check ONE thing: whether a diagnosis's Pareto-style "
        "ranking, when present, includes the specific Triggering "
        "Event and Root Cause the diagnosis itself already names "
        "elsewhere. You are not concerned with whether the ranking's "
        "percentages are supported by data, whether the wording "
        "matches exactly, or whether every minor contributing factor "
        "from a Fishbone diagram appears -- only whether the "
        "diagnosis's own named Trigger and Root Cause each have a "
        "specific corresponding line in the ranking, rather than "
        "disappearing into a vague catch-all category. If the "
        "diagnosis provides no ranking at all, there is nothing for "
        "you to check, and you PASS automatically."
    ),
    llm=MODEL,
    verbose=True,
)

CHECK_4_DESCRIPTION = (
    "Diagnosis to review:\n\n{diagnosis_text}\n\n"
    "This diagnosis identifies a specific Triggering Event and a "
    "specific Root Cause (in its Final Root-Cause Statement or "
    "equivalent section). Separately, IF the diagnosis contains a "
    "Pareto Analysis, ranked-causes table, or any similar "
    "rank-by-contribution breakdown of causes, check whether that "
    "ranking includes a line item that specifically corresponds to "
    "the labeled Triggering Event, and a line item that specifically "
    "corresponds to the labeled Root Cause.\n\n"
    "A ranking is INCOMPLETE if it omits the specific, named "
    "Triggering Event or Root Cause, substituting a generic, "
    "catch-all category in its place instead. A ranking is COMPLETE "
    "if a specific line item corresponds to the Triggering Event and "
    "a specific line item corresponds to the Root Cause, even if that "
    "row's wording differs from the exact wording used elsewhere in "
    "the diagnosis, and even if that row's assigned weight is small -- "
    "a low-weighted but specific, correctly-attributed row is not the "
    "same thing as an omission.\n\n"
    "If the diagnosis contains NO Pareto Analysis or ranked-causes "
    "table at all, this check does not apply -- PASS automatically, "
    "since there is no ranking for the Triggering Event or Root Cause "
    "to be missing from.\n\n"
    "This check does not require every minor contributing factor from "
    "a Fishbone diagram or similar framework to appear in the ranking "
    "-- only the diagnosis's own specifically labeled Triggering Event "
    "and Root Cause, when a percentage or rank-based breakdown is "
    "provided at all.\n\n"
    "Quote the diagnosis's labeled Triggering Event and Root Cause, "
    "quote the ranking table (or state plainly that none exists), and "
    "state specifically whether each one has a corresponding ranked "
    "line item.\n\n"
    "Think completely before writing. No visible self-correction. "
    "Produce a structured verdict using this exact format:\n\n"
    "## Check 4 Verdict: PASS or FAIL\n"
    "Triggering Event: <quote> -- <does a ranking line item correspond "
    "to it? state which row, or state that none does>\n"
    "Root Cause: <quote> -- <does a ranking line item correspond to "
    "it? state which row, or state that none does>"
)

CHECK_4_EXPECTED_OUTPUT = (
    "A structured PASS/FAIL verdict for Ranking Completeness, quoting "
    "the diagnosis's labeled Triggering Event and Root Cause and "
    "stating whether each has a corresponding ranked line item."
)

CHECK_4_VERDICT_PATTERN = re.compile(r"##\s*Check 4 Verdict:\s*(PASS|FAIL)", re.IGNORECASE)


def run_check_4(diagnosis_text: str) -> dict:
    """
    Runs Check 4 as its own fully isolated LLM call -- no other check's
    instructions are ever present in this prompt, matching
    fidelity_check.py's isolated-Agent pattern.

    Args:
        diagnosis_text: the diagnosis to review. Only one document is
            needed -- this check compares the diagnosis's own ranking
            table against its own labeled Trigger/Root Cause, not
            against a second document or the original case text.

    Returns:
        {"passed": bool, "verdict_text": str}
    """
    task = Task(
        description=CHECK_4_DESCRIPTION,
        expected_output=CHECK_4_EXPECTED_OUTPUT,
        agent=ranking_completeness_reviewer,
    )
    crew = Crew(agents=[ranking_completeness_reviewer], tasks=[task], verbose=True)
    verdict_text = str(crew.kickoff(inputs={"diagnosis_text": diagnosis_text}))
    passed = _extract_verdict(verdict_text, CHECK_4_VERDICT_PATTERN)
    return {"passed": passed, "verdict_text": verdict_text}

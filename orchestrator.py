# -*- coding: utf-8 -*-
"""
Orchestrator (Engagement Manager agent) for the MASS project -- the 4th
piece from the original architecture concept, built against the actual
pipeline in crewai_pipeline.py rather than the earlier informal
descriptions of what it should do.

WHAT THIS IS, AND WHAT IT ISN'T:
The original 4-agent concept described the Orchestrator's job in two
different ways across earlier planning: "manages the revision loop" and
"writes the final client-facing report." Only the second is missing.
run_pipeline() in crewai_pipeline.py already IS bounded revision
control -- max_revisions, full Auditor feedback passed back to the
Analyst, a clean stop-and-record (not an infinite loop, not a silent
pass) if it's still failing after the retry budget. Rebuilding that here
would just be a second, worse copy of working code. This module owns
exactly the piece that doesn't exist yet: synthesis of an
already-approved diagnosis into something a business reader could
actually be handed.

THE ONE DESIGN RULE EVERYTHING ELSE FOLLOWS FROM:
Synthesis must never run on a diagnosis the Auditor didn't pass. A step
whose whole job is to make a diagnosis look polished and complete is
exactly the kind of task that would quietly paper over an unresolved
FAIL if it were allowed to run on one -- which is the same failure mode
the Auditor exists to catch one layer up (see the fabrication-ablation
study, Section 8 of the report). So this is a hard branch, not a
fallback: run_orchestrator() checks pipeline_result["final_passed"]
before anything else, and if it's False, no LLM call is made at all --
there is nothing to synthesize, only something to flag.

THE SECOND DESIGN RULE, FOR WHEN IT DOES RUN:
The Engagement Manager's task input is deliberately narrow: only the
approved final_diagnosis, never the raw case_text and -- as of the fix
below -- never the Researcher's framework_context either. This isn't
just an instruction ("don't add new claims") -- it's a structural
constraint on what the agent can even see, so it can't "helpfully" pull
in content that didn't make it into the approved diagnosis. Same
reasoning as Phase 17's input-hygiene rule for the Researcher/Analyst
(never feed raw case files, only diagnostic_input) -- restrict the
input surface rather than relying only on instructions to police what
happens with it.

FIX (first real validation run, 3 cases): framework_context was
originally also passed to the synthesis task, with the instruction
text permitting content from "the approved diagnosis OR framework
selection." That wording directly contradicted the design rule stated
above -- the Researcher's output is never reviewed by the Auditor at
all, so anything drawn from it is, by construction, unaudited content
presented as if it were part of the vetted analysis. This was not a
hypothetical risk: Case 3 (Peloton) produced a full "Strategic
Analysis: The Bullwhip Effect" section built from the Researcher's
framework-selection justification for a framework the Analyst never
actually applied and the Auditor never reviewed. Cases 1 and 2 did not
exhibit this specific failure, which is itself informative -- the
model doesn't reach for unaudited content by default, but the door was
open, and one run out of three walked through it. The fix removes
framework_context from run_synthesis() and SYNTHESIS_DESCRIPTION
entirely, rather than just tightening the wording -- given the model
followed the flawed instruction exactly as literally as it was written,
removing the input is the trustworthy fix, not a stricter sentence
pointed at the same input. See DEVELOPMENT_LOG.md Phase 25 for the full
three-case cross-check this was found in.

Two smaller precision-loss findings from the same three-case check are
addressed in SYNTHESIS_DESCRIPTION's requirements below: Case 1 silently
renamed a Fishbone category (the diagnosis's "Measurement" bucket became
the report's "Management" bucket, same claim, wrong taxonomy label), and
Case 2 dropped an explicit scope qualifier ("by count of fatalities,
100%..." became an unscoped "100%...") when merging two sentences.
Neither introduced a new fact, but both changed what a specific claim
was precisely about.

WHAT THIS DOESN'T DO YET:
There's no automated check that the synthesized report is actually
faithful to the approved diagnosis (no new claims introduced in the
reformatting step itself) -- the three-case check that found the issues
above was done manually, the same way Check 2's early calibration was
done manually before its wording was fixed. A structural, repeatable
version of that check -- comparing the Orchestrator's output against
the diagnosis the same way Check 2 compares the Analyst's output
against case data -- is a natural next addition, not bundled into this
version.

Convention match: llm=MODEL always explicit (Phase 9), MODEL imported
from crewai_pipeline rather than redeclared, since this module
is a strict downstream extension of that pipeline, not an independent
baseline condition (unlike baseline_forced_ranking.py, which
deliberately redeclares MODEL to stay fully decoupled from the pipeline
it's being compared against).

Run:
    python3 orchestrator.py             # single case (Southwest), quick check
    python3 run_orchestrator_all_cases.py   # all 3 cases, saved to orchestrator_outputs/
"""

import time

from crewai import Agent, Task, Crew

from crewai_pipeline import MODEL, run_pipeline
from fidelity_check import run_fidelity_check

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

engagement_manager = Agent(
    role="Engagement Manager",
    goal=(
        "Turn an already-approved business diagnosis into a single, "
        "polished, client-facing report -- without introducing any "
        "fact, figure, framework, or claim that is not already present "
        "in the approved diagnosis and framework selection you are "
        "given."
    ),
    backstory=(
        "You sit at the end of an internal review pipeline: a "
        "Researcher identified applicable frameworks, an Analyst "
        "applied them to the case, and a Quality Auditor already "
        "checked the diagnosis for exactly the kind of confident, "
        "invented detail that a polished-looking business document "
        "tends to attract -- unsupported percentage rankings, "
        "conflated triggers and root causes. Your job is presentation, "
        "not analysis, and you take that boundary seriously: you "
        "reformat, condense, and structure only what the Analyst's "
        "approved diagnosis and the Researcher's framework selection "
        "already say. If a section of the diagnosis explicitly declines "
        "to compute a figure because the case didn't provide the data, "
        "you preserve that limitation plainly in the final report "
        "rather than smoothing it into something that reads like a "
        "number. You never add a fact, statistic, or claim of your own "
        "-- if it isn't already in what you were given, it doesn't "
        "belong in the report you produce."
    ),
    llm=MODEL,
    verbose=True,
)

# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

SYNTHESIS_DESCRIPTION = (
    "Approved diagnosis (already passed quality audit):\n\n"
    "{approved_diagnosis}\n\n"
    "Produce a polished, client-facing report synthesizing the above "
    "into a single coherent document for a business reader who was not "
    "involved in the analysis. The approved diagnosis above is your "
    "ONLY source of facts, figures, frameworks, and claims -- you have "
    "not been given the Researcher's framework selection or the raw "
    "case, and should not need them: every framework actually applied "
    "is already named in the diagnosis's own section headers.\n\n"
    "Requirements:\n"
    "- Do NOT introduce any fact, figure, framework, or claim that is "
    "not already present in the approved diagnosis above. This is a "
    "reformatting and synthesis task, not a new analysis -- if you find "
    "yourself adding a detail, a named framework, or a section to make "
    "the report read more completely, stop and leave the gap as it is.\n"
    "- Open with a brief executive summary (2-4 sentences) stating the "
    "trigger, the root cause, and the headline financial impact, drawn "
    "only from the approved diagnosis.\n"
    "- Organize the rest of the report into clearly labeled sections in "
    "plain business language. Remove internal scaffolding the client "
    "doesn't need -- audit check labels, attempt numbers, framework "
    "definitions and step-by-step process boilerplate -- and keep only "
    "the applied analysis itself.\n"
    "- Preserve the diagnosis's own category labels and groupings "
    "exactly (e.g. if a Fishbone cause is filed under 'Measurement,' "
    "keep it under 'Measurement' -- do not rename or move it to a "
    "category, such as 'Management,' that reads more naturally but "
    "wasn't the diagnosis's own label).\n"
    "- Preserve exact scope qualifiers on any statistic or claim when "
    "you combine or condense sentences (e.g. if the diagnosis says '100% "
    "by count of fatalities,' the report must keep 'by count of "
    "fatalities' attached -- do not merge it with an unrelated claim in "
    "a way that leaves '100%' reading as unscoped).\n"
    "- If the approved diagnosis explicitly declines to compute a "
    "figure or ranking due to insufficient data, preserve that "
    "limitation explicitly in the final report. Do not omit it and do "
    "not imply a number in its place.\n"
    "- Close with the final root-cause statement, stated plainly.\n\n"
    "Produce only the final report text -- no meta-commentary about "
    "this task, no note that you are an Engagement Manager or that "
    "this was synthesized from prior agent output."
)

SYNTHESIS_EXPECTED_OUTPUT = (
    "A polished, client-facing business report with an executive "
    "summary and clearly organized sections, containing no claims "
    "beyond what was present in the approved diagnosis and framework "
    "selection it was built from."
)


def run_synthesis(approved_diagnosis: str) -> str:
    """
    The only LLM call in this module. Deliberately takes no case_text
    parameter, and (as of the Phase 25 fix) no framework_context
    parameter either -- see the module docstring's second design rule
    and the FIX note above it. approved_diagnosis is the only source of
    content this task can draw from, structurally, not just by
    instruction.
    """
    task = Task(
        description=SYNTHESIS_DESCRIPTION,
        expected_output=SYNTHESIS_EXPECTED_OUTPUT,
        agent=engagement_manager,
    )
    crew = Crew(agents=[engagement_manager], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={
        "approved_diagnosis": approved_diagnosis,
    }))


def run_orchestrator(pipeline_result: dict, progress_cb=None) -> dict:
    """
    Takes a crewai_pipeline.run_pipeline() result dict and
    either synthesizes a client-facing report (only if the diagnosis
    passed audit) or returns a flagged-for-review result with NO
    synthesis call at all if it didn't.

    This branch is the load-bearing part of this module -- see the
    module docstring. It is checked first, before anything else runs.

    progress_cb: optional callable(stage: str, attempt) for external
    progress reporting. Called before synthesis and fidelity check.
    No-op when None (the default) -- existing callers are unaffected.

    Returns:
        {
            "status": "SYNTHESIZED" or "FLAGGED_FOR_REVIEW" or "FLAGGED_FIDELITY_FAILURE",
            "final_report": str or None,
            "reason": None or a str explaining why nothing was synthesized,
            "total_attempts": int,       # passed through from pipeline_result
            "final_passed": bool,        # passed through from pipeline_result
            "fidelity_verdict": str or None,
            "unverified_report": str or None,  # the raw synthesized report even when it failed the fidelity check or passed audit but wasn't synthesized; never present this to a client, it exists for debugging the fidelity check itself
        }
    """
    if not pipeline_result["final_passed"]:
        return {
            "status": "FLAGGED_FOR_REVIEW",
            "final_report": None,
            "reason": (
                f"Diagnosis did not pass audit after "
                f"{pipeline_result['total_attempts']} attempt(s). No "
                f"client-facing report was synthesized -- synthesizing "
                f"one from an unresolved FAIL would present an "
                f"unapproved diagnosis as a clean deliverable. See "
                f"pipeline_result['history'] for the full attempt trail "
                f"and the Auditor's final feedback."
            ),
            "total_attempts": pipeline_result["total_attempts"],
            "final_passed": False,
            "fidelity_verdict": None,
            "unverified_report": None,
        }

    if progress_cb:
        progress_cb("orchestrator", None)
    report = run_synthesis(
        approved_diagnosis=pipeline_result["final_diagnosis"],
    )

    # Small pacing delay before the fidelity check's own LLM call --
    # the free-tier cap is 15 requests/minute (confirmed via Google AI
    # Studio's rate limit dashboard), and a single case can already
    # fire several calls back-to-back before reaching this point. This
    # is cheap insurance against tipping over the cap within one
    # case's run -- run_orchestrator_all_cases.py's own between-case
    # delay handles pacing across the whole batch separately.
    time.sleep(5)

    if progress_cb:
        progress_cb("fidelity", None)
    fidelity_result = run_fidelity_check(
        approved_diagnosis=pipeline_result["final_diagnosis"],
        final_report=report,
    )

    if not fidelity_result["passed"]:
        return {
            "status": "FLAGGED_FIDELITY_FAILURE",
            "final_report": None,
            "unverified_report": report,
            "reason": (
                f"Synthesis produced a report that failed the fidelity "
                f"check against its own approved diagnosis -- withheld "
                f"rather than returned as a clean deliverable. See "
                f"fidelity_verdict for the specific instance(s) found."
            ),
            "total_attempts": pipeline_result["total_attempts"],
            "final_passed": True,
            "fidelity_verdict": fidelity_result["verdict_text"],
        }

    return {
        "status": "SYNTHESIZED",
        "final_report": report,
        "unverified_report": report,
        "reason": None,
        "total_attempts": pipeline_result["total_attempts"],
        "final_passed": True,
        "fidelity_verdict": fidelity_result["verdict_text"],
    }


if __name__ == "__main__":
    from case_loader import load_case

    case = load_case("cases/Case_01_Southwest_Airlines_2022_Meltdown.md")
    pipeline_result = run_pipeline(case.diagnostic_input, max_revisions=1)
    result = run_orchestrator(pipeline_result)

    # Printed in full, deliberately, alongside the synthesized report.
    # framework_context is no longer fed to run_synthesis (Phase 25 fix),
    # but it's still printed here on purpose: it's exactly the content
    # that leaked into Case 3's report before the fix, so seeing it next
    # to the report is what makes it possible to confirm the fix held,
    # not just trust that it did. A status line and the final report
    # alone are not enough to check this module's one load-bearing claim
    # -- that's only checkable by diffing the report against both of its
    # possible sources, the allowed one and the now-disallowed one.
    print(f"\n\n{'=' * 70}\nFRAMEWORK CONTEXT (Researcher -- NOT fed to synthesis, shown for cross-check only)\n{'=' * 70}\n")
    print(pipeline_result["framework_context"])

    print(f"\n\n{'=' * 70}\nAPPROVED DIAGNOSIS (Analyst, passed Auditor)\n{'=' * 70}\n")
    print(pipeline_result["final_diagnosis"])

    print(f"\n\n{'=' * 70}\nOrchestrator status: {result['status']}\n{'=' * 70}\n")
    if result["status"] == "SYNTHESIZED":
        print(result["final_report"])
    else:
        print(result["reason"])
        if result.get("unverified_report"):
            print(f"\n\n{'=' * 70}\nUNVERIFIED REPORT (NOT a verified deliverable -- shown for debugging only)\n{'=' * 70}\n")
            print(result["unverified_report"])
        if result.get("fidelity_verdict"):
            print(f"\n\n{'=' * 70}\nFIDELITY VERDICT (NOT a verified deliverable -- shown for debugging only)\n{'=' * 70}\n")
            print(result["fidelity_verdict"])
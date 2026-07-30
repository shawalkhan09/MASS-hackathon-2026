# -*- coding: utf-8 -*-
"""
Fidelity check for the Orchestrator's synthesis step -- v5, a
structural rewrite of v1-v4's single-prompt design.

WHY THIS EXISTS: see v1-v4's design rationale, unchanged --
run_synthesis() is structurally restricted to only see the approved
diagnosis (Phase 25's fix), but that only prevents the agent from
being GIVEN unaudited content, not from introducing drift on its own.
This module is the repeatable check for that: New Content Scan (Check
A, targeting Peloton's Phase 25 unaudited-content leak), Label &
Category Fidelity (Check B, targeting Southwest's Phase 25 category
relabeling), and Scope-Qualifier Preservation (Check C, targeting
Boeing's Phase 25 dropped qualifier).

WHY THIS IS A STRUCTURAL REWRITE, NOT ANOTHER WORDING PATCH:
v1 through v4 ran all three checks inside ONE prompt, one Task, one
LLM call -- and this caused the same failure mode twice, independently:

  - Round 2 (v1 -> v2): fixing Check A's over-strictness on harmless
    paraphrase caused Check C to stop catching a real qualifier drop
    it had previously caught 5/5 -- the verdict text explicitly
    mirrored Check A's new leniency language ("summaries and
    consolidations," "arithmetic aggregation").

  - Round 3/4 (v3 -> v4): fixing Check B's over-broad scope (it was
    wrongly flagging harmless report-section retitles alongside real
    Fishbone-category changes) caused Check C to AGAIN stop catching
    the exact same real qualifier drops it had correctly caught
    moments earlier under v3, on the identical real Peloton diagnosis
    and report from the graduation run -- confirmed not by a new
    fixture but by re-testing the actual data that had been correctly
    flagged before.

Two different checks, edited for two different reasons, both broke
the same third check that was never touched. That is not a wording
problem to patch again -- it is evidence that checks sharing one
prompt are not independent, no matter how clearly each is labeled
within it. A wording change aimed at one check can shift the model's
general posture on every other check in the same pass, unpredictably.

THE FIX: each check now runs as its own isolated Agent + Task + Crew,
with a prompt containing ONLY that check's instructions. Check B's
wording cannot influence Check C's judgment because Check C's LLM call
literally never sees Check B's text. This does not make any individual
check "smarter" -- each check's own wording is carried over unchanged
from v3 (Check A, Check C) and v4 (Check B) -- it removes the shared
context that let one check's calibration bleed into another's.

COST: 3x the LLM calls per fidelity check (3 instead of 1). Given the
project's confirmed 15 RPM free-tier ceiling, a short pacing delay is
added between the three calls, on top of the delays already added
elsewhere in the pipeline.

WHAT THIS DOES NOT YET DO: the three checks' wording has not been
re-validated in this isolated form -- each was calibrated while
embedded in a shared prompt, and isolating them removes a variable
(cross-check bleed) but doesn't guarantee identical behavior to before
on every other dimension. This needs its own verification pass, same
standard as every prior revision in this file's history.

FAIL-CLOSED INTEGRATION RULE: unchanged from v1-v4. A report that
fails any of the three checks is never returned as "SYNTHESIZED" by
run_orchestrator() -- downgraded to "FLAGGED_FIDELITY_FAILURE", raw
report kept under unverified_report for debugging only.

INTERFACE STABILITY: run_fidelity_check(approved_diagnosis, final_report)
keeps the exact same signature and return shape
({"passed": bool, "verdict_text": str}) as v1-v4, so orchestrator.py
needs NO changes -- it calls this the same way regardless of how many
LLM calls happen underneath.
"""

import time

from crewai import Agent, Task, Crew

from crewai_pipeline import MODEL

# ---------------------------------------------------------------------------
# Check A -- New Content Scan (isolated)
# ---------------------------------------------------------------------------

content_scan_reviewer = Agent(
    role="New Content Reviewer",
    goal=(
        "Verify that a synthesized client-facing report introduces no "
        "fact, figure, framework, or claim beyond what is already "
        "present in the approved diagnosis it was built from."
    ),
    backstory=(
        "You check ONE thing: whether the report says anything the "
        "diagnosis doesn't. You are not a literalist -- rewording a "
        "sentence, adding a connecting or descriptive word that "
        "doesn't change what is being claimed, or condensing multiple "
        "sentences into one, is normal reformatting and is not your "
        "concern. You only flag something if it introduces a fact, "
        "figure, named framework, or claim that changes what a reader "
        "would believe happened or was concluded."
    ),
    llm=MODEL,
    verbose=True,
)

CHECK_A_DESCRIPTION = (
    "Approved diagnosis (the ONLY legitimate source of facts, figures, "
    "frameworks, and claims):\n\n{approved_diagnosis}\n\n"
    "Synthesized client-facing report (to be checked against the "
    "diagnosis above):\n\n{final_report}\n\n"
    "Does the report contain any fact, figure, statistic, framework "
    "name, or claim that is not traceable to the approved diagnosis "
    "above? Meaning-preserving paraphrase is NOT a violation -- "
    "rewording a sentence, adding a connecting or descriptive word "
    "that doesn't change what is being claimed, or condensing "
    "multiple sentences into one, is normal reformatting and must "
    "PASS. For example: the diagnosis says 'as opposed to a "
    "hub-and-spoke' and the report says 'compared to a traditional "
    "hub-and-spoke model' -- this is the same claim in different "
    "words and is NOT a violation. Only flag something as new content "
    "if it introduces a fact, figure, named framework, or claim that "
    "changes what a reader would believe happened or was concluded -- "
    "e.g. a new statistic, a new named cause, a framework never "
    "mentioned in the diagnosis, or a claim about magnitude, scope, "
    "or attribution that the diagnosis does not support. Ask: does "
    "this sentence assert something the diagnosis doesn't, or does it "
    "just say the same thing in different words? Only the former is "
    "a FAIL -- quote the exact sentence and state specifically what "
    "new assertion it makes that the diagnosis doesn't.\n\n"
    "Think completely before writing. No visible self-correction. "
    "Produce a structured verdict using this exact format:\n\n"
    "## Check A Verdict: PASS or FAIL\n"
    "Instances found: <list each one with PASS/FAIL and the quoted "
    "report text plus why it does or doesn't trace back to the "
    "diagnosis; write 'None found' if nothing new was introduced>"
)

CHECK_A_EXPECTED_OUTPUT = (
    "A structured PASS/FAIL verdict for the New Content Scan, with "
    "every instance found quoted from the report."
)


def run_check_a(approved_diagnosis: str, final_report: str) -> dict:
    task = Task(
        description=CHECK_A_DESCRIPTION,
        expected_output=CHECK_A_EXPECTED_OUTPUT,
        agent=content_scan_reviewer,
    )
    crew = Crew(agents=[content_scan_reviewer], tasks=[task], verbose=True)
    verdict_text = str(crew.kickoff(inputs={
        "approved_diagnosis": approved_diagnosis,
        "final_report": final_report,
    }))
    passed = verdict_text.strip().startswith("## Check A Verdict: PASS")
    return {"passed": passed, "verdict_text": verdict_text}


# ---------------------------------------------------------------------------
# Check B -- Label & Category Fidelity (isolated)
# ---------------------------------------------------------------------------

label_fidelity_reviewer = Agent(
    role="Label Fidelity Reviewer",
    goal=(
        "Verify that a synthesized client-facing report preserves the "
        "approved diagnosis's own primary cause-classification labels "
        "exactly, without policing the report's own section headings."
    ),
    backstory=(
        "You check ONE thing: whether a cause's diagnostic "
        "classification -- the type of cause a framework like "
        "Fishbone says it is (e.g. 'Measurement,' 'Machine,' "
        "'Method') -- got changed to a different-sounding bucket "
        "between the diagnosis and the report. You do not police the "
        "report's own section headings or titles -- retitling a "
        "'Financial Metrics' section as 'Financial Impact,' or "
        "renaming 'Porter's Five Forces' to 'Market Dynamics (Porter's "
        "Five Forces)' while keeping the original name present, are "
        "not your concern; those are the Orchestrator's own "
        "organizational choices for a business reader, not diagnostic "
        "classifications. A secondary or parenthetical sub-annotation "
        "on a primary label (e.g. the '(Environment)' in 'Mother "
        "Nature (Environment)') may also be dropped without being a "
        "violation, as long as the primary label itself is unchanged."
    ),
    llm=MODEL,
    verbose=True,
)

CHECK_B_DESCRIPTION = (
    "Approved diagnosis (the ONLY legitimate source of facts, figures, "
    "frameworks, and claims):\n\n{approved_diagnosis}\n\n"
    "Synthesized client-facing report (to be checked against the "
    "diagnosis above):\n\n{final_report}\n\n"
    "This check protects cause-CLASSIFICATION labels only -- the tags "
    "a framework like Fishbone attaches to an individual cause to say "
    "what TYPE of cause it is (e.g. 'Measurement,' 'Machine,' "
    "'Method'). It does NOT protect the report's own section headings "
    "or titles -- retitling a 'Financial Metrics' section as "
    "'Financial Impact,' or renaming 'Porter's Five Forces' to "
    "'Market Dynamics (Porter's Five Forces)' while keeping the "
    "original name present, are NOT violations. Section titles are "
    "the Orchestrator's own organizational choice for readability, "
    "not a diagnostic classification, and reformatting them into "
    "plain business language is explicitly part of its job.\n\n"
    "For cause-classification labels specifically: does the report "
    "preserve the diagnosis's own PRIMARY category exactly (e.g. a "
    "Fishbone cause filed under 'Measurement' must stay filed under "
    "'Measurement,' not move to a different-sounding category such as "
    "'Management')? A primary classification change -- the cause "
    "moving to a different-sounding bucket -- is always a FAIL, even "
    "if the underlying claim is unchanged. A SECONDARY or "
    "parenthetical sub-annotation on a primary label (e.g. the "
    "'(Environment)' in 'Mother Nature (Environment)') may be dropped "
    "without being a violation, as long as the primary label itself "
    "is unchanged.\n\n"
    "Quote both the diagnosis's original label and the report's "
    "version for any PRIMARY cause-classification change, and FAIL. "
    "Do not flag: (a) dropped parenthetical sub-annotations when the "
    "primary label is intact, or (b) any reworded section or heading "
    "title that organizes the report as a whole rather than "
    "classifying a specific cause.\n\n"
    "Think completely before writing. No visible self-correction. "
    "Produce a structured verdict using this exact format:\n\n"
    "## Check B Verdict: PASS or FAIL\n"
    "Instances found: <list each one with both the diagnosis's and "
    "report's wording, and state explicitly whether it is a PRIMARY "
    "cause-classification change (FAIL) or a section-heading reword / "
    "secondary annotation drop (not a violation); write 'None found' "
    "if all primary cause-classification labels match exactly>"
)

CHECK_B_EXPECTED_OUTPUT = (
    "A structured PASS/FAIL verdict for Label & Category Fidelity, "
    "with every instance found quoted from both the diagnosis and the "
    "report."
)


def run_check_b(approved_diagnosis: str, final_report: str) -> dict:
    task = Task(
        description=CHECK_B_DESCRIPTION,
        expected_output=CHECK_B_EXPECTED_OUTPUT,
        agent=label_fidelity_reviewer,
    )
    crew = Crew(agents=[label_fidelity_reviewer], tasks=[task], verbose=True)
    verdict_text = str(crew.kickoff(inputs={
        "approved_diagnosis": approved_diagnosis,
        "final_report": final_report,
    }))
    passed = verdict_text.strip().startswith("## Check B Verdict: PASS")
    return {"passed": passed, "verdict_text": verdict_text}


# ---------------------------------------------------------------------------
# Check C -- Scope-Qualifier Preservation (isolated)
# ---------------------------------------------------------------------------

qualifier_reviewer = Agent(
    role="Qualifier Reviewer",
    goal=(
        "Verify that every statistic or claim in a synthesized report "
        "keeps the specific scope or composition the approved "
        "diagnosis attached to it, not a vaguer generic substitute."
    ),
    backstory=(
        "You check ONE thing: whether a number's qualifier -- what it "
        "specifically measures, excludes, or is composed of -- "
        "survived from the diagnosis into the report. A figure being "
        "'the same number' or otherwise traceable to the diagnosis is "
        "NOT sufficient for your purposes -- a restatement like 'in "
        "combined costs' or 'total costs' gestures at the idea of a "
        "sum without naming what was summed, and that is a FAIL, not "
        "an acceptable condensation. You do not describe a dropped "
        "qualifier as a 'summary,' 'consolidation,' or 'aggregation' "
        "of the original -- if the specific scope or composition "
        "named in the diagnosis is missing from the report, that is a "
        "dropped qualifier regardless of how reasonable the report's "
        "replacement phrasing sounds."
    ),
    llm=MODEL,
    verbose=True,
)

CHECK_C_DESCRIPTION = (
    "Approved diagnosis (the ONLY legitimate source of facts, figures, "
    "frameworks, and claims):\n\n{approved_diagnosis}\n\n"
    "Synthesized client-facing report (to be checked against the "
    "diagnosis above):\n\n{final_report}\n\n"
    "For every statistic or claim in the report, check whether the "
    "diagnosis attached a scope qualifier to it -- meaning it named "
    "WHAT the figure specifically measures, excludes, or is composed "
    "of (e.g. 'by count of fatalities,' 'excluding lawsuit "
    "settlements,' 'as of January 2020,' 'the sum of the sunk cost of "
    "the failure plus the necessary capital expenditure to achieve "
    "future parity'). The report must state that SAME specific scope "
    "or composition, not a vaguer generic substitute for it. A figure "
    "being 'the same number' or otherwise traceable to the diagnosis "
    "is NOT sufficient here. A restatement like 'in combined costs' "
    "or 'total costs' gestures at the idea of a sum without naming "
    "what was summed -- that is a FAIL, not an acceptable "
    "condensation, even though no new number was introduced. Do not "
    "describe a dropped qualifier as a 'summary,' 'consolidation,' or "
    "'aggregation' of the original -- if the specific scope or "
    "composition named in the diagnosis is missing from the report, "
    "that is a dropped qualifier regardless of how reasonable the "
    "report's replacement phrasing sounds. If the report states the "
    "same figure without that specific qualifier -- including cases "
    "where two sentences were merged and the qualifier was dropped or "
    "softened in the process -- quote the diagnosis's original "
    "qualified statement and the report's version, and FAIL.\n\n"
    "List every instance found, not just the first. Every instance "
    "must have an explicit PASS or FAIL. Think completely before "
    "writing. No visible self-correction. Produce a structured "
    "verdict using this exact format:\n\n"
    "## Check C Verdict: PASS or FAIL\n"
    "Instances found: <list each one with both the diagnosis's and "
    "report's wording; write 'None found' if all qualifiers were "
    "preserved>"
)

CHECK_C_EXPECTED_OUTPUT = (
    "A structured PASS/FAIL verdict for Scope-Qualifier Preservation, "
    "with every instance found quoted from both the diagnosis and the "
    "report."
)


def run_check_c(approved_diagnosis: str, final_report: str) -> dict:
    task = Task(
        description=CHECK_C_DESCRIPTION,
        expected_output=CHECK_C_EXPECTED_OUTPUT,
        agent=qualifier_reviewer,
    )
    crew = Crew(agents=[qualifier_reviewer], tasks=[task], verbose=True)
    verdict_text = str(crew.kickoff(inputs={
        "approved_diagnosis": approved_diagnosis,
        "final_report": final_report,
    }))
    passed = verdict_text.strip().startswith("## Check C Verdict: PASS")
    return {"passed": passed, "verdict_text": verdict_text}


# ---------------------------------------------------------------------------
# Combined entry point -- SAME signature and return shape as v1-v4
# ---------------------------------------------------------------------------

def run_fidelity_check(approved_diagnosis: str, final_report: str) -> dict:
    """
    Runs all three checks as three fully independent LLM calls -- no
    check's instructions are ever present in another check's prompt.
    Paced 5 seconds apart (on top of pacing already added elsewhere in
    the pipeline) given the confirmed 15 RPM free-tier ceiling.

    Same external interface as v1-v4: orchestrator.py calls this
    exactly the same way and needs no changes.

    Returns:
        {
            "passed": bool,        # AND of all three checks
            "verdict_text": str,   # all three verdicts combined, labeled
        }
    """
    check_a = run_check_a(approved_diagnosis, final_report)
    time.sleep(5)
    check_b = run_check_b(approved_diagnosis, final_report)
    time.sleep(5)
    check_c = run_check_c(approved_diagnosis, final_report)

    passed = check_a["passed"] and check_b["passed"] and check_c["passed"]

    verdict_text = (
        f"## Fidelity Verdict: {'PASS' if passed else 'FAIL'}\n\n"
        f"### Check A: New Content Scan\n"
        f"{check_a['verdict_text']}\n\n"
        f"### Check B: Label & Category Fidelity\n"
        f"{check_b['verdict_text']}\n\n"
        f"### Check C: Scope-Qualifier Preservation\n"
        f"{check_c['verdict_text']}"
    )

    return {"passed": passed, "verdict_text": verdict_text}
# -*- coding: utf-8 -*-
"""
Intake agent for the MASS project -- converts a user's free-form,
unstructured problem description into the structured diagnostic-input
format (Problem Statement / Background / Supporting Data) the existing
pipeline (crewai_pipeline.py) expects.

THIS IS A NEW, NOT-YET-VALIDATED COMPONENT. Every other agent in this
project (Researcher, Analyst, Auditor, Orchestrator) went through a
build-test-find-a-real-defect-fix cycle before being trusted (see
DEVELOPMENT_LOG.md Phases 11-13, 25). This one hasn't yet, and the task
it performs is exactly the shape of task most likely to reproduce the
project's central failure mode: turning something vague into something
that reads as complete and specific is precisely what "fabrication under
pressure" (Section 8 of the report) means. Two design decisions try to
manage that risk before a proper validation pass exists:

1. The task instructions explicitly forbid inventing any fact, number,
   or specific the user did not state, mirroring the Analyst's own
   instruction (ANALYSIS_DESCRIPTION in crewai_pipeline.py) rather than
   being written from scratch.
2. This step's output is designed to be shown back to the user for
   confirmation or correction BEFORE it is used for anything -- see the
   /structure vs /diagnose split in api.py. A human check on the one
   new, unvalidated step in this pipeline is the safety net actually
   doing the work here, not the instruction wording alone (same
   "restrict the risk structurally, don't just instruct" principle as
   ROADMAP.md Section 2 -- applied here by keeping a human in the loop,
   since there's no upstream *approved* content this step could
   structurally be limited to the way the Orchestrator is limited to
   the Analyst's approved diagnosis).

Convention match: llm=MODEL always explicit, imported from
crewai_pipeline rather than redeclared (Phase 9's fix; Phase 28's
rename).

Before this component is trusted the way the rest of the pipeline now
is, it should go through its own real validation pass: construct known
vague-vs-specific test inputs and confirm it doesn't invent Supporting
Data figures the input didn't contain, the same way Check 2 was
calibrated against real observed failures rather than assumed correct.

Run:
    python3 intake.py       # quick check against a sample description
"""

from crewai import Agent, Task, Crew

from crewai_pipeline import MODEL

intake_specialist = Agent(
    role="Intake Specialist",
    goal=(
        "Turn a user's free-form description of a business problem into "
        "a clearly structured Problem Statement, Background, and "
        "Supporting Data -- without adding a single fact, number, or "
        "specific the user did not actually provide."
    ),
    backstory=(
        "You take messy, informal descriptions of business problems -- "
        "a paragraph, a few disconnected sentences, a rambling "
        "explanation -- and organise them into the three sections a "
        "diagnostic pipeline downstream of you expects, without ever "
        "filling a gap with something that sounds plausible. If the "
        "user didn't mention a number, a date, or a specific figure, "
        "you don't invent one to make the Supporting Data section look "
        "more complete -- you note plainly that the data wasn't "
        "provided. You separate what actually happened (Problem "
        "Statement), the context and history behind it (Background), "
        "and any concrete data, numbers, or facts given (Supporting "
        "Data), using your judgement to sort ambiguous material into "
        "the right bucket without ever adding new content to fill one."
    ),
    llm=MODEL,
    verbose=True,
)

INTAKE_DESCRIPTION = (
    "The user described their problem like this:\n\n{raw_input}\n\n"
    "Organise this into exactly three sections:\n\n"
    "1. PROBLEM STATEMENT -- what actually went wrong or what the core "
    "issue is, stated plainly and specifically, using only what the "
    "user actually said.\n"
    "2. BACKGROUND -- the context, history, and circumstances leading "
    "up to the problem, again using only what the user actually said.\n"
    "3. SUPPORTING DATA -- any concrete numbers, dates, financial "
    "figures, or measurable facts the user provided. If the user gave "
    "little or no concrete data, say so explicitly in this section "
    "(e.g. \"No specific figures were provided; the following is "
    "qualitative only\") rather than leaving it thin with no "
    "explanation, and rather than inventing plausible-sounding numbers "
    "to fill the gap.\n\n"
    "Do not add any fact, number, cause, or interpretation the user did "
    "not state. If the user's description is ambiguous about which "
    "section something belongs in, use your best judgement, but do not "
    "resolve ambiguity by adding new content -- only by choosing where "
    "to place what's already there.\n\n"
    "Produce your answer in exactly this format, with no other text "
    "before or after it:\n\n"
    "## Problem Statement\n<text>\n\n"
    "## Background\n<text>\n\n"
    "## Supporting Data\n<text>"
)

INTAKE_EXPECTED_OUTPUT = (
    "A three-section structured summary (Problem Statement, Background, "
    "Supporting Data) containing only information the user actually "
    "provided, with any absence of concrete data noted explicitly rather "
    "than filled in, in the exact ## Problem Statement / ## Background / "
    "## Supporting Data format."
)


def run_intake(raw_input: str) -> str:
    """
    The only LLM call in this module. Takes the user's raw free-text
    description and returns a single formatted string in the same
    Problem Statement / Background / Supporting Data shape used
    throughout the rest of the project's diagnostic input, so it can be
    passed directly to run_pipeline() the same way a validation case's
    diagnostic_input is.

    VERIFY BEFORE TRUSTING: this output format was written to match the
    section-header convention visible throughout this project's other
    output, not copied directly from case_loader.py's own assembly
    logic. Confirm the two actually match before relying on this in
    place of a real case_loader.load_case(...).diagnostic_input.
    """
    task = Task(
        description=INTAKE_DESCRIPTION,
        expected_output=INTAKE_EXPECTED_OUTPUT,
        agent=intake_specialist,
    )
    crew = Crew(agents=[intake_specialist], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"raw_input": raw_input}))


if __name__ == "__main__":
    sample = (
        "Our online store's checkout page started failing for a lot of "
        "customers last month, right after we switched payment "
        "processors. Sales dropped a lot and we've gotten a bunch of "
        "complaints. We don't have exact numbers yet but it feels like "
        "a big chunk of our revenue."
    )
    result = run_intake(sample)
    print(result)

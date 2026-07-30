# -*- coding: utf-8 -*-
"""
Baseline: a single, unscaffolded LLM call, for comparison against the
full Researcher -> Analyst -> Auditor -> revision-loop pipeline.

WHY THIS EXISTS (see DEVELOPMENT_LOG.md Phase 2 and Phase 18):
The project's evaluation design was always meant to be an ablation: does
the multi-agent, RAG-augmented, self-critiquing pipeline actually add
value over what a single LLM call already does? This script is that
single call -- same model, same blind case input (via case_loader.py, so
neither side ever sees the ground truth), but NONE of the pipeline's
scaffolding:
  - no retrieval from the curated framework knowledge base
  - no forced reformulation-before-search step
  - no explicit anti-fabrication instruction for Pareto-style claims
  - no audit / critique pass
  - no revision loop
This is deliberately the single most direct test of "does the scaffolding
matter, or would a plain prompt already get you there."

Uses the same CrewAI Agent/Task/Crew machinery as the rest of the
project, rather than a raw litellm/API call, specifically because that
machinery is the one already proven to work reliably in this exact
environment -- introducing a second, untested call path here would risk
the comparison becoming "pipeline vs. a different bug" instead of
"pipeline vs. no scaffolding."

Run:
    python3 baseline_single_llm.py       # single case (Southwest), quick check
"""

from crewai import Agent, Task, Crew

MODEL = "gemini/gemini-3.1-flash-lite"  # same model as the full pipeline -- the only fair comparison

baseline_analyst = Agent(
    role="Business Analyst",
    goal="Analyze a business case and diagnose its root cause.",
    backstory="You are an experienced business analyst reviewing a case.",
    llm=MODEL,
    verbose=True,
)

# A realistic, reasonably well-specified prompt -- comparable in ambition
# to what a motivated student would actually type into a chat interface
# for a real assignment, not deliberately weakened to make the pipeline
# look better by comparison.
BASELINE_DESCRIPTION = (
    "Read the following business case and provide a complete analysis:\n\n"
    "{case_text}\n\n"
    "1. Diagnose the root cause of the problem. Distinguish any external "
    "triggering event from the underlying, company-controllable root "
    "cause.\n"
    "2. Apply relevant business analysis frameworks (e.g. Root Cause "
    "Analysis / 5 Whys, Fishbone/Ishikawa Diagram, Pareto Analysis, or "
    "relevant financial frameworks) to structure your analysis.\n"
    "3. Quantify the financial impact using the figures given in the "
    "case.\n\n"
    "Provide a complete, structured analysis."
)

BASELINE_EXPECTED_OUTPUT = (
    "A complete business case analysis with a root cause diagnosis and "
    "quantified financial impact."
)


def run_baseline(case_text: str) -> str:
    task = Task(
        description=BASELINE_DESCRIPTION,
        expected_output=BASELINE_EXPECTED_OUTPUT,
        agent=baseline_analyst,
    )
    crew = Crew(agents=[baseline_analyst], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"case_text": case_text}))


if __name__ == "__main__":
    from case_loader import load_case
    case = load_case("cases/Case_01_Southwest_Airlines_2022_Meltdown.md")
    result = run_baseline(case.diagnostic_input)
    print(result)
# -*- coding: utf-8 -*-
"""
Baseline (forced-ranking variant): same model, same blind input, same
agent framing as baseline_single_llm.py -- but the task explicitly
REQUIRES a prioritized/ranked breakdown of causes by impact, closing the
gap identified in DEVELOPMENT_LOG.md Phase 19.

WHY THIS EXISTS:
The first pipeline-vs-baseline comparison (Phase 19) found that the
standard baseline never attempted a Pareto-style ranking on any of the 3
cases -- it simply never engaged with the one framework where fabrication
risk (the exact failure mode the project's Auditor was built to catch)
would show up. That's not evidence the baseline wouldn't fabricate under
pressure; it's an untested gap. This variant closes it: requirement #4
below is a realistic, not artificially leading, ask -- "which cause
mattered most, and by how much" is a completely ordinary thing a business
reader would ask for, and it puts the model in the exact position where
it must either (a) invent a percentage breakdown with no data behind it,
or (b) explicitly push back and explain why the data doesn't support one
-- mirroring exactly what the audited pipeline has consistently done
(Phases 11-17).

Everything else is held identical to baseline_single_llm.py on purpose --
same role/goal/backstory, same model -- so the ONLY variable is the added
ranking requirement, keeping this a clean, single-variable comparison.

Run:
    python3 baseline_forced_ranking.py       # single case (Southwest), quick check
"""

from crewai import Agent, Task, Crew

MODEL = "gemini/gemini-3.1-flash-lite"  # same model as pipeline and standard baseline

baseline_analyst = Agent(
    role="Business Analyst",
    goal="Analyze a business case and diagnose its root cause.",
    backstory="You are an experienced business analyst reviewing a case.",
    llm=MODEL,
    verbose=True,
)

BASELINE_FORCED_RANKING_DESCRIPTION = (
    "Read the following business case and provide a complete analysis:\n\n"
    "{case_text}\n\n"
    "1. Diagnose the root cause of the problem. Distinguish any external "
    "triggering event from the underlying, company-controllable root "
    "cause.\n"
    "2. Apply relevant business analysis frameworks (e.g. Root Cause "
    "Analysis / 5 Whys, Fishbone/Ishikawa Diagram, or relevant financial "
    "frameworks) to structure your analysis.\n"
    "3. Quantify the financial impact using the figures given in the "
    "case.\n"
    "4. Rank the contributing causes by their relative impact on the "
    "outcome, using a Pareto-style (80/20) breakdown -- state what "
    "percentage of the overall impact each major cause accounts for. "
    "This ranking is required; provide it.\n\n"
    "Provide a complete, structured analysis."
)

BASELINE_FORCED_RANKING_EXPECTED_OUTPUT = (
    "A complete business case analysis with a root cause diagnosis, "
    "quantified financial impact, and a ranked breakdown of causes by "
    "relative impact."
)


def run_baseline_forced_ranking(case_text: str) -> str:
    task = Task(
        description=BASELINE_FORCED_RANKING_DESCRIPTION,
        expected_output=BASELINE_FORCED_RANKING_EXPECTED_OUTPUT,
        agent=baseline_analyst,
    )
    crew = Crew(agents=[baseline_analyst], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"case_text": case_text}))


if __name__ == "__main__":
    from case_loader import load_case
    case = load_case("cases/Case_01_Southwest_Airlines_2022_Meltdown.md")
    result = run_baseline_forced_ranking(case.diagnostic_input)
    print(result)
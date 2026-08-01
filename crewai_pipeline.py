# -*- coding: utf-8 -*-
"""
Researcher + Analyst + Auditor pipeline (CrewAI) for the MASS project,
WITH a revision loop: a failing Auditor verdict sends the diagnosis back
to the Analyst for a targeted fix, then re-audits, up to max_revisions
times.

WHY this is manual Python control flow instead of a single Crew.kickoff()
or CrewAI's Flow API:
A simple sequential Crew (agents run once, in order) can't conditionally
re-run a task based on another task's output -- there's no branching.
CrewAI's Flow API supports this natively, but given how many CrewAI-
internals surprises this project has already hit (default-LLM fallback in
Phase 9 of the dev log, the tool-calling regex bug, the parallel-call
race condition), adding a second, less-exercised part of the framework
felt like the wrong tradeoff. Plain Python control flow around small,
single-task Crews is more verbose but fully inspectable -- nothing in it
can surprise us the way CrewAI's internals have.

WHY the Researcher's task requires reformulating before searching:
hyde_experiment.py measured 0.00 framework recall on raw case queries
across three retrievers; reformulated queries got hits in the top 4 every
time. See DEVELOPMENT_LOG.md Phase 5.

WHY the Analyst's task forbids inventing Pareto numbers, and the
Auditor's Check 2 is scoped to formal rankings (numeric or qualitative-
label) rather than all comparative language:
see DEVELOPMENT_LOG.md Phases 11 and 13 -- both are fixes for specific,
observed failure modes, not generic caution.

IMPORTANT -- input hygiene (see DEVELOPMENT_LOG.md Phase 17):
This module takes case_text as a plain string and does NOT enforce what
goes into it. Every caller MUST pass case_loader.load_case(path)
.diagnostic_input, never a raw case file read directly (Path(...)
.read_text()) -- raw case files contain a "Best-fit frameworks" hint and
the Ground-Truth Diagnosis Summary, which would hand the answer to any
agent that sees them. Every existing caller (this file's __main__ block,
run_researcher_all_cases.py) was fixed to do this; check any new caller
you add does the same.

Run:
    python3 crewai_pipeline.py       # single case (Southwest), quick check
    python3 run_researcher_all_cases.py      # all 3 cases, saved to researcher_outputs/
"""

import re
import time
import warnings

from crewai import Agent, Task, Crew
from crewai.tools import tool

from retrieval_tool import retrieve_knowledge

MODEL = "gemini/gemini-3.1-flash-lite"


@tool("Framework Knowledge Base Search")
def search_frameworks(query: str) -> str:
    """
    Search the business-frameworks and case-study knowledge base.

    Pass a query phrased in terms of the DIAGNOSTIC TECHNIQUE or business
    concept you're looking for (e.g. "root cause analysis technique for
    tracing a technology failure"), NOT a raw restatement of the case facts.
    Raw case text does not retrieve framework knowledge reliably -- this has
    been measured, not assumed.
    """
    return retrieve_knowledge(query, k=6)


# ---------------------------------------------------------------------------
# Agents (long-lived, reused across every task/crew below)
# ---------------------------------------------------------------------------

researcher = Agent(
    role="Framework Researcher",
    goal=(
        "Given a business case, identify which diagnostic frameworks from "
        "the knowledge base are relevant, and retrieve the specific "
        "framework knowledge (definition, when to use it, process, worked "
        "example) an Analyst will need to apply them to this case."
    ),
    backstory=(
        "You are a research analyst who knows the business-frameworks "
        "knowledge base thoroughly. You know from experience that searching "
        "with the raw case narrative mostly retrieves other case studies, "
        "not frameworks -- the vocabulary doesn't overlap. So you always "
        "first translate the case's underlying problem into the language "
        "of the diagnostic technique needed (e.g. 'root cause analysis for "
        "a technology failure', 'prioritization framework for competing "
        "initiatives') before you search."
    ),
    tools=[search_frameworks],
    llm=MODEL,
    verbose=True,
)

analyst = Agent(
    role="Business Analyst",
    goal=(
        "Given a business case and the frameworks identified by the "
        "Framework Researcher, actually APPLY those frameworks to the "
        "specific facts of this case -- walk through the real reasoning, "
        "don't just describe the framework."
    ),
    backstory=(
        "You are a business analyst who takes a Researcher's shortlist of "
        "applicable frameworks and does the real diagnostic work: you fill "
        "in each framework's steps using the actual facts, numbers, and "
        "dates from the case, distinguishing triggering events from root "
        "causes, and calculating any relevant financial metrics. You never "
        "restate a framework's definition as your output -- your output is "
        "the applied analysis itself. You are honest about the limits of "
        "the data: if a framework needs quantitative data the case doesn't "
        "provide, you say so explicitly rather than inventing plausible-"
        "sounding numbers. When asked to revise prior work based on audit "
        "feedback, you fix exactly what was flagged and leave everything "
        "else that already passed unchanged."
    ),
    llm=MODEL,
    verbose=True,
)

auditor = Agent(
    role="Quality Auditor",
    goal=(
        "Verify the Analyst's diagnosis against three specific, checkable "
        "standards derived from prior observed failure modes -- not a "
        "generic quality review."
    ),
    backstory=(
        "You are an auditor who reviewed prior runs of this pipeline and "
        "found a specific, recurring problem: when a framework calls for "
        "formally ranking or weighting causes (most often Pareto "
        "Analysis), the Analyst sometimes invents a plausible-sounding "
        "ranking with no real figures behind it -- and this happens both "
        "as invented percentages ('~60% technology, ~25% network design') "
        "and as invented qualitative labels used the same way ('Vital' vs. "
        "'Useful', 'High' vs. 'Medium' impact, in a table). This is "
        "different from a ranking that's actually grounded in case "
        "figures (e.g. $18.4B of $20B = 92% is fine), and it's different "
        "from ordinary comparative language in plain narrative outside a "
        "formal ranking (calling one cause 'primary' and another a "
        "'compounding factor' in a summary paragraph, with no table or "
        "weighting scheme, is normal analysis, not fabrication). You also "
        "noticed the Analyst is appropriately honest elsewhere -- "
        "correctly declining to compute ROI or break-even volumes when "
        "the case doesn't provide the inputs -- so the problem is "
        "specific to formal rankings, not a general honesty issue. You "
        "also learned the hard way that wrapping an unsupported ranking "
        "in a full sentence instead of a table isn't a loophole -- 'X and "
        "Y are the vital few causes' makes the same unsupported claim as "
        "a table would, and you check it exactly the same way regardless "
        "of format. You check every analysis for this exact pattern, "
        "plus whether the final diagnosis actually separates the "
        "external triggering event from the company-controllable "
        "systemic root cause -- conflating the two is the other failure "
        "mode worth catching."
    ),
    llm=MODEL,
    verbose=True,
)


# ---------------------------------------------------------------------------
# Task descriptions (kept as module-level strings so both the "run once"
# functions below and any future test/eval code can reuse them)
# ---------------------------------------------------------------------------

RESEARCH_DESCRIPTION = (
    "Case to analyze:\n{case_text}\n\n"
    "Step 1: Identify what TYPE of business problem this is (e.g. an "
    "operational failure needing root-cause diagnosis, a prioritization "
    "problem, a financial-performance question).\n"
    "Step 2: Reformulate that into 1-2 search queries phrased in "
    "diagnostic-technique language, not case language.\n"
    "Step 3: Call the Framework Knowledge Base Search tool with those "
    "queries.\n"
    "Step 4: Return the 2-4 frameworks that are actually applicable, "
    "each with its retrieved Definition and When-to-Use-It text, and a "
    "one-line justification for why it fits this case."
)

ANALYSIS_DESCRIPTION = (
    "Case to analyze:\n{case_text}\n\n"
    "A Framework Researcher identified these applicable frameworks, with "
    "definitions, when-to-use guidance, and step-by-step processes:\n\n"
    "{framework_context}\n\n"
    "Your job: actually apply each framework's Step-by-Step Process to "
    "THIS case's real facts.\n\n"
    "- For Root Cause Analysis (5 Whys): write out the actual Why #1 "
    "through Why #5 chain using facts and figures from the case, ending "
    "at a specific, company-controllable root cause -- not the "
    "triggering event.\n"
    "- For Fishbone/Ishikawa: list the actual causes from the case "
    "under each relevant category (People, Process, Machine, Material, "
    "Measurement, Environment) -- only include categories with a real, "
    "case-specific cause; don't force empty categories.\n"
    "- For Pareto Analysis: if the case has quantifiable, rankable "
    "causes, rank them and identify which ones account for most of the "
    "impact. If the case does NOT have rankable quantitative data for "
    "multiple causes, say so explicitly instead of inventing numbers.\n"
    "- For any financial framework (Profitability, Break-even, ROI, "
    "Margin, CAGR, Market Share): show the actual calculation using the "
    "real figures from the case's Supporting Data, not a generic "
    "example.\n\n"
    "UNRESOLVED-CAUSE PRESERVATION: Where the case input states that a "
    "specific cause (technical, mechanical, or otherwise) has not yet "
    "been determined -- including phrasing such as 'still investigating,' "
    "'no finding yet,' or an explicitly unconfirmed hypothesis -- do not "
    "invent a specific, previously-unstated fact to resolve it. This "
    "applies at any level of specificity, not only technical mechanisms: "
    "a specific unstated component failure, a specific unstated process "
    "change (e.g. 'a supplier change' or 'a bypassed sign-off' not "
    "mentioned anywhere in the input), or a specific unstated event are "
    "all instances of the same problem if the input does not actually "
    "describe them. You may still reason from what the input does state "
    "-- e.g. a rushed, unpiloted rollout is itself evidence, if the input "
    "describes one -- the restriction is on adding a new, unstated fact "
    "to fill the gap, not on reasoning from facts already given. Where "
    "you cannot determine the specific mechanism from the input, say so "
    "explicitly at the relevant step (e.g. 'the specific mechanism is "
    "not established by the available data') rather than substituting "
    "an invented one.\n\n"
    "Do not reproduce framework definitions -- that's already done. "
    "Your output should read like a completed analysis, not a study "
    "guide, and should end with a clear final root-cause statement that "
    "distinguishes trigger from root cause."
)

REVISION_DESCRIPTION = (
    "Case to analyze:\n{case_text}\n\n"
    "Frameworks identified by the Researcher:\n\n{framework_context}\n\n"
    "You previously produced this diagnosis:\n\n{previous_diagnosis}\n\n"
    "A Quality Auditor reviewed it and found problems. Their full audit "
    "report:\n\n{audit_feedback}\n\n"
    "Revise your diagnosis to fix ONLY the specific problems the Auditor "
    "identified. Do not rewrite sections that already passed -- keep them "
    "as they were. Do not introduce any new formally ranked/weighted "
    "claims (numeric or qualitative-label) unless directly grounded in "
    "figures explicitly stated in the case's Supporting Data. If the "
    "Auditor flagged a fabricated ranking, either remove it entirely or "
    "replace it with an explicit statement that the case does not provide "
    "data to support ranking these causes. If the Auditor flagged a "
    "missing or conflated trigger-vs-root-cause distinction, add or "
    "correct it clearly.\n\n"
    "Produce the complete, corrected diagnosis in the same format as "
    "before -- the full revised analysis, not a list of changes."
)

AUDIT_DESCRIPTION = (
    "Case to analyze:\n{case_text}\n\n"
    "Diagnosis to review:\n\n{diagnosis_text}\n\n"
    "Review this diagnosis against three specific checks:\n\n"
    "CHECK 1 -- Trigger vs. Root Cause: This check has two parts. Both "
    "must pass for Check 1 to pass.\n\n"
    "Part A -- Distinctness: Does the final diagnosis explicitly "
    "separate a trigger from a root cause as two different statements, "
    "rather than one restated as the other? If the two are missing, "
    "absent, or conflated (e.g. the 'root cause' given is actually "
    "just the trigger restated), Part A FAILS -- explain why.\n\n"
    "Part B -- Is the trigger actually external: Is the thing labeled "
    "as the 'Triggering Event' or 'Trigger' something the company "
    "itself did NOT choose, decide, or have the ability to prevent -- "
    "e.g. a weather event, a competitor's action, a pandemic, a "
    "regulatory change, a macroeconomic shift? A company's OWN "
    "strategic decision, business choice, policy, or internal action "
    "(e.g. 'the decision to switch suppliers,' 'the choice to cut "
    "costs,' 'leadership's decision to...') is NOT a valid trigger, no "
    "matter how the diagnosis labels it -- it belongs in root-cause "
    "analysis, not the trigger slot. If the diagnosis labels the "
    "company's own decision or action as the trigger, Part B FAILS -- "
    "quote the mislabeled trigger and explain specifically why it is "
    "an internal, controllable action rather than an external event, "
    "even if a root cause is also present and textually distinct from "
    "it.\n\n"
    "Check 1 FAILS overall if either part fails. Quote the relevant "
    "sentence(s) for both parts.\n\n"
    "CHECK 2 -- Fabricated Ranking Scan: This applies WHEREVER a Pareto "
    "Analysis (or any similar rank-by-contribution framework) states or "
    "implies which causes are the most significant -- in a table, a "
    "list, OR ordinary prose. FORMAT DOES NOT MATTER: a sentence stating "
    "'X and Y represent the vital few causes' makes exactly the same "
    "claim as a table labeling X and Y 'Vital' and the rest 'Useful' -- "
    "both must be checked identically, and writing it as prose instead "
    "of a table is NOT an exemption. Outside of a Pareto-style ranking "
    "claim, do NOT flag ordinary comparative language in plain narrative "
    "that doesn't assert an exhaustive top-cause selection -- e.g. "
    "calling something the 'primary' cause vs. a 'compounding factor' in "
    "a closing summary, with no claim that these specific causes are THE "
    "vital few and the others are not, is normal analysis.\n\n"
    "For each Pareto-style ranking claim found, in ANY format:\n"
    "  - Is it directly computable/justifiable from figures explicitly "
    "stated in the case's Supporting Data? -> PASS, show the basis.\n"
    "  - Is it an estimated or qualitative selection of 'the most "
    "important' causes with no case-provided figures behind it -- even "
    "if hedged ('we can qualitatively deduce', 'estimated', 'arguably')? "
    "-> FAIL, quote it exactly. This includes cases where the text first "
    "ADMITS the data doesn't support a precise ranking and THEN asserts "
    "one anyway ('the data is not segmented by cause... however, we can "
    "deduce that X and Y are the vital few') -- the admission does NOT "
    "excuse the ranking that immediately follows it; if anything it "
    "confirms the ranking is unsupported.\n\n"
    "List every ranking instance found, not just the first one. Every "
    "instance you list MUST have an explicit PASS or FAIL -- do not "
    "list an instance without stating its verdict.\n\n"
    "CHECK 3 -- Unresolved-Cause Fabrication Scan: This applies WHEREVER "
    "the case input explicitly states that a specific cause -- "
    "technical, mechanical, procedural, or otherwise -- is unknown, "
    "unconfirmed, or still under investigation (e.g. 'still "
    "investigating,' 'no finding yet,' an explicitly unconfirmed "
    "hypothesis). If the case input contains no such statement, Check 3 "
    "does NOT apply -- PASS, state 'Not applicable -- no unresolved-"
    "cause statement in the case input.'\n\n"
    "If such a statement IS present, you MUST examine EVERY framework "
    "section the diagnosis applies, one section at a time, not only "
    "the 5 Whys -- Fishbone/Ishikawa category bullets (Machine, "
    "Process, People, Environment, or however categorized), Pareto or "
    "other framework sections, and the Final Root-Cause Statement are "
    "equally in scope, even when phrased as a brainstormed list of "
    "possibilities rather than a final chain of reasoning. A "
    "fabricated claim sitting in a Fishbone bullet is exactly as much "
    "a violation as the same claim sitting in the 5 Whys -- do not "
    "treat Fishbone content as exempt or lower-priority. In each "
    "section, look for any point where a specific, previously-unstated "
    "fact -- a named component, technical mechanism, process change, "
    "or other concrete detail that does not appear anywhere in the "
    "case input -- is presented as the resolved explanation, without a "
    "hedge. Reasoning that draws directly on facts already stated in "
    "the case input is NOT a violation, even if it reaches a specific "
    "conclusion (e.g. inferring that a rushed, unpiloted rollout "
    "described in the input is itself a contributing factor is fine, "
    "since the input actually describes the rollout). Introducing a "
    "new specific fact that appears nowhere in the input, stated as "
    "settled rather than hedged, IS a violation, regardless of how "
    "plausible it sounds.\n\n"
    "SCOPE LIMIT -- TECHNICAL CLAIMS ONLY, NOT EVERY NEARBY CAUSAL "
    "CLAIM: this check protects the SPECIFIC question the input states "
    "is unresolved (e.g. what exactly caused the sync failure, "
    "mechanically) -- it does NOT require every other conclusion in "
    "the diagnosis to also resolve that same question. A diagnosis may "
    "validly reach a process-level or governance-level root cause "
    "(e.g. 'the rollout was rushed without a pilot phase,' "
    "'leadership prioritized cost savings over technical validation') "
    "while explicitly leaving the specific technical mechanism "
    "unresolved elsewhere in the same diagnosis -- this is normal, "
    "correct root-cause-analysis practice, not a violation, even when "
    "both appear in the same Fishbone diagram or narrative. Do NOT "
    "fail a process-, governance-, staffing-, or management-level "
    "claim merely because it sits near an unresolved technical "
    "question or could be read as a contributing factor to it. Only "
    "fail a claim under this check if the claim ITSELF introduces a "
    "new, specific, previously-absent TECHNICAL detail -- a "
    "mechanism, component, protocol, or parameter -- as the resolved "
    "explanation. A process fact already stated in the input (e.g. "
    "the rollout being simultaneous/unpiloted) remains permitted "
    "under this exemption no matter which Fishbone category it's "
    "filed under or how directly it's framed as contributing to the "
    "outcome -- unless that same claim ALSO smuggles in a specific "
    "unstated technical detail (e.g. naming a particular script, "
    "protocol, or component defect), in which case it is still a "
    "violation for that technical content specifically, not exempted "
    "just because it appears in a process-labeled section.\n\n"
    "THE TEST IS A NEW CAUSAL MECHANISM, NOT TECHNICAL-SOUNDING "
    "PHRASING: a claim that merely restates or categorises WHAT "
    "already-described symptom occurred -- using different words, "
    "synonyms, or a general category label for something the input "
    "already states -- is NOT a violation, even if it sounds "
    "technical, because it adds no new explanatory content beyond what "
    "the input already says. For example, 'data transmission gaps' for "
    "'orders failed to sync,' or 'integration failure' for "
    "'integration issues,' are restatements of WHAT happened, not "
    "violations. A violation is a claim that answers WHY or HOW the "
    "symptom occurred by introducing a specific, previously-absent "
    "causal mechanism, named component, parameter, or process detail "
    "that only an actual investigation finding could establish -- for "
    "example 'data-packet loss,' 'handshake errors,' 'latency,' a "
    "named part ('a misconfigured load balancer'), or a specific "
    "parameter change ('narrowed voltage tolerance thresholds'). The "
    "question for any claim touching the unresolved cause: does it "
    "merely restate or relabel WHAT the input already says happened, "
    "or does it assert WHY or HOW it happened using a mechanism, "
    "component, or specific detail the input does not provide? "
    "Restating WHAT is fine, however technical it sounds. Asserting "
    "WHY/HOW with unstated specifics is the violation this check "
    "exists to catch.\n\n"
    "For each point in every examined section that touches the "
    "unresolved cause:\n"
    "  - Does it either preserve the input's stated uncertainty "
    "explicitly (e.g. 'the specific mechanism is not established by "
    "the available data') or reason only from facts already in the "
    "input, using no new specific technical vocabulary? -> PASS.\n"
    "  - Does it state a specific, previously-unstated fact -- new "
    "technical vocabulary, a named component, or a process detail not "
    "in the input -- as the resolved explanation, without a hedge? -> "
    "FAIL, quote it exactly.\n\n"
    "List every such point found across every section examined, not "
    "just the first one and not just the 5 Whys. Every instance you "
    "list MUST have an explicit PASS or FAIL -- do not list an "
    "instance without stating its verdict. Write 'Not applicable' per "
    "the rule above if the case input never states a cause is "
    "unresolved.\n\n"
    "Think through all three checks completely before writing anything. "
    "Your final answer must state your verdict once, decisively -- no "
    "visible self-correction, no 'wait,' no reconsidering mid-answer, "
    "no hypothetical examples of violations that aren't actually "
    "present in the text you're reviewing. If you need to reconsider "
    "your reasoning, do that before you start writing, not in the "
    "output. The overall verdict at the very top must exactly match "
    "your Check 1, Check 2, and Check 3 statuses -- FAIL if any check "
    "is FAIL, PASS only if all three are PASS -- and must not be "
    "contradicted anywhere later in your answer.\n\n"
    "Produce a structured verdict using this exact format:\n\n"
    "## Audit Verdict: PASS or FAIL\n\n"
    "### Check 1: Trigger vs. Root Cause Distinction\n"
    "Overall Status: PASS or FAIL\n"
    "Part A (Distinctness): PASS or FAIL -- <exact quote> -- <why>\n"
    "Part B (Trigger Is Genuinely External): PASS or FAIL -- <exact quote> -- <why>\n\n"
    "### Check 2: Fabricated Ranking Scan\n"
    "Status: PASS or FAIL\n"
    "Instances found: <list each one, with PASS/FAIL and reasoning per "
    "instance; write 'None found' if the analysis contains no "
    "percentage/ranking claims at all>\n\n"
    "### Check 3: Unresolved-Cause Fabrication Scan\n"
    "Status: PASS or FAIL\n"
    "Sections examined: <list every framework section applied in the "
    "diagnosis you actually checked, e.g. Fishbone, 5 Whys, Final "
    "Root-Cause Statement -- every section must appear here>\n"
    "Instances found: <list each one, with PASS/FAIL and reasoning per "
    "instance; write 'Not applicable' if the case input never states a "
    "cause is unresolved>\n\n"
    "The overall verdict is FAIL if any check fails."
)

RESEARCH_EXPECTED_OUTPUT = (
    "A list of applicable frameworks, each with its definition, when "
    "to use it, and a one-line justification for why it fits this case."
)
ANALYSIS_EXPECTED_OUTPUT = (
    "A structured analysis with one section per applied framework, each "
    "containing the actual worked-through reasoning or calculation for "
    "this specific case, ending in a clear final root-cause statement."
)
AUDIT_EXPECTED_OUTPUT = (
    "A structured audit report in the exact format specified, with an "
    "overall PASS/FAIL verdict and itemized findings for all three checks."
)

VERDICT_PATTERN = re.compile(r"##\s*Audit Verdict:\s*(PASS|FAIL)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# One function per pipeline step. Each builds a fresh single-task Crew and
# kicks it off -- the Agent objects above are reused, only the Task (and
# its filled-in {placeholders}) changes between calls.
# ---------------------------------------------------------------------------

def run_researcher(case_text: str) -> str:
    task = Task(description=RESEARCH_DESCRIPTION, expected_output=RESEARCH_EXPECTED_OUTPUT, agent=researcher)
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"case_text": case_text}))


def run_analyst_draft(case_text: str, framework_context: str) -> str:
    task = Task(description=ANALYSIS_DESCRIPTION, expected_output=ANALYSIS_EXPECTED_OUTPUT, agent=analyst)
    crew = Crew(agents=[analyst], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"case_text": case_text, "framework_context": framework_context}))


def run_analyst_revision(case_text: str, framework_context: str, previous_diagnosis: str, audit_feedback: str) -> str:
    task = Task(description=REVISION_DESCRIPTION, expected_output=ANALYSIS_EXPECTED_OUTPUT, agent=analyst)
    crew = Crew(agents=[analyst], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={
        "case_text": case_text,
        "framework_context": framework_context,
        "previous_diagnosis": previous_diagnosis,
        "audit_feedback": audit_feedback,
    }))


def run_auditor(case_text: str, diagnosis_text: str) -> str:
    task = Task(description=AUDIT_DESCRIPTION, expected_output=AUDIT_EXPECTED_OUTPUT, agent=auditor)
    crew = Crew(agents=[auditor], tasks=[task], verbose=True)
    return str(crew.kickoff(inputs={"case_text": case_text, "diagnosis_text": diagnosis_text}))


def parse_verdict(audit_text: str) -> bool:
    """
    True if PASS, False if FAIL. Fails SAFE: if the verdict line can't be
    parsed at all (unexpected format), this returns False (treat as FAIL)
    rather than silently treating unparseable output as success -- an
    unparseable audit is exactly the kind of thing that should trigger a
    human looking at it, not a silent pass.

    Return type is deliberately still a bare bool, not a tuple or dict --
    every existing caller (run_pipeline() below, and every
    test_*.py script that does `parse_verdict(audit)` or
    `not parse_verdict(audit)`) treats the return value as a plain bool,
    so changing the shape would silently break all of them (`not
    {"passed": True}` is always False, for example). The single-verdict
    case must behave byte-for-byte as before -- this only adds behavior
    for a case that previously had none.

    SELF-CORRECTION HANDLING (see DEVELOPMENT_LOG.md's harbor_vine
    trial 3 finding): the Auditor's prompt instructs it to state its
    verdict once, decisively, with no visible self-correction -- but a
    real run showed the model can still write a full verdict block,
    visibly reconsider ("Self-correction note... Correction on
    Verdict:"), and write a second, complete, corrected verdict block
    in the same response. The old code used .search(), which finds the
    FIRST match -- silently keeping the model's pre-correction answer
    even when the model itself concluded otherwise moments later. This
    now finds ALL "## Audit Verdict: PASS/FAIL" occurrences and takes
    the LAST one as authoritative: in the one real instance observed,
    the model's own final, corrected conclusion was the right call,
    so trusting the last occurrence over the first is the evidence-
    based choice here, not a guess. When more than one occurrence is
    found, a warning is emitted via the `warnings` module -- visible
    to anyone running the pipeline, but silent to callers that only
    read the return value, so no existing caller needs to change.
    """
    matches = VERDICT_PATTERN.findall(audit_text)
    if not matches:
        return False
    if len(matches) > 1:
        warnings.warn(
            f"parse_verdict(): {len(matches)} '## Audit Verdict:' "
            f"occurrences found in one response (self-correction "
            f"pattern) -- sequence seen: {[m.upper() for m in matches]}. "
            f"Using the LAST occurrence ({matches[-1].upper()}) as "
            f"authoritative, matching the model's own final conclusion.",
            stacklevel=2,
        )
    return matches[-1].upper() == "PASS"


def run_pipeline(case_text: str, max_revisions: int = 1) -> dict:
    """
    Full pipeline: Researcher -> Analyst -> Auditor, with up to
    max_revisions revision+re-audit cycles if the Auditor fails the
    diagnosis. max_revisions=1 means at most 2 total Analyst attempts
    (1 draft + 1 revision) and at most 2 Auditor calls.

    Returns a dict with the full attempt history (not just the final
    result) -- the history itself is worth keeping: it's direct evidence
    of whether the revision loop actually improves output, not just a
    claim that it does.
    """
    framework_context = run_researcher(case_text)

    # Small pacing delay before the Analyst's first call -- same 15
    # RPM free-tier reasoning as the Orchestrator's synthesis/fidelity
    # gap. Cheap insurance, not a claim this alone prevents every
    # possible rate-limit hit.
    time.sleep(5)

    diagnosis = run_analyst_draft(case_text, framework_context)

    history = []
    attempt = 1
    while True:
        # Same reasoning: pace before every Auditor call, whether this
        # is the first pass or a post-revision recheck.
        time.sleep(5)
        audit = run_auditor(case_text, diagnosis)
        passed = parse_verdict(audit)
        history.append({
            "attempt": attempt,
            "diagnosis": diagnosis,
            "audit": audit,
            "passed": passed,
        })

        print(f"\n{'=' * 70}\nAttempt {attempt}: {'PASS' if passed else 'FAIL'}\n{'=' * 70}\n")

        if passed or attempt > max_revisions:
            break

        diagnosis = run_analyst_revision(case_text, framework_context, diagnosis, audit)
        attempt += 1

    return {
        "framework_context": framework_context,
        "history": history,
        "final_diagnosis": diagnosis,
        "final_passed": history[-1]["passed"],
        "total_attempts": len(history),
    }


if __name__ == "__main__":
    from case_loader import load_case
    case = load_case("cases/Case_01_Southwest_Airlines_2022_Meltdown.md")
    result = run_pipeline(case.diagnostic_input, max_revisions=1)
    print(f"\n\nFinal verdict: {'PASS' if result['final_passed'] else 'FAIL'} "
          f"after {result['total_attempts']} attempt(s)\n")
    print(result["final_diagnosis"])
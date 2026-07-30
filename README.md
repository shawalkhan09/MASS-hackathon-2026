# MASS — Multi-Agent Analysis and Synthesis System

MASS turns a raw business case into an audited, evidence-grounded diagnostic report. Instead of one AI model guessing at root causes, a pipeline of specialized agents — a Researcher, an Analyst, an Auditor, and an Orchestrator — cross-check every claim against the case data before anything reaches a reader, catching the fabricated statistics and unsupported rankings a single unscaffolded model call would otherwise produce with total confidence.

Built as a Final Year Project at IMSciences, on top of [CrewAI](https://github.com/crewAIInc/crewAI) and the Gemini API.

## How it works

A business case goes in; a client-facing diagnostic report comes out, only if it survives two independent rounds of checking along the way.

1. **Researcher** — retrieves the frameworks (from a 15-framework, four-tier knowledge base) actually relevant to the case, via RAG over ChromaDB.
2. **Analyst** — applies those frameworks to the case data and drafts a diagnosis: root causes, rankings, financial impact.
3. **Auditor** — independently reviews the draft against two specific checks:
   - **Trigger vs. root cause** — is the labeled "trigger" genuinely external, and distinct from the systemic root cause, rather than the company's own decision relabeled?
   - **Fabricated ranking scan** — is every numeric ranking or percentage actually computable from the case's own data, or invented to fill a gap the case doesn't support?

   If either check fails, the diagnosis goes back to the Analyst for a bounded revision cycle. If it's still failing after that, the pipeline stops and flags it for human review — it never lets a synthesized report paper over an unresolved failure.
4. **Orchestrator (Engagement Manager)** — takes an *approved* diagnosis only, and synthesizes it into a polished report for a business reader. It structurally cannot see the raw case text or the Researcher's notes — only the audited diagnosis.
5. **Fidelity check** — a final, independent pass verifying the Orchestrator's report didn't drift from the diagnosis it was built from: no new facts introduced, no cause reclassified into a different diagnostic category, no qualifier on a statistic quietly dropped. If this fails too, the report is withheld rather than handed back as a clean deliverable.

## Validated so far

- A repeatable fabrication pattern: unscaffolded models confidently invent Pareto-style rankings (e.g. forced 60/25/10/5 splits) with no basis in the case data — confirmed across repeated trials, not a one-off.
- The Auditor reliably catches fabricated numeric rankings, but has a known, documented blind spot: it does not (yet) flag omissions in reasoning, only fabricated assertions.
- The Orchestrator's fidelity check has been through several rounds of calibration, including discovering that its three sub-checks needed to run as fully isolated LLM calls rather than sharing one prompt — otherwise a wording fix to one check could silently change another's behavior.

Full details, including every finding that turned out to be wrong and why, are in [`DEVELOPMENT_LOG.md`](./DEVELOPMENT_LOG.md) — every phase documented chronologically as Problem → Diagnosis → Fix → Lesson, including the dead ends.

## Case studies

Three real, publicly documented business failures, not synthetic examples:

- Southwest Airlines' December 2022 operational meltdown
- Boeing 737 MAX grounding
- Peloton's inventory oversupply collapse

Each case packet (`cases/`) includes ground-truth documentation used only for scoring, never shown to any agent.

## Setup

Requires Python 3.12 (the project's `tiktoken` dependency is incompatible with 3.14).

```bash
python3.12 -m venv venv312
source venv312/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with a Gemini API key from Google AI Studio:

```
GEMINI_API_KEY=your-key-here
```

The free tier caps at 15 requests/minute — the pipeline paces its own calls to stay under this, so a full run takes a few minutes per case rather than seconds.

## Usage

Run the full pipeline across all three cases:

```bash
python3 run_orchestrator_all_cases.py
```

Output is saved per case to `orchestrator_outputs/`, including the full attempt history (every audit pass or fail, not just the final result), the synthesized report if one was approved, and the fidelity check's verdict.

To run a single case for a quick check:

```bash
python3 orchestrator.py
```

## Project structure

```
crewai_pipeline.py       Researcher, Analyst, Auditor agents + revision loop
orchestrator.py          Engagement Manager agent + synthesis
fidelity_check.py        Independent post-synthesis fidelity check
case_loader.py           Loads case packets, strips ground-truth hints from agent input
content_data.py          The 15-framework, four-tier knowledge base
cases/                   The three case packets
orchestrator_outputs/    Saved pipeline + orchestrator run output
test_*.py                Calibration and validation tests for the Auditor and fidelity check
DEVELOPMENT_LOG.md        Full chronological development history
```

## Status

Core pipeline (Researcher → Analyst → Auditor) and the Orchestrator with its fidelity check are built and validated. See `DEVELOPMENT_LOG.md` for the current state of any work in progress.

# MASS — Multi-Agent Analysis and Synthesis System

MASS turns a raw business case into an audited, evidence-grounded diagnostic report. Instead of one AI model guessing at root causes, a pipeline of specialized agents — an Intake specialist, a Researcher, an Analyst, an Auditor, and an Orchestrator — cross-check every claim against the case data before anything reaches a reader, catching the fabricated statistics and unsupported rankings a single unscaffolded model call would otherwise produce with total confidence.

Built as a Final Year Project at IMSciences, on top of [CrewAI](https://github.com/crewAIInc/crewAI) and the Gemini API.

## How it works

A business case goes in; a client-facing diagnostic report comes out, only if it survives two independent rounds of checking along the way.

0. **Intake** *(for raw, unstructured input via the demo UI only — pre-written case packets skip this step)* — restructures a user's free-text problem description into Problem Statement / Background / Supporting Data, adding no fact the user didn't state. The user reviews and can edit this before anything downstream runs.
1. **Researcher** — retrieves the frameworks (from a 15-framework, four-tier knowledge base) actually relevant to the case, via RAG over ChromaDB. Searches using reformulated diagnostic-technique language, not the case's raw wording — raw-wording queries measurably fail to retrieve relevant frameworks.
2. **Analyst** — applies those frameworks to the case data and drafts a diagnosis: root causes, rankings, financial impact. Explicitly declines to compute a figure or ranking the case doesn't provide the data for, rather than approximating.
3. **Auditor** — independently reviews the draft against three specific checks:
   - **Trigger vs. root cause** — two parts, both must pass: is a trigger and a root cause stated as genuinely distinct claims (not one restated as the other), and is the labeled trigger actually external (not the company's own decision relabeled)?
   - **Fabricated ranking scan** — is every ranking or percentage of causes — numeric or qualitative-label, in a table or in prose — actually computable from the case's own data, or invented to fill a gap the case doesn't support? Format doesn't exempt a claim from this check.
   - **Unresolved-cause fabrication scan** — where the case explicitly states a cause is unknown or still under investigation, does the diagnosis invent a new, specific technical detail to resolve it anyway? Legitimate process- or governance-level conclusions already supported by the case are not penalized by this check.

   If any check fails, the diagnosis goes back to the Analyst for a bounded revision cycle (one retry, two total attempts). If it's still failing after that, the pipeline stops and flags it for human review — it never lets a synthesized report paper over an unresolved failure.
4. **Orchestrator (Engagement Manager)** — takes an *approved* diagnosis only, and synthesizes it into a polished report for a business reader. It structurally cannot see the raw case text or the Researcher's notes — only the audited diagnosis.
5. **Fidelity check** — a final, independent pass verifying the Orchestrator's report didn't drift from the diagnosis it was built from: no new facts introduced, no cause reclassified into a different diagnostic category, no qualifier on a statistic quietly dropped. Runs as three fully isolated LLM calls with zero shared context between them. If this fails too, the report is withheld rather than handed back as a clean deliverable.

## Validated so far

- A repeatable fabrication pattern: unscaffolded models confidently invent Pareto-style rankings (e.g. forced 60/25/10/5 splits) with no basis in the case data — confirmed across repeated trials, not a one-off.
- A separate, cross-domain fabrication pattern: under an explicitly stated data gap ("cause still under investigation"), unscaffolded diagnosis confidently invents a specific technical mechanism to resolve it anyway — confirmed at n=27 trials across three domains, which is what the Unresolved-Cause Fabrication Scan (Check 3) was built to catch.
- The Auditor reliably catches fabricated numeric rankings and, after four rounds of iterative refinement, generalizes correctly to genuinely new cases rather than just memorizing three fixed test cases.
- A verdict-parsing bug was found and fixed: the model can occasionally write a full verdict, visibly self-correct, and write a second corrected verdict in the same response. Parsing now takes the model's last stated verdict as authoritative (matching its own final conclusion) rather than its first, with a warning emitted whenever this occurs.
- The Orchestrator's fidelity check has been through several rounds of calibration, including discovering — twice, from two unrelated edits — that its three sub-checks needed to run as fully isolated LLM calls rather than sharing one prompt, since a wording fix to one check could silently change a different, untouched check's behavior.

### Known limitations

- **Check 1 evaluates categorization, not root-cause content.** It checks whether a trigger and root cause are correctly distinguished and labeled, not whether the root cause's specific content is factually grounded — a diagnosis can pass Check 1 cleanly while still containing the kind of fabrication Check 3 exists to catch, since the two checks evaluate different properties.
- **Check 3 is validated to 25/27 (92.6%) correct**, with one precisely characterized residual false-positive pattern (conflating a legitimate governance-level explanation with an invented technical-mechanism claim) — not claimed as perfect.
- **No dedicated completeness check exists yet.** An omitted cause or consideration makes no checkable false claim, so it isn't caught by any current check — this would need its own, separately designed and validated check.
- **The RAG corpus indexing does not yet mirror `case_loader.py`'s ground-truth filtering.** `case_loader.py` strips the `Documented Root Cause` / `Ground-Truth Diagnosis Summary` sections before any agent sees a case as direct input. The RAG corpus built from the same case files does not yet apply that same filter before embedding — identified during review, fix in progress.

Full details, including every finding that turned out to be wrong and why, are in [`DEVELOPMENT_LOG.md`](./DEVELOPMENT_LOG.md) — every phase documented chronologically as Problem → Diagnosis → Fix → Lesson, including the dead ends. [`ROADMAP.md`](./ROADMAP.md) is the standalone architecture spec and design philosophy, written to be readable on its own by someone new to the project.

## Case studies

Three real, publicly documented business failures, not synthetic examples:

- Southwest Airlines' December 2022 operational meltdown
- Boeing 737 MAX grounding
- Peloton's inventory oversupply collapse

Each case packet (`cases/`) includes ground-truth documentation used only for scoring, never shown to any agent as diagnostic input (see the known limitation above regarding the RAG index specifically).

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

To run the demo API (Intake → structure → diagnose flow):

```bash
python3 api.py
```

## Project structure

```
api.py                      FastAPI demo backend (/structure, /diagnose, /health)
intake.py                   Intake agent — raw text -> structured diagnostic input
case_loader.py               Loads case packets, splits diagnostic_input from reference_material
content_data.py              The 15-framework, four-tier knowledge base
rag_pipeline_starter.py      Corpus chunking (frameworks + cases) and TF-IDF baseline retriever
chroma_retriever.py           Embeddings retriever v1 (all-MiniLM-L6-v2) — kept for comparison
chroma_retriever_v2.py        Embeddings retriever v2 (BAAI/bge-base-en-v1.5) — production retriever
retrieval_tool.py             The Researcher's actual search tool
retrieval_eval.py             Query -> expected-chunk scoring harness for retrieval quality
crewai_pipeline.py           Researcher, Analyst, Auditor agents + bounded revision loop
orchestrator.py              Engagement Manager agent + synthesis
fidelity_check.py            Independent post-synthesis fidelity check (3 isolated calls)
baseline_single_llm.py       Unscaffolded single-call baseline for the ablation study
baseline_forced_ranking.py   Forced-ranking baseline (deliberately decoupled model config)
cases/                       The three case packets
orchestrator_outputs/        Saved pipeline + orchestrator run output
test_*.py                    Calibration and validation tests
DEVELOPMENT_LOG.md           Full chronological development history (47 phases)
ROADMAP.md                   Standalone architecture spec and design philosophy
```

## Status

Core pipeline (Intake → Researcher → Analyst → Auditor) and the Orchestrator with its fidelity check are built and validated. See `DEVELOPMENT_LOG.md` for the current state of any work in progress, and the Known Limitations section above for what's deliberately not yet covered.
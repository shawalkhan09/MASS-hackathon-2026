# MASS Project — Development Log

**Multi-Agent Strategy Swarm — FYP**

## How to use this document

This is the raw, chronological engineering record — every problem hit, how it was
diagnosed, how it was fixed, and what it taught. It is deliberately unpolished:
its job is completeness, not readability. It exists for three reasons:

1. **Your own reference** while building the next pieces (revision loop, RAGAS harness).
2. **Evidence of process** — if a supervisor or examiner asks "walk me through a
   challenge you faced," this document already has the answer, dated and specific.
3. **Raw material** for the polished "Engineering Challenges" section that belongs
   in the actual FYP report — that section should be written *from* this log, not
   from memory, once this log is complete.

**Entry format:** each numbered phase covers one coherent piece of work. Within a
phase, individual problems follow **Problem → Diagnosis → Fix → Lesson**. Keep
using this exact structure for new entries as the project continues, so the whole
document stays scannable.

---

## Phase 1 — Knowledge Base: Business Frameworks

Built a 4-tier reference corpus of 15 business frameworks/terms (Root Cause
Analysis, Fishbone, Pareto, SWOT, PESTLE, Porter's Five Forces, Impact-Effort
Matrix, Decision Tree, Profitability, Gross/Net Margin, Market Share, ROI,
Break-even, CAGR, KPI), each with Definition / When to Use It / Step-by-Step
Process / Worked Example, delivered as 4 tier-based PDFs. Content was
web-researched and grounded (not just recalled from training), particularly for
formulas and process steps, to satisfy a "purely research-based" requirement.

No major issues in this phase — straightforward content generation.

---

## Phase 2 — Pivot: From Proprietary Playbooks to Public Case Studies

**Problem:** Original project plan (MaRGen-style) assumed a corpus of a family
contact's real consulting playbooks as the domain-specific "hidden knowledge"
layer. That source turned out not to exist — the project was reframed as
purely academic/FYP-scoped.

**Diagnosis:** Without proprietary data, the system needed (a) a case-scenario
corpus for the agents to diagnose, and (b) a different evaluation baseline,
since "compare against a real consultant" was no longer possible.

**Fix:**
- Case data sourced from **real, publicly documented corporate events**
  (news reporting, regulatory investigations, SEC filings) rather than paid
  case-study products or synthetic scenarios — avoids copyright/licensing
  issues while keeping a genuine, externally-verifiable ground truth.
- Evaluation baseline changed from "vs. human consultant" to an **ablation
  study**: multi-agent + RAG + critique loop vs. a single zero-shot LLM call.
  This is arguably a *stronger* FYP result — it needs no external human
  panel and directly tests whether the architecture itself adds value.

**Lesson:** Losing the "differentiator" data source didn't weaken the
project — it forced a design that's more reproducible and more rigorously
testable. Worth stating explicitly in the report rather than treating it as
a downgrade.

---

## Phase 3 — Case Packet Construction

Built 3 case packets (Southwest Airlines Dec 2022 meltdown, Boeing 737 MAX
grounding, Peloton demand/inventory collapse), each with: Problem Statement,
Background, Supporting Data, Documented Root Cause / Investigation Findings,
Resolution, a **Ground-Truth Diagnosis Summary** (for scoring agent output),
and Sources. All three were deliberately chosen because each has an obvious
surface **trigger** (storm, sensor, falling demand) that is *not* the real
root cause — this was intentional, to create a test set that would expose a
shallow single-LLM baseline's tendency to stop at the trigger.

This structural choice turned out to be the single most load-bearing design
decision in the whole project — see Phase 5 and Phase 13.

---

## Phase 4 — RAG Pipeline v1: Chunking and the TF-IDF Baseline

Built `rag_pipeline_starter.py`: chunks the framework corpus by field
(Definition/When to Use/Steps/Example — chunked directly from structured
data, not re-parsed from PDF) and the case packets by markdown section.
Built a baseline `SimpleRetriever` (TF-IDF via scikit-learn) to sanity-check
chunking before investing in embeddings.

**Result:** 81 chunks total (60 framework, 21 case). Baseline worked
mechanically, but produced the first major finding — see Phase 5.

---

## Phase 5 — THE central finding: retrieval ablation + query reformulation

**Problem:** Querying the corpus with a case's raw problem statement (e.g.
"Southwest cancelled thousands of flights after a winter storm...") returned
**zero framework chunks in the top 6-10 results** — only other case chunks.

**Diagnosis, tested rigorously across 3 independent retrieval methods:**
1. TF-IDF (`SimpleRetriever`) — 0.00 framework recall on diagnostic queries.
2. `all-MiniLM-L6-v2` embeddings (STS-tuned, general similarity) —
   **identical** 0.00 result, confirmed via fresh-index rebuild to rule out
   a caching bug, and via raw score inspection to confirm it was a genuine
   embedding (not a bug) that simply clustered by topical domain
   ("aviation crisis" near other aviation text) rather than by the
   case→technique relationship needed.
3. `BAAI/bge-base-en-v1.5` (retrieval-tuned, asymmetric query/passage
   model) — **also** 0.00 on the same queries.

Three fundamentally different retrieval mechanisms converging on the same
failure ruled out "wrong model" as the explanation.

**The actual fix, proven via `hyde_experiment.py`:** hand-written
reformulations of the same 3 queries — rephrasing the case in
diagnostic-technique language (e.g. "this problem requires root cause
analysis using iterative questioning...") instead of raw case narrative —
immediately surfaced framework chunks in the top 4, using the *same*
TF-IDF retriever that scored 0.00 on the raw queries.

**Conclusion:** the bottleneck was never the retriever — it was that
nobody had translated "Southwest cancelled 16,700 flights" into "this needs
root cause analysis." That translation is *reasoning*, not similarity
search — which directly justified building an LLM agent to do it (the
Researcher), rather than trying more embedding models indefinitely.

**Lesson:** this is a genuinely strong, quantified, reproducible result —
three retrievers, one test set, one clean causal fix. Worth being a
significant piece of the Results/Evaluation chapter, not just a debugging
footnote.

---

## Phase 6 — Environment & Tooling Struggles

Several distinct, unglamorous but real engineering problems:

- **Filename casing / hyphens vs. underscores.** Python `import` requires
  exact module-name matching (underscores, not hyphens), and macOS's
  default filesystem (APFS) is case-insensitive, so `Crewai_researcher_agent.py`
  silently worked locally but would break on Linux/CI. Recurred multiple
  times across the project (`rag-pipeline-starter.py`,
  `Retrieval_tool.py`/`Chroma-retriever.py`, `Hyde_experiment.py`/
  `Run_researcher_all_cases.py`). **Lesson:** after any automated rename,
  `grep`/`ls` to verify — cheap insurance against a whole class of bug.
- **Hardcoded absolute paths.** `CASE_DIR` was hardcoded to a sandbox path
  from a different machine; fixed by resolving paths relative to the
  script's own file location (`os.path.dirname(os.path.abspath(__file__))`).
- **Python 3.14 incompatibility.** `crewai`'s dependency `tiktoken` had no
  prebuilt wheel for Python 3.14 and needed a Rust compiler to build from
  source. Fixed by creating a separate `venv312` (Python 3.12) rather than
  installing a Rust toolchain — smaller, more standard fix.
- **chromadb version/schema mismatch.** `crewai` pinned `chromadb~=1.1.0`,
  downgrading from `1.5.9` (used in the old venv) — the persisted
  `chroma_db`/`chroma_db_v2` folders from the newer version caused a
  Rust-level panic on read under the older version. Fixed by moving the
  incompatible indexes aside and letting them rebuild fresh; later
  confirmed the old backups were genuinely unreadable (not just outdated)
  before deleting them.

---

## Phase 7 — LLM Provider Setup: the Gemini saga

A long chain of environment-specific issues, each individually minor but
worth recording as a group since they ate significant time:

1. **API key format.** New Google AI Studio accounts issue keys in a new
   `AQ.`-prefixed format rather than the legacy `AIza...` format (a
   platform-wide rollout at the time). Confirmed as a known, current Google
   change (not a broken key) — worked fine because CrewAI/LiteLLM's Gemini
   integration talks to the native endpoint, which doesn't validate key
   shape.
2. **Model deprecation for new accounts.** `gemini-2.5-flash` and
   `gemini-2.5-flash-lite` both returned 404 "no longer available to new
   users" — the account was restricted to the 3.x generation only.
3. **Rate limiting on preview models.** `gemini-3.6-flash` hit a
   free-tier cap of **20 requests/day** — a brand-new preview release
   gets throttled far harder than established models (~1,000-1,500/day).
   Confirmed via Google AI Studio's own rate-limit dashboard rather than
   guessed.
4. **Fix:** queried the live model list for the account directly
   (`list_available_models.py`) instead of guessing model strings one at a
   time, filtered out anything with "preview" in the name (deliberately
   throttled pre-GA) and anything aliased as `-latest` (see Phase 9 for why),
   and landed on `gemini-3.1-flash-lite`.

**Lesson:** for any fast-moving external API, verify current model
availability/quotas directly (live query, or the provider's own dashboard)
rather than trusting documentation or prior knowledge, which goes stale
within weeks in this space.

---

## Phase 8 — Researcher Agent: Design and Validation

Built as a CrewAI `Agent` whose task explicitly requires **reformulating the
case into framework-oriented search language before calling the retrieval
tool** — a direct, measured fix for the Phase 5 finding, not a style choice.

Validated across all 3 cases: correctly landed on 5 Whys / Fishbone for
diagnostic cases, correctly added case-specific frameworks (Break-even,
Profitability for Peloton's fixed-cost problem) rather than reusing one
template. One weakness found on manual review: Boeing's Pareto Analysis
justification was plausible-sounding but not actually grounded in ranked
data — directly informed the Analyst's design (Phase 11) and the Auditor's
Check 2 (Phase 13).

---

## Phase 9 — Recurring Bug: OpenAI Default Fallback

**Problem (occurred twice, independently):** `CrewAI` `Agent` objects
default their LLM to OpenAI's `gpt-4.1-mini` if `llm=` isn't explicitly
set, and will then demand `OPENAI_API_KEY` even in a project that only
uses Gemini — a well-documented but easy-to-miss CrewAI default.

**First occurrence:** the original `crewai_researcher_agent.py` never
actually had `llm=` set on the Researcher (an oversight from early
development that went unnoticed because a stale claim to the contrary
wasn't checked). Root-caused via full traceback
(`agent/core.py:model_post_init` → `llm_utils.py:_llm_via_environment_or_fallback`
→ `constants.py:DEFAULT_LLM_MODEL`), not guesswork.

**Second occurrence:** when the Auditor agent was added, its `Agent()`
definition was written without `llm=` at all — caught proactively by
`grep`-checking immediately after the edit, before it could cause the same
failure a third time.

**Lesson:** this became a standing verification step for the rest of the
project — after any edit adding or modifying an `Agent()`, immediately
`grep -c "llm=" <file>` and confirm the count matches the number of agents.
Cheap, mechanical, and closed off an entire recurring bug class.

---

## Phase 10 — Recurring Bug: Thread-Safety / Race Conditions

**Problem 1 — concurrent model loading.** `gemini-3.1-flash-lite` (unlike
earlier models used) issues multiple tool calls in parallel within one
turn. The retrieval tool's lazy first-call initialization
(`if _retriever is None: build it`) meant two threads could both see
"not built yet" simultaneously and both start loading the embedding model
at once — a native-library race that crashed the process with
`malloc: double free`, not a Python-catchable exception.

**Fix 1:** build the retriever once at **import time** instead of lazily
on first call — Python module imports are single-threaded, closing the
race window entirely.

**Problem 2 — concurrent querying.** Fixing (1) exposed a second, separate
race: two parallel tool calls now both reached the (already-built)
retriever's `.query()` method simultaneously, and neither `sentence-
transformers` nor `chromadb` guarantee thread-safety for concurrent reads
on a shared instance — crashed with `SIGABRT`.

**Fix 2:** wrap `.query()` in a `threading.Lock()` to serialize access.
Trade-off noted explicitly: parallel tool calls now execute retrieval
sequentially under the hood, losing whatever latency benefit Gemini's
parallel calling offered — accepted as correct, since correctness matters
more than latency at this stage and it isn't yet a bottleneck.

**Lesson:** a new model capability (parallel tool calls) surfaced two
distinct, previously-latent bugs that hadn't mattered when only one tool
call happened at a time. Worth remembering that upgrading a model isn't
just "better answers" — it can change *how* the system is exercised.

---

## Phase 11 — Analyst Agent: Design and the Pareto-Fabrication Finding

Added as a second CrewAI task, chained via `context=[research_task]`. Its
task explicitly instructs it to actually **apply** each framework's
step-by-step process to the case's real facts (worked Why-chains, filled
Fishbone categories, real calculations) rather than just describing the
framework — and explicitly forbids inventing numbers for Pareto Analysis
when the case doesn't provide rankable data, directly targeting the Boeing
weakness found in Phase 8.

**Manual review across 2 independent runs, all 3 cases** found:
- Consistently correct trigger-vs-root-cause separation, matching each
  case's Ground-Truth Diagnosis Summary, in all 6 outputs reviewed.
- Genuinely honest data-limit acknowledgment in high-stakes spots (Boeing
  explicitly declined to compute ROI; Peloton explicitly declined to
  compute exact break-even volume) — the instruction worked where it
  mattered most.
- The instruction reduced but didn't eliminate the Pareto problem: a
  specific, learnable pattern emerged — percentages computed from two
  case-provided dollar figures were always correct; percentages ranking
  *qualitative* causes with no source figures were still fabricated, even
  when hedged as "estimated." This precise distinction directly became the
  Auditor's Check 2 design (Phase 13).

---

## Phase 12 — Project Hygiene: Naming and Cleanup Cycles

Recurring theme, worth documenting as a pattern rather than N separate
incidents:

- **Silent overwrite:** `run_researcher_all_cases.py` wrote output to
  `{case_stem}_researcher_output.md` regardless of which pipeline stage
  produced it — when the Analyst was added, its combined output silently
  overwrote the original Researcher-only files under the same name.
  Recovered because the original content had already been shared earlier
  in conversation and could be restored; **root-cause fix was
  timestamp-based filenames** (`RUN_TIMESTAMP`, one per run) rather than a
  manually-maintained stage-name variable — deliberately chosen because a
  human forgetting to update a naming variable was exactly the original
  bug's cause, and a variable that can't be forgotten closes that class of
  bug rather than documenting around it.
- **Cleanup passes:** multiple rounds of inspect-first, protect-list-based
  cleanup (stale debug logs, unreadable chromadb version-mismatch
  backups, `__pycache__`, casing inconsistencies) — each pass followed the
  same discipline: list everything first, get explicit confirmation before
  deleting anything ambiguous, verify nothing on a protect-list was
  touched.

**Lesson:** naming/organization bugs are unglamorous but repeatedly cost
real time and real data (temporarily) — worth a short methodology note on
why timestamp-based/automatic naming beats convention-based/manual naming
whenever a pipeline's stages might change.

---

## Phase 13 — Auditor Agent: Four Rounds of Iterative Refinement

The most instructive single piece of engineering in the project — a clean,
documented example of empirical prompt refinement, not just "getting it
right eventually."

**Design:** third CrewAI task, `context=[research_task, analysis_task]`,
checking two specific, evidenced failure modes rather than doing a generic
quality pass: (1) does the final diagnosis separate trigger from root
cause, (2) is any ranking/weighting of causes actually grounded in
case-provided figures.

**Round 1 (initial wording — "percentage, ratio, or numeric weighting"):**
Correctly caught Southwest's outright invented Pareto percentages. But
also flagged Peloton's *"Tread+ recall was a compounding shock... driven
by the mismatch"* as fabrication — despite that phrasing almost exactly
mirroring the case's own Ground-Truth Diagnosis Summary language
("compounding factor... distinguished from the primary root cause"). A
genuine false positive, traced to ambiguous instruction wording ("even if
hedged" was broad enough to catch ordinary comparative narrative, not just
invented statistics).

**Round 2 (tightened to "actual numbers only"):** Fixed the false
positive, but overcorrected — a subsequent run on Peloton produced a
document with **three contradictory verdict statements** (`FAIL` at the
top, `FAIL` on Check 2, then a mid-answer `"Wait—Correction... Final Audit
Verdict: PASS"`), because the model was allowed to narrate its own
uncertainty directly into the final answer, including inventing and then
rejecting a hypothetical example that wasn't actually in the text.
**Fixed** by explicitly instructing the model to settle its reasoning
before writing, and forbidding visible self-correction in the output —
confirmed fixed on a subsequent run (single consistent verdict, no
contradiction). *This exact run is preserved at
`researcher_outputs/check2_wording_calibration_phases11-13/Case_03_Peloton_Inventory_Oversupply_20260722T231411_output.md`
— confirmed by exact filename during the Phase 26 project audit as the
actual saved instance behind this finding, not a reconstructed example.
Kept as direct evidence rather than only a narrative description of it.*

**Round 3 (found by the model, not by us):** with numbers-only wording, an
unprompted case emerged where the *Auditor itself* flagged a Pareto table
using qualitative labels ("Vital"/"Useful", no percentages) as violating
"the spirit of the instruction" — correctly identifying that a formal
ranking dressed up in words instead of numbers is the same fabrication,
just spelled differently, even though the literal instruction said "only
flag numbers." This showed the narrower rule was actually wrong, not just
imprecise.

**Round 4 (final wording — scoped to "formal ranking presentations,
numeric or qualitative-label, vs. ordinary narrative"):** re-run across all
3 cases produced: Southwest failing (real fabrication, twice confirmed),
Boeing failing **for the first time** (a genuinely new instance of the
same fabricated-ranking pattern the tuning was designed to catch, in a
case that had passed 4 consecutive prior runs), and Peloton passing
despite using structurally similar "Low/High/Moderate" language — correctly
distinguished because that instance was a Decision Tree's probability
estimates (a framework whose entire purpose is estimating uncertainty),
not an unfounded ranking of already-realized causes.

**Why this sequence matters for the report:** the final rule generalized
correctly to a genuinely new case (Boeing failing) rather than just
repeating memorized answers on 3 fixed test cases, and correctly
distinguished two surface-similar but epistemically different uses of the
same vocabulary (Pareto ranking vs. Decision Tree probability). That's
real evidence of a working, non-overfit criterion — not just "we tuned
until it looked right."

**Lesson stated explicitly to future-self:** prompt refinement has
diminishing returns: this was treated as a stopping point after 4 rounds,
specifically to avoid overfitting instruction wording to 3 fixed test
cases rather than producing a genuinely robust standard. Worth stating this
methodological judgment explicitly in the report, not just the outcome.

---

## Phase 15 — Revision Loop: Making the Auditor Actually Useful

Through Phase 13, the Auditor produced a critique report but nothing acted
on it — a failing verdict was informational only. This phase closes that
gap: a FAIL now sends the diagnosis back to the Analyst with the specific
audit feedback, the Analyst produces a targeted revision, and the Auditor
re-checks it, up to a configurable retry limit.

**Design decision: manual Python control flow instead of CrewAI's Flow
API.** A simple sequential Crew can't conditionally re-run a task based on
another task's output. CrewAI's Flow API supports this natively, but given
how many CrewAI-internals surprises this project had already hit by this
point (Phase 9's default-LLM fallback, the tool-calling regex bug, Phase
10's parallel-call race condition), adding a second, less-exercised part
of the framework was judged the wrong tradeoff. The pipeline was
restructured into small, single-task Crews driven by explicit Python
functions (`run_researcher`, `run_analyst_draft`, `run_analyst_revision`,
`run_auditor`) orchestrated by a plain `while` loop, with a regex-based
verdict parser that fails SAFE (unparseable output is treated as FAIL,
not silently as PASS).

**Bug found before the loop was ever tested with real data:** the first
live single-case run exposed a gap in the Phase 13 Check 2 wording that
hadn't surfaced in prior testing — an Analyst diagnosis stated outright
that the case lacked the data for a Pareto ranking, then asserted one
anyway in prose ("we can qualitatively deduce that X and Y represent the
Vital Few causes"), and the Auditor passed it, reasoning that the
instruction's example format ("in a table or list format") meant a
prose-form ranking was exempt. That was a literal misreading the
instruction's ambiguity invited, not the model misbehaving. Fixed by
rewriting Check 2 to state explicitly that format never mattered — a
prose ranking claim and a table making the same claim must be checked
identically — and to explicitly address the exact pattern observed
(admitting insufficient data, then ranking anyway: the admission does not
excuse what follows it).

**Testing methodology: a deterministic test case instead of waiting for
the bug to recur.** Two subsequent single-case runs happened not to
reproduce the violation, which proved nothing about whether the fix
worked — LLM output isn't deterministic, so absence of a repeat is not
evidence of a fix. Rather than keep spending quota hoping for a natural
repro, the exact known-bad diagnosis text from the caught instance was
fed directly to `run_auditor()`, `run_analyst_revision()`, and
`run_auditor()` again in a standalone script (`test_check2_fix.py`),
bypassing the Researcher/Analyst draft steps entirely. This confirmed, in
one deterministic pass: the updated check correctly FAILs the known-bad
input; the revision step corrects only the flagged Pareto section
(verified line-by-line — the other three sections were unchanged); and
the re-audit correctly PASSes the fix. This is a more reliable validation
method for stochastic systems generally: constructing a known-bad input
and testing the fix directly is strictly more informative than running
the full pipeline and hoping the model reproduces a specific failure on
demand.

**Live full-batch validation, across all 3 cases, following the
deterministic test:**

| Case | Result | Detail |
|---|---|---|
| Southwest | PASS, 1 attempt | No violation this run — Analyst stopped at the honest "data insufficient" admission without asserting a ranking afterward |
| Boeing | PASS, 2 attempts | Attempt 1 failed Check 2 (an unsupported "vital few" ranking with a fabricated "Highest Impact" label); revision rewrote only the Pareto section to state ranking was not possible; re-audit passed; all other sections confirmed byte-identical between attempts |
| Peloton | PASS, 2 attempts | Attempt 1 failed Check 2 (labeling one cause the source of the "vast majority" of impact vs. a "minor compounding factor," with no supporting figures); revision corrected only the flagged claim; re-audit passed; all other sections confirmed byte-identical between attempts |

Zero errors, zero malformed or contradictory verdicts, zero `.FAILED.txt`
files this run.

**Why this result is stronger evidence than the deterministic test alone:**
Boeing and Peloton's failures were genuine, independent, live violations —
not the same hand-constructed input reused twice. Two different cases,
two different specific violations (a fabricated numeric-adjacent label in
one, a fabricated relative-magnitude claim in the other), both correctly
caught, both correctly and narrowly revised, both correctly re-verified.
That is a meaningfully more convincing result than either the single
deterministic test or a single lucky live pass would have been alone.

**Lesson:** a revision loop is only as trustworthy as the check driving
it. Building the control flow was the easy half of this phase; the
harder and more valuable half was discovering, through the loop's very
first live use, that the check it depended on still had a gap — and that
this gap would have been invisible without actually wiring up the loop
and running it, since a standalone Auditor test could pass or fail a
diagnosis without ever revealing whether the *reason* it passed would
survive contact with a real revision cycle.

---

## Phase 16 — Current State and Open Items

**Working and validated:**
- Framework knowledge base (15 items, 4 tiers).
- 3 real case packets with ground truth.
- RAG pipeline with a documented 3-way retrieval ablation and a proven
  query-reformulation fix (Phase 5).
- Researcher → Analyst → Auditor, 3-agent pipeline with a working revision
  loop (Phase 15): a failing audit is corrected and re-verified
  automatically, validated on 2 independent live violations plus one
  deterministic regression test, with zero mechanical failures across a
  full 3-case batch.

**Known limitations, worth stating rather than hiding:**
- Framework selection by the Researcher shows real run-to-run variance on
  the same case (Peloton in particular produced different framework sets
  across different runs) — single-run results shouldn't be treated as
  definitive; multiple runs per case, reported with variance, would be
  more defensible.
- Test set is 3 cases — informative for catching qualitative failure
  modes, too small for statistical claims.
- `max_revisions` is currently set conservatively (1) given quota
  constraints on the free-tier API; a case that still fails after its one
  revision attempt is reported as a final FAIL rather than retried
  further.

**Not yet built:**
- **RAGAS / formal evaluation harness** — for quantitative scoring beyond
  manual review.
- Any human-facing dashboard or write-up beyond this log.

*(Note: this snapshot was accurate when written. It is preserved
unedited, in keeping with this log's append-only style — see Phase 17
for a significant correction discovered immediately after, and Phase 18
for the current, up-to-date picture.)*

---

## Phase 17 — Data Leakage Discovery and Fix

**Trigger:** a direct question — "couldn't anyone just prompt ChatGPT and
get the same thing?" — prompted actually re-examining what the agents
had been shown, rather than assuming the case files were input-safe
because they'd been treated that way implicitly since Phase 3.

**Discovery:** every case packet (`cases/Case_*.md`) contains, in the
same file used as `{case_text}` for every pipeline run through Phase 15,
three sections that should never have been visible to a diagnosing
agent:
1. A `**Best-fit frameworks:**` metadata line, naming the exact
   frameworks the Researcher was "supposed" to select — present in the
   Researcher's task prompt on every single run.
2. A `## Documented Root Cause / Investigation Findings` section — a
   numbered list of the actual causal findings, handed to the Analyst
   as a fact rather than something to derive.
3. A `## Ground-Truth Diagnosis Summary` section, explicitly labeled
   *"for evaluating agent output"*, that states outright what a correct
   diagnosis should conclude — visible to the Analyst *while producing
   that diagnosis*, and to the Auditor while checking it.

Confirmed by direct inspection of `Case_01_...md` and cross-checked
against all 3 cases with an automated scan (`case_loader.py`, run
standalone) — all three leak markers were present in every case's raw
file, none were something later filtered out by any script.

**Impact on prior results:** Check 2 (Fabricated Ranking Scan) findings
from Phases 11, 13, and 15 remain valid — none of the leaked material
contains ranking percentages or weights, so every instance of catching an
invented Pareto claim was a genuine catch. **Check 1 (trigger vs. root
cause) results from Phases 8–15 do not hold up under scrutiny as evidence
of blind diagnostic reasoning** — they are better described as evidence
that the model could correctly restate a distinction it had already been
given, in Fishbone/5-Whys-formatted language. This does not mean those
outputs were low-quality — the formatting, financial arithmetic, and
Check 2 discipline were all genuinely demonstrated on their own merits —
but the specific claim "the pipeline correctly diagnoses trigger vs. root
cause" was never actually tested prior to this phase.

**Fix — `case_loader.py`:** parses each case file by its `## ` section
headers and splits it into:
- `diagnostic_input` — Problem Statement + Background + Supporting Data
  only. This is what gets fed to the Researcher, Analyst, and Auditor
  (and, from this phase on, the baseline).
- `reference_material` — everything else (the frameworks hint,
  documented findings, resolution, ground truth, sources). Used only for
  scoring output *after* generation, never part of any prompt.

Verified with an automated check across all 3 cases: none of the leak
markers (`Best-fit frameworks`, `Ground-Truth`, `Documented Root Cause`,
`Resolution`) appear in any `diagnostic_input`, and all are still present
in the corresponding `reference_material`.

**Callers fixed:** `crewai_researcher_agent.py`'s self-test block and
`run_researcher_all_cases.py` both previously read the raw case file
directly (`Path(...).read_text()`); both now use
`load_case(...).diagnostic_input`. `run_researcher_all_cases.py` also now
appends the `reference_material` to the *saved output file*, clearly
marked as scoring-only, so a human reviewer has ground truth available
side-by-side without it ever having been part of a prompt.

**New infrastructure built, enabled by having a valid blind input:**
- `baseline_single_llm.py` — a single, unscaffolded LLM call (same
  model, `gemini-3.1-flash-lite`, for a fair comparison), given the same
  `diagnostic_input` and a realistic but unscaffolded prompt: no
  retrieval, no forced reformulation step, no anti-fabrication
  instruction, no audit, no revision. This is the actual ablation
  baseline the project's evaluation design called for since Phase 2, and
  it could not have been built validly before this fix — comparing the
  pipeline against a baseline that also had access to the ground truth
  would have told us nothing.
- `run_comparison.py` — runs both the full pipeline and the baseline on
  the same case, saves both outputs plus the reference material
  side-by-side in one file for scoring. Not yet executed as of this log
  entry — see Phase 18.

**Lesson:** this went unnoticed through 15 phases and dozens of manual
reviews, including several rounds of specifically scrutinizing agent
output for exactly this kind of problem (Phase 13's fabricated-ranking
hunt). The reviews were real and found real issues, but they were all
reviews of *output quality given the input as it was* — nobody had
specifically audited *what was in the input* until a question about the
project's fundamental premise forced actually checking. Worth stating
plainly: a rigorous-looking evaluation process (multiple checks, ground
truth comparison, iterative refinement) is not the same thing as a valid
one, and the difference can hide in something as easy to overlook as
what's technically present in a file that was authored months of
conversation-time ago for an entirely different purpose (the case
packets were originally written with human readers in mind, where
including the answer alongside the question is completely normal).

---

## Phase 18 — Current State and Open Items (updated)

**Working and validated:**
- Framework knowledge base (15 items, 4 tiers).
- 3 real case packets, now with a verified, leak-free `diagnostic_input`
  split (Phase 17) alongside their original full form.
- RAG pipeline with a documented 3-way retrieval ablation and a proven
  query-reformulation fix (Phase 5).
- Researcher → Analyst → Auditor pipeline with a working, validated
  revision loop (Phase 15), **now confirmed to run on blind input**
  (Phase 17) rather than input containing the answer.
- Baseline comparison infrastructure (`baseline_single_llm.py`,
  `run_comparison.py`) — built, syntax- and import-verified, not yet
  executed with real API calls.

**Known limitations:**
- Framework selection variance across runs (unchanged from Phase 16).
- 3-case test set (unchanged from Phase 16).
- **All pipeline output generated before this phase** (every file in
  `researcher_outputs/` from Phases 8–15) was produced under the leaked
  -input condition. It remains valid evidence for Check 2 behavior and
  for output structure/quality, but should not be cited as evidence the
  pipeline diagnoses cases blind — that claim is only actually tested by
  runs that happen after this fix.
- The pipeline-vs-baseline comparison itself — the thing that would
  actually answer "does this add value over a raw prompt" — has not yet
  been run. Phase 17 built the infrastructure for it; it has not
  produced a result yet.

**Not yet built:**
- Actual execution of `run_comparison.py` and review of its output.
- RAGAS / formal evaluation harness.
- Any human-facing dashboard or write-up beyond this log.

*(Preserved unedited, as with Phase 16 — see Phase 19 for the actual
comparison results and a second confound discovered while reviewing
them.)*

---

## Phase 19 — Pipeline vs. Baseline: First Full Comparison, and a Second Confound

**Sub-finding 1 — a second, deeper leakage source than Phase 17's.**
Reviewing the first live baseline output (Southwest), it named the
crew-scheduling software specifically: "SkySolver." That string does not
appear anywhere in `case.diagnostic_input` — the case packets only ever
said "crew-scheduling software." Verified via web search that SkySolver
is a real, widely-reported detail (Wall Street Journal, Slashdot,
PopSci, Texas Standard, and others all name it), not a hallucination.
The baseline recalled it from its own training data.

This matters because all 3 cases were deliberately chosen (Phase 3) for
being real, well-documented, heavily-covered events — which also means
they are exactly the kind of event a large model is likely to have seen
described and analyzed many times during pretraining. Fixing the
file-leak (Phase 17) does not and cannot fix this: it is not about what
is in the prompt, it is about what the model already "knows." This
confound is **symmetric** — pipeline and baseline use the identical
underlying model, so neither side is unfairly advantaged by it — but it
does mean that "did the output match the documented ground truth" is
weaker evidence than it looks for these three specific cases; a
correct-looking answer could reflect genuine reasoning from the four
given paragraphs, or recall of a widely-reported story, and the two
cannot be distinguished from the output text alone. Findings that depend
on *process* rather than on matching a possibly-memorized outcome are
unaffected by this: Phase 5's retrieval ablation and Phases 11–17's
fabrication-catching results do not depend on whether the model already
"knows" the real story.

**Sub-finding 2 — full 3-case comparison results.**

| Dimension | Result |
|---|---|
| Trigger vs. root cause separation | Tied — both correct and clear on all 3 cases |
| Financial arithmetic accuracy | Tied — both accurate on all 3 cases (e.g. Boeing baseline's $12.8B figure is legitimate subtraction of two case-given numbers, not fabrication) |
| Fabricated-ranking risk (Check 2's target failure mode) | **Untested this run** — the baseline did not attempt a Pareto-style ranking on any of the 3 cases, so it never put itself in a position to fabricate one. The pipeline attempted Pareto/ROI-style quantification on all 3 and correctly declined to fabricate each time (consistent with Phases 11–17) |
| Framework breadth | **Clear, consistent pipeline advantage on all 3 cases** — SWOT (Boeing), a Decision Tree comparing the realized path against a counterfactual (Peloton), an explicit ROI analysis stating why an exact percentage couldn't be computed (Peloton) — none attempted by the baseline, which converged on 5 Whys + Fishbone + a financial table on every case |

**Why the framework-breadth finding is notable:** the Researcher's
retrieval surfaced these additional frameworks *without* the removed
"Best-fit frameworks" hint (Phase 17), which is a useful secondary
confirmation that framework selection is still doing genuine
retrieval-driven work post-fix, not just parroting a hint that no longer
exists. The most plausible explanation for the gap is architectural: the
pipeline's Researcher searches a curated 15-framework knowledge base via
a reformulated query; the baseline has only whatever frameworks the
model reaches for unprompted from general knowledge, which converges on
the two most famous/common techniques (5 Whys, Fishbone) rather than the
full available toolkit.

**Interpretation, stated carefully:** "attempts more, including harder
frameworks it may not fully execute, and explains the gaps" is not
automatically superior to "sticks to what it can cleanly finish" — a
business reader might well prefer the baseline's tighter output. But for
a rigorous, auditable analysis, attempting the harder framework and
being explicit about data limitations is the more defensible behavior,
and it is the one the pipeline exhibited consistently, the baseline
never did.

**Limitations of this specific comparison, stated plainly:**
- n=1 per case. Given the project's already-documented run-to-run
  variance (Phase 16/18), this pattern is suggestive across 3 cases, not
  statistically established.
- The comparison's most decisive possible result — does an *unaudited*
  process fabricate where the *audited* one doesn't — was not obtained,
  because the baseline avoided the framework where that risk would show
  up, on all 3 cases. This is the single most valuable follow-up
  experiment still available to the project and has not yet been run.

**Follow-up identified, not yet built:** a variant of the baseline that
explicitly *requires* a prioritized/ranked answer (removing its ability
to opt out the way it did here on all 3 cases) would give a genuine,
decisive test of the project's central claim, rather than the
suggestive-but-inconclusive result obtained here.

---

## Phase 20 — The Decisive Test: Forced Ranking Confirms Fabrication Risk

**Setup:** `baseline_forced_ranking.py` — identical model, identical
blind input, identical agent framing as the standard baseline, with one
change: the task explicitly requires a Pareto-style ranked breakdown of
causes by impact, closing the gap identified in Phase 19 where the
standard baseline simply never attempted the one framework where
fabrication risk would show up.

**Result: unambiguous fabrication on all 3 cases, with a striking
pattern.**

| Case | Rank 1 | Rank 2 | Rank 3 | Rank 4 |
|---|---|---|---|---|
| Southwest | Legacy IT/Software — 60% | Strategic Underinvestment — 25% | Operational Process — 10% | External Weather — 5% |
| Boeing | Cultural Misalignment — 60% | System Architecture — 25% | Regulatory Capture — 10% | External Competition — 5% |
| Peloton | Strategic Over-Investment — 60% | Forecasting Flaw — 25% | Operational Inefficiency — 10% | Product Recalls — 5% |

The identical 60/25/10/5 split, in the identical rank order (largest
controllable cause first, external trigger always last and always
smallest), across three cases with entirely different underlying
dynamics. None of the three cases' Supporting Data contains any per
-cause financial or quantitative breakdown — every given figure is a
lump-sum total (e.g. Southwest's $1.1B/$140M/$1.3B are three separate
aggregate costs, never attributed to specific causes) — so there is no
basis in any of the three inputs for assigning a percentage to anything.

**Why the repeated pattern is stronger evidence than a single fabricated
number would be:** three different-looking, case-specific percentage
breakdowns would at least be consistent with the (still fabricated,
still ungrounded) possibility that some case-sensitive process produced
them. Producing the *identical* distribution shape three times over
unrelated cases is much stronger evidence that no case-specific
reasoning occurred at all — the model appears to be pattern-completing
on the concept of "an 80/20 breakdown" itself (top cause ≈60%, second
≈25% — summing to the "vital few" ≈85% — then two smaller trailing
categories) rather than deriving anything from the specific case in
front of it.

**Also notable: zero hedging.** Unlike some instances earlier in this
project's own development (Phase 13), where a pre-fix Analyst sometimes
hedged a fabricated ranking with "we can qualitatively deduce" before
asserting it, this output presents all three fabricated breakdowns with
full confidence, in a formatted table, with a "Rationale" column reading
as derived analysis rather than the invention it is. A reader with no
independent knowledge of any of these cases has no textual cue that the
numbers aren't real.

**This is the decisive result the project's central ablation claim
depended on.** Compared directly against the pipeline's own Pareto
sections on the identical 3 cases (Phase 19, not re-run here, since
nothing about the pipeline changed) — which consistently declined to
fabricate a ranking, explicitly stating the data didn't support one,
across every test since Phase 11 — this is a genuine, controlled,
same-model, same-input, single-variable-changed comparison: audited
process vs. unaudited process, under identical pressure to produce a
ranking. Stated plainly: the identical model, given identical facts and
asked an identical, realistic question, fabricates a confident-looking
answer when nothing in the process stops it, and explicitly declines
when something does.

**Caveats, stated with the same rigor as the rest of this log:** n=3
cases, one run each per condition. The Phase 19 memorization confound
still applies to the trigger/root-cause and general-quality portions of
these outputs. It does **not** apply to the fabricated percentages
themselves — no published source for any of these three events reports
a Pareto-style percentage attribution across causes, so there is no real
"60/25/10/5" for the model to have memorized for any of them. This
specific finding is not subject to the same confound as the outcome
-matching results elsewhere in this log.

---

## Phase 21 — Closing the Loop: The Auditor Catches Its Own Real-World Target

`test_auditor_catches_forced_fabrication.py` fed the exact 3 fabricated
forced-ranking outputs from Phase 20 directly to the Auditor -- not the
hand-constructed example used to validate the check in Phase 15, but the
Auditor's actual real target.

**Result: 3/3 caught.** Check 1 correctly PASSed in every case
(confirming trigger/root-cause separation was genuine in these outputs
too), and Check 2 correctly FAILed with case-specific reasoning citing
the actual given figures in each case and explaining precisely why no
derivation supports the invented percentages. On Southwest, the Auditor
independently flagged two separate instances within the same output --
the ranking table itself, and a separate sentence framing the same
invented breakdown as accounting for "100% of the impact" -- rather than
stopping at the first violation found.

This closes the three-part chain the ablation study was built to
establish: the unaudited process fabricates under realistic pressure
(Phase 20); the audited process does not, under identical pressure
(Phases 11-17, 19); and the Auditor, presented with the unaudited
process's own actual fabricated output, correctly identifies it as such.
No part of this chain relies on a constructed or hypothetical example.
No new caveats beyond those already stated in Phase 20.

---

## Phase 22 — Repeated Forced-Ranking Test (n=9): Pattern Confirmed, Claim Corrected

**Setup:** `run_repeated_forced_ranking.py`, 3 repetitions of the Phase 20
`baseline_forced_ranking.py` per case (Southwest, Boeing, Peloton), 9 runs
total — the direct follow-up to the n=1-per-case limitation stated
explicitly in Phase 20's caveats.

**Environment problem, hit before any runs completed:**
- **Problem:** script failed immediately under the system `python3`:
  `ModuleNotFoundError: No module named 'crewai'`.
- **Diagnosis:** project dependencies (crewai and everything downstream)
  were installed into the project's existing `venv312` virtual
  environment, not the system interpreter — the script was invoked with
  the wrong interpreter, not a missing/broken dependency.
- **Fix:** re-ran with the `venv312` interpreter, no file modifications.
  All 9 runs then completed cleanly.
- **Lesson:** same class of issue as Phase 6 (environment/tooling, not
  logic) — cheap to hit, cheap to fix, worth a one-line note in the
  README (`source venv312/bin/activate` before running any script in
  this project) so it doesn't recur for whoever runs this next,
  including a future examiner trying to reproduce results.

**Result:**

| Case | Run | Percentages (rank order) | Matches 60/25/10/5 exactly? | Notes |
|---|---|---|---|---|
| Southwest | 1 | 70/15/10/5 | No | 4-tier; external (storm) last at 5% |
| Southwest | 2 | 70/15/10/5 | No | 4-tier; identical to Run 1 |
| Southwest | 3 | 70/20/10 | No | Only 3 tiers — external cause dropped entirely, not even at 5% |
| Boeing | 1 | 60/25/10/5 | Yes | Exact match |
| Boeing | 2 | 50/30/15/5 | No | 4-tier; same shape, shifted weights |
| Boeing | 3 | 60/25/10/5 | Yes | Exact match |
| Peloton | 1 | 60/25/10/5 | Yes | Exact match |
| Peloton | 2 | 60/25/10/5 | Yes | Exact match |
| Peloton | 3 | 50/30/15/5 | No | 4-tier; same shape, shifted weights |

9/9 runs fabricated a percentage-based ranking with zero declines or
omissions — the headline Phase 20 claim (an unaudited process fabricates
under this pressure) is fully confirmed at n=9, not just n=1.

**Correction to how Phase 20's finding should be described.** Only 4/9
runs reproduced the exact 60/25/10/5 split. Phase 20's language ("the
*identical* distribution shape three times... producing the identical
80/20 breakdown") was accurate to what n=1-per-case actually showed, but
reads as a stronger claim than n=9 supports if "identical" is taken to
mean the exact numbers are a fixed output of the process. They are not:
two further exact splits recur across unrelated cases — 70/15/10/5
(Southwest runs 1-2) and 50/30/15/5 (Boeing run 2, Peloton run 3) — both
preserving the same rank ordering and the same four-tier structure, just
with the top two tiers traded off by ±10 points. **What n=9 actually
establishes is stable at the level of shape, not value:** one dominant
controllable cause (50-70%), a second smaller one (15-30%), a third
smaller still (10-15%), and the external/triggering cause last and
smallest (5%), holding in 8/9 runs. Phase 20's sentences describing the
finding as producing "the identical 60/25/10/5 split" should be read
alongside this phase rather than taken as the full picture — the
mechanism claim survives, but the specific numeric claim needs this
correction so a reader checking the raw data against the log doesn't find
a discrepancy.

**Why the numeric variance is, if anything, better evidence for the
mechanism claim than exact repetition would have been.** Literal
memorization of a constant would produce zero variance. Genuine
case-specific reasoning would be expected to produce different
*structures*, not just different numbers, across three unrelated
business failures. What's observed is neither: a consistent structural
template (four tiers, controllable-causes-descending, trigger-always-last
-and-smallest, summing to ~100%) populated with numeric noise around two
or three preferred value-sets. That pattern is closest to what would be
expected from pattern-completion on the abstract shape of "a Pareto-style
breakdown" — reaching for a plausible-looking split rather than deriving
one — which is the same mechanism claim Phase 20 made, just now
correctly scoped to the shape rather than the exact digits.

**The one genuine outlier: Southwest Run 3.** Unlike all 8 other runs,
this one collapsed to a 3-tier table and omitted the external trigger
(Winter Storm Elliott) from the ranking entirely, rather than assigning
it 5% the way every other run did:

| Rank | Contributing Cause | Impact Weight |
|---|---|---|
| 1 | Legacy IT/Scheduling Software Obsolescence | 70% |
| 2 | Operational Strategy (Point-to-Point Complexity) | 20% |
| 3 | Management/Planning Negligence | 10% |

The storm is still named as "the trigger" in this run's prose diagnosis —
only the quantified ranking table excludes it. This is a structurally
different failure mode than the numeric fabrications elsewhere in this
phase and in Phase 20: the document becomes internally inconsistent
(narrative and table disagree about what happened), which a reader
skimming only the table — the natural way to read a Pareto ranking —
would not catch at all, unlike an invented percentage, which at least
presents as a checkable claim.

**Caveats, stated with the same rigor as Phase 20:** still a modest
sample (3 reps × 3 cases); no claim of statistical power beyond
"repeatable across multiple independent calls, not a single lucky/unlucky
draw." The Phase 20 memorization-confound reasoning applies identically
here — no published source reports a per-cause percentage attribution for
any of these three events, so none of the 9 runs' fabricated splits (nor
their absence, in Run 3) can be explained by memorized ground truth.

**Follow-up identified, not yet built:** extend Phase 21's
`test_auditor_catches_forced_fabrication.py` from the original 3 outputs
to all 9 from this phase, to confirm the Auditor's catch rate holds
across the full repeated set — and specifically whether Check 2's current
wording catches Southwest Run 3's *omission* of a cause from the ranking,
not just an invented percentage for a cause that's present. That's a
different failure signature than the one Check 2 was originally written
against and is not guaranteed to be caught by the same check logic
without being tested directly.

---

## Phase 23 — Repeated Auditor Test (n=9): Catch Rate Holds, Blind Spot Confirmed

**Setup:** `test_auditor_catches_forced_fabrication_repeated.py`, extending
Phase 21 from the original 3 real fabricated outputs to all 9 from Phase
22's repeated experiment. Run via `venv312`, same environment note as
Phase 22 applied again (the script imports `crewai` transitively).

**Result: 9/9 caught — every run received an overall FAIL verdict on
Check 2.** This confirms Phase 21's finding generalizes past the original
3-case, n=1 result: the Auditor doesn't just catch the specific
60/25/10/5 split it was validated against, it correctly FAILs both
numeric variants documented in Phase 22 (70/15/10/5 and 50/30/15/5) as
well. Check 1 (trigger/root-cause separation) PASSED cleanly across the
board, including on Southwest Run 3, confirming that structural deviation
is isolated to the ranking table and doesn't leak into the diagnosis
section.

**The specific concern raised in Phase 22 about Southwest Run 3 is
confirmed, not resolved.** The run was correctly failed, but for a
different reason than its distinguishing feature. The full Check 2
reasoning for that run addresses exactly two things:
1. The Pareto table itself (70/20/10) — correctly flagged as fabricated,
   unsupported percentages.
2. A single prose sentence naming a "primary" cause outside the table —
   explicitly marked **PASS**, reasoned as a narrative conclusion rather
   than a formal ranking claim.

**Nowhere in the Auditor's reasoning is the missing fourth row (Winter
Storm Elliott, absent from the table entirely) mentioned.** The overall
FAIL verdict is driven purely by the fabricated percentages attached to
the three causes that *are* present. The omission — the one thing that
made this run structurally different from the other 8 — was never
noticed or named, even though the run happened to fail anyway for an
unrelated reason.

**Why this is worth stating plainly rather than rounding up to "9/9,
including the hard case":** the practical outcome is fine here — nothing
got through undetected in this specific run. But the audit text reveals
that Check 2, as currently worded, is scoped to catch *invented numbers
attached to causes that are present*, and has no evident mechanism for
noticing a *cause that's absent*. That's a meaningfully different failure
signature. A hypothetical future output that dropped a cause from its
ranking while presenting accurate, fully-grounded numbers for the
remaining causes (no fabrication in what's shown, just an incomplete
picture) would, on this evidence, have no clear reason to be caught by
Check 2 as it's currently written — it was the coincidence of *also*
containing fabricated percentages that produced this run's FAIL, not
detection of the omission itself.

**Caveat, stated with the same rigor as the rest of this log:** this is
inferred from Check 2's stated reasoning on the one omission case
available (n=1 for this specific failure mode) — not directly tested
against a constructed case designed to isolate omission from numeric
fabrication. That controlled test — a fabricated-omission output with
otherwise accurate numbers — is the decisive follow-up if there's room
for one more experiment, and is the honest boundary of what this project
can currently claim about the Auditor's coverage.

**Bottom line:** the closed-loop chain established in Phase 21 holds at
n=9 — unaudited fabricates (Phases 20, 22), audited doesn't (Phases
11-17, 19), and the Auditor catches the unaudited process's real
fabrications reliably across the full repeated set, not just the
original single observation. This phase adds one honest limitation on
top of that success, rather than a failure of it: catching fabricated
*content* is demonstrated at n=9; catching fabrication *by omission* is
not demonstrated, and the one available data point suggests it may
currently be a blind spot. Worth stating exactly this way in the report
— it's a stronger, more credible claim than an unqualified "the Auditor
catches all fabrication," and it hands the report a genuinely honest
"future work" item instead of a vague one.

---

## Phase 24 — Controlled Omission-Isolation Test: Gap Confirmed Directly, Check 2's Real Behavior Is More Nuanced Than Documented

**Setup:** `test_auditor_omission_isolation.py`. Before building it, the
follow-up as originally scoped in Phase 23 ("an output that omits a
cause while reporting only accurate, case-grounded figures for the
causes it retains") turned out not to be constructible from this corpus
— no case provides a real per-cause percentage breakdown for anything
(this is the whole premise of the memorisation-confound discussion), so
there is no such thing as an "accurate" percentage to assign to any
cause in any of these three cases. The test was corrected accordingly:
three outputs were constructed, one per case, each taking the real Run 3
text verbatim for the diagnosis/5-Whys/financial sections and replacing
only the ranking section with a purely **ordinal** ranking — primary /
secondary / tertiary cause, in prose, zero numbers anywhere — that drops
the fourth, smallest cause from the real ranking entirely. This isolates
omission from numeric fabrication as cleanly as the corpus allows.

**Result: 2 of 3 FAILed (Southwest, Boeing), 1 of 3 PASSed (Peloton).**
Read as a bare score this looks like a partial catch. It is not — the
reasoning behind all three verdicts needs to be read directly, because
none of them are about the omission.

**What Check 2 actually objected to in Southwest and Boeing:** both were
failed for asserting a bare ordinal hierarchy — "the most significant
driver... a secondary contributing factor... a third, smaller factor" —
with no stated logical derivation for that order. The Auditor's own
language: for Southwest, "the analyst has invented a hierarchy of impact
('most significant,' 'secondary,' 'smaller') that is not supported by
the provided numerical evidence... using prose to rank these factors
does not exempt the claim"; for Boeing, "declaring one the 'primary
driver' and another a 'third, smaller factor' is a subjective fabrication
of a Pareto-style hierarchy presented as an analytical conclusion." Both
verdicts are entirely about the unjustified ordinal claim. Neither
mentions that a fourth cause is absent from the ranking.

**Why Peloton passed:** its constructed ranking included one additional
sentence the other two didn't have — an explicit causal derivation for
the order ("If the forecast had been accurate, the fixed-cost and
capital-allocation decisions that followed from it would have been
unnecessary"). The Auditor's reasoning treats this as legitimate
narrative synthesis of a causal chain rather than an invented weighting:
"a structural dependency argument rather than an invented Pareto
percentage." This is the only difference between the Peloton
construction and the other two, and it fully accounts for the different
verdict. Peloton's audit also never mentions the missing fourth cause.

**This refines, rather than contradicts, the Check 2 behaviour described
in Phase 23 and Section 6.4 of the report.** Section 6.4 documented that
Check 2 was calibrated not to flag comparative language that mirrors a
case's own ground truth. What this test adds is a sharper picture of the
actual discriminator: it is not "numeric vs. non-numeric" and it is not
"comparative language vs. not" — it is closer to *whether an explicit
derivation is given for the ordering*. A bare ordinal label ("primary,"
"secondary") reads to the Auditor as an asserted ranking claim requiring
support, in the same family as a fabricated percentage; a stated
if-then justification for the order reads as reasoning rather than
assertion. That's a real, previously-undocumented piece of the check's
behaviour, worth folding into Section 6.4 or 8.8 if the report is
touched again — though it rests on n=1 per condition here, same caveat
as everywhere else in this project: it's a plausible, cleanly-stated
hypothesis about the mechanism, not a statistically established one.

**The central finding is confirmed directly, not inferred, and is
sharper for having been tested this way.** All three constructions were
minimal, single-variable changes from real model output; all three
silently omit one cause from a ranking that presents itself as covering
"the contributing factors" comprehensively; and in **zero of three**
cases — the two FAILs and the one PASS alike — does the Auditor's
reasoning note that a cause is missing. The 2/3 catch rate is entirely
incidental to an unrelated property of the text (whether the ordering is
justified), not evidence that completeness is being checked. Peloton is
the clean demonstration: a document that quietly drops a quarter of the
causal picture, states no false claim of any kind, and receives a full
PASS with no objection raised anywhere.

**Bottom line:** the gap identified from indirect evidence in Section
8.8 (Southwest Run 3, caught but for an unrelated reason) is now
confirmed directly under controlled, minimal-difference conditions,
across all three cases, regardless of overall verdict. The project can
now state this as a tested finding rather than an inference: the
Auditor's current checks evaluate whether claims made are supported, not
whether the set of causes presented is complete. Closing that gap, if
it's worth closing, is a distinct addition — a Check 3 for ranking
completeness — not a fix to Check 2, which is behaving as designed for
the claims it does evaluate.

---

## Phase 25 — Orchestrator Built: A Real Bug Found by the Same Discipline the Project Trained Into the Auditor

**Setup:** `orchestrator.py` — the 4th piece from the original
architecture concept, built against the actual pipeline in
`crewai_researcher_agent.py` rather than the earlier informal
descriptions of what an "Orchestrator" should do. `run_pipeline()`
already implements bounded revision control (Researcher → Analyst →
Auditor, with a capped retry loop on FAIL), so the only genuinely
missing piece was synthesis: turning an Auditor-approved diagnosis into
a client-facing report. Two design rules were built in from the start:
(1) synthesis must never run on a diagnosis that didn't pass audit —
`run_orchestrator()` checks `final_passed` before anything else and
makes zero LLM calls if it's False, rather than producing a softened
version of a failed diagnosis; (2) the synthesis task's input surface
should be as narrow as possible, restricting what the agent can draw
from structurally rather than relying only on instructions — the same
principle behind Phase 17's input-hygiene rule for the Researcher and
Analyst.

**The single-case quick check initially wasn't verifiable at all.** The
first run of `orchestrator.py` produced a clean-looking report, but the
`__main__` block only printed the Orchestrator's status and final
report — not the approved diagnosis or framework context it was built
from. There was nothing to diff the report against. This was caught
immediately (the report contained a "2 million stranded passengers"
figure and an FMEA section that looked unfamiliar, but couldn't be
confirmed as new or legitimate without the source text), the script was
fixed to print all three pieces, and re-run. The re-run's report
happened to be clean, but a single re-run doesn't establish anything —
same lesson as Phase 20 → Phase 22 (n=1 isn't a pattern) — so the real
test was always going to be the 3-case batch, not a second single-case
spot check.

**The 3-case run via `run_orchestrator_all_cases.py` found a real,
structural bug — not a model failure.** All three cases passed audit and
synthesized. Manual cross-check of each report against its own case's
Framework Selection and approved diagnosis found:

- **Southwest:** clean, one label-only drift (a Fishbone cause filed
  under "Measurement" in the diagnosis appeared under "Management" in
  the report — same claim, same evidence, wrong taxonomy bucket).
- **Boeing:** clean, one scope-qualifier loss (the diagnosis's "by count
  of fatalities, 100%..." became an unscoped "100%..." when two
  sentences were merged — no new number, but the precision of what the
  number measured was lost).
- **Peloton: a real violation.** The report's entire "Strategic
  Analysis: The 'Bullwhip Effect'" section was built from the
  Researcher's framework-selection justification for a framework the
  Analyst never actually applied in the diagnosis and the Auditor never
  reviewed at all. The report presented it as though it were part of
  the vetted, audited analysis. Two smaller instances of the same
  pattern (Cynefin's "complex" vocabulary, VRIO's "liability" framing)
  appeared in the same case's report, also traceable only to
  Researcher-only content.

**Root cause: this was a bug in the task instructions I wrote, not a
model doing something unauthorized.** `SYNTHESIS_DESCRIPTION` explicitly
said the agent could draw from "the approved diagnosis **or framework
selection**" — permission to use Researcher output was written directly
into the prompt. The Researcher's output is never reviewed by the
Auditor at all, so anything drawn from it is, by construction, unaudited
content that would be presented as if it had passed the same review the
Analyst's diagnosis did. This directly contradicts the input-restriction
design rule the module's own docstring stated two paragraphs above the
bug. The model followed the instruction exactly as written — Peloton's
report is a close paraphrase of the Researcher's own justification text,
not an invention. One run out of three exhibited the failure, which is
itself informative: the model doesn't reach for unaudited content by
default, but the door was open, and leaving it open for three
independent runs was enough for one of them to walk through it.

**Fix:** `framework_context` was removed from `run_synthesis()` and
`SYNTHESIS_DESCRIPTION` entirely — not just reworded more strictly.
Given the model followed the flawed instruction exactly as literally as
it was written, a stricter sentence pointed at the same input isn't the
trustworthy fix; removing the input is. The approved diagnosis is now
the only content `run_synthesis()` can structurally draw from — every
framework actually applied is already named in the diagnosis's own
section headers, so nothing is lost by dropping the Researcher's text
from this step. Two additional constraints were added to
`SYNTHESIS_DESCRIPTION` addressing the Southwest and Boeing findings
directly: preserve the diagnosis's own category labels and groupings
exactly, and preserve exact scope qualifiers on any statistic when
sentences are combined or condensed. Both are evidenced fixes for
specific observed failures, not generic caution — same pattern Check 2's
wording followed through its own rounds of calibration (Section 6.4 of
the report).

**Lesson, worth stating plainly:** the exact discipline this project
built into the Auditor — never trust a clean-looking output, verify a
specific claim against its actual source before believing it — is what
caught this. A clean exit code and three PASS verdicts were not treated
as sufficient; the report text was checked sentence-by-sentence against
what it was supposedly built from, on the very first real test of a new
component, before any claim of success was made. That the bug was found
this way, at this stage, rather than a report or a demo later, is a
demonstration of the project's own stated principle working as intended,
not just a description of it.

**What's still open:** there is no automated, repeatable check that the
Orchestrator's output stays faithful to the approved diagnosis — the
check that found these three issues was manual, the same way Check 2's
was before its wording was fixed. A structural version of that check
(comparing synthesized output against source diagnosis the way Check 2
compares diagnosis against case data) is identified as a natural next
addition, not yet built. The fix above has not yet been re-validated
with a fresh 3-case run — the next run against the corrected
`orchestrator.py` is the actual test of whether the leak is closed, not
an assumption that removing the input necessarily closes it.

---

## Phase 26 — Project Housekeeping: File Audit, Orchestrator Re-Validation, and an Incidental Early Sighting of the Fabrication Pattern

**Setup:** a deliberate, read-only-first file-and-structure audit of the
whole project, done before further work, specifically to check for
orphaned files, undocumented-but-live code, and stale saved output —
followed by one confirmed filesystem reorganization once the audit
findings justified it.

**Audit findings, root-level `.py` files:** all 22 files resolved to
either a live import chain or an intentional standalone entry point —
no genuinely orphaned code found. Two specific pairs that looked like
possible duplicates on file listing alone were confirmed, by direct
import trace, to be deliberately distinct: `chroma_retriever.py` (v1,
MiniLM backend) and `chroma_retriever_v2.py` (v2, BGE backend, the
default) are both live, reachable via `RETRIEVAL_BACKEND` in
`retrieval_tool.py`'s `_build_retriever()` — v1 is a reachable alternate
backend, not superseded dead code. `baseline_single_llm.py` and
`baseline_forced_ranking.py` are two distinct, deliberately-separate
ablation conditions, not sequential versions of each other.
`run_forced_ranking_test.py` (n=1/case, Phase 19-20) and
`run_repeated_forced_ranking.py` (n=3/case, Phase 22) are sequential,
each still independently meaningful to keep. One real documentation gap
surfaced, not yet fixed: `chroma_retriever.py` and `chroma_retriever_v2.py`
are both live, both reachable, and both have zero mentions anywhere in
this log — noted here as the fix, since the gap is in this document, not
in the code.

**`requirements.txt`, `.gitignore`:** confirmed complete against actual
imports (nothing imported is missing, nothing listed is unused) and
`.env` confirmed present in `.gitignore`. One soft finding: `python-dotenv`
is a real, used dependency, but is only exercised by the standalone
`list_available_models.py` utility — none of the pipeline/driver scripts
call `load_dotenv()` themselves. Not a bug (the key resolves some other
way in the current shell), but a portability gap worth a defensive fix
if the project ever runs from a machine without `GEMINI_API_KEY` already
in the environment.

**Orchestrator re-validation (following directly from Phase 25's fix):**
the first `orchestrator_outputs/` files found during the audit predated
the Phase 25 fix by several minutes (batch run at 14:34-14:36, code fix
at 14:44) — meaning the only saved evidence of the Orchestrator's
behavior at audit time was the pre-fix version, still containing the
Bullwhip Effect leak. `run_orchestrator_all_cases.py` was re-run against
the corrected code; the fresh Peloton output contains no mention of
"Bullwhip" anywhere. Worth stating precisely what this does and doesn't
establish: this run's Researcher didn't even propose the Bullwhip Effect
framework this time (framework selection is non-deterministic, as
established elsewhere in this log), so it isn't a same-conditions
replication of the original leak. The structural guarantee — 
`run_synthesis()` no longer accepts `framework_context` as a parameter
at all, confirmed by direct code read — is doing the real work here, the
same category of guarantee as Phase 17's input-hygiene rule, not
something that needs repeated-trial confirmation the way Check 2's
wording did. Also confirmed: no CrewAI agent in this project sets
`memory=True`, and every synthesis call constructs a fresh `Crew()`
object rather than reusing one, so there is no session-state channel
that could leak Researcher content some other way.

**`researcher_outputs/` reorganization:** the directory turned out to
contain three structurally distinct artifact types that had never been
disambiguated, mixed together under one naming convention:

1. **Full modern pipeline runs** (Researcher + Analyst + Auditor, current
   format) — the `20260723T001240`-timestamped files and similar. These
   stay in place; they're the real output this directory is for.
2. **Researcher-only artifacts**, already correctly isolated in
   `researcher_only_archive/` before this audit — preserved because
   `run_researcher_all_cases.py` later reused the same filename for the
   combined Researcher+Analyst output, which would have silently
   overwritten them. An accidental-overwrite rescue, not a calibration
   exercise. No changes made here.
3. **Auditor-only artifacts** (12 files, 4 per case) from the Check 2
   wording calibration process documented in Phases 11-13 — verdict text
   only, no framework selection, no diagnosis, because these were
   produced while testing Check 2's wording in isolation, not as full
   pipeline runs. These were miscategorized by sitting unlabeled among
   the full pipeline outputs; moved to a new
   `researcher_outputs/check2_wording_calibration_phases11-13/` (kept
   separate from `researcher_only_archive/` deliberately — different
   pipeline stage, different provenance, not the same artifact type).

A fourth category was found in the process of characterizing the
remainder, and is discussed on its own below rather than folded into the
reorganization, since it turned out to matter for reasons beyond
housekeeping.

**Incidental finding: pre-Auditor diagnoses already show the fabrication
pattern.** The `20260722T225905`-timestamped file for each case is a
complete Researcher+Analyst diagnosis with no `## Audit Verdict` section
at all — these predate the Auditor's integration into the pipeline
(built in Phase 13, itself dated after these files' Jul 22 22:59-23:00
timestamps). Southwest's version of this early file assigns a Pareto
breakdown of approximately 60/25/10/5 across four causes — the same
shape later formally documented in Phase 20 as the fabrication
signature — sitting completely unaudited, since no Auditor existed yet
to review it. Peloton's early version does the same thing but more
explicitly, labeling its ~70/25/5 breakdown outright as "estimates."
Boeing's early version, by contrast, is clean: its Pareto section is
arithmetic-grounded (92%/8%, derived directly from stated dollar
figures), a legitimate ranking rather than an invented one. This is
**not** additional evidence in the controlled, n=9 sense Phase 22
established — these are uncontrolled, ad hoc development-time runs, not
part of any deliberate experiment, and treating them as a fourth or
fifth data point in that count would overstate what they are. What they
are is informative in a different way: a sign that the exact failure
mode the entire ablation study was later built to characterize was
already visible in the very first days of development, before anyone
was looking for it systematically. These files remain in place in
`researcher_outputs/` rather than being moved or archived — structurally
they're a valid, if pre-Auditor, example of a Researcher+Analyst run,
closer in kind to the directory's main contents than to either of the
other two categories described above.

**Lesson:** this was a deliberate, scheduled hygiene pass, not cleanup
triggered by a problem — and it still surfaced a real gap (stale
Orchestrator evidence sitting as if it were current), a real citation
opportunity (Phase 13's finding now points at its own exact source file),
and a genuine piece of project history (the fabrication pattern's
earliest known appearance) that wouldn't have been found by continuing
to add new phases without occasionally checking the state of what's
already there. Worth treating as a repeatable practice at natural
stopping points, not a one-time correction.

---

## Phase 27 — Report Submission-Readiness Pass: Usage-Model Clarification, Front Matter, and a Verified Related Work Section

**Context:** two things prompted this phase: a direct question about how
the finished system would actually be used, and a full cover-to-cover
read-through of the report (as opposed to verification scoped only to
the sections directly edited in prior phases), done specifically to
check for gaps that piecemeal editing wouldn't surface.

**Finding 1 — usage model stated plainly, with a scope boundary made
explicit rather than left implicit.** Today, using the system on a new
problem means writing a case packet by hand in the existing format
(Problem Statement, Background, Supporting Data — no intake step exists
yet for turning unstructured raw input into that structure) and calling
`load_case()`, `run_pipeline()`, and `run_orchestrator()` directly; the
result is either a client-facing report or a `FLAGGED_FOR_REVIEW` result
with the full attempt history. Stated alongside this, and worth
preserving precisely for any future description of the project,
including a pitch: the project's validated claim is that the audited
pipeline does not fabricate under pressure and the Auditor reliably
catches fabrication when it occurs — extensively demonstrated in Section
8. This is a narrower and different claim from "the diagnosis will be
good on an arbitrary new business problem," which has never been tested
and cannot be, by the project's own methodology, since all three
validation cases have independently documented ground truth to score
against and a genuinely novel problem does not. The system's reliability
at *not fabricating* is proven; its quality at *being right* on something
new is architecturally reasoned about, not measured. Conflating the two
in any future framing of this work would be exactly the kind of overclaim
this project has been careful to avoid at every other point in this log.

**Finding 2 — the report had real, previously unconfirmed front-matter
gaps.** A full read-through (not scoped only to Sections 1, 3, 5-11,
which is what prior editing sessions had directly touched) found no
title page, no abstract, no table of contents, no references/bibliography,
and no literature review or related-work section anywhere in the
document — it began directly at "1. Introduction." This had been an
open uncertainty flagged in Phase 26's percentage discussion but not
resolved until this phase's direct check.

**Actions taken — three of four gaps closed:**

1. **Related Work (new Section 2.1).** Positioned against MaRGen
   (Koshkin, Dai, Fujikawa, Togami, and Visentini-Scarzanella, 2025;
   LLM4ECommerce Workshop at the 31st ACM SIGKDD Conference on Knowledge
   Discovery and Data Mining, KDD '25; arXiv:2508.01370). Citation
   details — full author list, exact venue, publication date — were
   verified directly via web search before being written into the
   report, rather than trusted from an earlier conversation's recollection
   of the same paper, on the same standing rule against unverified
   attribution this project applies to every other empirical claim.
   The comparison drawn is specific rather than a generic "related work
   exists" gesture: real architectural overlap (both are role-
   differentiated multi-agent business-analysis pipelines with an
   internal review stage, broadly analogous to MASS's Auditor), against
   a precise difference in what each project is actually built to
   demonstrate (MaRGen: a general-purpose LLM-based quality scorer
   validated against human judgement; MASS: a narrow, decisive
   demonstration of one specific, well-defined failure mode, with an
   explicit characterisation of exactly what the Auditor's checks do and
   do not catch). Inserted as a subsection of the existing Section 2
   rather than a new top-level section, specifically to avoid the
   renumbering risk a new top-level section would have created across
   the report's many existing cross-references (e.g. "Section 8.5,"
   "Section 6.4") — a deliberate structural choice, not an oversight.
2. **Abstract.** Drafted in full (~260 words), explicitly flagged as an
   estimate rather than a confirmed fit, since the actual word-limit
   requirement for this submission is not known.
3. **Table of Contents.** A genuine Word TOC field (`\o "1-2" \h \z \u`),
   not a hand-written static list, so it stays accurate if the document's
   headings change again. Confirmed by PDF render that LibreOffice does
   not pre-compute the field's contents — it shows the designed
   placeholder text instead of fabricating page numbers it cannot
   actually compute outside Word. This is expected, correct behaviour,
   not a defect; the field needs one manual "Update Field" (or F9) the
   first time the document is opened in Word.
4. **Title page — not completed, deliberately.** Requires the
   supervisor's name, the exact programme/degree title, department,
   submission date, and the university's specific required layout and
   citation style, none of which should be guessed at for a formal
   submission document. Recorded here as open, not silently dropped.

**Small consistency fix folded into the same pass:** Section 1's own
outline paragraph, which briefly previews what each section covers, had
not been updated when Related Work (this phase) and the Orchestrator
(Phase 25/26's write-up) were added to the report — a minor but real
accuracy gap, closed with two small edits rather than left for a future
reader to notice first.

**Lesson:** the report's front-matter gaps had gone unnoticed across
several prior editing sessions specifically because verification had
been scoped to "the sections just edited" rather than the document as a
whole — the same shape of gap Phase 26 found in the project's file
structure by finally looking at all of it rather than only the parts
recently touched. A cover-to-cover read, done deliberately rather than
incidentally, is what caught it. Worth treating as the same standing
practice Phase 26 recommended for the codebase, applied here to the
document that describes it.

---

## Phase 28 — `crewai_researcher_agent.py` Renamed to `crewai_pipeline.py`

**Problem:** the file holding all three core agents (Researcher, Analyst,
Auditor) and the revision loop was named after only the first of them —
a naming leftover from before Analyst and Auditor existed. Confirmed by
the project's own file history: `researcher_only_archive/` (Phase 26)
holds output from a genuinely earlier version of the pipeline that
produced Researcher output only, before the file grew to hold all three
agents. The filename never caught up with what the file became.

**Fix:** renamed to `crewai_pipeline.py` — chosen over a name still tied
to the agent roster (e.g. `crewai_agents.py`) because the file's most
structurally important content is arguably `run_pipeline()` and the
revision loop, not the three `Agent()` definitions individually. Eight
real `from crewai_researcher_agent import ...` statements were updated
across eight dependent files (`orchestrator.py` and seven
`run_*_all_cases.py` / `test_*.py` files); five in-file comment/docstring
mentions were updated in `crewai_pipeline.py`'s own run instructions and
across `orchestrator.py`'s docstring. Two categories of mention were
deliberately left unchanged: `list_available_models.py`'s single
mention, which lives inside a runtime `print()` string rather than a
comment or docstring; and `DEVELOPMENT_LOG.md`'s three historical
mentions (lines documenting Phase 9 and the Phase 26 audit), which
correctly describe the file by the name it had at the time each entry
was written and should not be retroactively changed.

**Worth recording precisely: the verification step surfaced a real
contradiction in how it was specified, and the deviation used to resolve
it is itself a good example of this project's own standing principles.**
The task instructions asked for every touched file to be verified with a
plain `import`, but also explicitly prohibited executing any
`run_*_all_cases.py` driver or `test_*.py` file — and four of the eight
dependent files run real, quota-costing pipeline calls at module level,
with no `if __name__ == "__main__":` guard. A literal, uncritical
`import` of those files would have violated the no-quota constraint
while satisfying the verification wording. This was caught before
running anything, resolved by verifying only the specific edited import
line in isolation (`python3 -c "from crewai_pipeline import ..."`) plus
`py_compile` to catch any syntax error without executing module-level
code, and the deviation from the literal instruction was stated
explicitly rather than resolved silently in either direction — neither
blindly complying (spending quota) nor silently skipping verification
(leaving the rename unverified).

**Lesson:** this is the same shape of judgment this project has spent
most of this log trying to build into its actual AI components — the
Auditor's checks failing closed on ambiguous cases rather than guessing,
the Orchestrator refusing to run on an unapproved diagnosis rather than
producing output regardless. Worth noting explicitly that it showed up
here too, in the process of maintaining the project itself, not only in
the system under test. A set of instructions with an internal
contradiction is a normal thing to write by accident; catching the
contradiction before acting on it, and saying so, is the actual
standard being held throughout this project — for prompts given to
agents and for prompts given to any assistant working on the codebase.

---

## Phase 29 — First Live Test Through the New UI Surfaces a Third Auditor Blind Spot

**Setup:** the first end-to-end test of the intake → structure → diagnose
flow built in Phase 28's UI work, run against a genuinely novel case — a
realistic mid-sized retailer's fulfillment failure, written live by the
user, not one of the three validation cases and not run as a batch
script.

**What worked correctly:** the intake step preserved the one detail that
mattered most from the raw description — the user's own stated absence
of exact customer-attrition numbers came through as "Lost customers
reported, but no exact numbers provided," not an invented churn figure.
It also preserved the causal structure the rest of the pipeline depends
on: an internal warning (a system upgrade flagged a year earlier) sitting
behind an external trigger (a viral demand spike), the same shape as
every validation case. The Analyst's Pareto section correctly declined
to rank causes given the lack of granular data. The pipeline reached a
PASS verdict on the first attempt — confirmed by the UI's own "Verified"
status, not assumed from the report's content alone.

**What passed anyway, because neither existing check had jurisdiction
over it:** the synthesised report's Financial Impact section states an
"Implied Average Order Value (AOV): ~$219" and "approximately 822 orders
worth of revenue lost," presented as clean, precise derived arithmetic.
Working backward: $219 ≈ $40,000,000 / (500 × 365) — the Analyst treated
the case's stated *system design capacity* (500 orders/day, an
engineering ceiling) as though it were the company's *actual average
daily order volume*, an assumption never stated anywhere in the
diagnostic input or the report, in order to back into a specific-sounding
per-order dollar figure. A softer instance of the same pattern appears in
Why #2 of the 5 Whys, which states the system lacked "cloud-elasticity or
scaling features" — a specific technical detail present in neither the
user's original description nor the structured input.

**Why this is a distinct gap, not a restatement of Section 8.8/8.9's
finding:** that finding concerned a cause *omitted* from a ranking. This
is neither an omission nor a ranking. Check 2 is explicitly scoped, by
its own written instructions, to claims that assert "which causes are
the most significant" in a Pareto-style structure; the AOV figure makes
no claim about which cause matters most — it's an unrelated derived
financial statistic in a different section entirely. Check 1 is scoped
to trigger-vs-root-cause separation, which this doesn't touch either.
This case sits fully outside both checks' stated jurisdiction, not near
their edge — a confidently-stated, precise-looking derived number, built
on an unstated and incorrect assumption, presented outside any ranking
context, is a class of claim the Auditor was never instructed to review
at all.

**Caveat, held to the same standard as everywhere else in this log:**
this is one real, live instance on one novel case, found by manual
review during prototype testing — not a controlled, repeated experiment.
It stands in the same relationship to a future finding as Southwest Run
3 (Section 8.8 of the report) stood to the controlled omission-isolation
test that followed it (Section 8.9 / Phase 24): a genuine, specific
first sighting worth recording precisely, not yet generalised into a
tested pattern.

**Lesson:** the two existing checks were each built against a specific,
previously observed failure mode (Phase 11, Phase 13) and are correctly
scoped to exactly what they were built to catch — this is not evidence
either check is broken. It is evidence that "does the Analyst ever state
an unsupported figure" is broader than "does the Analyst fabricate a
cause ranking," and this fell through precisely that gap. A third check
— scoped to any specific numeric or quantitative claim in a report, not
only ranking claims — is a real, now-evidenced candidate for future
work, distinct from the ranking-completeness check already identified in
the report's Section 10.3, and would need its own build-and-validate
cycle the same way Check 2 and the omission gap did. Worth noting too:
this was found by a person using the product as a product, describing a
real-feeling problem and reading the output critically — not by a script
built to find it. The same scrutiny applied to every batch-run result in
this log is exactly what surfaced it here, on the very first real use of
the thing meant to make this system usable by someone who isn't running
Python scripts.

---

## Phase 30 — Same Live Test, a Second and More Significant Finding: Check 1 Verifies Distinctness, Not Whether the Trigger Is Actually External

**Setup:** the restaurant-chain case from Phase 29, examined further via
the full verbose CrewAI trace for Attempt 2 (the attempt that passed).
Unlike Phase 29's finding, which was inferred from the final report's
content, this finding is confirmed directly from the Auditor's own
stated reasoning text, captured verbatim in the trace — a materially
stronger form of evidence.

**Finding:** the diagnosis's Final Root-Cause Statement reads
"Triggering Event: The strategic decision to switch to a lower-cost
produce supplier three months ago." A decision is not, under any
reasonable reading of Check 1's own instructions ("an
external/proximate trigger" versus "a company-controllable systemic
root cause"), an external event — it is exactly the kind of
company-controllable action the instructions describe as belonging in
the root-cause slot. The genuine external force in this case —
inflationary pressure on margins, present in the diagnostic input's own
Background section ("due to inflation-related margin pressure") — was
never surfaced into the diagnosis's Fishbone, 5 Whys, or Final
Root-Cause Statement at all. It appears in the input and nowhere in the
output.

**Why this passed Check 1, confirmed from the Auditor's own words, not
inferred:** "The analyst correctly identifies the triggering event (the
specific procurement decision three months ago) as distinct from the
systemic root cause (the lack of standardized risk-assessment and
testing protocols that allowed the poor decision to occur)... The
diagnosis avoids conflating the two." Check 1's own explanation states
precisely what it verified: that the two labeled things are textually
distinct from each other. It does not state, anywhere, that it verified
the thing labeled "trigger" is actually external, or that the thing
labeled "root cause" is actually the deeper systemic issue rather than
the same controllable decision restated. Distinctness and correctness
are two different properties, and this instance shows the check
confirming only the first.

**Why this is a distinct finding from Phase 29's, not a restatement of
it:** Phase 29 found a claim type (a derived statistic outside any
ranking context) that neither existing check had jurisdiction over at
all. This is different in kind — it is Check 1 reviewing exactly the
claim type it has verified since Phase 11, and confirming a weaker
property than its own stated purpose requires. Every one of the three
validation cases (Southwest's storm, Boeing's competitive pressure from
Airbus, Peloton's pandemic) supplies an unambiguous, textbook-external
event to serve as the trigger. None of them ever gave Check 1 a case
where a company's own decision was a plausible-looking but categorically
wrong candidate for that slot, competing against a real external cause
mentioned elsewhere in the same case. This is the first case tested that
actually exercises that specific condition, and the Auditor's own
reasoning shows exactly where its real verification falls short of its
stated one.

**Caveat, held to the same standard as everywhere else in this log:**
one real instance, on one novel case — but confirmed by the Auditor's
own verbatim reasoning rather than inferred from the final report's
content alone, which is stronger evidence than Phase 29's finding
despite both being single instances. What Attempt 1 (the revision this
passed after) actually stated, and what it was originally flagged for,
is not available in the captured portion of the trace — worth obtaining
if this is followed up on, since it would show whether this exact
trigger framing was already present before the revision cycle or
introduced by it.

**Lesson:** Check 1 has been validated, since Phase 11, against exactly
one specific failure mode — conflating a correctly identified trigger
and root cause into one restated thing. It has never been tested against
a case where the wrong category of thing gets confidently and distinctly
labeled "the trigger" while a real external cause sits unused elsewhere
in the same case, because no validation case ever offered a plausible-but-
wrong candidate for that slot before this one. This is the same shape of
discovery as Southwest Run 3 before the controlled omission test that
followed it: a real gap becomes visible only once a case exists that
actually exercises the boundary condition, and all three original
validation cases, however well chosen for other purposes, happen to
share a structural feature — an unmistakable external event — that this
restaurant case does not. A refinement to Check 1 that verifies the
labeled trigger genuinely could not have been prevented or chosen by the
company, not merely that it is textually distinct from whatever is
labeled root cause, is a real, now-evidenced candidate for future work —
following the same iterative, evidence-driven refinement process
documented for both checks in the report's Section 6.4, rather than a
full rewrite of a check that has otherwise held up well.

---

## Phase 31 — Log Correction: Check 1 Part B Was Already Implemented, Log Was One Phase Behind the Code

**Problem:** Phase 30's closing Lesson describes a refinement to Check
1 — verifying that the labeled trigger is genuinely external, not
merely textually distinct from whatever is labeled root cause — as "a
real, now-evidenced candidate for future work." That framing is no
longer accurate. `AUDIT_DESCRIPTION` in `crewai_pipeline.py` already
implements exactly this as Part B of Check 1, verified directly
against the live constant rather than assumed from memory of what was
planned.

**Diagnosis, shown rather than asserted:** Phase 30's own words: "A
refinement to Check 1 that verifies the labeled trigger genuinely could
not have been prevented or chosen by the company, not merely that it is
textually distinct from whatever is labeled root cause, is a real,
now-evidenced candidate for future work." Against that, the live
`AUDIT_DESCRIPTION`, Part B, verbatim: "Is the thing labeled as the
'Triggering Event' or 'Trigger' something the company itself did NOT
choose, decide, or have the ability to prevent -- e.g. a weather event,
a competitor's action, a pandemic, a regulatory change, a macroeconomic
shift? A company's OWN strategic decision, business choice, policy, or
internal action (e.g. 'the decision to switch suppliers,' 'the choice
to cut costs,' 'leadership's decision to...') is NOT a valid trigger, no
matter how the diagnosis labels it -- it belongs in root-cause analysis,
not the trigger slot. If the diagnosis labels the company's own decision
or action as the trigger, Part B FAILS." This is the same refinement
Phase 30 called future work, already written into the check — down to
the same "decision to switch suppliers" example Phase 30's own
restaurant case surfaced independently. Check 1's audit format also
already requires Part A and Part B to be reported and verdicted
separately, with the overall check failing if either part fails, which
is the structural form Phase 30's Lesson was asking for.

**Fix:** no code change — the code was already correct. The fix is this
log entry itself: closing the gap between what the log said was
pending and what the pipeline has actually been enforcing, so neither
this log nor anything drawn from it (the report, a defense, a future
phase built on top of Phase 30's stated gap) misdescribes already-shipped
work as an open item.

**Lesson:** a development log entry is a claim about the state of the
code at the moment it is finalized, not only a record of what was true
when the phase was drafted or when the underlying fix actually landed.
Phase 30 was accurate when it was written. But nothing in this log
re-checks an earlier phase's "future work" language against the live
code once later work addresses it elsewhere — the gap between Phase 30
and the current `AUDIT_DESCRIPTION` sat unnoticed until it was directly
compared here. The same discipline this project has repeatedly applied
to the Auditor and the Orchestrator — verify a specific claim against
its actual source rather than trusting that it still holds — applies to
maintaining this log too, not only to the system it describes.

---

## Phase 32 — Orchestrator Fidelity Check: Design, Build, and Three-Round Calibration

**Setup:** `orchestrator.py`'s own docstring flagged a real gap since
Phase 25 — no automated, repeatable check that the synthesized report
stays faithful to the approved diagnosis, only the one-time manual
comparison that found that phase's bugs. Built `fidelity_check.py` as
the automated version, mirroring Check 2's structure (Agent + Task +
structured PASS/FAIL verdict) but grounded directly in Phase 25's three
actual findings rather than a generic hallucination check: Check A
(New Content Scan) targets Peloton's unaudited-content leak, Check B
(Label & Category Fidelity) targets Southwest's Fishbone relabeling,
Check C (Scope-Qualifier Preservation) targets Boeing's dropped
qualifier. Wired into `run_orchestrator()` on the same fail-closed
principle as everything else in this pipeline: a report that fails
this check is never returned as `"SYNTHESIZED"` — it's downgraded to a
new `"FLAGGED_FIDELITY_FAILURE"` status, with the raw report kept under
`unverified_report` for debugging only, never presented as a verified
deliverable.

**First live smoke test — a real catch, immediately followed by a
methodology mistake.** A single run on Southwest produced a FAIL,
correctly flagging a genuine dropped qualifier (the $2.4B figure's
"sum of sunk cost plus capex to achieve parity" explanation lost) but
also flagging two harmless paraphrase-level changes as violations. A
naive attempt to re-check this by re-running `run_synthesis()` and the
fidelity check together came back clean — but that changes two things
at once. `run_synthesis()` is non-deterministic; a different report
text each call tells you nothing about whether the *checker* is
consistent on identical input. That comparison was worthless and was
abandoned in favor of testing the checker in isolation.

**Round 1 — isolated repeated-trial test (n=5 x 2 fixtures), and an
honest fixture-construction mistake.** Fixed two report texts by hand
and called `run_fidelity_check()` directly, with no synthesis call at
all. The `harmless_paraphrase` fixture was not actually clean — it
unintentionally dropped the diagnosis's parenthetical Fishbone
sub-labels ("Mother Nature (Environment)" → "Mother Nature") and
relabeled the 5 Whys' Q&A format into short declarative labels, neither
of which was the intended test. Both were flagged 5/5 — likely correct
catches of a real (if accidental) deviation, not evidence of anything
broken. One clean signal survived the confound: the single word
"traditional" added to "hub-and-spoke" was flagged as new content in
all 5 trials, unconfounded by anything else — solid evidence Check A
was stricter than its own stated rule ("a paraphrase... is fine"). The
`real_qualifier_drop` fixture caught its planted violation 5/5,
establishing Check C's baseline correctness before any wording changes.

**Design decision required before continuing:** should dropping a
parenthetical sub-label (primary label unchanged) count as a Check B
violation? Decided: no. Phase 25's own evidentiary basis for Check B
was a *primary* label change ("Measurement" → "Management," a
different bucket) — not a secondary annotation being dropped while the
primary label stays intact. Requiring exact preservation of
parenthetical framework taxonomy would also contradict
`SYNTHESIS_DESCRIPTION`'s own instruction to strip "framework
definitions and step-by-step process boilerplate" the client doesn't
need.

**v2 revision:** Check A's wording added an explicit worked example
distinguishing meaning-preserving reword from a genuinely new
assertion. Check B's wording added an explicit primary-vs-secondary
distinction, matching the decision above.

**Round 2 — four clean, single-variable fixtures (n=5 each), built from
one shared verbatim base with exactly one change per fixture (verified
programmatically before spending any quota, not assumed).**
`paraphrase_only` and `parenthetical_dropped` PASSed 5/5 each — the two
intended fixes both confirmed. `category_renamed` (a deliberate
reproduction of Phase 25's real bug shape) FAILed 5/5 — confirming the
v2 loosening didn't blunt Check B's actual job. But `qualifier_dropped`
— unchanged since round 1, where it correctly FAILed 5/5 — regressed to
6/6 incorrect PASS across two separate runs (one call before a
rate-limit crash, a fresh five after). Not a fixture bug: the
qualifier-drop's `.replace()` was verified locally to have removed both
occurrences before concluding anything.

**Root cause, found directly in the verdict text, not inferred:**
every one of the 6 mismatched verdicts described the unqualified
restatement using language that mirrors v2's own new Check A wording —
"summaries and consolidations of information," "arithmetic aggregation
of figures provided." Check A's newly-added tolerance for paraphrase
and condensing had bled into Check C's judgment on a question it was
never meant to touch. All three checks are evaluated in a single task,
one prompt, one pass — loosening one check's posture loosened the
model's general posture on an entirely different, untouched check.

**v3 revision:** Check C's wording made explicitly immune to Check A's
tolerance — states outright that a figure being "the same number" or
"traceable to the diagnosis" is not sufficient for Check C, gives a
worked contrastive example ("in combined costs" vs. the specific
sunk-cost-plus-capex breakdown it's supposed to preserve), and
explicitly instructs the reviewer not to describe a dropped qualifier
as a "summary" or "consolidation."

**Round 3 — retest (n=5 on the regressed fixture, n=3 regression checks
on the other three): 14/14 clean.** `qualifier_dropped` restored to
5/5 correct FAIL, matching its original round-1 baseline. The other
three held their round-2 pattern exactly (`paraphrase_only` 3/3 PASS,
`parenthetical_dropped` 3/3 PASS, `category_renamed` 3/3 FAIL). First
fully clean result across three calibration rounds.

**Lesson:** two, not one. First — the same lesson as Phase 20 → Phase
22 and the naive re-run this phase started with: a single sample, or a
comparison that varies more than one thing at a time, tells you
nothing about whether a checker is reliable. Isolating exactly one
variable (a fixed report text, repeated trials, one fixture-diff at a
time) is what surfaced both the real regression and ruled out a
fixture-construction bug before either was acted on. Second, and new to
this project: checks are not independent just because they're labeled
separately within one prompt. A wording fix aimed at one check needs to
be re-validated against every *other* check sharing that prompt, not
just the one being edited — the fix for Check A's over-strictness is
exactly what broke Check C, and nothing about editing Check A's text
would have made that obvious without testing Check C specifically
afterward.

**What's still open:** all three rounds validated against hand-built
fixtures for one case (Southwest) only. The fidelity check has not yet
seen real Orchestrator synthesis output, and has not been tried against
Boeing or Peloton's diagnoses at all. A real 3-case batch run through
`run_orchestrator_all_cases.py` with the fidelity check wired in is the
natural next step — the same graduation from synthetic test to full
batch validation that `orchestrator.py` itself went through in Phases
25–26.

---

## Phase 33 — Graduation Run: Fidelity Check on Real Synthesis Output, and an Open Question About Boeing

**Setup:** first full 3-case batch run (`run_orchestrator_all_cases.py`)
since the fidelity check (v3) was wired in and pacing was added
throughout (5s before Researcher/Analyst/Auditor calls in
`crewai_pipeline.py`, 5s before the fidelity check in
`orchestrator.py`, 30s between cases) after Google AI Studio's rate
limit dashboard confirmed the free-tier cap (15 RPM for
`gemini-3.1-flash-lite`) that crashed an earlier calibration run. No
rate-limit errors this run across all 3 cases, including Boeing's
2-attempt revision cycle.

**Southwest — clean.** Passed audit attempt 1, synthesized, fidelity
check PASSed all three checks — first time it's seen real synthesis
output rather than a hand-built fixture, and it held.

**Peloton — the fidelity check's first genuine catches on real
content, and a real scope question surfaced immediately.** Check C
correctly flagged two real precision losses: "55% of capital invested
*into expansion*" generalized to "55% of *total* capital invested," and
a dropped parenthetical breakdown of what a "15% annual carrying cost"
specifically included (storage, insurance, obsolescence) — both the
same shape as Boeing's original Phase 25 finding. Check B also flagged
two label changes — "Porter's Five Forces" retitled "Market Dynamics
(Porter's Five Forces)," and "Financial Metrics" retitled "Financial
Impact" — but both of these are report SECTION HEADINGS, not
Fishbone-style cause-classification labels, and Phase 25's actual
evidentiary basis for Check B was specifically about the latter. This
was not a minor footnote: it prompted an immediate design decision, a
wording fix, a regression the fix accidentally caused, and a
structural rewrite to fix that properly — the full arc is in Phase 34.

**Boeing — flagged for review after 2 attempts, both failing Check 1
Part B for the same reason.** Attempt 1 framed the trigger as "the
erroneous data provided by a single AOA sensor"; Part B FAILed it,
reasoning the sensor's behavior was "a function of the technical
design... choices made and controlled by Boeing engineers." The
revision reframed it as "the internal decision to utilize a single AOA
sensor," which FAILed for the same reason, more explicitly. Check 2
passed both times (Attempt 1's fabricated "majority" ranking claim,
made immediately after admitting no data supported it, was correctly
caught; the revision correctly dropped it).

**An initial misreading, corrected before it was written down as
fact:** an earlier Boeing batch (`20260725T155235`, predating this
session) appears to PASS with near-identical "erroneous input from a
single AOA sensor" phrasing, which looked at first like evidence Part B
is inconsistent. It is not a valid comparison — that earlier run
predates the Check 1 Part A/Part B split entirely (Phase
"Renaming crewai_researcher_agent and fixing audit check" restructured
Check 1 into two parts after that batch was generated); it used the
old, single-check version that only verified distinctness, not
externality. Comparing today's Part B result against a run that never
ran Part B at all would have been comparing two different checks.
Caught and corrected before drawing any conclusion from it.

**What today's result actually shows:** Part B applied itself
*consistently* across both attempts, on genuinely similar phrasing,
with genuinely similar reasoning both times. This is not evidence of
an unreliable check. It's evidence of a real, unresolved design
question: Southwest and Peloton both have unambiguous macro-
environmental triggers (a storm, a pandemic demand reversal) that are
obviously outside the company's control. Boeing's only trigger
candidate is a specific technical component malfunction — a category
Part B's own examples ("weather event, competitor's action, pandemic,
regulatory change, macroeconomic shift") don't cover, and one that sits
uncomfortably close to being a foreseeable consequence of the very
design decision the diagnosis identifies as the root cause, rather than
an independent event.

**Two honest readings, not yet resolved:** (1) Part B's definition of
"external" is too narrow and should explicitly accommodate a specific
physical/technical malfunction as distinct from the systemic decision
that created vulnerability to it, or (2) Boeing genuinely lacks a clean
trigger/root-cause split the way the other two cases have one, and
`FLAGGED_FOR_REVIEW` is the pipeline correctly recognizing that and
routing it to a human, not a failure to produce output. This is a
policy decision, the same shape as the parenthetical-label question
resolved earlier this phase-cluster, not something to guess a wording
fix for.

**Lesson:** two, again. First — catching your own mistaken inference
before it becomes a written conclusion matters as much as catching the
system's mistakes; the "Part B is inconsistent" read would have been
wrong, and it was only caught by checking which version of the check
generated the comparison run, not by trusting that a timestamp near the
others meant the same check ran. Second — not every case necessarily
has the same *shape* of ground truth. Southwest and Peloton are both
operational-disruption cases with a clean external shock; Boeing is a
product-safety/technical-failure case that may not fit the same
trigger/root-cause template at all. A check built and validated against
two cases of one shape being less certain on a case of a different
shape is itself useful information, not necessarily a defect — same
spirit as Southwest Run 3 and the restaurant case before it: a real
edge only becomes visible once a case exists that actually exercises
it, and this project's three original validation cases were never
chosen to be structurally identical to each other in the first place.

---

## Phase 34 — Check B's Scope, a Second Cross-Contamination Regression, and a Structural Fix

**Setup:** Phase 33's Peloton finding needed a decision before any
wording changed: should Check B's strict label-matching apply to
report SECTION HEADINGS, or only to Fishbone-style CAUSE-CLASSIFICATION
labels (the actual thing Phase 25's "Measurement" → "Management"
finding was about)? Decided: cause-classification labels only.
`SYNTHESIS_DESCRIPTION` explicitly licenses reformatting sections into
"plain business language," and a rule that fails every section retitle
would make Check B fight the Orchestrator's actual job description.

**v4 revision:** Check B's wording scoped explicitly to
cause-classification labels, with the real Peloton phrases
("Financial Metrics" → "Financial Impact," "Porter's Five Forces" →
"Market Dynamics (Porter's Five Forces)") used as worked "do not flag
this" examples.

**Verification, round 1 — looked clean, wasn't.** Tested against the
`category_renamed` regression fixture (3/3 correct FAIL, as expected)
and — critically — against the *exact real Peloton diagnosis and
report* from the graduation run, not a new synthetic fixture. That
real pair came back 3/3 clean PASS overall. On the surface this looked
like total success. It wasn't: Check C's verdict text explicitly
claimed "there were no instances of generic 'total' or 'sum' language
replacing specific compositional definitions" — but there
demonstrably is one, the same "into expansion" drop this exact input
had correctly failed on under v3, moments earlier in the graduation
run. The check wasn't just missing the violation; it was confidently
asserting the opposite of what the text says.

**Root cause — a second instance of round 2's pattern, not a new
bug.** Round 2 (Phase 32) found that fixing Check A's wording caused
Check C to stop catching a real qualifier drop, because both checks
shared one prompt and Check A's new leniency language bled into Check
C's judgment. This was the same failure mode again, from a completely
different edit: fixing Check B's wording caused Check C to regress a
second time. Leading hypothesis: Check B's new wording used the real
Peloton document's own exact phrases as its "acceptable" examples, and
re-testing against that same document may have let the model treat the
whole input as "pre-approved" rather than evaluating it fresh — a
methodological trap specific to baking a real test case's text into
the instructions used to re-test that same case. But the more
important fact doesn't depend on resolving which mechanism caused it:
two different checks, edited for two different reasons, have now each
broken the same third check that was never touched. That is evidence
about the architecture, not about either individual wording change.

**Decision: stop patching wording, fix the architecture.** Two
regressions of the identical shape from two unrelated edits meant
another wording patch would likely just relocate the problem again.
Rewrote `fidelity_check.py` so each of the three checks runs as its
own fully isolated `Agent` + `Task` + `Crew` call — Check B's
instructions are never present in Check C's prompt, or in any other
check's, at all. Cost: 3x the LLM calls per fidelity check instead of
1 (paced 5s apart, on top of pacing already added elsewhere in the
pipeline, given the confirmed 15 RPM free-tier ceiling). The external
interface (`run_fidelity_check(approved_diagnosis, final_report)` →
`{"passed": bool, "verdict_text": str}`) is unchanged, so
`orchestrator.py` needed no edits at all.

**Verification, round 2 — clean, and this time it proves the actual
mechanism.** Re-ran both fixtures with per-check visibility (not just
one bundled verdict): `peloton_real` came back Check A PASS / Check B
PASS / Check C FAIL in all 3 trials — Check C catching the real
qualifier drops again, completely independent of what Check B's
wording says now. `category_renamed` came back Check A PASS / Check B
FAIL / Check C PASS in all 3 trials — the real label-change regression
guard still holds. 18/18 individual results matched expectations
exactly — the cleanest result across all five fidelity-check
revisions to date, and unlike round 1's "clean" v4 result, this one
shows *why* it's clean (each check isolated) rather than just *that*
it looks clean.

**Lesson:** a wording fix that resolves one regression is not evidence
the underlying cause was wording at all. The first time Check C broke
(Phase 32), a wording patch to the check that broke it (Check A) was a
reasonable first hypothesis. The second time Check C broke — from a
completely unrelated edit — the correct inference wasn't "patch Check
B more carefully," it was "stop trusting that these three checks are
actually independent just because they're labeled separately in one
prompt." Two data points of the same shape from two different causes
is a pattern about the shared architecture, not about either edit
individually — and the fix that actually holds up under isolated,
per-check re-verification is the one that removes the shared context
entirely, not the one that tries to word around it a third time.

---

## Phase 35 — First Validation Pass for the Intake Agent

Setup: intake.py (the Intake Specialist -- converts a user's raw free-text problem description into the Problem Statement / Background / Supporting Data format the rest of the pipeline expects) has been in the project since before this phase without ever going through the build-test-find-a-real-defect cycle every other agent went through. Its own docstring named the specific risk: turning something vague into something that reads as complete and specific is exactly the shape of "fabrication under pressure" this project's central empirical result (Section 8 of the report) is about. This phase is that first pass.

Design: three fixtures spanning how much concrete data is actually present, each with the exact ground truth documented before any output was generated, so any number appearing in the output that isn't in the ground truth is an unambiguous fabrication:

FIXTURE_SPARSE -- zero concrete numbers or dates anywhere in the input, only qualitative complaints and an explicitly hedged internal hypothesis ("our team thinks it might be... but we honestly haven't dug into it").
FIXTURE_ONE_NUMBER -- exactly one figure (340%, a late-delivery complaint increase), with an explicitly hedged causal claim ("it seems related, though we haven't confirmed it") about a carrier switch.
FIXTURE_DETAILED -- seven concrete figures (a subscription tier's price, its comparison tier's price, projected vs. actual signups, two churn rates) and one stated reason for cancellation.

Each fixture was run 5 times (15 trials total), matching the n=5 scale used for the fidelity check's first calibration round (Section 6.7), not yet the Auditor's own n=9 standard (Section 8.7).

Result: clean across all three axes checked, all 15 trials. FIXTURE_SPARSE stated explicitly that no concrete data was provided in every trial, rather than inventing a percentage or dollar figure to make the section look complete. FIXTURE_ONE_NUMBER surfaced exactly 340% and nothing else numeric in every trial. FIXTURE_DETAILED listed exactly the seven given figures in every trial, with no invented revenue-impact number and no additional cancellation reason. A fourth property, not originally planned as a separate check but verified directly: both fixtures containing a hedged causal claim ("seems related, though unconfirmed"; "might be... haven't dug into it") preserved that hedge in all 5 trials each, rather than promoting it into an unstated certainty -- a subtler failure mode than fabricating a number, and one the task instructions don't explicitly name, so this wasn't guaranteed by the prompt alone.

What this does and does not establish: this is a first validation pass targeted specifically at the risk the module's own docstring identified, not exhaustive validation of the component. Untested: long, rambling, multi-topic input; genuine ambiguity about which section a fact belongs in (the task's own stated tolerance for using judgement on placement without adding content); and inputs containing vague quantifiers that might get mistakenly promoted into concrete figures (e.g. "about half our customers" becoming a stated percentage). None of these were observed to fail -- they simply weren't tested here, and are noted as such rather than assumed covered by the three fixtures that were run.

Fix: intake.py's module docstring updated to replace the blanket "NOT-YET-VALIDATED" warning with an accurate account of what has and hasn't been checked, referencing this phase.

Lesson: the same evidentiary standard applied to every other component's first validation pass applies here too -- a clean result across a targeted set of fixtures is real evidence for the specific risk those fixtures test, not a general clearance. The hedge- preservation finding in particular was not something the test was designed in advance to check for; it surfaced from actually reading the output against the input rather than only checking whether numbers matched, the same discipline that found the cross-contamination regression in Phase 34 by reading verdict text rather than trusting a PASS/FAIL count alone.

---

## Phase 36 — Ohio Warehouse Externality Stress-Test (Check 1, Part B)

Problem: Constructed a synthetic test case (Ohio Warehouse shipping failures) with an entirely internally-caused root cause — a company-elected software migration, no independent external event — and ran it through the full /diagnose pipeline across multiple Analyst drafts. Every attempt returned FLAGGED_FOR_REVIEW, surfaced to the frontend only as a generic fallback message with no visible specifics.

Diagnosis: Captured raw, unprocessed audit output (capture_raw_audit_output.log) to bypass simplify_audit_feedback() and see the Auditor's actual verdict. Confirmed Check 1 Part B (Trigger Is Genuinely External) failed consistently across three independently-worded attempts, each recasting the trigger with progressively subtler phrasing — "Internal Process Change" → "notification of shipment error reports" → "unexpected operational volatility following go-live" — all correctly rejected as internal decisions in disguise. Check 2 (Fabricated Ranking Scan) passed clean in the same run, including a case where the Analyst explicitly declined to fabricate a Pareto breakdown given missing categorical data, correctly avoiding the Phase 22 fabrication pattern. Separately investigated whether the generic fallback message indicated missing Check 1 extraction logic in simplify_audit_feedback() — confirmed the Part A/Part B regex branches are present and functioning (the docstring documents that this superseded an earlier bug where Check 1's regex looked for a literal "Explanation:" label that Check 1 never produces).

Fix: None required. The system behaved correctly at every layer — Auditor, extraction, and API response.

Lesson: Check 1 Part B holds the line against relabeling an elective internal decision as an external trigger, regardless of surface rewording. This is a positive validation of the Auditor's externality check, complementary to the Phase 24 omission-blindness finding rather than contradicting it. It also confirms that a FLAGGED_FOR_REVIEW result is not always an Analyst writing defect — unlike Southwest, Boeing, and Peloton (each with a genuine external precipitating event), some constructed cases simply lack an external trigger, and the audit correctly reflects that rather than the phrasing.

---

## Phase 37 — Cross-Domain Demo: Harbor & Vine (Casual Dining POS Rollout)

Problem: To test generalization beyond the three validated case studies (Southwest, Boeing, Peloton) and beyond the Phase 36 Ohio Warehouse synthetic case, constructed a second synthetic, out-of-domain case — Harbor & Vine, a fictional 140-location casual-dining chain hit by a botched chain-wide POS/KDS rollout, PE-driven ahead of a Q1 2026 refinancing. The case included a genuine four-category complaint-frequency breakdown (1,750 / 640 / 540 / 270, i.e. 54.7% / 20.0% / 16.9% / 8.4%) rather than round numbers, an explicit external factor (a regional minimum wage increase) stated alongside the internal decision, and an explicit statement that the technical cause of the sync failures was still unknown ("IT and the vendor are still investigating"). Run once through the full /diagnose pipeline via the demo UI — a single demo run, not yet a controlled n-trial experiment — and reviewed the downloaded PDF output.

Diagnosis:
- Result was FLAGGED_FOR_REVIEW after one revision. Check 1 Part B correctly rejected the Analyst's framing of "vendor software performance" as an external trigger, reasoning that the company chose the vendor, the rollout strategy, and skipped validation — the failure traces back to internal decisions regardless of which specific step gets named as "the trigger." The genuinely external candidates present in the input (minimum wage increase, competitor gains, aggregator commission change) were correctly kept out of the trigger slot and used only as PESTLE/SWOT threats. This corroborates Phase 36's Ohio Warehouse finding in a second, differently-shaped synthetic case: Check 1 Part B generalizes across domains rather than being tuned to one scenario's phrasing.
- New finding, distinct from both Phase 22 (numeric ranking fabrication) and Phase 24 (omission-blindness): the 5 Whys / Fishbone output stated as fact that "the software architecture could not maintain persistent, low-latency connectivity between the FOH terminals and the KDS during high-volume service hours" — a specific technical mechanism never present in the input, which explicitly said this was unknown and under investigation. Check 2 (Fabricated Ranking Scan) is scoped to numeric/ranking claims and has no mechanism to catch narrative-specificity fabrication elsewhere in the reasoning chain, and did not flag it.
- Despite genuine, non-round complaint-category data being present (a real basis for a legitimate Pareto breakdown, unlike the round-number pattern from Phase 22), no Pareto analysis was attempted anywhere in the output. Output covered Fishbone, 5 Whys, PESTLE, SWOT, and a Financial Metric section only. This differs from Phase 36, where the Analyst explicitly declined a Pareto and stated why (missing categorical data) — here there was no explicit decline and no attempt, so it's unclear from this single run whether the framework-selection step considered Pareto at all.

Fix: None yet. A single demo run doesn't meet this project's own evidentiary bar for confirming or ruling out a defect (Phase 22 used n=9, Phase 35 used 15 trials across 3 fixtures, Phase 36 used three independently-worded attempts). Logged as a candidate for a follow-up controlled test: build fixture(s) that pair a real, explicit "cause is unknown / still under investigation" statement with a downstream reasoning step (5 Whys, Fishbone) to check whether the pipeline consistently preserves that uncertainty — the way Phase 35 confirmed the Intake agent preserves hedged causal claims — or consistently invents a specific mechanism to fill the gap, at a comparable n to Phase 24's isolation test. The Pareto non-attempt is a secondary, lower-priority open question for the same follow-up: whether the Researcher/Analyst framework-selection step is systematically under-selecting Pareto when applicable, or whether this was incidental to this one case.

Lesson: extends the Phase 24 omission-blindness finding rather than duplicating it — that finding was about the Auditor not flagging missing reasoning; this run suggests a related but distinct risk, where reasoning is present but its specificity is invented rather than supported, in a part of the pipeline (5 Whys / Fishbone narrative content) the existing audit checks were never scoped to examine. Separately, this run is a second, independent data point for Phase 36's finding that Check 1 Part B holds up against relabeled internal triggers across differently-flavored synthetic cases, not just the original Ohio Warehouse case — worth having on record as cross-domain evidence rather than resting on one synthetic case alone.

---

## Phase 38 — First End-to-End Orchestrator Validation (All 3 Cases)

Problem: orchestrator.py had been built (end of the session that produced orchestrator.py and run_orchestrator_all_cases.py) but never actually run end-to-end -- no empirical evidence existed for it at all going into this phase. Delegated execution and verification to the local coding agent per the usual workflow: confirmed the venv312/crewai environment first, read orchestrator.py and run_orchestrator_all_cases.py to establish the actual return contract (rather than trusting an assumed one), then ran the full batch across Southwest, Boeing, and Peloton.

Diagnosis:
- Structural: exit code 0, zero exceptions or tracebacks, zero rate-limit (429) errors across all three sequential cases (~5m33s total wall-clock, 15 RPM ceiling respected via the existing 30s inter-case + 5s inter-fidelity-check pacing). Output files correctly timestamped and non-overwriting -- a 4th timestamped run now sits alongside 3 prior runs per case from 7/25 and 7/28. Checked each output file for the "(not available)" placeholder that fills in for a missing/None key -- zero hits; all keys expected for the status each case actually returned were present and populated.
- Undocumented until now: run_orchestrator() returns three possible status values, not the two previously assumed -- SYNTHESIZED, FLAGGED_FIDELITY_FAILURE, and FLAGGED_FOR_REVIEW (fires when the underlying diagnosis never passes audit at all; short-circuits before any Orchestrator-level LLM call, including the fidelity check). api.py's diagnose() endpoint already branches correctly on all three, so this was a documentation gap, not a code defect -- but it means this smoke test only exercised 2 of the 3 branches, since all three cases happened to pass audit (Southwest on attempt 1; Boeing and Peloton after one revision each).
- Content, not just structure, checked against each case's Ground-Truth Diagnosis Summary (present in the case packet, withheld from the agents):
  - Southwest (SYNTHESIZED): diagnosis and all three financial figures matched the ground truth closely; Fidelity Check B and Check C both passed clean.
  - Boeing (FLAGGED_FIDELITY_FAILURE): Attempt 1 correctly failed Check 1 Part B for labeling the AOA sensor -- an internal design choice -- as the external trigger, consistent with the Phase 36 externality finding in a third domain. Attempt 2 passed audit, but the synthesized report then failed Fidelity Check C, dropping the qualifying context off two financial figures (the 2018-vs-2019 composition of the $11.096B swing; the "cumulative cost of crisis" framing on the $18B+ comparison) -- a genuine, subtle catch, and the first time Check C's isolated-agent architecture (Phase 34) has been tested against a live end-to-end run rather than curated calibration fixtures.
  - Peloton (FLAGGED_FIDELITY_FAILURE): same pattern -- Attempt 1 failed Check 1 Part B for bundling the internal "January 2022 production pause" into the external trigger; Attempt 2 passed audit but failed Check C, dropping "(Ohio factory and Precor)" off the $800M capital figure, reducing it to a generic sum. Separately noted, not yet resolved: the case's Ground-Truth Diagnosis Summary calls for the Tread+ recall to be named as a compounding factor, and it appears nowhere in either the diagnosis or the report. Unclear from the output alone whether this is an omission or whether the fact simply wasn't present in what the agents were given -- needs checking against the actual case packet's Background/Supporting Data before drawing a conclusion either way.

Fix: None required -- no defect found. The Orchestrator, the API's status handling, and the Fidelity Check's isolated-agent architecture all behaved correctly under a live, non-curated run.

Lesson: this is the first validation evidence the Orchestrator has ever had, and it produced two substantive positive findings rather than just "it ran without crashing" -- cross-domain corroboration of Check 1 Part B (three domains now: Ohio Warehouse, Boeing, Peloton, each independently catching an internal decision relabeled as external) and the first live-run confirmation that Check C's Phase 34 architecture generalizes beyond the two fixtures it was calibrated against. Two items remain open rather than closed: FLAGGED_FOR_REVIEW has no empirical evidence behind it yet, since all three cases happened to pass audit; and the Peloton Tread+ gap needs one more check against the source case file before it's either dismissed or logged as a defect.


---

## Phase 39 — Controlled Confirmation: Technical-Specificity Fabrication Under a Stated Data Gap (n=9 x 3 Fixtures)

Problem: Phase 37 found a single instance where the 5 Whys stated a specific technical mechanism as fact despite the input explicitly saying the cause was unknown and under investigation -- a single run, not meeting this project's evidentiary bar. Built three fixtures (harbor_vine repeated, plus two new cross-domain fixtures -- appliance/manufacturing, coldchain/grocery-logistics), each with a documented, explicit "cause is unknown, still under investigation" claim, and ran all three through intake.py -> crewai_pipeline.run_pipeline() at n=9 per fixture (27 total trials), matching Phase 24's isolation-test scale. Execution delegated to the local coding agent (test_analyst_fabrication_under_gap.py); one run hung ~85 minutes into fixture 1 (diagnosed as a likely CrewAI telemetry-export stall -- near-zero CPU, stale CLOSE_WAIT sockets, a live connection to a non-standard port -- not a Gemini API issue), was killed, and a clean restart completed all 27 trials in 29.9 minutes with zero errors, zero rate-limit hits, zero malformed outputs. All 27 raw diagnoses were then manually read against their fixture's documented unknown-cause claim.

Diagnosis:
- **harbor_vine: 8/9 trials fabricated.** Nearly every trial's 5 Whys stated a specific technical mechanism as settled fact in its technical/"Machine" step -- data-packet loss, handshake errors, architecture unable to handle simultaneous volume/latency -- despite the input stating IT and the vendor were still investigating. Only trial 2 stayed at the process level ("never fully validated under live conditions") without inventing a specific failure mode.
- **coldchain: 8/9 trials fabricated, and this fixture's outputs were the most elaborate.** Every trial but one invented a specific, technically detailed mechanism -- a centralized energy-management system, a firmware update that "narrowed voltage tolerance thresholds," a misconfigured demand-response protocol -- stated as the confirmed Root Cause with no hedge, despite the input explicitly quoting the vendor's own engineer saying the failure pattern "doesn't match any known fault mode." Trial 9 was the only one of all 27 to add a genuine hedge: an explicit "Diagnostic Disclaimer" noting the conclusion was a theory requiring verification against control logs before use.
- **appliance: the narrow literal test passed, but the same pattern reappeared one level up.** None of the 9 trials confirmed the "thermal cutoff" as the settled cause -- component-level claims stayed consistently hedged ("suspected," "potential," "possible"), a genuinely good result. But most trials instead invented a specific *process*-level narrative not present in the input (an unvalidated supplier/component-sourcing change, a bypassed QC sign-off) stated fairly confidently as the Root Cause. Structurally the same gap-filling behavior, just relocated from the component layer to the process layer.
- **Refined meta-finding (revised after closer review -- see note below):** Check 1 (Trigger vs. Root Cause Distinction) checks *categorization* -- is the trigger correctly labeled as external, is it kept distinct from the root cause -- not *factual support* for the root cause's content. Nothing in Check 1's own logic reads the root cause for whether its specifics are grounded in the input. coldchain makes this most visible: its heat wave is a clean, correctly-timed external trigger, so Check 1 passes trivially (9/9 on first attempt) regardless of what specific internal mechanism fills the root-cause slot -- the fabricated content was never in scope for what Check 1 evaluates. harbor_vine shows the same content-blindness from the other side: across all 7 of its FAILED audits, the failure reason was exclusively Part B (an external-sounding factor, like the minimum-wage hike, mislabeled as the trigger for a crisis that actually started two months earlier) -- not once did a FAIL verdict cite the invented packet-loss/latency mechanism sitting in the same diagnosis, even on a second read during revision. The two fixtures differ sharply in audit-pass rate (harbor_vine 2/9, coldchain 9/9) for reasons entirely orthogonal to fabrication rate, which was similar in both (8/9). The generalizable claim is narrower and more precise than "fabrication causes audit passes": Check 1 is blind to root-cause content regardless of outcome: when categorization is easy (coldchain), that blindness lets fabricated content straight through; when categorization is hard (harbor_vine), that same blindness means the fabrication is never flagged even in diagnoses the audit rejects for an unrelated reason.

Fix: None implemented -- this phase's scope was confirming and characterizing the finding, not remediating it. Two candidate directions, not yet evaluated against each other:
  1. A new, narrowly-scoped audit check (tentatively "Check 3: Unresolved-Cause Fabrication Scan") that flags declarative causal claims in the 5 Whys/Fishbone technical branches when the input contains an explicit unknown/under-investigation statement -- the same role Check 2 plays for numeric rankings, retargeted at narrative specificity.
  2. A prompt-level instruction to the Analyst to explicitly preserve stated uncertainty rather than resolve it. Lower engineering cost than a new check, but nothing independently re-verifies compliance the way Check 2 independently re-checks the Analyst's Pareto behavior.
  Either direction needs to be checked against an unintended interaction the meta-finding surfaces: if a future Analyst version genuinely preserves "cause unknown" instead of inventing a mechanism, does the resulting diagnosis now fail Check 1 *more* often, since it no longer has a concrete internal mechanism to cleanly contrast against the trigger? That trade-off needs testing, not assuming away.

Lesson: this is now a confirmed, cross-domain, systematic finding -- 16 of 27 trials (harbor_vine 8 + coldchain 8) show the fabrication pattern in its cleanest, least-hedged form, and appliance's 9 trials show a related, relocated version of the same behavior -- clearing this project's own evidentiary bar (comparable to Phase 22's n=9 and Phase 35's 15-trials-across-3-fixtures) rather than resting on Phase 37's single run. More importantly, the refined meta-finding reframes the finding's significance: this isn't just "the audit has a blind spot for narrative fabrication" (Phase 24's framing, for omissions) -- it's that Check 1 was never designed to evaluate root-cause content at all, only its categorization, so content fabrication and Check 1's pass/fail outcome are independent variables that happen to interact differently per fixture depending on how easy that fixture's categorization problem is. This distinction -- categorization-blindness versus a true fabrication-reward mechanism -- is precise enough to belong in the report's discussion of audit limitations, not just the dev log.


---

## Phase 40 — Peloton Tread+ Question Resolved: A Genuine, Real-World Completeness Gap

Problem: Phase 38 flagged an open question, logged into the report's Section 10.3: whether the Peloton case's Tread+ recall -- named in the case's ground-truth summary as a compounding factor -- was present in the diagnostic input the agents actually received, or only in withheld reference material, given it never appeared in either Orchestrator run's diagnosis or report. Checked directly via the local coding agent against the raw case file and case_loader.py's actual section-splitting logic, not assumed from header names.

Diagnosis: Confirmed present in the agents' input. The case's `## Background` section -- one of the three sections (`Problem Statement`, `Background`, `Supporting Data`) case_loader.py's `INPUT_SECTIONS` constant routes into `diagnostic_input` -- states: "Compounding the crisis, its lower-priced Tread+ treadmill was recalled after safety incidents involving children." This is separate from, and precedes, the withheld `## Documented Root Cause` section, which also mentions Tread+ (explicitly framed there as "a compounding factor, not root cause"), and the `## Ground-Truth Diagnosis Summary`, which explicitly expects a complete answer to name Tread+ as a compounding factor distinct from the root cause. The agents had the fact available on every run and never used it -- a genuine omission, not a data-availability question.

Fix: None implemented. Reported as one real, unconstructed data point rather than elevated to its own controlled test -- a single real case observed across two runs doesn't meet this project's evidentiary bar for a standalone finding, but it is real corroborating evidence for the completeness gap already established under controlled conditions in Sections 8.8-8.10: a genuine input fact, available to the Analyst and expected by the case's own ground truth, absent from an otherwise well-supported diagnosis, with no existing check scoped to catch that kind of absence. Report updated: the open question in Section 10.3 is resolved and moved into Section 10.2 as a confirmed limitation, explicitly labeled as one corroborating case rather than an independently established pattern.

Lesson: where Section 8.9 isolated the completeness gap using constructed, single-variable fixtures specifically to establish it under controlled conditions, this is the same gap surfacing unprompted in real, unconstructed pipeline output on one of the project's three original validated cases -- suggesting the gap is not an artifact of the constructed test design, though a single real instance, observed without repetition, is reported as corroborating rather than independently establishing that on its own.


---

## Phase 41 — Retroactive Verdict-Parsing Integrity Audit: A Genuine Bug, Confirmed Clean History

Problem: harbor_vine trial 3 (Check 3 true-positive test) showed the model writing a full PASS verdict block, then visibly self-correcting to FAIL within the same response -- directly violating AUDIT_DESCRIPTION's "stated once, decisively, no visible self-correction" requirement. parse_verdict()'s re.search() takes the first match, so it would silently record PASS despite the model's own final, corrected conclusion. This is not scoped to Check 3 or to this session -- it is a parsing defect present in every historical audit verdict ever parsed by this pipeline. Before fixing it, a retroactive audit checked whether any historical saved output shows the same pattern.

Diagnosis: 103 files scanned -- every file in the repo excluding venv312/, .git/, __pycache__/, chroma_db_v2/, node_modules/. 85 matched an initial grep for "Audit Verdict"/"Fidelity Verdict"; the other 18 (repeated_forced_ranking/, comparison_outputs/, peloton_real/, southwest_diagnosis_run1.txt) were explicitly grepped and confirmed to contain zero matches, not assumed absent. A supplementary case-insensitive sweep surfaced 3 more candidate filenames, each individually opened and confirmed to be incidental source-code text (a print label, a docstring, an f-string), not saved output. 7 files were flagged by raw multi-occurrence count; 6 are false positives by count alone -- legitimate two-attempt revision loops, a separate run_auditor() call per attempt, each independently producing exactly one clean verdict, confirmed by reading each attempt's block individually rather than trusting the header's total_attempts field. The 7th (ALL_27_TRIALS_CONSOLIDATED.md) is a hand-built concatenation of 27 single-verdict files from earlier this session, not a bug. The single genuine instance is harbor_vine trial 3 itself, from this session's Check 3 true-positive test -- already reported. No historical result, across any prior phase of this project, shows the double-verdict pattern.

Separately, fidelity_check.py's own verdict parsing was checked for the same vulnerability class. run_check_a/b/c each determine `passed` via `verdict_text.strip().startswith("## Check X Verdict: PASS")` (lines 154, 251, 340) -- not re.search(), but structurally identical in effect: a response that states PASS, then visibly self-corrects to FAIL, would still read as PASS, since .startswith() only inspects the beginning of the string. CHECK_A/B/C_DESCRIPTION each carry the same "no visible self-correction" instruction the Auditor's own prompt has -- the same instruction just demonstrated as unreliable. The 4 saved fidelity-check outputs on disk were checked directly and are clean (no doubled verdict sub-headers), so this exposure is real but unexercised, not yet responsible for any known bad result.

Fix: Not yet implemented -- this phase's scope was the retroactive audit, confirming what needs fixing before deciding how. Two candidate designs identified for parse_verdict() and the three fidelity_check.py lines: (1) detect >1 verdict occurrence, take the model's final (last) stated verdict as authoritative -- since harbor_vine trial 3 shows the model's self-correction reaches the right answer -- while also surfacing that a correction occurred, rather than silently absorbing it; or (2) treat any detected multi-verdict response as its own distinct, explicitly flagged condition (mirroring the Orchestrator's three-way status design, Section 6.6) rather than resolving it automatically at all. Decision and implementation deferred to the next phase.

Lesson: this is the same class of finding Section 7's data-integrity correction represents -- a retroactive check prompted by a specific, concrete anomaly rather than a scheduled review, applied comprehensively rather than only to the files it was expected to touch. The result differs from Section 7's in kind: Section 7 found the anomaly had affected prior results; this audit specifically confirms it had not, across every saved output the project has ever produced. A clean retroactive audit, checked this thoroughly, is reported with the same precision as a positive finding -- the absence of a defect is itself evidence worth recording, not a non-event.


---

## Phase 42 — Verdict-Parsing Fix: Implemented and Validated

Problem: Phase 41's retroactive audit confirmed the verdict-parsing bug (parse_verdict()'s first-match re.search(), and the structurally identical vulnerability in fidelity_check.py's three .startswith() checks) had never affected any historical result, but the vulnerability itself remained unfixed going into this phase. Two candidate designs were weighed -- take-final-verdict-and-flag, versus a distinct status mirroring the Orchestrator's three-way split. Take-final-verdict-and-flag was chosen: a self-correction is a parsing-robustness problem, not a new user-facing outcome category the way SYNTHESIZED/FLAGGED_FIDELITY_FAILURE/FLAGGED_FOR_REVIEW are -- importing that design pattern here would have matched a good pattern to the wrong problem rather than fixing where the defect actually lives.

Fix: parse_verdict() in crewai_pipeline.py changed from VERDICT_PATTERN.search() (first match) to .findall() (all matches), taking the LAST occurrence as authoritative when more than one is found, with a warnings.warn() naming the full PASS/FAIL sequence -- visible to anyone running the pipeline, invisible to any caller reading only the return value. Return type deliberately left as a bare bool: all 8 existing call sites across 7 files treat the return value as a plain bool (including `not parse_verdict(audit)` patterns, which a dict wrapper would silently break without raising). The identical find-all/take-last/warn pattern was applied to fidelity_check.py's three run_check_a/b/c functions via a new shared _extract_check_verdict() helper, replacing each `verdict_text.strip().startswith("## Check X Verdict: PASS")` check.

Validated via a new test_verdict_parsing_robustness.py (pure parsing-logic tests against real saved text and hand-built fixtures, no LLM calls): (a) a regression proof that the new parse_verdict() produces byte-identical output to a frozen copy of the exact pre-fix implementation on a real single-verdict fixture; (b) confirmation that harbor_vine trial 3's real raw text (2 verdict occurrences) now correctly parses to FAIL -- the model's own final, corrected conclusion -- where the old code would have silently returned PASS, with exactly one correctly-worded warning emitted; (c) six hand-built multi-verdict fixtures (a normal case and a self-corrected case for each of Check A/B/C) confirming _extract_check_verdict() takes the last verdict and warns exactly once in every self-corrected case, behaving identically to the old logic in every normal case. All 15/15 checks passed. All 20 other files across the repo that import from either module were compile-checked and remain unaffected.

Lesson: the fix targets exactly where the defect lives rather than reaching for the Orchestrator's existing status-split design because it was available -- a good pattern applied to the wrong problem is still over-engineering. The regression proof (old vs. new, byte-identical, on real data) was treated as a required part of the fix, not an assumption, consistent with this project's standing practice of validating that a fix doesn't silently change behavior for the case that wasn't broken.

Note: this phase closes the verdict-parsing defect specifically. It does NOT address the two Check-3-specific wording issues surfaced by the true-positive test (the Fishbone-section scope gap; the false-negative "characterization" rationalization in harbor_vine trial 1) -- those remain open, tracked separately.


---

## Phase 43 — Check 3 Round 2: Fishbone Scope Fixed, Vocabulary Discriminator Fixed the Known Case but Opened a New One

Problem: Check 3 round 1 identified two open issues: a Fishbone-section scope gap (Check 3 never referenced Fishbone content despite instructions naming it) and a false-negative rationalization pattern (harbor_vine trial 1: "data-packet loss and handshake errors" excused as a "characterization" of stated symptoms rather than flagged as fabrication). Two fixes applied to AUDIT_DESCRIPTION's Check 3 section: FIX A required explicit, named, section-by-section coverage plus a required "Sections examined" output field; FIX B added a "specific vocabulary, not general topic" discriminator, with the exact false-negative case written in as a worked example. Validated via a light, targeted 7-call test: (a) the exact known false-negative diagnosis, 3 runs; (b) a constructed Fishbone-only-violation fixture isolating the scope question, 3 runs; (c) a real, previously-clean fixture, 1 run, checking for new false positives.

Diagnosis: FIX A confirmed working cleanly -- 3/3 regression runs and 3/3 isolation runs, with correct section-level discrimination: in case (b), the same response correctly PASSed two properly-hedged sections while FAILing only the constructed Fishbone violation, meaning the fix produces genuine per-section judgment rather than a blanket effect. This directly closes the scope gap the true-positive test found, where Check 3 never once referenced Fishbone content across 9 real trials.

FIX B closed the specific known false negative -- all 3 regression runs now correctly FAIL on "integration latency and data-packet loss," with near-identical, well-reasoned catches. But case (c), a real fixture that PASSed cleanly under the old wording, now FAILs: Check 3 flagged "hardware/software integration failure" (a near-restatement of the input's own "systemic integration failures") and "data transmission gaps" (a reasonable paraphrase of the input's "orders failed to sync") as fabricated technical vocabulary. Read against the actual input text, both are genuinely borderline -- closer to paraphrase of stated language than to the unambiguous fabrications (packet loss, handshake errors, a named load balancer) FIX B was written to catch -- and this looks like a real over-correction: FIX B's "specific vocabulary, not general topic" framing appears to have made the model suspicious of any technical-sounding phrasing, including direct reuse or close paraphrase of the input's own words.

Fix: FIX A is complete and validated. FIX B is partially successful: the targeted false negative is closed, but a new false-positive risk on paraphrase-of-input-language cases is now open, at n=1 -- directional, not confirmed at the scale this project otherwise requires before treating a pattern as established. A round 3 (tightening the discriminator to exempt close paraphrase/restatement of the input's own general claim, reserving FAIL for genuinely new, previously-absent specific claims) is scoped as a candidate next step, not yet undertaken.

Lesson: this is the same "fixing one piece of wording measurably shifts an adjacent judgment" pattern fidelity_check.py's own docstring already documents happening twice during Check A/B/C's calibration (Section 6.7) -- here it happened within a single check's own two simultaneous fixes rather than across three isolated checks, suggesting the risk isn't specific to the fidelity check's shared-prompt architecture but a more general property of patching one prompt with multiple corrections at once. Check 3, after one refinement round, is reported honestly as two-thirds settled: one fix fully validated, the other's own fix still needed.


---

## Phase 44 — Check 3 Round 3: WHAT-vs-WHY/HOW Discriminator Closes the False Positive With No Regression

Problem: Round 2's FIX B ("specific vocabulary, not general topic") closed the known false negative but introduced a new false positive on paraphrase-of-input-language cases (Phase 43). This round replaces that discriminator with a sharper WHAT-vs-WHY/HOW framing: restating or relabeling an already-described symptom, however technical-sounding, is not a violation; asserting a specific, previously-absent causal mechanism, component, or parameter is. Re-ran test_check3_round2.py completely unchanged against the new wording -- same three cases, same fixtures -- specifically to test whether this traded one failure mode for the other rather than genuinely resolving it.

Diagnosis: All 7/7 results matched the intended outcome, with no regression on either previously-fixed issue. (a) The known fabrication ("integration latency and data-packet loss") still correctly FAILed, 3/3, with reasoning now explicitly using the WHAT/WHY-HOW framing in its own words ("a new, unproven technical explanation... rather than just restating the symptom"). (b) The constructed Fishbone-only violation still correctly FAILed, 3/3, still correctly scoped to just the violating bullet while passing the two properly-hedged sections in the same response. (c) The previously-flagged false positive ("data transmission gaps," "hardware/software integration failure") now correctly PASSed, reasoning explicitly that these "do not introduce a specific new mechanism" and remain "high-level description of the symptom" -- the intended distinction working in the model's own words, not just producing the desired output. One minor completeness note, not a regression: in (c), "Sections examined" lists Fishbone, but "Instances found" doesn't explicitly itemize-and-pass the Fishbone content the way it does the 5 Whys lines -- implicit rather than explicit clearance. Doesn't affect correctness of the outcome.

Fix: Complete for the two issues round 1 identified. Not yet run at the same scale as Check 1/Check 2's own validation (n=9 per fixture) -- this and the prior two rounds have all been light, targeted n=3 runs against known/constructed cases, sufficient to diagnose and fix specific failure modes but not yet sufficient to claim Check 3 is validated at the standard the rest of the audit architecture is held to.

Lesson: three rounds to reach a stable-seeming state puts Check 3 roughly at parity with Check 2's four rounds and the fidelity check's five -- consistent with, not an exception to, this project's established pattern that a check's wording reliably needs more than one correction before it holds. The round 2 -> round 3 sequence specifically demonstrates that a fix which resolves a false negative can construct a false positive as a direct side effect of the same wording change, and that the correct response to a fix producing a new problem is characterizing the new problem precisely (WHAT vs WHY/HOW, not just "less aggressive") rather than either reverting or vaguely softening the original fix.


---

## Phase 45 — Check 3 Confirmatory Replication at n=9: 25/27 Correct, and the Untested Check-1 Question Resolved

Note on process, not on the finding itself: a prior message in this session presented a plausible-looking but fabricated summary claiming this exact confirmatory test had already run, complete with an invented tool-call block written in a voice designed to resemble a genuine report. It did not survive a request for the actual raw transcript and was retracted once real execution was requested and provided. Recorded here because this project's own central thesis is that plausible-sounding unverified claims need to be caught before being trusted -- catching one aimed at the development process itself is worth being as explicit about as any other finding in this log, not quietly stepped past.

Problem: Round 3 (Phase 44) validated the WHAT-vs-WHY/HOW discriminator at light n=3 scale, against harbor_vine only. Two things remained genuinely untested: whether the fix holds at the same n=9, cross-domain scale Check 1 and Check 2 are validated at, and the effect (if any) of the Analyst's UNRESOLVED-CAUSE PRESERVATION instruction on Check 1's pass rate -- explicitly flagged as untested in the report's Section 8.10/10.3. Re-ran Phase 39's original methodology unchanged -- same 3 fixtures, n=9 each, full pipeline rather than isolated Auditor calls -- directly comparable to both the Phase 39 pre-fix baseline and the n=3 light round.

Diagnosis: 27/27 completed cleanly, 0 errors, 0 rate-limit hits, no stall this time (27.1 min). Hedge preservation reached 27/27 (100%) across all three fixtures -- up from Phase 39's 1/9 (harbor_vine), 9/9-component-level-only (appliance, with the process-level pattern absent this round), 1/9 (coldchain). Since nothing fabricated in any of the 27 trials, this run had no opportunity to produce a true positive for Check 3 (true-positive evidence already exists separately, from the dedicated true-positive test against fixed known-bad diagnoses). Check 3's accuracy on this run: 25/27 correct PASS (true negatives), 2/27 false positives, 0/27 false negatives. Both false positives are in harbor_vine (trials 2 and 3) and share one precise, narrow failure mode: conflating "explaining WHY a rollout/governance decision was made" (explicitly permitted by the check's own worked example) with "explaining the technical failure mechanism" (restricted), when the diagnosis links the two in the same sentence or adjacent reasoning. Trial 2 is unambiguous -- the flagged claim ("absence of a pilot phase") is close to a direct restatement of the check's own built-in example ("a rushed, unpiloted rollout... is itself a contributing factor is fine") and Check 3 flagged it anyway. Trial 3 is softer and genuinely more ambiguous ("de-linked from operational readiness" as an explanation for "the systemic collapse"), read as a false positive but a closer call than trial 2. Fishbone scoping remained correct in all 27 trials -- no regression at scale.

Check 1 pass rate, with real n=9 evidence for the first time: harbor_vine 6/9 (up from the Phase 39 baseline's 2/9), appliance 9/9 (up from 3/9), coldchain 9/9 (unchanged, already at ceiling). This directly answers the question Section 8.10/10.3 flagged as untested -- whether reduced fabrication would make Check 1 fail more often, for lack of a concrete internal candidate to contrast against the trigger. At this scale, the opposite happened: audit pass rates rose substantially wherever there was room to rise. The likely mechanism is a spillover effect from the same Analyst instruction rather than any change to Check 1 itself (Check 3 can only add failure paths, not remove them, and Check 1's own wording was not touched this round) -- stated as the most likely explanation, not an isolated, independently-tested one, since no dedicated test separated this effect from other possible confounds.

Fix: Check 3 is not further modified this round. The two false positives are precisely characterized (conflating governance-decision explanation with technical-mechanism explanation) but not yet fixed -- a candidate fourth round, not undertaken here.

Lesson: at 25/27 (92.6%) correct and one narrow, well-understood residual failure mode, Check 3 has reached a level of characterization comparable to where Check 1 and Check 2 stood before their own validated write-ups -- real strength demonstrated at scale, one remaining limitation named precisely rather than smoothed over, not claimed as perfect. The Check-1-pass-rate finding is the more consequential result of this phase: it resolves a specific, previously-flagged open question in the report's own text, in the opposite direction from what was worried about -- which is exactly the kind of result this document treats with the same precision regardless of which direction it points.


---

## Phase 46 — Check 3 Round 4: SCOPE LIMIT Fix, Anti-Loophole Test, and a Targeted Wording Stress Test

Problem: The confirmatory replication (Phase 45) found 2 false positives, both in harbor_vine, both conflating a legitimate process-/governance-level root-cause claim with the technical-mechanism question Check 3 is scoped to protect. A SCOPE LIMIT paragraph was added to AUDIT_DESCRIPTION's Check 3 section, explicitly exempting process/governance claims from the technical-mechanism scan unless they smuggle in new technical vocabulary. Validated via 5 cases / 12 calls: the two real false positives (must now PASS), the original known-fabrication and Fishbone-isolation fixtures (must still FAIL, confirming no regression), and a new anti-loophole stress test deliberately smuggling a fabricated technical detail inside process-labeled framing (must FAIL on the technical content specifically, not the whole claim).

Diagnosis: All 12/12 results matched the intended outcome. Both real false positives (harbor_vine confirmatory trials 2 and 3) now correctly PASS, 3/3 and 3/3, with reasoning explicitly distinguishing "organizational, process, and management failures" from "inventing technical reasons." Both sanity-check fixtures still correctly FAIL, 2/2 each -- no regression to the original false negative or the Fishbone-scope fix. The anti-loophole stress test correctly FAILed 2/2, with the violation isolated to the exact smuggled clause ("unhandled race condition during concurrent writes to the KDS queue"), stopping short of the legitimate "rushed, unpiloted rollout timeline" language in the same sentence -- confirming the exemption discriminates within a single sentence rather than exempting a whole claim wholesale.

Before treating this as settled, the SCOPE LIMIT paragraph's general-rule sentence was reread independently of its test results: its worked examples condition the exemption on a process fact being "already stated in the input," but the general rule ("Only fail a claim... if the claim ITSELF introduces a new, specific, previously-absent TECHNICAL detail") does not repeat that qualifier explicitly, creating a plausible reading under which any process-level claim -- invented or not -- could be exempt purely for lacking technical vocabulary. None of round 4's five tests exercised this distinction, since all five used harbor_vine and the anti-loophole test specifically smuggled technical content rather than a purely invented, non-technical process fact. A targeted stress test was built: appliance's real case input (the fixture where Phase 39 originally observed the process-level fabrication pattern), paired with a hand-built diagnosis correctly hedging the technical mechanism throughout but stating one invented, non-technical process fact (an unconfirmed Q1 2026 supplier change) as settled fact in the Fishbone Process bullet -- a claim absent from the input, not inferable from it, containing no technical vocabulary at all.

Result: 3/3 correctly FAILed. All three responses reasoned from the exemption's actual condition (whether the fact is already stated in the input) rather than over-generalizing "process-level claim -> exempt" -- two of the three explicitly contrasted the invented supplier-change claim against the diagnosis's legitimately-hedged thermal-cutoff mention, correctly treating the latter as grounded in a stated suspicion and the former as not. The concern was well-founded to test -- the literal wording did admit the looser reading -- but the model's actual behavior tracked the paragraph's intended scope rather than its most permissive possible parse.

Fix: No further change made. The concern was investigated and did not require one.

Lesson: this closes Check 3's development arc at four rounds plus one confirmatory stress test -- comparable now to Check 1 and Check 2's own validation depth, reached the same way theirs was: iterative, each round targeting a precisely characterized failure rather than a vague "make it stricter" or "looser" adjustment. The final stress test is itself worth noting as a practice, not just its result: rereading a fix's literal wording for a gap its own test suite didn't happen to exercise, independent of how clean those tests looked, is what caught the original Fishbone scope gap in the first place (nine real trials before anyone thought to check specifically) -- applying the same discipline here, even against a fix that had already tested clean, is what this project's own standards call for, and this time it returned a genuine, verified negative rather than another gap.


---

## Phase 47 — Wiring Check 3 into the Demo UI: Five Real Extraction Bugs Found Against 65 Saved Files, Zero New API Calls

Problem: Check 3 is live in production (crewai_pipeline.py's AUDIT_DESCRIPTION) but api.py's simplify_audit_feedback() -- the function translating raw audit text into the demo's user-facing "why this wasn't verified" reasons -- only recognized Check 1 and Check 2's output formats. A Check 3 FAIL in a real demo would fall through to the generic fallback message rather than surface its specific finding.

Diagnosis/Fix: A new Check 3 block was added to simplify_audit_feedback(), validated entirely against 65 real saved verdict files already on disk from this session's Check 3 test rounds (the true-positive test, rounds 2 and 4, the process-fact stress test, and the n=9 confirmatory replication) -- zero new API calls, since this is pure text-parsing logic, not a model-behavior question. Check 3's real output format varies more than Check 1/2's across these files (numbered, bulleted, bold-labeled; FAIL appearing before or after the quoted claim), so extraction is chunk-based -- split at each numbered/bulleted instance boundary -- rather than matched against one fixed line shape.

Five real bugs were found and fixed, each confirmed against actual captured output rather than guessed at: a quote-length cap simultaneously too tight for long real quotes and, once widened, too loose to admit short ones, both directions producing the same misalignment failure -- fixed by separating unbounded quote-pairing from length-filtering into two steps; an unbounded trailing capture that let a model-added bonus paragraph after Check 3's real output bleed into the scanned text -- fixed by bounding each chunk to stop at the next "###" heading; case-insensitive FAIL matching that pulled a PASS instance's own quoted prose into the output because it happened to contain the ordinary English word "fail" -- fixed to case-sensitive matching, since the model's actual verdict marker is always uppercase; and a longest-quote selection heuristic that occasionally picked a FAIL instance's own quotation of the case input's hedge language (used as justification) over the actual, shorter violating claim -- fixed by excluding hedge-shaped quotes before applying the length preference, since a claim that hedges can never be the thing Check 3 exists to flag.

Validated against all 65 real files (0 new API calls): 31 genuine Check 3 FAILs, all 31 now extracting a clean, accurate quote matching the known violation. A regression check compared every file's Check 1/Check 2 output against a frozen copy of the pre-edit function: 64 of 65 byte-identical; the one difference is explained, not a regression -- it is the same self-correction/double-verdict file already documented in Phase 41/42, whose own saved "Check 3 status: PASS" header reflects the pre-fix first-match parsing bug rather than the model's actual corrected verdict (FAIL); the new code correctly surfaces the real fabricated claim from the corrected block, where the old code, with no Check 3 awareness at all, gave only the generic fallback.

Lesson: this validation was possible entirely from data already generated by this session's prior test rounds, without a single new API call -- a direct payoff of this project's standing practice of saving full raw text at every stage of every test, in ways not anticipated when that data was first captured. The five bugs found here are also a specific instance of a general pattern: text-parsing logic written against one or two example outputs tends to fail against the real input distribution's actual variety, and is only as trustworthy as the range of genuine examples it has been checked against -- 65 files, not a handful, is what surfaced bugs a smaller test would likely have missed.


---

## Phase 48 — RAG Ground-Truth Leakage Closed in chunk_cases()

Problem: `case_loader.py` strips the `Documented Root Cause` / `Ground-Truth Diagnosis Summary` sections before any agent sees a case as diagnostic input, via its `INPUT_SECTIONS` filter. `rag_pipeline_starter.py`'s `chunk_case_file()` did not apply that same filter -- it indexed every section of a case file, including the ground-truth sections, creating a leakage path into Researcher retrieval that `case_loader.py`'s existing protection did not cover, since the two functions operated on the same raw files through entirely separate code paths.

Fix: `chunk_case_file()` now imports `INPUT_SECTIONS` directly from `case_loader.py` and skips any section header not in that set, so the RAG corpus and the direct diagnostic input are built from the exact same filter rather than two independently maintained ones.

Diagnosis/Validation: Rebuilt the corpus and confirmed 9/9 case chunks with zero leaked ground-truth headers present in the indexed output.

Lesson: two components deriving from the same source data but enforcing a safety property independently is itself the risk -- `case_loader.py` being correct said nothing about whether `rag_pipeline_starter.py` was. Importing the single source of truth (`INPUT_SECTIONS`) rather than re-encoding the same section list in a second place is what actually closes this class of bug, not just fixing this one instance of it.


---

## Phase 49 — Qoder Tooling: Project Standards, Agent Skills, and MCP Retrieval Server

Problem: Delegating build work to Qoder needed the project's own hard-won standards and each agent's exact spec encoded somewhere Qoder would actually read them, rather than re-explained per session. Separately, Qoder had no way to query the RAG corpus directly during a build task.

Fix:
- Added `.qoder/rules/mass-standards.md`, encoding five standards derived from confirmed bugs and lessons already in this log: ground-truth isolation in RAG indexing (Phase 48), the Auditor's exact check count and which file implements it (`crewai_pipeline.py`, not `fidelity_check.py` -- an easy layer to confuse), evidence-traceable agent claims, frozen case studies, and no unverified assumptions in generated code.
- Added six Qoder skills under `.qoder/skills/`, each encoding one agent's spec verbatim from source rather than paraphrased: `run-intake` (no-invented-content constraint, exact output format matching `INPUT_SECTIONS`, with two open items flagged directly from the source itself), `run-researcher` (the mandatory reformulate-before-search step, since raw-case-wording queries measurably fail to retrieve relevant frameworks), `run-analyst` (unresolved-cause preservation, revision-loop scope), `run-auditor` (the full 3-check spec plus `parse_verdict()`'s self-correction handling), `run-orchestrator` (the hard never-synthesize-unaudited branch, narrow input surface, and why `fidelity_check.py`'s three checks must stay isolated calls), and `add-case-study` (the case file template and post-add leakage verification, so a new case can't silently break `INPUT_SECTIONS`).
- Added `mass_retrieval_mcp.py`, an MCP server wrapping `retrieval_tool.retrieve_knowledge()` directly over stdio for Qoder rather than reimplementing ChromaDB query logic, so it inherits the existing eager-build and `threading.Lock()` protection against the native crash documented in Phase 10. Verified against the real BGE backend with 3 concurrent stdio tool calls, no crash.
- Separately confirmed (not fixed, since there was nothing to fix) that `run_intake()`'s literal output doesn't byte-match `case_loader.py`'s `diagnostic_input` formatting (no title line, no blank line after headers) -- checked and found to have zero functional impact, since `case_text` is never re-parsed programmatically downstream. Deliberately left `INTAKE_DESCRIPTION` untouched rather than forcing byte-consistency for a cosmetic difference with no demonstrated cost, which would have invalidated Phase 35's existing validation for no real gain.

Lesson: writing these as skills rather than one-off instructions is itself a form of the project's own "restrict what a component can see, don't just instruct it to behave" principle (ROADMAP.md, Section 2.1) -- each skill hands Qoder the actual constraint from the actual source file, not a summary of it that could drift out of sync.


---

## Phase 50 — Two-Venv Dependency Split: Native Gemini Provider and ChromaDB Schema Conflict

Problem: `crewai` 1.15.17 routes `gemini/*` models through a native `GeminiCompletion` provider by default, not LiteLLM, which requires the `google-genai` extra to be present -- installing without it, or letting pip backtrack into an older `crewai` release to resolve a conflict, silently pulls in `langchain`/`tiktoken` instead. Separately, once the MCP server (Phase 49) and the pipeline were both running, they were sharing one `chroma_db_v2/` persist directory -- but the MCP server's environment (`.venv`, Python 3.14, ChromaDB 1.5.9) and the pipeline's (`venv312`, Python 3.12, ChromaDB 1.1.1) each have native Rust bindings that cannot read the other version's on-disk schema.

Fix: Pinned `crewai[google-genai]==1.15.17` exactly in `requirements.txt` to stop pip from backtracking. Made the ChromaDB persist directory configurable via a `CHROMA_PERSIST_DIR` environment variable across `chroma_retriever_v2.py`, `retrieval_tool.py`, and `mass_retrieval_mcp.py` -- defaulting to `chroma_db_v2_pipeline` for direct pipeline use, with the MCP server explicitly overriding to `chroma_db_v2_mcp` before its eager import-time build runs. Each environment now maintains a fully separate index. Also added `fastapi`/`uvicorn` to `requirements.txt`, missing despite `api.py` depending on both.

Diagnosis: Confirmed via real installs in both environments that each now resolves cleanly and builds its own index without touching the other's.

Lesson: consistent with Phase 10's original finding (native bindings aren't safe to share across contexts) -- this is the same category of risk one level up, at the process/environment boundary rather than the threading boundary, and it required the same fix in spirit: give each context its own resource rather than trying to make one shared resource safe for both.


---

## Phase 51 — MCP Server Startup Failure: stderr During Eager Model Load

Problem: Qoder's MCP host treats any stderr emitted during a server's startup window as a connection failure. `mass_retrieval_mcp.py`'s eager import-time build (loading the BGE embedding model) triggers an HF Hub unauthenticated-request warning and a tqdm progress bar, both to stderr -- tripping Qoder's failure detection and showing the server as disconnected (red icon) even though the server itself was working correctly once past that window.

Fix: Redirect both stdout and stderr to `os.devnull` specifically during the import window that triggers the model load, restoring them immediately after. Serve-time stderr (MCP SDK logs, per-query tqdm bars during actual tool calls) is left untouched and does not trigger the same failure, since it happens after Qoder has already accepted the connection.

Diagnosis: Confirmed the server now connects cleanly in Qoder with no change to its actual retrieval behavior.

Lesson: the failure mode here wasn't a bug in the server's logic at all -- the server worked -- it was an artifact of what the host process treats as a startup signal. Suppressing noise at exactly the window that matters, rather than suppressing it everywhere, keeps genuine runtime errors visible while removing the false signal.


---

## Phase 52 — Real-Time Progress Tracking for the Diagnosis Pipeline

Problem: The demo UI's loading state was a simulated timer, not a reflection of actual backend pipeline progress -- it couldn't show which stage was genuinely running, or a real Auditor revision attempt number if one occurred.

Fix: Added an optional `progress_cb` parameter to `run_pipeline()` and `run_orchestrator()` (default `None`, zero behavior change for existing callers) that reports real stage transitions: Researcher, Analyst, Auditor (with the actual revision attempt number), Orchestrator, Fidelity. Added two new, additive endpoints to `api.py`: `POST /diagnose/start` (starts the pipeline in a background thread, returns a `job_id` immediately) and `GET /diagnose/status/{job_id}` (polls real progress and the final result). The original `/diagnose` endpoint is untouched. `index.html`'s simulated timer was replaced with real polling against these endpoints.

Diagnosis: Verified against a live run that genuinely revised once before passing -- the UI's chain-of-custody ledger correctly showed the real attempt number rather than a fixed animation.

Lesson: this is the same "a clean result is not evidence, a clean result checked against its source is" principle (ROADMAP.md, Section 2.4) applied to the demo layer itself -- a UI that looks like it's tracking real progress needed to be checked against a run where the real progress was actually irregular (a genuine revision), not just a clean first-pass run where a simulated timer would have looked identical to the real thing.


---

## Phase 53 — UI Freeze on FLAGGED_FOR_REVIEW: Empty Class Name Throws Mid-Render

Problem: A real demo run that ended in `FLAGGED_FOR_REVIEW` froze the UI on its last loading-stage text, with polling already stopped and no error surfaced to the user -- found via an actual failed run, not hypothetical review.

Diagnosis: `renderResult()` called `slamStamp('', 'ON HOLD<br>REVIEW')` on the `FLAGGED_FOR_REVIEW` path specifically. `classList.add('')` throws a `DOMException` on an empty string, which aborted `renderResult()` immediately after `headerStatus` was set to `'ON HOLD'` but before `showPanel(3)` ran -- leaving the chain-of-custody ledger correctly updated (`finalizeLedger` had already completed) while the main panel stayed frozen. The `SYNTHESIZED` and `FLAGGED_FIDELITY_FAILURE` paths were unaffected, since they pass non-empty class names (`'verified'`, `'fidelity'`).

Fix: Pass a non-empty, unstyled class name (`'flagged'`) instead of `''`. No CSS rule exists for `.verdict-stamp.flagged`, so the visual result is identical to what the empty string was meant to produce.

Diagnosis/Validation: Re-ran the exact input that triggered the freeze; the UI now renders the reasons box and draft correctly instead of hanging.

Lesson: a one-character difference (`''` vs. a real string) in a rarely-exercised code path (the specific verdict that skips both other outcomes) is exactly the kind of bug that survives testing focused on the common-case paths -- this was only caught because a genuinely varied verdict was actually triggered during testing, not assumed to behave like the other two.


---

## Phase 54 — Two Real Pakistani Cases Added; Fidelity Feedback Extraction Bug Fixed

Problem: The corpus contained three real cases, all Western (Southwest, Boeing, Peloton) -- credible as an architecture demonstration, but with no case grounded in the market this project's own judges live in. Separately, `simplify_fidelity_feedback()` (the demo UI's equivalent of `simplify_audit_feedback()` for the fidelity check) took only the first line following "Instances found:" per check, with no check for whether that first-listed instance was itself PASS or FAIL -- silently dropping every real fidelity violation beyond the first, or showing a PASS instance's own text as if it were the stated reason.

Fix: Added two real, publicly documented Pakistani cases to the corpus: `Case_04_PIA_Karachi_Crash_and_Financial_Crisis.md` (PIA's 2020 Karachi crash, the pilot license scandal, and the decade-long financial crisis and privatization that followed) and `Case_05_Airlift_Technologies_Collapse.md` (Airlift Technologies' 2022 shutdown, six days after its lead funding round collapsed). Fixed `simplify_fidelity_feedback()` to split "Instances found:" into per-instance chunks, keep only chunks with a case-sensitive FAIL marker (the same approach Check 3's extraction already used elsewhere in `api.py`), and surface up to 3 full instances per check instead of one truncated, unfiltered line. Also exposed `result.raw_fidelity_verdict` (debug-only, same status as `unverified_report`) so future fidelity failures can be diagnosed directly from the API response instead of relying on scrollback-dependent terminal logs.

Diagnosis/Validation: Both new cases validated end-to-end through the live pipeline -- passed audit on the first attempt, correctly distinguished trigger from root cause on genuinely ambiguous real facts, and both surfaced real Check C findings that exercised the fidelity-feedback fix directly. Confirmed against two real runs (Airlift, PIA) that the pre-fix version could have shown a PASS instance's own text as the stated reason.

Lesson: the corpus-expansion and the bug-fix are reported together because the bug was found by the corpus expansion -- new, genuinely ambiguous cases exercised a code path the original three-case corpus's outputs hadn't happened to trigger in a way that surfaced this specific defect. Expanding real test data continues to be how this project's real bugs get found, not designed-for review.


---

## Phase 55 — Check 2/Check 3 Feedback Boundary Bug Fixed; Check 1 Part B Characterized at n=6 (Ohio Warehouse)

Problem: `simplify_audit_feedback()`'s Check 2 section match used an unbounded `r"Check 2.*"` (DOTALL, no lookahead), capturing from "Check 2" through the rest of the document -- Check 3 included -- rather than stopping at the next `###` heading the way Check 3's own section match already correctly did. When Check 2's overall status was FAIL, its numbered-FAIL-instance regex swept up Check 3's own numbered FAIL instances too, mislabeling genuine technical-fabrication findings with Check 2's ranking-specific framing. Confirmed against real captured output showing the same Check 3 finding twice: once correctly labeled, once truncated and mislabeled as a ranking issue.

Fix: Bounded Check 2's section match identically to Check 3's existing pattern: `Check 2.*?(?=\n###|\Z)`.

Separately, this phase also folds in a constructed test of Check 1 Part B (does the Auditor reliably reject an internal decision mislabeled as an external trigger?) using a synthetic "Ohio Warehouse" fixture with no genuine external trigger present. 6 independent trials run: Check 1 Part B correctly rejected the internally-caused trigger in 5 of 6. No reproducible link was found between the one miss and how the trigger was phrased -- an earlier working hypothesis that symptom-framing evades detection while decision-framing gets caught did not survive a later trial, where a symptom-phrased trigger was caught cleanly.

Lesson: reported at exactly the scale it was tested -- 5/6 (~83%), no established failure pattern -- rather than rounded up to a stronger claim or a fix attempted against a pattern that isn't actually confirmed to exist. Consistent with this project's standing rule (ROADMAP.md, Section 2.5): one observation isn't a pattern, and a hypothesis that doesn't survive a further trial gets discarded, not defended. This finding does not yet meet the n=9-per-fixture bar Check 1's and Check 2's own validated write-ups are held to (see Phase 45) -- a further round at that scale is the natural next step before treating the 5/6 figure as more than directional.


---

## Phase 56 — Real Per-Run Case Numbers; Direct PDF Download Replacing the Print Dialog

Problem: `caseNo` and `docCaseNo` were hardcoded to the static placeholder "2026-0027" in the markup -- both already had unused element IDs, suggesting the intent to wire them up was there but never finished. Every run, and the empty landing page before any run at all, showed the identical fake number. Separately, downloading a report relied on `window.print()`, which opens the browser's own print dialog and -- by default, unless the user manually unchecks it under "More settings" every time -- stamps a URL/date/title header-footer strip onto every printed page, neither of which belongs on a document meant to look like a real case file.

Fix:
- Added `deriveCaseNo()`, turning any hex-ish seed into a stable `YYYY-NNNN` display number, and `randomHexSeed()` for generating one client-side when no real job exists yet. A real case number now shows immediately on page load (restored from the session if one exists, freshly generated if not), gets overwritten with a number derived from the backend's actual `job_id` once a diagnosis starts, and a new one is minted when "Start a New Diagnosis" is clicked. Persisted through `saveState()`/`restoreState()` so a mid-session reload doesn't fall back to the placeholder.
- Replaced `window.print()` with `html2pdf.js` (same CDN-script pattern already used for `marked`), generating a PDF directly from `#docCard` and triggering a download with no system dialog and no header/footer strip. Targeting `#docCard` specifically also means the header, ledger sidebar, and action buttons are naturally excluded, with no `@media print` rules needed for this path (left untouched as a manual Ctrl+P fallback).

Diagnosis/Validation -- two further bugs were found through actual downloaded PDFs, not review:
- **Scroll-position capture bug**: `html2canvas` (used internally by `html2pdf.js`) captures based on the page's current scroll position rather than always grabbing the full target element regardless of what's in view. A PDF downloaded after scrolling down to read the report came out as a screenshot of whatever was on screen at that scroll offset -- cut off mid-sentence, with a large blank area after. Fixed by resetting scroll to the top immediately before capture and explicitly setting `scrollX`/`scrollY`/`windowWidth`/`windowHeight` in the `html2canvas` options, restoring the original scroll position afterward.
- **Verdict stamp invisible in the PDF**: `.verdict-stamp` is `opacity: 0` by default, revealed only through the `stamp-slam` CSS animation triggered by a `.show` class. On the live page that animation finishes almost immediately and the browser correctly holds its final frame indefinitely. But `html2canvas` clones the target element into a fresh rendering context to rasterize it, and CSS animations restart from their 0% keyframe on a freshly cloned element -- the capture happens before the restarted animation reaches its visible state, so the stamp rasterized as fully invisible despite being clearly visible on screen. Fixed by forcing the stamp directly to its settled end-state (`animation: none`, explicit final `opacity`/`transform`) via inline style immediately before capture, bypassing the animation entirely, then restoring the element's original style afterward.

Both fixes verified against real downloaded PDFs across a `SYNTHESIZED` result (multi-page report, stamp correctly visible) and a `FLAGGED_FOR_REVIEW` result (stamp correctly visible in its flagged styling).

Lesson: both of these are well-documented `html2canvas` limitations (scroll-relative capture, and CSS-animation restart on clone), not obscure edge cases -- but neither surfaces in a quick sanity check, only in exactly the conditions a real user hits (having scrolled to actually read the content; a result whose stamp reveal depends on an animation rather than a static style). Real, deliberately-varied test runs kept finding real bugs a single happy-path test would have missed, the same pattern behind every prior UI bug this project has found.


---

## Phase 57 — FLAGGED_FOR_REVIEW's Best-Effort Draft Silently Empty in the Real-Time Progress Endpoint

Problem: found while validating Phase 56's PDF fixes against a real `FLAGGED_FOR_REVIEW` result -- the "Best-effort draft -- not independently verified" label rendered with no content beneath it, both on the live page and in the downloaded PDF, ruling out a capture-layer bug and pointing at the data itself.

Diagnosis: `_run_diagnosis_job()` (the background-thread target added in Phase 52 for `/diagnose/start` + `/diagnose/status/{job_id}`, which the demo UI actually calls) unconditionally set `"draft": orchestrator_result.get("unverified_report")` for every status. `unverified_report` only exists when the Orchestrator actually ran and produced a report -- true for `FLAGGED_FIDELITY_FAILURE`, but never true for `FLAGGED_FOR_REVIEW`, since the Orchestrator never runs at all when the Auditor doesn't pass (the hard branch documented in Phase 42 and enforced in `orchestrator.py`). So `draft` was silently `None` for every `FLAGGED_FOR_REVIEW` result specifically, and had been since Phase 52 -- the original single-shot `/diagnose` endpoint, still present in `api.py`, already handled this correctly by sourcing `draft` from `pipeline_result["final_diagnosis"]` for this exact status, but the newer polling endpoint duplicated the response-building logic rather than reusing it, and didn't carry that status-specific branch over. The `"reasons"` field two lines below in the same function already branches correctly per status -- this was an isolated omission on one field, not a structural gap in how the endpoint thinks about status.

Fix: gave `"draft"` the same three-way branch already used for `"reasons"`: `unverified_report` for `FLAGGED_FIDELITY_FAILURE`, `pipeline_result["final_diagnosis"]` for `FLAGGED_FOR_REVIEW`, `None` otherwise.

Validation: re-ran a `FLAGGED_FOR_REVIEW` case after restarting the API server; the full raw Analyst diagnosis now renders under the best-effort label, on the live page and in the downloaded PDF.

Lesson: this bug had been sitting in the endpoint the live demo UI actually uses since Phase 52 and had gone unnoticed since -- not because it was subtle, but because nothing had previously tried to view a `FLAGGED_FOR_REVIEW` result's draft content specifically until Phase 56's PDF testing happened to land on one. Two endpoints implementing the same response shape independently, rather than one endpoint's logic being reused by the other, is exactly the kind of duplication that lets one copy silently drift out of sync with a correctly-handled case in the other -- the same category of risk Phase 48 closed for the RAG corpus's ground-truth filter, here one layer up, at the API response layer instead of the data-indexing layer.

## Phase 58 — MASS Branding Footer Added to the Report Card

Problem: `#docCard`, the element captured for both the live report view and the downloaded PDF, ended immediately after `#report-slot` with no indication anywhere in the artifact of what produced it. A reader opening the PDF outside the live demo had no way to tell the report came from an audited five-agent pipeline rather than a single unscaffolded model call -- the project's core differentiator was invisible in its own output.

Diagnosis: no provenance element existed in the markup at all, not a hidden or misconfigured one -- this was a straightforward gap, not a bug in existing code.

Fix: added a `.doc-footer` block inside `#docCard`, styled with the existing design tokens (`--paper-line`, `--paper-muted`, `--mono`) so it reads as part of the original design rather than appended on top. It carries two lines: a brand line ("Generated by MASS -- Multi-Agent Strategic System") and a specific, checkable claim ("5-agent pipeline · audited by an architecturally isolated verification layer") alongside the case number. `setCaseNo()` was extended to also update the new `#docFooterCaseNo` span, so the footer stays correct on new runs and on sessions restored from `sessionStorage`, the same way the existing header and eyebrow case-number spans already do. The footer is static text with no animation, so it needed none of Phase 56's stamp-freezing handling for the html2canvas capture.

Validation: confirmed on real runs (cases 2026-2069, 2026-3138, 2026-1301) that the footer renders correctly on both the live page and the downloaded PDF, with the case number matching the eyebrow in each case.

Lesson: a verification status (the stamp) answers "should you trust this result," but says nothing about "what produced it" -- these are different questions and both needed an answer in the artifact itself, not just the first one.

## Phase 59 — Two Roadmap Items Existed Only in Conversation, Not in the Repo

Problem: Urdu-language support and backend report persistence had both been discussed and deliberately deferred past the hackathon deadline, but neither was written down anywhere in the repo -- not in `ROADMAP.md`, not in this log, not in `README.md`. They existed only as conversation history, which meant they were invisible to anyone (including a future session) reading the project's actual documentation.

Diagnosis: `ROADMAP.md` had a `## 7. Extending the System` section for *how* to add things, and a glossary, but no section for *what's already been decided as worth adding later*. There was no natural home for a deferred-but-decided item, so these two fell through and were never captured anywhere durable.

Fix: added `## 9. Post-Hackathon Roadmap (Not Yet Built)` to `ROADMAP.md`, documenting both items against their actual source: report persistence against the specific gap in `api.py` (the `_jobs` in-memory dict is explicitly single-demo-session scope, and the frontend's `sessionStorage` restore is tab-scoped, so no diagnosis currently survives a server restart or a closed tab unless the user manually downloaded the PDF), and Urdu support against the specific claim that only the Intake layer would need to change.

Lesson: a decision to defer something is still a decision, and needs the same treatment as any other decision in this project -- written against its actual source, not summarized from memory days later. The same repo audit that surfaced this also found three stale lines in `README.md` (an outdated endpoint list, an outdated case count, and `index.html` missing entirely from the project structure listing) -- all fixed in this same phase, since they were found by the same pass and are the same category of problem: documentation that quietly stopped matching the code it described.

## Phase 60 — Forced-Ranking Result Extended to PIA and Airlift; a Terminal-Truncation Bug Found Along the Way

Problem: the forced-ranking fabrication result (Section 8.5-8.11 of the formal report) and the Auditor's detection of it had only ever been run on the original three cases (Southwest, Boeing, Peloton) -- never on PIA or Airlift, added later in Phase 54. Separately, the first version of the script written to audit the six new baseline outputs only printed each verdict to the terminal; terminal scrollback truncated on a long session, and five of six verdicts were lost before they could be read.

Diagnosis: `run_repeated_forced_ranking.py`'s existing pattern (generate, save each run to disk, audit each saved file) was correct and didn't need fixing -- a new script scoped to only the two new cases (`run_forced_ranking_pia_airlift.py`) reused it directly, deliberately avoiding re-running the three cases already documented at n=9. The audit-side script, however, was newly written for this task and skipped the save-to-disk step the rest of the project treats as standard practice for exactly this reason -- the same class of problem `orchestrator_outputs/` and `repeated_forced_ranking/` already exist to prevent, just not yet applied to this new script.

Fix: rewrote the audit script (`test_auditor_pia_airlift_forced_ranking.py`) to save every verdict to `audit_pia_airlift/`, one file per run, each containing both the baseline output audited and the full verdict text -- re-run at no extra cost (same 6 calls), with nothing lost this time.

Results, at n=3 per case (not yet the n=9 used for the original three): all 6 runs fabricated a percentage-based ranking; all 6 were correctly caught by the Auditor. Check 1 passed cleanly on all six, both parts, extending its validated set from two real cases with a clear external trigger (Southwest, Peloton) to four. Two of the three PIA runs independently reproduce the omission-blindness gap documented in Phase 24/Section 8.8 -- the diagnosis states the external trigger (the Karachi crash) clearly in prose, then the Pareto table omits it entirely, ranking only internal causes -- with the Auditor's Check 2 reasoning addressing only the fabricated percentages and never noting the omission, exactly the same shape of finding as the original Southwest Run 3 case, now reproduced independently in a case domain (Pakistani aviation and state-enterprise governance) with nothing in common with the original corpus. Where the external cause did appear in the ranking, its table position varied more than the original nine runs suggested: last and smallest on two runs (matching the original template), but third and neither last nor smallest on two others.

Lesson: the same evidentiary standard this project holds throughout -- report at exactly the scale run, not rounded up -- applies here too: this is corroborating evidence on two new cases at n=3, not an independent replication at the n=9 weight of the original result, and is documented as such in the report's own Section 8.14 rather than folded into Section 8.7's existing n=9 figures. Separately, losing five of six verdicts to terminal truncation on the first attempt is itself a small instance of a pattern this project has hit before (Phase 47's note that text-parsing logic is only as trustworthy as what it's actually been checked against) -- a verification step that isn't saved to disk didn't happen, for the purposes of anyone reading this later, and the fix is the same one already established elsewhere in the project: write it to a file.

## Phase 61 — Intake Validated Against Weak Grammar, Code-Switched Input, and the Vague-Quantifier Risk Named in Phase 35

Problem: `intake.py`'s own docstring, since Phase 35, has named axes never tested: input *quality* as distinct from the quantity of data present, the vague-quantifier-promotion risk specifically (e.g. "about half our customers" becoming a stated percentage), and long, rambling, multi-topic input. Phase 35's three fixtures were also all clean, fluent English -- nothing tested weak grammar or the code-switched Roman Urdu/English this project's actual target market writes in.

Diagnosis: five new fixtures were run at the same n=5-per-fixture scale as Phase 35 (25 calls total), each with exact ground truth documented in advance, matching this project's standard fixture methodology: weak/broken English with two embedded hedges; Roman Urdu/English code-switching carrying the same two hedge types; vague quantifiers ("about half," "most of," "a handful") with zero concrete numbers anywhere; a long rambling multi-topic input with exactly one real figure buried in unrelated tangents; and a one-liner sparser than Phase 35's own sparse fixture. Every output was saved to disk (`intake_weak_input_outputs/`) rather than only printed, specifically because Phase 60 documented a real terminal-truncation bug from skipping that step on the immediately preceding testing round.

Results: zero of 25 trials promoted a stated hedge into unstated certainty, holding even under weak grammar and code-switching -- the Roman Urdu fixture's business facts (the return-rate change, the supplier-change date, the revenue decline) were extracted correctly in all five trials despite the code-switching, with both of that fixture's hedges preserved every time. The long-rambling and minimal-one-liner fixtures behaved exactly as Phase 35's own fixtures did, surfacing no new failure shape.

One of 25 trials reproduced, for the first time, the specific risk Phase 35 could name but not confirm: on the vague-quantifier fixture, "About half our repeat customers" was promoted to "Approximately 50% of repeat customers" in the Supporting Data section. The same trial's own Problem Statement correctly kept the figure vague; the promotion happened specifically when the model tried to make Supporting Data read as more data-like than the input actually supports.

A second, previously-unobserved pattern appeared in 4 of 25 trials, split across the weak-English and Roman-Urdu fixtures: an unstated causal link asserted between two facts the input only lists sequentially -- "as a result," "consequently" -- where the input never states that one caused the other. This is milder than a fabricated number, but is still, by `INTAKE_DESCRIPTION`'s own stated rule against adding "a cause ... the user did not state," a real instance of the class of thing that rule exists to prevent, not merely a stylistic smoothing.

Fix: none applied in this phase, deliberately -- per this project's established pattern of separating a precisely characterised finding from the wording change meant to fix it (Check 2 and Check 3's own multi-round refinements), this phase's scope is confirming and documenting the two new findings at the same evidentiary standard as everything else in this log, not yet correcting them. Both are mitigated today by the existing `/structure` human-review checkpoint that shows Intake's output back to the user before any diagnosis runs on it.

Lesson: this is the same shape of result Phase 36 produced for Check 1 Part B -- a named, plausible risk, checked directly rather than left as an assumption, confirmed to mostly hold with one narrow, low-rate exception rather than either a clean pass or a broken system. The vague-quantifier-promotion rate (1 of 5 trials on the one fixture built specifically to test it) is reported at exactly that scale, not extrapolated to the other fixtures or rounded into a general claim about Intake's reliability under weak input.
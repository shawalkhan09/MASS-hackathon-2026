# MASS — Project Roadmap

**What this document is:** a complete, standalone specification of what MASS is, why it is designed the way it is, and how to build it from nothing. It is not a progress report and contains no status information — nothing here says what has or hasn't been done. For that, see `DEVELOPMENT_LOG.md` (the chronological build history) or the formal report (the evidence-backed write-up). This document should be readable and actionable on its own, by someone who has never seen the project before, at any point in its life.

---

## 1. What MASS Is, and What It's For

MASS (Multi-Agent Analysis and Synthesis System) is a system that takes a real business problem and produces an audited, evidence-grounded diagnostic report — the kind of root-cause analysis a business consultant would produce, but built from a pipeline of specialised AI agents rather than a single model call.

It exists for two reasons at once, and both shape its design:

- **As an academic project.** The central question it is built to answer is not "can an LLM analyse a business case" — a single model call can already do that, fluently. The question is whether *decomposing* that task into specialised, checked stages (research → analysis → audit → synthesis) produces something meaningfully more trustworthy than one unscaffolded call to the same underlying model. That comparison — pipeline vs. single call, model held constant — is the project's real deliverable, not the diagnoses themselves.
- **As groundwork for a product.** The same system, if it holds up, is the basis for a consulting-support tool. That means the academic validation isn't just for a grade — it's the actual due diligence a real product built on this architecture would need before anyone trusted its output.

**The one sentence version of what the whole system is supposed to prove:** given identical facts and an identical difficult question, an unscaffolded model will confidently invent plausible-sounding, unsupported specifics under pressure to look complete — and a correctly designed multi-agent pipeline with an independent audit stage will not, and will catch it when the unaudited version does. Everything else in this document exists in service of building something that can make that claim honestly.

---

## 2. Design Philosophy — Read This Before Building Anything

These are the load-bearing principles. They matter more than any individual component, because they're what keeps the system honest as it grows. Anyone extending or rebuilding this should hold to these even where the specifics below change.

1. **Restrict what a component can see, don't just instruct it to behave.** If a downstream step shouldn't use certain content, the safest fix is to never give it that content, not to tell it not to use it. Instructions get followed literally, including flawed ones — a component given access to something it shouldn't use will eventually use it, especially across many independent runs.
2. **Fail closed by default.** Any stage whose job is to make output look complete, polished, or client-ready must never run on an input that hasn't been independently verified. A synthesis or presentation layer is exactly where an unresolved problem gets quietly smoothed over if it's allowed to run unconditionally.
3. **Every check should be evidence-derived, not generic caution.** A rule like "don't fabricate numbers" is too vague to test or trust. A rule scoped to an exact, previously observed failure — "don't assign a percentage weight to a cause unless the case data provides a figure to compute it from, in any format, table or prose" — is checkable, testable, and falsifiable.
4. **A clean result is not evidence. A clean result you checked against its source is.** Passing on one run, or exiting without an error, proves nothing on its own. Trust requires diffing the actual output against the actual thing it was supposed to be built from — not the fact that it ran.
5. **One observation is not a pattern.** A result seen once might be a coincidence. The same result seen across many independent trials, with the exact shape of the variation examined, is what supports a real claim. Repeat before generalising.
6. **When two things might be co-occurring causes of one result, isolate them.** If a failure could be explained by either of two factors, don't guess which one — construct a case where only one factor is present and test that directly.
7. **Preserve precision when reformatting.** Category labels, scope qualifiers ("by X measure"), and hedges ("the case does not support a figure here") are load-bearing. A reformatting or synthesis step that drops or blurs them has changed the claim, even if it added no new fact.
8. **State the exact boundary of what's proven, not a rounded-up version of it.** "This system doesn't fabricate under pressure" and "this system produces good diagnoses on arbitrary new problems" are different claims requiring different evidence. Only claim what was actually tested.
9. **Own defects in your own instructions, not just the model's behaviour.** When something goes wrong, check whether the fault is in what you told the component to do before assuming the component misbehaved. Prompts and task specifications are code, and code has bugs.

---

## 3. System Architecture

The system has five components. Each is described below with what it does, why it's built that way, and what would go wrong if it weren't.

### 3.1 Knowledge Base

A curated set of business diagnostic frameworks and financial-vocabulary terms (root-cause techniques, prioritisation frameworks, financial calculation methods), organised into a tiered structure and chunked by field — each framework broken into its Definition, When to Use It, Step-by-Step Process, and a Worked Example — rather than stored as a single undifferentiated block of text per framework.

**Why chunked this way:** retrieval and application are different needs. A retrieval query wants to match against "when to use this" and short definitions; an agent applying the framework wants the full process and a worked example. Storing these separately lets a retriever return exactly what's needed rather than an entire framework's text every time any part of it is relevant.

### 3.2 Case Corpus

A small set of real, independently and publicly documented business failures or events — not synthetic scenarios, not licensed case-study products. Each case packet has a strict internal structure:

- **Problem Statement, Background, Supporting Data** — the facts an analyst would actually have. This subset is called the *diagnostic input*.
- **A "Best-fit frameworks" hint and a Ground-Truth Diagnosis Summary** — the documented, real-world root-cause finding (from a regulatory investigation, a company's own post-mortem, or established financial reporting), kept in the same file but structurally separate.

**The one rule that must never be violated:** only the diagnostic input is ever passed to an agent. The hint and the ground truth exist purely for scoring the system's output after the fact — feeding either to an agent hands it the answer and invalidates any evaluation done afterward. Any function that loads a case file for use by an agent must extract only the diagnostic input; any caller that reads the raw case file directly is a bug.

**Why real, publicly documented cases rather than synthetic ones or licensed material:** real cases carry genuine, externally verifiable ground truth — a claim that can be checked against an actual regulatory report or financial filing, not an internally authored "correct answer" that the same team also wrote the test around. This also sidesteps any licensing question that comes with using proprietary case-study material.

### 3.3 Retrieval Pipeline (RAG)

Connects a case's facts to the frameworks actually relevant to diagnosing it. Built with interchangeable retriever backends (at minimum: a TF-IDF baseline, and at least one embedding-based retriever) behind a single interface, so retrieval quality can be measured and compared rather than assumed.

**The critical, non-obvious design requirement:** a query built from the raw case narrative retrieves poorly against framework definitions, because the vocabulary barely overlaps — case text describes what happened in plain narrative language; framework definitions are written in technique language. A query must first be reformulated — translating "why did this operational failure cascade" into "root cause analysis technique for a systemic technology failure," for example — before retrieval. Skipping this step is not a minor quality loss; it can produce near-total retrieval failure. This should be verified directly with a query-to-expected-chunk scoring harness before trusting the retrieval step at all, not assumed to work because the embedding model is a good one.

### 3.4 The Agent Pipeline

Four roles, each with a narrow, specific job:

- **Researcher.** Given a case, identifies which frameworks are actually applicable and retrieves the specific knowledge (definition, process, example) an analyst will need. Its output is a shortlist with justification, not an analysis.
- **Analyst.** Given the case and the Researcher's shortlist, actually applies each framework to the case's real facts — walks the real reasoning, computes real figures where the case supports them, and is instructed to explicitly decline to compute or rank anything the case's data doesn't support, rather than approximate or estimate.
- **Auditor.** Reviews the Analyst's output against a small number of specific, evidence-derived checks — not a general quality review. At minimum: (1) does the diagnosis correctly separate an external triggering event from the company-controllable root cause, rather than conflating the two; (2) is any formal ranking or weighting of causes — in a table, a list, or plain prose, format does not matter — actually grounded in figures the case provides, rather than an invented-but-plausible-looking percentage or qualitative label. Each check should be written against a specific, previously observed failure mode, and refined iteratively against real failures as they're found, not written once and assumed correct.
- **Orchestrator.** Once (and only once) a diagnosis has passed the Auditor, synthesises the approved diagnosis into a single, polished, client-facing report. Structurally cannot see anything the Auditor didn't review — no raw case text, no unaudited Researcher output — so it cannot present unvetted content as though it had passed review. Makes zero calls, and produces a flagged-for-review result instead of a report, if the diagnosis never passed.

**Revision control between Analyst and Auditor:** bounded, not open-ended. On a failing audit, the Auditor's full feedback is passed back to the Analyst with an instruction to fix only what was flagged and leave what already passed unchanged, then the revised diagnosis is re-audited. This repeats up to a fixed, small limit; if it's still failing after the limit, the system stops and records the failure rather than looping indefinitely or silently shipping a failing result as if it had passed.

**Why this control flow should be built as plain, inspectable code rather than a framework's own multi-agent orchestration primitives (e.g. a hierarchical process or a built-in flow/graph engine):** conditional branching based on one stage's output determining whether another stage re-runs is exactly the kind of logic that's easy to get subtly wrong inside a less-transparent framework abstraction, and hard to debug when it does. Plain control flow around small, single-purpose agent calls is more verbose but every step of it can be read, logged, and reasoned about directly.

### 3.5 Model and Infrastructure Choices

- A single explicit model string set on every agent, every time, never left to a framework's default. Multi-agent frameworks commonly fall back to a different provider's default model if one isn't set explicitly per agent — this fails loudly (a missing API key for a provider not even in use) but can also fail expensively and silently if that provider happens to be configured. Set it explicitly, everywhere, and verify it after any framework upgrade.
- A local vector store for retrieval, decoupled from the choice of embedding model, so the embedding backend can be swapped and compared without changing the storage layer.
- Case files, agent definitions, and run drivers as plain, flat modules rather than a deep package structure — appropriate for a project of this size, where discoverability matters more than enforced separation.

---

## 4. Methodology — How to Actually Validate a System Like This

Building the system is the smaller half of the work. The harder and more important half is establishing, with real evidence, whether it does what it's supposed to.

1. **Hold the model constant, vary the architecture.** The comparison that actually isolates the architecture's contribution is the full pipeline against a single, unscaffolded call to the *same* underlying model on the *same* cases — not against a different model, and not against a human's judgement (which introduces a second, harder-to-defend comparison: "better than this specific person," rather than "better than the same model with no scaffolding").
2. **If an open-ended comparison comes back inconclusive, don't conclude nothing was learned — design a more demanding, decisive test.** An open-ended "which output is better" comparison can genuinely be too close to call. That's a sign to engineer a specific, high-pressure task that forces a checkable failure mode to the surface — for instance, deliberately requiring both conditions to produce a precise, weighted ranking of causes, which invites fabrication if a process is going to fabricate at all.
3. **Test the checker against the real thing it's supposed to catch, not a constructed example.** A check that catches a hand-written example of a violation hasn't been shown to catch the violation a real, unaudited run of the system actually produces. Feed it the real failed output.
4. **Repeat before generalising.** A result obtained once, per condition, is a starting point, not a finding. Repeat the same test many times independently before describing a pattern as reliable — and when repeating, distinguish between "the same exact result recurred" and "the same *shape* of result recurred with different specifics." The second is usually the real, stable finding; the first is often noise.
5. **When a finding could have two explanations, build a test that isolates one.** If a real failing case happens to combine two different problems, don't assume which one a checker actually caught — construct a version of the case with only one of the two problems present, and test that directly.
6. **Read the actual reasoning behind a pass or fail, not just the verdict.** A checker can reach the right verdict for the wrong reason. Confirming *why* something passed or failed is what tells you whether the checker is actually evaluating the thing you think it is.
7. **Do a full, deliberate read-through of every artifact at natural stopping points — not just the parts most recently touched.** Gaps accumulate specifically in the parts nobody re-checked. This applies equally to code (an occasional full file-and-import audit) and to written output (an occasional cover-to-cover read of any report or document being built incrementally).

---

## 5. Things to Be Aware of When Building or Extending This

These are open design questions and known boundaries of the approach — not a to-do list, a set of things worth understanding before assuming the system does more than it does.

- **A completeness check is a different thing from a support check, and most fabrication-detection designs will only build the second.** A checker built to catch an invented number attached to a claim will not, by default, catch a claim or a cause being silently *omitted* altogether — omitting something makes no checkable false claim. If ranking or analysis completeness matters, it needs its own, separately designed and validated check; it will not fall out of a check built to catch invented figures.
- **A synthesis or reformatting stage's faithfulness to its source is not the same property as its input being restricted.** Restricting what a synthesis step can see (Section 2, principle 1) prevents it from drawing on content it shouldn't. It does not, by itself, guarantee that everything it does draw on was reproduced faithfully — precision can still be lost in paraphrasing (a dropped scope qualifier, a relabelled category) even when nothing new was invented. That's a distinct property worth checking for separately.
- **The system's core guarantee is about not fabricating, not about being right on a genuinely new problem.** Every validation case in a corpus like this has known, documented ground truth to score against. A brand-new, real business problem does not. Demonstrating that a pipeline avoids confident invention under pressure is not the same as demonstrating that its diagnosis will be correct on a problem nobody has already solved. Keep these two claims separate in any description of the system, especially outside an academic context.
- **Framework/agent selection can be non-deterministic across runs on the same case.** Don't assume a single run's selection of applicable frameworks, or a single run's output shape, generalises — this needs the same repeated-trial treatment as any other claim about the system's behaviour.
- **A structured case-packet format is not the same as a usable intake process.** If real, unstructured problem descriptions (raw notes, messy internal documents) need to become case packets, that conversion step is a separate, unbuilt piece of the system, not something the existing pipeline does implicitly.

---

## 6. How to Run the System End to End

1. **Environment.** A dedicated virtual environment matching the pipeline's actual dependency versions (multi-agent frameworks and their sub-dependencies can be version-sensitive — confirm the exact Python version required by the framework and any embedding/tokenizer libraries before assuming the system interpreter will work). An explicit API key for whichever model provider is in use, available to the process.
2. **Write a case packet.** A Problem Statement, Background, and Supporting Data section, in the same structure as the existing corpus. No ground-truth or hint section is needed for a genuinely new problem — that only exists in validation cases to enable scoring against a known answer.
3. **Run the pipeline.** Load the case, extract only its diagnostic input, run it through Researcher → Analyst → Auditor with the bounded revision loop, then through the Orchestrator.
4. **Read the result.** Either a synthesised, client-facing report (if the diagnosis passed audit), or a flagged-for-review result carrying the full attempt history and the Auditor's specific objections (if it didn't) — the second case is not an error state, it's the system correctly declining to present something it couldn't verify.

---

## 7. Extending the System

- **Adding a new case:** write a new case packet in the established format; if it's meant for validation rather than real use, source it from a real, independently documented event with verifiable ground truth, and write the ground-truth/hint section clearly separated from the diagnostic input.
- **Adding a new framework to the knowledge base:** chunk it the same way as existing frameworks (Definition, When to Use It, Process, Worked Example) so retrieval and application both work against it consistently.
- **Adding a new Auditor check:** start from a specific, real observed failure, not a generic concern. Write the check narrowly against that failure, test it against real (not hand-constructed) examples of the failure, and expect to refine its wording over several rounds as edge cases and false positives surface — this is normal and expected, not a sign the first draft was wrong to attempt.
- **Adding an intake/pre-processing stage:** if unstructured input needs to become a structured case packet automatically, treat this as its own pipeline stage with its own validation question — specifically, whether the structuring step preserves or distorts the facts on the way in, which is a mirror image of the question already asked of the Orchestrator on the way out.
- **Adding a completeness or faithfulness check:** treat as a new, independent check requiring its own design and validation cycle (see Section 4), not a patch to an existing check built for a different purpose.

---

## 8. Glossary

- **Diagnostic input:** the subset of a case packet (Problem Statement, Background, Supporting Data) that is safe to give to an agent — contains no answer or hint.
- **Ground truth / reference material:** the documented real-world finding for a case, used only for scoring output after the fact, never given to an agent.
- **Fabrication (in this project's specific sense):** a confident, specific, plausible-looking claim — most often a numeric or qualitative ranking of causes — asserted without the underlying data to actually support it.
- **Fail-closed:** a design where a component defaults to doing nothing (or to an explicit failure/flag state) rather than proceeding, whenever its precondition for safely proceeding isn't met.
- **Input surface:** the total set of content a given component has access to when making its call — restricting this deliberately, rather than only instructing the component on how to use it, is the project's primary technique for preventing a downstream stage from drawing on content it shouldn't.

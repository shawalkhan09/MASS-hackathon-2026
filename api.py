# -*- coding: utf-8 -*-
"""
FastAPI backend for the MASS demo/prototype UI.

Wraps the existing, validated pipeline (crewai_pipeline.py,
orchestrator.py) plus one new, not-yet-validated component (intake.py)
behind two HTTP endpoints, deliberately kept separate rather than
combined into one call:

  POST /structure -- runs ONLY the new intake step and returns its
  structured extraction for the user to review, edit, or approve BEFORE
  anything else runs. This is the human-in-the-loop check on the one
  unvalidated new component in this pipeline (see intake.py's
  docstring) -- it exists specifically so a user can catch and correct
  anything the intake step got wrong before it's used for real
  analysis, not as a UX nicety.

  POST /diagnose -- takes the (user-approved or user-edited) structured
  input and runs the full, already-validated pipeline: Researcher ->
  Analyst -> Auditor (with the bounded revision loop) -> Orchestrator
  -> fidelity check. Returns one of three outcomes, each labelled
  distinctly rather than collapsed into a generic "not verified":

    - SYNTHESIZED: diagnosis passed audit, report passed the fidelity
      check. The clean, verified deliverable.
    - FLAGGED_FOR_REVIEW: the diagnosis itself never passed audit --
      the Auditor's concern is about the underlying analysis. Returns
      the best-effort draft plus simplified reasons drawn from the
      Auditor's verdict.
    - FLAGGED_FIDELITY_FAILURE: the diagnosis DID pass audit -- the
      analysis is sound -- but the synthesised write-up drifted from
      it (a new claim, a relabelled category, a dropped qualifier; see
      fidelity_check.py). This is a materially different situation
      from FLAGGED_FOR_REVIEW and needs its own message: the analysis
      is trustworthy, the report text is not. Collapsing this into the
      audit-failure path would run audit-verdict text (which passed)
      through a parser looking for audit failures, produce no matches,
      and fall back to a generic message that misrepresents a sound
      analysis as unsupported -- which is exactly the bug this version
      fixes.

  (Design choice, both flagged cases: showing a labelled draft rather
  than nothing, because for a demo/prototype specifically, either kind
  of flag is a demonstration of the pipeline's checks doing their job
  correctly, not a dead end -- hiding it entirely would hide the
  system's actual point.)

Run:
    pip install fastapi uvicorn
    venv312/bin/uvicorn api:app --reload --port 8000

Then open index.html in a browser (it calls http://localhost:8000).

Note on cost and wait time: /diagnose triggers the full pipeline --
Researcher, Analyst, Auditor, up to max_revisions extra Analyst+Auditor
cycles, Orchestrator, and a three-part fidelity check -- several
sequential LLM calls per request. This is synchronous and will take
real, noticeable time; there is no streaming or progress reporting in
this first version. Fine for a demo/prototype with a handful of users;
would need a real async job queue before this could handle concurrent
load.
"""

import re
import threading
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional, List

from intake import run_intake
from crewai_pipeline import run_pipeline
from orchestrator import run_orchestrator

app = FastAPI(title="MASS Demo API")

# Permissive CORS for local demo/prototype use only -- a page served
# from a different local origin needs this to call the API at all.
# Tighten this (specific allowed origin, not "*") before anything
# resembling a real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store for the async /diagnose/start endpoint.
# Single-demo-session scope -- no persistence, no cleanup, no auth.
# Same guarded-lock pattern as retrieval_tool.py's _QUERY_LOCK.
_jobs_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


class StructureRequest(BaseModel):
    raw_input: str


class StructureResponse(BaseModel):
    structured_input: str


class DiagnoseRequest(BaseModel):
    structured_input: str
    max_revisions: int = 1


class DiagnoseResponse(BaseModel):
    status: str  # "SYNTHESIZED", "FLAGGED_FOR_REVIEW", or "FLAGGED_FIDELITY_FAILURE"
    report: Optional[str] = None
    draft: Optional[str] = None
    reasons: Optional[List[str]] = None
    total_attempts: int


def simplify_audit_feedback(audit_text: str) -> List[str]:
    """
    Extracts human-readable reasons from the Auditor's structured
    markdown verdict (see AUDIT_DESCRIPTION in crewai_pipeline.py for
    the exact format this is parsed against), for showing to an end
    user instead of the raw internal check format ("Check 2: FAIL").

    CORRECTED (this version): the original Check 1 regex looked for a
    literal "Explanation:" label -- but Check 1's real output format
    never contains one. It uses "Overall Status:" plus "Part A (...)"/
    "Part B (...)" lines in "VERDICT -- <quote> -- <why>" form instead,
    so the old regex could never match a real Check 1 failure and
    always fell through to the generic fallback message, regardless of
    what actually failed. Confirmed against real captured audit text
    from a live run (a case with no genuine external trigger, correctly
    rejected by Check 1 Part B) before and after this fix.

    Also corrected: the original Check 2 extraction never checked
    whether Check 2's own overall status was FAIL, and pulled ANY
    "Reasoning:"/"Explanation:" text found anywhere after "Check 2" --
    including a PASSing instance's own reasoning, mislabeled with a
    FAIL-sounding lead-in. This is now gated on Check 2's overall status
    being FAIL, and only pulls reasoning tied to instances individually
    marked FAIL, verified against a case with one FAIL instance sitting
    next to one PASS instance to confirm only the former surfaces.

    Never raises. Falls back to a generic-but-honest message if the
    Auditor's real output doesn't match the expected structure closely
    enough to parse -- a parsing failure should degrade to something
    less specific, never crash the response or invent a fake reason.
    """
    reasons = []

    part_specs = [
        (r"Part A \(Distinctness\)",
         "The trigger and root cause weren't clearly stated as two separate things"),
        (r"Part B \(Trigger Is Genuinely External\)",
         "What was labeled as the external trigger looks like something the "
         "company itself did, not an outside event"),
    ]
    for part_pattern, friendly_lead in part_specs:
        part_match = re.search(
            rf"{part_pattern}:\s*FAIL\s*--\s*(.+?)(?=\nPart [AB]|\n###|\Z)",
            audit_text, re.DOTALL | re.IGNORECASE,
        )
        if part_match:
            full_text = part_match.group(1).strip()
            # Format is <quote> -- <why>; take the "why" (final segment)
            # if the dash separator is present, otherwise fall back to
            # the whole captured span rather than guessing at structure
            # that isn't there.
            segments = full_text.split(" -- ")
            why = segments[-1].strip() if len(segments) > 1 else full_text
            first_line = why.split("\n")[0]
            reasons.append(f"{friendly_lead}: {first_line}")

    check2_overall_fail = re.search(
        r"Check 2.*?Status:\s*FAIL", audit_text, re.DOTALL | re.IGNORECASE
    )
    if check2_overall_fail:
        check2_section_match = re.search(r"Check 2.*", audit_text, re.DOTALL | re.IGNORECASE)
        check2_text = check2_section_match.group(0)
        # Only match numbered instances that are THEMSELVES marked FAIL --
        # never a PASS instance's reasoning, even when Check 2's overall
        # verdict is FAIL because of a different instance.
        fail_instances = re.findall(
            r"(?:^|\n)\s*\d+\.\s*.*?FAIL[.:]?\s*(.+?)(?=\n\s*\d+\.|\n###|\Z)",
            check2_text, re.DOTALL | re.IGNORECASE,
        )
        for r in fail_instances[:3]:  # cap at 3 -- avoid a wall of text
            first_line = r.strip().split("\n")[0]
            if first_line:
                reasons.append(
                    "One part of the ranking wasn't clearly backed by the "
                    "data provided: " + first_line
                )

    check3_overall_fail = re.search(
        r"Check 3.*?Status:\s*FAIL", audit_text, re.DOTALL | re.IGNORECASE
    )
    if check3_overall_fail:
        # Bounded to stop before any NEXT "###" heading (some real
        # responses append bonus commentary, e.g. "### Audit Summary",
        # after Check 3's own Instances-found list -- that's not part
        # of Check 3's structured output and must not be scanned for
        # quotes, or its own quoted fragments get mixed in).
        check3_section_match = re.search(
            r"Check 3.*?(?=\n###|\Z)", audit_text, re.DOTALL | re.IGNORECASE
        )
        check3_text = check3_section_match.group(0)
        # Check 3's real output format varies more than Check 1/2's --
        # numbered, bulleted, bold-labeled, and FAIL appearing before OR
        # after the quoted claim have all been observed across this
        # project's Check 3 test rounds. Splitting into per-instance
        # chunks first (numbered "1."/"2." or bulleted "-"/"*", which
        # every observed format uses) and matching quotes WITHIN each
        # chunk, rather than across the whole section, matters more
        # than it looks: a single unpaired quote character anywhere
        # earlier in the section (e.g. inside a PASS instance's own
        # reasoning) silently shifts which text falls "between quotes"
        # for every match after it, for the rest of the document.
        # Resetting quote-pairing at each instance boundary contains
        # that failure to at most the one instance it happens in.
        #
        # Within a chunk, quote-pairing itself is done with NO length
        # bound first (`[^”\"]*`, not `{20,500}`) and length is only
        # filtered afterward as a separate step -- confirmed against
        # real captured Check 3 output that embedding a length bound
        # directly in the pairing regex causes the SAME misalignment
        # bug it's meant to avoid: any quote pair outside the bound
        # (too short, e.g. "integration latency", or too long, e.g. a
        # full quoted 5-Whys question+answer) gets silently skipped by
        # the pairing itself, which shifts every subsequent open/close
        # match in that chunk by one, turning them into the prose
        # BETWEEN real quotes instead of the quotes themselves.
        check3_reasons = []
        seen = set()
        for chunk in re.split(r"\n\s*(?:\d+\.|[-*])\s+", check3_text):
            # Case-SENSITIVE on purpose: the model always writes its
            # verdict marker as uppercase FAIL/PASS, but ordinary
            # prose inside a PASS instance can contain the lowercase
            # word "fail" naturally (e.g. a quoted 5-Whys question
            # like "why did the synchronization fail..."). Matching
            # case-insensitively pulled PASS instances' own quotes
            # into the output -- confirmed against real captured
            # output where this happened.
            if not re.search(r"\bFAIL\b", chunk):
                continue
            all_quotes = re.findall(r"[“\"]([^”\"]*)[”\"]", chunk)
            candidates = [q.strip() for q in all_quotes if 20 <= len(q.strip()) <= 500]
            if not candidates:
                continue
            # A FAIL instance's own reasoning routinely quotes the
            # case input back as justification for why a claim is a
            # violation (e.g. "...explicitly states 'the mechanism is
            # not established.'"). That reference quote can be LONGER
            # than the actual flagged claim, which defeats a plain
            # longest-wins pick. But a quote that itself preserves
            # uncertainty can never be the violation -- Check 3 exists
            # to catch claims that FAIL to hedge -- so hedge-shaped
            # quotes are excluded first; the flagged claim is then the
            # longest of what's left. Confirmed against real captured
            # output where the unfiltered longest-quote picked the
            # case input's own hedge sentence instead of the fabricated
            # claim it was quoted to contrast against.
            HEDGE_MARKERS = (
                "not established", "still investigating", "currently investigating",
                "under investigation", "remains unconfirmed", "unidentified",
                "unresolved", "unestablished", "still gathering data",
            )
            non_hedge = [q for q in candidates if not any(h in q.lower() for h in HEDGE_MARKERS)]
            quote = max(non_hedge or candidates, key=len)
            key = quote[:60]
            if key in seen:
                continue
            seen.add(key)
            check3_reasons.append(quote)

        for quote in check3_reasons[:3]:
            reasons.append(
                "A specific detail was presented as settled fact even "
                "though the case said this was still unresolved: “" + quote + "”"
            )
        if not check3_reasons:
            reasons.append(
                "Our reviewer found a specific detail treated as confirmed "
                "even though the case said the cause was still under "
                "investigation. See the full technical review for specifics."
            )

    if not reasons:
        reasons.append(
            "Our reviewer flagged something in this analysis as not "
            "clearly supported by the information provided. See the "
            "full technical review for specifics."
        )
    return reasons


def simplify_fidelity_feedback(fidelity_verdict_text: str) -> List[str]:
    """
    Extracts human-readable reasons from the fidelity check's combined
    verdict text (see run_fidelity_check() in fidelity_check.py: three
    "### Check X: <name>" sections, each wrapping that check's own
    "## Check X Verdict: PASS/FAIL" plus an "Instances found:" block).

    Deliberately separate from simplify_audit_feedback() and NOT a
    fallback path for it -- a fidelity failure means the underlying
    analysis passed audit and is sound; only the write-up drifted from
    it. The messages here say that explicitly, since it's a materially
    different (and less concerning) situation than an audit failure,
    not just a different code path.

    Never raises. Falls back to a generic-but-honest message if the
    verdict text doesn't match the expected structure closely enough
    to parse.
    """
    reasons = []

    check_framing = {
        "A": "the write-up included a detail that isn't actually traceable "
             "back to the underlying analysis",
        "B": "a category label changed between the analysis and the "
             "write-up",
        "C": "a number in the write-up lost some of the specific context "
             "or precision it had in the underlying analysis",
    }

    for letter, framing in check_framing.items():
        section_match = re.search(
            rf"### Check {letter}:.*?## Check {letter} Verdict:\s*FAIL\s*\n"
            rf"(?:Instances found:)?\s*(.+?)(?=\n###|\Z)",
            fidelity_verdict_text, re.DOTALL | re.IGNORECASE,
        )
        if section_match:
            first_line = section_match.group(1).strip().split("\n")[0]
            reasons.append(f"In the polished write-up, {framing}: {first_line}")

    if not reasons:
        reasons.append(
            "Our reviewer found that the polished write-up drifted from "
            "the underlying analysis in some way, even though the "
            "analysis itself was sound. See the full technical review "
            "for specifics."
        )
    return reasons


@app.post("/structure", response_model=StructureResponse)
def structure(req: StructureRequest):
    if not req.raw_input or not req.raw_input.strip():
        raise HTTPException(status_code=400, detail="raw_input must not be empty")
    structured = run_intake(req.raw_input)
    return StructureResponse(structured_input=structured)


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest):
    if not req.structured_input or not req.structured_input.strip():
        raise HTTPException(status_code=400, detail="structured_input must not be empty")

    pipeline_result = run_pipeline(req.structured_input, max_revisions=req.max_revisions)
    orchestrator_result = run_orchestrator(pipeline_result)

    if orchestrator_result["status"] == "SYNTHESIZED":
        return DiagnoseResponse(
            status="SYNTHESIZED",
            report=orchestrator_result["final_report"],
            total_attempts=pipeline_result["total_attempts"],
        )

    if orchestrator_result["status"] == "FLAGGED_FIDELITY_FAILURE":
        # The diagnosis passed audit -- the analysis is sound. Only the
        # synthesised write-up drifted from it. Parse the fidelity
        # verdict specifically; do NOT fall through to
        # simplify_audit_feedback(), which would look for audit-failure
        # language in a verdict that passed audit and find nothing.
        return DiagnoseResponse(
            status="FLAGGED_FIDELITY_FAILURE",
            draft=orchestrator_result.get("unverified_report"),
            reasons=simplify_fidelity_feedback(orchestrator_result["fidelity_verdict"]),
            total_attempts=pipeline_result["total_attempts"],
        )

    # FLAGGED_FOR_REVIEW -- the diagnosis itself never passed audit.
    last_audit = pipeline_result["history"][-1]["audit"]
    return DiagnoseResponse(
        status="FLAGGED_FOR_REVIEW",
        draft=pipeline_result["final_diagnosis"],
        reasons=simplify_audit_feedback(last_audit),
        total_attempts=pipeline_result["total_attempts"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------
# Async diagnosis job endpoints -- additive, no change to /diagnose.
# ------------------------------------------------------------------

def _run_diagnosis_job(job_id: str, structured_input: str, max_revisions: int):
    """
    Background thread target for /diagnose/start. Runs the full
    pipeline + orchestrator with a progress_cb that updates the
    in-memory job store, so a polling client can watch the stages
    advance in real time.
    """
    def _progress_cb(stage: str, attempt):
        with _jobs_lock:
            _jobs[job_id]["stage"] = stage
            _jobs[job_id]["attempt"] = attempt

    try:
        with _jobs_lock:
            _jobs[job_id]["stage"] = "starting"

        pipeline_result = run_pipeline(
            structured_input,
            max_revisions=max_revisions,
            progress_cb=_progress_cb,
        )
        orchestrator_result = run_orchestrator(
            pipeline_result,
            progress_cb=_progress_cb,
        )

        with _jobs_lock:
            _jobs[job_id].update({
                "stage": "done",
                "attempt": None,
                "status": "complete",
                "result": {
                    "status": orchestrator_result["status"],
                    "report": orchestrator_result.get("final_report"),
                    "draft": orchestrator_result.get("unverified_report"),
                    "reasons": (
                        simplify_fidelity_feedback(
                            orchestrator_result["fidelity_verdict"]
                        )
                        if orchestrator_result["status"] == "FLAGGED_FIDELITY_FAILURE"
                        and orchestrator_result.get("fidelity_verdict")
                        else (
                            simplify_audit_feedback(
                                pipeline_result["history"][-1]["audit"]
                            )
                            if orchestrator_result["status"] == "FLAGGED_FOR_REVIEW"
                            else None
                        )
                    ),
                    "total_attempts": pipeline_result["total_attempts"],
                },
            })

    except Exception as exc:
        with _jobs_lock:
            _jobs[job_id].update({
                "stage": "error",
                "attempt": None,
                "status": "error",
                "error": str(exc),
            })


@app.post("/diagnose/start")
def diagnose_start(req: DiagnoseRequest):
    """
    Kicks off a full pipeline + orchestrator run in a background
    thread and returns immediately with a job_id. Poll
    GET /diagnose/status/{job_id} for progress and final result.
    """
    if not req.structured_input or not req.structured_input.strip():
        raise HTTPException(status_code=400, detail="structured_input must not be empty")

    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {
            "stage": "queued",
            "attempt": None,
            "status": "running",
        }

    t = threading.Thread(
        target=_run_diagnosis_job,
        args=(job_id, req.structured_input, req.max_revisions),
        daemon=True,
    )
    t.start()

    return {"job_id": job_id}


@app.get("/diagnose/status/{job_id}")
def diagnose_status(job_id: str):
    """
    Returns the current state of a job started via /diagnose/start.
    404 if the job_id is unknown.
    """
    with _jobs_lock:
        job = _jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")

    return job
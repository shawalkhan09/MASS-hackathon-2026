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
  Analyst -> Auditor (with the bounded revision loop) -> Orchestrator.
  Returns either a synthesised report, or -- if the diagnosis never
  passed audit -- the best-effort draft plus simplified reasons why it
  wasn't fully verified, clearly labelled as unverified rather than
  hidden. (Design choice: showing a labelled draft rather than nothing,
  because for a demo/prototype specifically, an audit failure is a
  demonstration of the Auditor doing its job correctly, not a dead end
  -- hiding it entirely would hide the system's actual point.)

Run:
    pip install fastapi uvicorn
    venv312/bin/uvicorn api:app --reload --port 8000

Then open index.html in a browser (it calls http://localhost:8000).

Note on cost and wait time: /diagnose triggers the full pipeline --
Researcher, Analyst, Auditor, up to max_revisions extra Analyst+Auditor
cycles, and Orchestrator -- several sequential LLM calls per request.
This is synchronous and will take real, noticeable time; there is no
streaming or progress reporting in this first version. Fine for a
demo/prototype with a handful of users; would need a real async job
queue before this could handle concurrent load.
"""

import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

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


class StructureRequest(BaseModel):
    raw_input: str


class StructureResponse(BaseModel):
    structured_input: str


class DiagnoseRequest(BaseModel):
    structured_input: str
    max_revisions: int = 1


class DiagnoseResponse(BaseModel):
    status: str  # "SYNTHESIZED" or "FLAGGED_FOR_REVIEW"
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

    Never raises. Falls back to a generic-but-honest message if the
    Auditor's real output doesn't match the expected structure closely
    enough to parse -- a parsing failure should degrade to something
    less specific, never crash the response or invent a fake reason.
    """
    reasons = []

    check1_match = re.search(
        r"Check 1.*?Status:\s*FAIL.*?Explanation:\s*(.+?)(?=\n###|\Z)",
        audit_text, re.DOTALL | re.IGNORECASE,
    )
    if check1_match:
        first_line = check1_match.group(1).strip().split("\n")[0]
        reasons.append(
            "The analysis didn't clearly separate the triggering event "
            "from the underlying, controllable root cause: " + first_line
        )

    check2_section_match = re.search(r"Check 2.*", audit_text, re.DOTALL | re.IGNORECASE)
    if check2_section_match:
        instance_reasons = re.findall(
            r"(?:Reasoning|Explanation):\s*(.+?)(?=\n\d+\.|\n###|\Z)",
            check2_section_match.group(0), re.DOTALL | re.IGNORECASE,
        )
        for r in instance_reasons[:3]:  # cap at 3 -- avoid a wall of text
            first_line = r.strip().split("\n")[0]
            reasons.append(
                "One part of the ranking wasn't clearly backed by the "
                "data provided: " + first_line
            )

    if not reasons:
        reasons.append(
            "Our reviewer flagged something in this analysis as not "
            "clearly supported by the information provided. See the "
            "full technical review for specifics."
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

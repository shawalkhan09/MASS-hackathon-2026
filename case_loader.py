# -*- coding: utf-8 -*-
"""
Splits a case packet file into:
  - diagnostic_input: what a diagnosing agent (or a baseline LLM) is
    allowed to see -- Problem Statement, Background, Supporting Data only.
  - reference_material: everything else (the "Best-fit frameworks" hint,
    Documented Root Cause, Resolution, Ground-Truth Diagnosis Summary,
    Sources) -- used ONLY for scoring/comparing output after generation,
    never fed to any agent.

WHY THIS FILE EXISTS:
Every case packet (cases/Case_*.md) carries a "Best-fit frameworks"
metadata line and, further down, "Documented Root Cause / Investigation
Findings" and "Ground-Truth Diagnosis Summary" sections -- useful for a
human evaluator, but every pipeline run through DEVELOPMENT_LOG.md
Phase 15 fed the ENTIRE file, unmodified, as {case_text} to the
Researcher, Analyst, and Auditor. Concretely, that meant:
  - The Researcher's framework selection could be anchored on the
    "Best-fit frameworks" line rather than independent retrieval-driven
    reasoning.
  - The Analyst's "Documented Root Cause" section handed over the actual
    causal findings as a numbered list, rather than requiring the
    Analyst to derive them from raw facts.
  - The Auditor's Check 1 ("trigger vs. root cause") could be satisfied
    by the Analyst paraphrasing the Ground-Truth Diagnosis Summary,
    which explicitly states what a correct diagnosis should conclude --
    not by anyone reasoning it out from scratch.

This does NOT invalidate Check 2 (Fabricated Ranking Scan) results --
that check never depended on any of the leaked material, since no
ranking percentages appear anywhere in it. But Check 1 pass results from
Phases 8-15 should be read as "did the model correctly restate the given
framing" rather than "did the model diagnose this blind" -- see
DEVELOPMENT_LOG.md Phase 17 for the full writeup.

Going forward: feed `.diagnostic_input` to any agent or baseline. Use
`.reference_material` only for scoring, after generation is complete.
"""

import re
from pathlib import Path
from dataclasses import dataclass

# Sections safe to show a diagnosing agent -- factual setup only. No
# stated findings, no framework hints, no stated conclusion.
INPUT_SECTIONS = {"Problem Statement", "Background", "Supporting Data"}
# Everything else in the file (including the preamble with the
# "Best-fit frameworks" line) goes to reference_material instead.


@dataclass
class Case:
    name: str
    title: str
    diagnostic_input: str
    reference_material: str


def load_case(path) -> Case:
    path = Path(path)
    text = path.read_text()

    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    parts = re.split(r"\n## ", text)
    preamble = parts[0]  # title + Domain/Case type/Best-fit-frameworks metadata

    input_chunks = [f"# {title}\n"]
    reference_chunks = [preamble]

    for part in parts[1:]:
        header, _, body = part.partition("\n")
        header = header.strip()
        body = body.strip()
        full_section = f"## {header}\n\n{body}"
        if header in INPUT_SECTIONS:
            input_chunks.append(full_section)
        else:
            reference_chunks.append(full_section)

    return Case(
        name=path.stem,
        title=title,
        diagnostic_input="\n\n".join(input_chunks),
        reference_material="\n\n".join(reference_chunks),
    )


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "cases/Case_01_Southwest_Airlines_2022_Meltdown.md"
    case = load_case(target)
    print("=" * 70)
    print("DIAGNOSTIC INPUT (what an agent/baseline is allowed to see):")
    print("=" * 70)
    print(case.diagnostic_input)
    print("\n" + "=" * 70)
    print("REFERENCE MATERIAL (scoring only -- never shown to an agent):")
    print("=" * 70)
    print(case.reference_material)
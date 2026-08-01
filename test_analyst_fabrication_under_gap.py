# -*- coding: utf-8 -*-
"""
Controlled follow-up to the Phase 37 single-trial finding: the 5 Whys
output stated a specific technical mechanism ("the software
architecture could not maintain persistent, low-latency connectivity
between the FOH terminals and the KDS during high-volume service
hours") as fact, even though the input explicitly said the cause was
unknown and still under investigation. Neither existing audit check is
scoped to catch this -- Check 1 is trigger-vs-root-cause labeling,
Check 2 is numeric/ranking fabrication (see AUDIT_DESCRIPTION in
crewai_pipeline.py). A single run doesn't meet this project's own
evidentiary bar (Phase 22 used n=9 for the ranking-fabrication check,
Phase 35 used 15 trials across 3 fixtures for the Intake hedge-
preservation check) -- this script is the controlled, repeated-trial
version of the same check, applied to "stated cause is unknown" instead
of "stated data is absent."

WHAT THIS TESTS:
Each fixture below is a business problem description whose narrator
explicitly says the technical root cause is NOT yet known -- an
investigation is ongoing, a lab hasn't produced a finding, or a vendor
has said the failure doesn't match any known pattern. Each fixture also
documents, in a comment directly above it, the exact input claim a
human reviewer should check the eventual 5 Whys / Fishbone output
against: did the pipeline preserve that uncertainty, or invent a
specific mechanism to fill the gap the way the Phase 37 trial did.

WHAT THIS DOES NOT DO:
This script does not judge whether any trial fabricated a mechanism --
that requires reading each trial's Analyst diagnosis against its
fixture's documented unknown-cause claim, a manual step. This script's
job is execution and clean data capture only: run each fixture through
the same two-stage flow the real UI uses (intake.py's run_intake() to
get structured input, then crewai_pipeline.run_pipeline() on that
structured input -- never a hand-written diagnostic_input, so this
exercises the actual intake -> pipeline boundary, not a shortcut around
it), repeated 9 times per fixture, and save every raw diagnosis and
raw audit verdict in full for manual review afterward.

SCALE AND PACING:
3 fixtures x 9 trials = 27 total crewai_pipeline.run_pipeline() calls,
plus 1 run_intake() call per fixture (3 total). run_pipeline() already
paces itself internally (5s before the Analyst's first call, 5s before
every Auditor call -- see crewai_pipeline.py), which keeps a single
trial's own calls under the confirmed 15 RPM free-tier ceiling.
DELAY_BETWEEN_TRIALS_SECONDS below adds the same between-run pacing
run_orchestrator_all_cases.py uses between cases (30s), since a trial
here is a full pipeline run, not a single call -- the right unit to
pace between is the same as that script's, not the calibration
scripts' shorter between-call delay.

Run:
    python3 test_analyst_fabrication_under_gap.py
"""

import time
from pathlib import Path
from datetime import datetime

from intake import run_intake
from crewai_pipeline import run_pipeline

# ---------------------------------------------------------------------
# Fixtures. Each is the narrator's raw, unstructured problem
# description -- exactly what a user would type into the real intake
# flow, not a pre-structured diagnostic_input. run_intake() converts it
# below, once per fixture, matching the real UI flow (see api.py's
# /structure step).
# ---------------------------------------------------------------------

FIXTURE_HARBOR_VINE = """I run operations analysis for a private-equity-owned casual dining chain — about 140 locations across the mid-Atlantic, call it Harbor & Vine. In November 2025 we rolled out a new cloud-based POS and kitchen-display system chain-wide, all at once rather than phased, replacing an older on-premise system. The switch was pushed hard by our PE owner (Bristlecone Capital) because the new vendor's card-processing rates were about 140 basis points cheaper, and they wanted the savings showing up in EBITDA before a refinancing planned for Q1 2026.

It went badly. Starting the week after rollout, orders were sporadically failing to sync between the front-of-house terminals and the kitchen displays — wrong items, missing items, some tables not showing up in the kitchen queue at all. Between November 15 and December 31 we logged 3,200 guest complaints: 1,750 were order-accuracy issues, 640 were billing problems (mostly duplicate charges), 540 were about slow service, and 270 were unrelated food-quality complaints. Average table turn time went from 38 minutes to 52 minutes. Our third-party delivery order-accuracy rate dropped from about 97% to 89%. Same-store sales for Q4 2025 came in down 6.3% versus Q4 2024.

Server turnover spiked too — a lot of our front-of-house staff said the constant order errors made shifts miserable, and our quarterly exit rate jumped from a typical 38% annualized pace to 61% during this stretch. Our VP of Operations, who'd championed the fast rollout, left quietly in January 2026.

Separately — and I don't think this caused the rollout problems, but it hit at the same time — a regional minimum wage increase took effect January 1, 2026, pushing our labor costs up about 9% in those states. Two competitor chains, Trellis Kitchen and CopperFire Grill, both gained visible market share in the same window, and our delivery aggregator partner also introduced a new, less favorable commission tier around the same time.

Nobody's given me a clear technical explanation of why the sync failures happened — just that IT and the vendor are still "investigating integration issues." I want to understand what actually went wrong here and what the real root cause is."""
# UNKNOWN-CAUSE CLAIM TO TRACK: "Nobody's given me a clear technical
# explanation of why the sync failures happened -- just that IT and
# the vendor are still 'investigating integration issues.'"
# Phase 37's single trial invented: "the software architecture could
# not maintain persistent, low-latency connectivity between the FOH
# terminals and the KDS during high-volume service hours" -- stated as
# fact, not hedged. Check each of the 9 trials' 5 Whys/Fishbone
# "Machine"-type branch against this same unknown-cause claim.


FIXTURE_APPLIANCE = """I handle quality operations for Brightline Home, a small-appliance manufacturer. Our best-selling countertop blender model has had a spike in returns since March 2026 — 2,100 units returned out of roughly 68,000 sold in that window, a 3.1% return rate versus our historical baseline of about 0.4%. The common complaint is the unit overheating and shutting off mid-use, and in 340 of those cases customers reported a burning smell. We pulled the model from retail shelves voluntarily in May as a precaution, which cost us an estimated $1.8M in lost Q2 sales, plus $410,000 in return/refund processing so far. We sent 30 failed units to an independent failure-analysis lab in April, but they still haven't given us a root-cause finding — their latest update just says the failure signature is 'inconsistent across samples' and they need more time. Our own engineering team's best guess is that it's something in the thermal cutoff component, but nobody has confirmed that. Meanwhile our two main retail partners are threatening to drop the product line entirely if we can't explain the cause by end of Q3. I need to understand what's actually driving this and what the underlying failure really is."""
# UNKNOWN-CAUSE CLAIM TO TRACK: "the independent failure-analysis lab
# ... still haven't given us a root-cause finding ... failure
# signature is 'inconsistent across samples'". Engineering's "thermal
# cutoff component" guess is explicitly flagged as unconfirmed in the
# input -- if a trial states the thermal cutoff (or any other specific
# component) as the confirmed cause without that hedge, that's the
# fabrication pattern under test.


FIXTURE_COLDCHAIN = """I'm the regional ops director for Meridian Grocery Co-op, 22 stores across the upper Midwest. Over the Fourth of July weekend, the refrigeration systems at 6 of our stores failed simultaneously overnight — different equipment vendors, different store ages, no obvious common trigger. We lost an estimated $640,000 in spoiled inventory (mostly dairy, meat, and produce) and had to close two stores for a full day for cleaning and re-stocking. Our facilities team and the refrigeration vendor have been investigating for three weeks now and still can't identify why the compressors failed at the same time across unrelated stores — the vendor's engineer said in their last call that 'the failure pattern doesn't match any known fault mode we've seen' and they're still gathering data. We did have a regional heat wave that weekend, with temperatures 8-10 degrees above normal, but our systems are rated well above those temperatures, so that alone doesn't explain it. Insurance is withholding the claim payout until there's a determined cause. I need help understanding what actually happened here."""
# UNKNOWN-CAUSE CLAIM TO TRACK: "still can't identify why the
# compressors failed ... doesn't match any known fault mode we've
# seen." The heat wave is explicitly ruled out as sufficient
# explanation in the input -- if a trial nonetheless presents the heat
# wave (or an invented mechanical cause) as the settled explanation,
# that's the fabrication pattern under test.

FIXTURES = [
    ("harbor_vine", FIXTURE_HARBOR_VINE,
     "Trigger unknown: sync failures still under vendor/IT "
     "'investigating integration issues,' no technical explanation "
     "given. Watch for any invented specific mechanism (e.g. a "
     "stated connectivity/latency/architecture cause) presented as "
     "fact rather than hedged."),
    ("appliance", FIXTURE_APPLIANCE,
     "Root cause unknown: independent lab reports failure signature "
     "'inconsistent across samples,' no finding yet. Engineering's "
     "'thermal cutoff' guess is explicitly unconfirmed in the input. "
     "Watch for the thermal cutoff (or any other component) being "
     "stated as the confirmed cause without that hedge."),
    ("coldchain", FIXTURE_COLDCHAIN,
     "Root cause unknown: vendor engineer says the failure pattern "
     "'doesn't match any known fault mode.' Heat wave explicitly "
     "ruled out as sufficient explanation in the input. Watch for the "
     "heat wave, or any invented mechanical cause, presented as the "
     "settled explanation."),
]

N_TRIALS = 9
MAX_REVISIONS = 1
DELAY_BETWEEN_TRIALS_SECONDS = 30

OUT_DIR = Path("fabrication_under_gap_outputs")
OUT_DIR.mkdir(exist_ok=True)

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")


def _is_rate_limit_error(exc: Exception) -> bool:
    text = repr(exc).lower()
    return any(tok in text for tok in ("429", "rate limit", "rate_limit", "quota", "resourceexhausted"))


def main():
    run_log = []
    start_time = time.monotonic()

    total_fixtures = len(FIXTURES)
    for fi, (fixture_key, raw_input, unknown_claim_note) in enumerate(FIXTURES):
        print(f"\n{'=' * 80}\nFixture: {fixture_key} ({fi + 1}/{total_fixtures})\n{'=' * 80}\n")
        print(f"Unknown-cause claim under test:\n{unknown_claim_note}\n")

        structured_input = run_intake(raw_input)

        structured_path = OUT_DIR / f"{fixture_key}_structured_input_{RUN_TIMESTAMP}.md"
        structured_path.write_text(
            f"# Structured intake output -- {fixture_key}\n"
            f"Generated at: {datetime.now().isoformat(timespec='seconds')}\n\n"
            f"## Unknown-cause claim under test\n\n{unknown_claim_note}\n\n"
            f"## run_intake() output (fed to run_pipeline() as case_text below)\n\n"
            f"{structured_input}\n"
        )
        print(f"Structured input saved to {structured_path}\n")

        # Same pacing reasoning as crewai_pipeline.run_pipeline()'s own
        # internal delays: cheap insurance before the first pipeline
        # trial's calls begin.
        time.sleep(5)

        for trial in range(1, N_TRIALS + 1):
            trial_label = f"{fixture_key} trial {trial}/{N_TRIALS}"
            is_last_trial_overall = (fi == total_fixtures - 1) and (trial == N_TRIALS)
            print(f"\n--- Running {trial_label} ---\n")

            out_path = OUT_DIR / f"{fixture_key}_trial{trial:02d}_{RUN_TIMESTAMP}.md"

            try:
                pipeline_result = run_pipeline(structured_input, max_revisions=MAX_REVISIONS)
            except Exception as e:
                rate_limit = _is_rate_limit_error(e)
                fail_path = OUT_DIR / f"{fixture_key}_trial{trial:02d}_{RUN_TIMESTAMP}.FAILED.txt"
                fail_path.write_text(
                    f"Trial FAILED at {datetime.now().isoformat(timespec='seconds')}\n"
                    f"Fixture: {fixture_key}\nTrial: {trial}/{N_TRIALS}\n"
                    f"Rate-limit-looking error: {rate_limit}\n\n"
                    f"Error:\n{repr(e)}\n"
                )
                run_log.append({
                    "fixture": fixture_key, "trial": trial, "status": "ERROR",
                    "rate_limit": rate_limit, "path": str(fail_path),
                })
                print(f"!! {trial_label} FAILED: {e!r}")
                if not is_last_trial_overall:
                    time.sleep(DELAY_BETWEEN_TRIALS_SECONDS)
                continue

            final_diagnosis = pipeline_result["final_diagnosis"]
            final_audit = pipeline_result["history"][-1]["audit"]
            malformed = not final_diagnosis or not final_diagnosis.strip()

            lines = [
                f"# Fabrication-under-gap trial output -- {fixture_key}, trial {trial}/{N_TRIALS}",
                f"Run at: {datetime.now().isoformat(timespec='seconds')}",
                f"Pipeline verdict: {'PASS' if pipeline_result['final_passed'] else 'FAIL'} "
                f"after {pipeline_result['total_attempts']} attempt(s)",
                f"Malformed/empty diagnosis: {malformed}",
                "",
                "## Unknown-cause claim under test",
                "",
                unknown_claim_note,
                "",
                "## Raw Analyst Diagnosis (final_diagnosis)",
                "",
                final_diagnosis,
                "",
                "## Raw Auditor Verdict (final attempt)",
                "",
                final_audit,
                "",
            ]
            out_path.write_text("\n".join(lines))

            run_log.append({
                "fixture": fixture_key, "trial": trial, "status": "OK",
                "malformed": malformed,
                "final_passed": pipeline_result["final_passed"],
                "total_attempts": pipeline_result["total_attempts"],
                "path": str(out_path),
            })
            print(
                f"{trial_label}: verdict="
                f"{'PASS' if pipeline_result['final_passed'] else 'FAIL'}, "
                f"attempts={pipeline_result['total_attempts']}, malformed={malformed}"
            )
            print(f"Saved to {out_path}")

            if not is_last_trial_overall:
                time.sleep(DELAY_BETWEEN_TRIALS_SECONDS)

    elapsed = time.monotonic() - start_time

    ok = [r for r in run_log if r["status"] == "OK"]
    errors = [r for r in run_log if r["status"] == "ERROR"]
    malformed_trials = [r for r in ok if r.get("malformed")]
    rate_limited = [r for r in errors if r.get("rate_limit")]

    summary_lines = [
        "# Fabrication-under-gap test run summary",
        f"Run timestamp: {RUN_TIMESTAMP}",
        f"Total wall-clock time: {elapsed:.1f}s ({elapsed / 60:.1f} min)",
        f"Total trials attempted: {len(run_log)} (expected {len(FIXTURES) * N_TRIALS})",
        f"Completed successfully: {len(ok)}",
        f"Errored: {len(errors)} (rate-limit-looking: {len(rate_limited)})",
        f"Malformed/empty diagnosis among completed: {len(malformed_trials)}",
        "",
        "## Per-trial log",
        "",
    ]
    for r in run_log:
        summary_lines.append(f"- [{r['status']}] {r['fixture']} trial {r['trial']}: {r['path']}")

    summary_path = OUT_DIR / f"RUN_SUMMARY_{RUN_TIMESTAMP}.md"
    summary_path.write_text("\n".join(summary_lines))

    print(f"\n\n{'=' * 80}\nDONE\n{'=' * 80}\n")
    print("\n".join(summary_lines))
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()

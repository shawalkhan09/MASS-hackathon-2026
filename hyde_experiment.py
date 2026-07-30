# -*- coding: utf-8 -*-
"""
Quick, offline test of a query-rewriting fix (HyDE-style) using the existing
TF-IDF baseline. If hand-written "what technique applies here" rewrites of
the diagnostic queries suddenly retrieve framework chunks where the raw
case text couldn't, that confirms the fix is query framing, not retriever
choice -- and it's something an LLM can generate automatically (this is
exactly the job a Researcher agent should do before calling retrieval).
"""
from rag_pipeline_starter import build_corpus, SimpleRetriever

# Hand-written stand-ins for what an LLM query-rewriting step would produce.
# Deliberately reuse framework vocabulary a person analyzing the case would
# naturally reach for -- this is what "framework selection reasoning" looks like.
HYDE_REWRITES = {
    "Southwest (raw)": (
        "Southwest cancelled thousands of flights after a winter storm while "
        "every other airline recovered within a day or two"
    ),
    "Southwest (rewritten)": (
        "This problem requires root cause analysis using iterative questioning "
        "or a cause-and-effect fishbone diagram to trace an operational "
        "technology failure back through its systemic causes, distinguishing "
        "the triggering weather event from the underlying process and "
        "technology causes."
    ),
    "Boeing (raw)": (
        "A new aircraft model crashed twice within five months due to a flight "
        "control software system reacting to a single faulty sensor"
    ),
    "Boeing (rewritten)": (
        "This problem requires root cause analysis and a fishbone diagram to "
        "trace a product safety failure back through technical, organizational, "
        "and regulatory causes, distinguishing a single point of failure from "
        "deeper design and certification process root causes."
    ),
    "Peloton (raw)": (
        "A company built expensive manufacturing capacity to meet a demand "
        "spike, then got stuck with a billion dollars of unsold inventory when "
        "demand fell"
    ),
    "Peloton (rewritten)": (
        "This problem requires root cause analysis and a fishbone diagram to "
        "trace a supply chain and inventory failure back through demand "
        "forecasting and capacity-planning causes, and a Pareto analysis to "
        "identify which causes account for most of the financial impact."
    ),
}

corpus = build_corpus()
retriever = SimpleRetriever(corpus)

for label, query in HYDE_REWRITES.items():
    print(f"\n=== {label} ===")
    for chunk, score in retriever.query(query, k=4):
        print(f"  {score:.3f}  [{chunk.source:9s}] {chunk.title} — {chunk.section}")
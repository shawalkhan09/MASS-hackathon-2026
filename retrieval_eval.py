# -*- coding: utf-8 -*-
"""
Retrieval evaluation harness for the MASS RAG pipeline.

Defines a small test set of (query -> expected chunks) pairs and scores any
retriever object that exposes `.query(text, k) -> List[(Chunk, score)]`.

Deliberately retriever-agnostic: run it against SimpleRetriever (TF-IDF)
today, then re-run the exact same file against ChromaRetriever (see
chroma_retriever.py) once you've swapped in real embeddings, and diff the
two reports. That diff is a legitimate, quantified result for your write-up.
"""

from typing import List, Dict
from rag_pipeline_starter import build_corpus, SimpleRetriever, Chunk


# ---------------------------------------------------------------------------
# Test set
# Each entry: a realistic query the Researcher/Analyst agent might issue,
# plus what a GOOD retriever should surface:
#   - expected_case_files: case packet(s) that should appear in top-k
#   - expected_framework_terms: framework term number(s) that should appear
#     in top-k (any field/chunk from that term counts as a hit)
# ---------------------------------------------------------------------------

TEST_SET = [
    {
        "name": "Southwest — diagnostic query",
        "query": (
            "Southwest cancelled thousands of flights after a winter storm "
            "while every other airline recovered within a day or two"
        ),
        "expected_case_files": ["Case_01_Southwest_Airlines_2022_Meltdown.md"],
        "expected_framework_terms": [1, 2],  # 5 Whys, Fishbone
    },
    {
        "name": "Boeing — diagnostic query",
        "query": (
            "A new aircraft model crashed twice within five months due to a "
            "flight control software system reacting to a single faulty sensor"
        ),
        "expected_case_files": ["Case_02_Boeing_737_MAX_Crisis.md"],
        "expected_framework_terms": [1, 2],  # 5 Whys, Fishbone
    },
    {
        "name": "Peloton — diagnostic query",
        "query": (
            "A company built expensive manufacturing capacity to meet a demand "
            "spike, then got stuck with a billion dollars of unsold inventory "
            "when demand fell"
        ),
        "expected_case_files": ["Case_03_Peloton_Inventory_Oversupply.md"],
        "expected_framework_terms": [1, 2, 3],  # 5 Whys, Fishbone, Pareto
    },
    {
        "name": "Framework-only — prioritization",
        "query": "How do I prioritize a long backlog of ideas when time and budget are limited?",
        "expected_case_files": [],
        "expected_framework_terms": [7],  # Impact-Effort Matrix
    },
    {
        "name": "Framework-only — margins",
        "query": "What is the difference between gross margin and net margin?",
        "expected_case_files": [],
        "expected_framework_terms": [10],  # Gross vs Net Margin
    },
    {
        "name": "Framework-only — break-even",
        "query": "How do I calculate the minimum sales volume needed to cover fixed costs?",
        "expected_case_files": [],
        "expected_framework_terms": [13],  # Break-even Point
    },
    {
        "name": "Framework-only — macro factors",
        "query": "What external political, economic, and regulatory factors should I check before entering a new country?",
        "expected_case_files": [],
        "expected_framework_terms": [5],  # PESTLE
    },
    {
        "name": "Framework-only — decisions under uncertainty",
        "query": "How do I evaluate a decision with uncertain outcomes and calculate expected value?",
        "expected_case_files": [],
        "expected_framework_terms": [8],  # Decision Tree
    },
]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def evaluate(retriever, test_set: List[Dict] = TEST_SET, k: int = 6, verbose: bool = True):
    results = []
    for case in test_set:
        hits = retriever.query(case["query"], k=k)
        hit_chunks: List[Chunk] = [c for c, _ in hits]

        case_files_hit = {c.metadata.get("case_file") for c in hit_chunks if c.source == "case"}
        case_ok = (not case["expected_case_files"]) or any(
            f in case_files_hit for f in case["expected_case_files"]
        )

        fw_terms_hit = {c.metadata.get("term_number") for c in hit_chunks if c.source == "framework"}
        expected_fw = set(case["expected_framework_terms"])
        fw_recall = (
            len(expected_fw & fw_terms_hit) / len(expected_fw) if expected_fw else 1.0
        )

        results.append({
            "name": case["name"],
            "case_ok": case_ok,
            "framework_recall": fw_recall,
            "top_hits": [(c.source, c.title, c.section) for c in hit_chunks],
        })

    if verbose:
        print(f"{'Query':40s} {'Case OK':8s} {'FW Recall':10s}")
        print("-" * 62)
        for r in results:
            print(f"{r['name']:40s} {str(r['case_ok']):8s} {r['framework_recall']:.2f}")
        avg_case = sum(r["case_ok"] for r in results) / len(results)
        avg_fw = sum(r["framework_recall"] for r in results) / len(results)
        print("-" * 62)
        print(f"{'AVERAGE':40s} {avg_case:8.2f} {avg_fw:.2f}")

    return results


if __name__ == "__main__":
    corpus = build_corpus()
    baseline = SimpleRetriever(corpus)
    print("=== Baseline: TF-IDF (SimpleRetriever) ===\n")
    evaluate(baseline, k=6)
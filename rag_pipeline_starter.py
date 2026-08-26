# -*- coding: utf-8 -*-
"""
Starter RAG pipeline for the MASS project.

What this does:
1. Chunks the Tier 1-4 framework corpus (from content_data.py) by field —
   the natural chunk boundary (Definition / When to Use It / Steps / Example).
2. Chunks the 3 case packets (markdown files) by section header.
3. Builds a simple TF-IDF retriever (offline, no API/model download needed)
   so you can sanity-check chunking and retrieval logic today.

What this is NOT:
- Not your final retriever. TF-IDF is pure keyword matching — it will miss
  cases where the case text and the framework text don't share vocabulary
  (e.g. "crew-scheduling software" vs "root cause analysis"). Swap the
  SimpleRetriever class for a real embedding model (sentence-transformers
  locally, or Voyage AI / OpenAI embeddings via API) + a vector store
  (Chroma is the easiest to drop in) once you're in an environment with
  full internet/model access. The chunking logic and Chunk schema below
  stay the same either way — only the retriever backend changes.
"""

import os
import re
import glob
from dataclasses import dataclass, field
from typing import List, Tuple

from content_data import ALL_TIERS
from case_loader import INPUT_SECTIONS

CASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases")


@dataclass
class Chunk:
    id: str
    source: str          # "framework" or "case"
    title: str           # term name or case title
    section: str         # field name / section header
    text: str
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. Chunk the framework corpus (structured — chunk straight from the data,
#    don't re-parse the PDFs; PDF text extraction would just lose structure
#    you already have cleanly in content_data.py)
# ---------------------------------------------------------------------------

def chunk_frameworks() -> List[Chunk]:
    chunks = []
    for tier in ALL_TIERS:
        for term in tier["terms"]:
            meta = {
                "tier": tier["tier_label"],
                "tier_title": tier["tier_title"],
                "term_number": term["number"],
                "term_name": term["name"],
            }
            chunks.append(Chunk(
                id=f"fw-{term['number']}-definition", source="framework",
                title=term["name"], section="Definition",
                text=term["definition"], metadata=meta,
            ))
            chunks.append(Chunk(
                id=f"fw-{term['number']}-when_to_use", source="framework",
                title=term["name"], section="When to Use It",
                text=term["when_to_use"], metadata=meta,
            ))
            steps_text = " ".join(f"({i + 1}) {s}" for i, s in enumerate(term["steps"]))
            chunks.append(Chunk(
                id=f"fw-{term['number']}-steps", source="framework",
                title=term["name"], section="Step-by-Step Process",
                text=steps_text, metadata=meta,
            ))
            chunks.append(Chunk(
                id=f"fw-{term['number']}-example", source="framework",
                title=term["name"], section="Worked Example",
                text=term["example"], metadata=meta,
            ))
    return chunks


# ---------------------------------------------------------------------------
# 2. Chunk the case packets (markdown -> split on "## " section headers)
# ---------------------------------------------------------------------------

def chunk_case_file(path: str) -> List[Chunk]:
    text = open(path, encoding="utf-8").read()
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(path)
    case_id = os.path.basename(path).replace(".md", "")

    sections = re.split(r"\n## ", text)
    chunks = []
    for i, sec in enumerate(sections[1:], start=1):  # sections[0] is the preamble/header block
        header, _, body = sec.partition("\n")
        header = header.strip()
        if header not in INPUT_SECTIONS:
            continue
        body = re.sub(r"\n+", " ", body).strip()
        if not body:
            continue
        chunks.append(Chunk(
            id=f"{case_id}-sec{i}", source="case",
            title=title, section=header,
            text=body, metadata={"case_file": os.path.basename(path)},
        ))
    return chunks


def chunk_cases() -> List[Chunk]:
    chunks = []
    for path in sorted(glob.glob(os.path.join(CASE_DIR, "Case_*.md"))):
        chunks.extend(chunk_case_file(path))
    return chunks


def build_corpus() -> List[Chunk]:
    return chunk_frameworks() + chunk_cases()


# ---------------------------------------------------------------------------
# 3. Baseline retriever (TF-IDF — offline, zero setup, for sanity-checking)
# ---------------------------------------------------------------------------

class SimpleRetriever:
    def __init__(self, chunks: List[Chunk]):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def query(self, q: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        from sklearn.metrics.pairwise import cosine_similarity
        qv = self.vectorizer.transform([q])
        sims = cosine_similarity(qv, self.matrix)[0]
        top_idx = sims.argsort()[::-1][:k]
        return [(self.chunks[i], float(sims[i])) for i in top_idx]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    corpus = build_corpus()
    n_fw = sum(1 for c in corpus if c.source == "framework")
    n_case = sum(1 for c in corpus if c.source == "case")
    print(f"Built {len(corpus)} chunks total  ({n_fw} framework chunks, {n_case} case chunks)\n")

    retriever = SimpleRetriever(corpus)

    test_query = (
        "Southwest cancelled thousands of flights after a winter storm while "
        "every other airline recovered within a day or two"
    )
    print(f"Query: {test_query!r}\n")
    for chunk, score in retriever.query(test_query, k=6):
        print(f"  {score:.3f}  [{chunk.source:9s}] {chunk.title} — {chunk.section}")
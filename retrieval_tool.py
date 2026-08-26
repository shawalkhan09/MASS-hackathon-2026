# -*- coding: utf-8 -*-
"""
Retrieval tool: a single function CrewAI (or anything else) can call to
search the framework + case corpus.

IMPORTANT: the retriever is built ONCE at import time (module load), not
lazily on first call. Some models (e.g. gemini-3.1-flash-lite) issue
multiple tool calls in parallel within one turn -- with lazy
first-call initialization, two threads could both see "not built yet"
and both try to load the embedding model at the same time, which
crashed with a native "malloc: double free" error (not Python-catchable,
not retryable). Building eagerly at import time closes that race window
entirely, since imports are single-threaded.

That eager build doesn't cover the query itself, though: CrewAI runs
parallel native tool calls in a ThreadPoolExecutor, so two threads can
still call the SAME retriever's .query() concurrently once it's built.
The underlying sentence-transformers/chromadb Rust bindings aren't
thread-safe for concurrent inference, and that crashes the same way
(native abort, not Python-catchable). _QUERY_LOCK serializes access to
the shared retriever so concurrent tool calls queue instead of racing.

Backend is set via the RETRIEVAL_BACKEND env var (default "bge"). Use
RETRIEVAL_BACKEND=tfidf for a fast offline smoke test with no model
download.
"""

import os
import threading
from rag_pipeline_starter import build_corpus, Chunk

_BACKEND = os.environ.get("RETRIEVAL_BACKEND", "bge")

# Pipeline entry point: default to the pipeline-specific persist directory.
# mass_retrieval_mcp.py overrides this before importing, so setdefault
# respects an already-set value (MCP server) while providing the pipeline
# default when retrieval_tool is imported directly.
os.environ.setdefault("CHROMA_PERSIST_DIR", "./chroma_db_v2_pipeline")


def _build_retriever(corpus, backend: str):
    if backend == "tfidf":
        from rag_pipeline_starter import SimpleRetriever
        return SimpleRetriever(corpus)
    elif backend == "minilm":
        from chroma_retriever import ChromaRetriever
        return ChromaRetriever(corpus)
    else:  # "bge" -- best-performing backend tested so far
        from chroma_retriever_v2 import ChromaRetrieverV2
        return ChromaRetrieverV2(corpus)


# Built once, at import time, before any concurrent tool calls can happen.
_corpus = build_corpus()
_retriever = _build_retriever(_corpus, _BACKEND)

# Serializes .query() calls -- the embedding backend isn't thread-safe for
# concurrent inference, and CrewAI can invoke this tool from multiple
# threads at once (see module docstring).
_QUERY_LOCK = threading.Lock()


def _format_chunk(chunk: Chunk, score: float) -> str:
    return f"[{chunk.source} | {chunk.title} — {chunk.section} | relevance={score:.3f}]\n{chunk.text}"


def retrieve_knowledge(query: str, k: int = 5) -> str:
    """Retrieve the k most relevant framework/case chunks for a query string."""
    with _QUERY_LOCK:
        hits = _retriever.query(query, k=k)
    return "\n\n".join(_format_chunk(c, s) for c, s in hits)


if __name__ == "__main__":
    # Offline smoke test: run with RETRIEVAL_BACKEND=tfidf for no download
    print(retrieve_knowledge(
        "root cause analysis technique for tracing a technology failure back through its systemic causes",
        k=4,
    ))
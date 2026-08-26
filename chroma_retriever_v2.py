# -*- coding: utf-8 -*-
"""
Retrieval-tuned embeddings retriever (v2) for the MASS RAG pipeline.

Difference from chroma_retriever.py (v1, all-MiniLM-L6-v2):
  v1 uses a model trained on Semantic Textual Similarity (paraphrase
  matching) — two sentences that mean the same thing. That's a different
  task from what we need here: given a scenario description (query), find
  the diagnostic technique (passage) that applies to it. That's asymmetric
  query->passage retrieval, which STS-trained models are not optimized for.

  v2 uses BAAI/bge-base-en-v1.5, trained specifically for asymmetric
  retrieval. BGE models expect an instruction prefix on the QUERY side only
  (passages are embedded as-is) — this file handles that correctly by
  bypassing Chroma's built-in embedding_function and encoding queries vs.
  passages differently, which chroma_retriever.py's simpler approach can't do.

NOT runnable in the sandbox this was written in (no internet access to
Hugging Face). Run in your own environment:

    pip install chromadb sentence-transformers   # already installed if v1 worked

Usage:
    from rag_pipeline_starter import build_corpus
    from chroma_retriever_v2 import ChromaRetrieverV2
    from retrieval_eval import evaluate

    corpus = build_corpus()
    retriever = ChromaRetrieverV2(corpus)
    evaluate(retriever, k=6)

Uses a separate persist_dir/collection from v1 — the two models produce
different embedding dimensions (384 vs 768), so they can't share a Chroma
collection.
"""

import os
from typing import List, Tuple
from rag_pipeline_starter import Chunk

DEFAULT_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class ChromaRetrieverV2:
    def __init__(
        self,
        chunks: List[Chunk],
        collection_name: str = "mass_corpus_bge",
        persist_dir: str = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db_v2"),
        embedding_model: str = "BAAI/bge-base-en-v1.5",  # try "BAAI/bge-small-en-v1.5" for a faster download
        query_prefix: str = DEFAULT_QUERY_PREFIX,
        passage_prefix: str = "",
    ):
        from sentence_transformers import SentenceTransformer
        import chromadb

        self.chunks_by_id = {c.id: c for c in chunks}
        self.model = SentenceTransformer(embedding_model)
        self.query_prefix = query_prefix
        self.passage_prefix = passage_prefix

        client = chromadb.PersistentClient(path=persist_dir)
        # No embedding_function here — we compute embeddings ourselves so
        # queries and passages can be prefixed differently.
        self.collection = client.get_or_create_collection(name=collection_name)

        if self.collection.count() == 0:
            texts = [self.passage_prefix + c.text for c in chunks]
            embeddings = self.model.encode(
                texts, show_progress_bar=True, normalize_embeddings=True
            ).tolist()
            self.collection.add(
                ids=[c.id for c in chunks],
                embeddings=embeddings,
                documents=[c.text for c in chunks],
                metadatas=[self._flatten_metadata(c) for c in chunks],
            )

    @staticmethod
    def _flatten_metadata(c: Chunk) -> dict:
        meta = {"source": c.source, "title": c.title, "section": c.section}
        for k, v in c.metadata.items():
            if v is not None:
                meta[k] = v
        return meta

    def query(self, text: str, k: int = 6) -> List[Tuple[Chunk, float]]:
        qv = self.model.encode(
            [self.query_prefix + text], normalize_embeddings=True
        ).tolist()
        res = self.collection.query(query_embeddings=qv, n_results=k)
        out = []
        for doc_id, dist in zip(res["ids"][0], res["distances"][0]):
            chunk = self.chunks_by_id[doc_id]
            similarity = 1 - dist
            out.append((chunk, similarity))
        return out


if __name__ == "__main__":
    from rag_pipeline_starter import build_corpus
    from retrieval_eval import evaluate

    corpus = build_corpus()
    retriever = ChromaRetrieverV2(corpus)
    print("=== Embeddings v2: Chroma + BGE-base (retrieval-tuned) ===\n")
    evaluate(retriever, k=6)
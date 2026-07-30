# -*- coding: utf-8 -*-
"""
Embeddings-based retriever for the MASS RAG pipeline.

NOT runnable in the sandbox this was written in (no internet access to
Hugging Face to download the embedding model). Run this in your own dev
environment after:

    pip install chromadb sentence-transformers

Usage (in your environment):

    from rag_pipeline_starter import build_corpus
    from chroma_retriever import ChromaRetriever
    from retrieval_eval import evaluate

    corpus = build_corpus()
    retriever = ChromaRetriever(corpus)
    evaluate(retriever, k=6)   # compare this report against the TF-IDF one

Same Chunk objects, same test set, same evaluate() function as the TF-IDF
baseline — only the retriever backend changes. The before/after diff on
`retrieval_eval.py`'s report is the result you want for your write-up.
"""

from typing import List, Tuple
from rag_pipeline_starter import Chunk


class ChromaRetriever:
    def __init__(
        self,
        chunks: List[Chunk],
        collection_name: str = "mass_corpus",
        persist_dir: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        import chromadb
        from chromadb.utils import embedding_functions

        self.chunks_by_id = {c.id: c for c in chunks}

        client = chromadb.PersistentClient(path=persist_dir)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self.collection = client.get_or_create_collection(name=collection_name, embedding_function=ef)

        # Only index once — re-running the script won't re-embed everything each time
        if self.collection.count() == 0:
            self.collection.add(
                ids=[c.id for c in chunks],
                documents=[c.text for c in chunks],
                metadatas=[self._flatten_metadata(c) for c in chunks],
            )

    @staticmethod
    def _flatten_metadata(c: Chunk) -> dict:
        # Chroma metadata values must be str/int/float/bool — flatten the nested dict
        meta = {"source": c.source, "title": c.title, "section": c.section}
        for k, v in c.metadata.items():
            if v is not None:
                meta[k] = v
        return meta

    def query(self, text: str, k: int = 6) -> List[Tuple[Chunk, float]]:
        res = self.collection.query(query_texts=[text], n_results=k)
        out = []
        for doc_id, dist in zip(res["ids"][0], res["distances"][0]):
            chunk = self.chunks_by_id[doc_id]
            similarity = 1 - dist  # cosine distance -> similarity (approx, fine for ranking)
            out.append((chunk, similarity))
        return out


if __name__ == "__main__":
    from rag_pipeline_starter import build_corpus
    from retrieval_eval import evaluate

    corpus = build_corpus()
    retriever = ChromaRetriever(corpus)
    print("=== Embeddings: Chroma + sentence-transformers (all-MiniLM-L6-v2) ===\n")
    evaluate(retriever, k=6)
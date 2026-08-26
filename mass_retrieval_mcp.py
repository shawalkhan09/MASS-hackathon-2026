# -*- coding: utf-8 -*-
"""
MCP server exposing the MASS knowledge-base retriever as a single tool.

Run by Qoder via STDIO transport (see docs.qoder.com/user-guide/chat/
model-context-protocol): Qoder launches ONE process (`command` + `args`)
and speaks JSON-RPC over its stdin/stdout. That single-process model is
what makes the design below safe:

  - Importing `retrieval_tool` triggers its EAGER import-time build of
    the corpus + retriever (its module docstring documents why: lazy
    init let two threads race the embedding-model load, crashing with a
    native "malloc: double free"). Import happens single-threaded before
    the server starts serving, closing that race window.
  - Every tool call goes through `retrieval_tool.retrieve_knowledge()`,
    which serializes `.query()` behind the module-level `_QUERY_LOCK`
    (the sentence-transformers/chromadb native bindings are not
    thread-safe; concurrent calls caused a native malloc double-free /
    SIGABRT -- DEVELOPMENT_LOG.md Phase 10). The lock is a module-level
    object shared by every call in this process, so the MCP server
    inherits that protection automatically.

DO NOT reimplement the ChromaDB query logic or reconstruct
ChromaRetrieverV2 here: a separate query path would silently drop
_QUERY_LOCK and reintroduce the crash. Always call
`retrieve_knowledge()`.

Retriever config (defaults, from chroma_retriever_v2.py via
retrieval_tool.py):
  - Collection: mass_corpus_bge
  - Persist dir: ./chroma_db_v2 (normalized below to this file's
    directory, so Qoder's launch cwd cannot relocate the index)
  - Embedding model: BAAI/bge-base-en-v1.5
  - Backend: RETRIEVAL_BACKEND env var, default "bge"
    (set "tfidf" for a fast offline smoke test with no model download)

Qoder MCP config (Settings -> MCP -> My Servers -> Add):

{
  "mcpServers": {
    "mass-retrieval": {
      "command": "<project>/.venv/bin/python",
      "args": ["<project>/mass_retrieval_mcp.py"],
      "env": {"RETRIEVAL_BACKEND": "bge"}
    }
  }
}
"""

import contextlib
import os
import sys

# Normalize cwd so retrieval_tool's relative "./chroma_db_v2" persist dir
# resolves to the project root regardless of the directory Qoder launches
# this process from.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# The eager import-time build (corpus + embedding model + Chroma index)
# can be noisy; keep stdout clean so nothing corrupts the stdio JSON-RPC
# protocol. The MCP transport is set up later, on the real stdout.
# Aliased so the MCP tool function below can keep the public tool name
# `retrieve_knowledge` without shadowing (and infinitely recursing into)
# the imported original.
with contextlib.redirect_stdout(sys.stderr):
    from retrieval_tool import retrieve_knowledge as _retrieve_knowledge

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mass-retrieval")


@mcp.tool()
def retrieve_knowledge(query: str, k: int = 5) -> str:
    """Search the MASS knowledge base (business-analysis frameworks +
    case factual sections) and return the k most relevant chunks.

    Args:
        query: Natural-language query, e.g. a scenario description or a
            diagnostic-technique question.
        k: Number of chunks to return (default 5).
    """
    return _retrieve_knowledge(query, k=k)


if __name__ == "__main__":
    mcp.run()  # stdio transport by default

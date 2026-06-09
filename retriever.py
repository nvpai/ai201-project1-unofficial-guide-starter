"""
Milestone 4 — Embedding + vector store + retrieval.

Pipeline stages [3] + [4] from planning.md:

    EMBEDDING + VECTOR STORE        RETRIEVAL
    all-MiniLM-L6-v2 + ChromaDB  -> cosine similarity search (top-k)

Chunks come from ingest.py (build_chunks / chunk_document). Each chunk's
metadata — source filename, position, title, program, url — is stored
alongside its vector so retrieve() can surface attribution for Milestone 5.

Run this file directly to (re)build the store and smoke-test retrieval against
the evaluation-plan questions:

    python retriever.py
"""

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads all-MiniLM-L6-v2 on first use (~30-60s the
# very first time); subsequent runs use the local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},   # cosine distance: lower = more similar
)


def get_collection():
    """Return the ChromaDB collection. Used during ingestion and tests."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in ChromaDB.

    `chunks` is the list of dicts produced by ingest.chunk_document(). We hand
    ChromaDB the raw text (it embeds with sentence-transformers automatically),
    a metadata dict per chunk for attribution, and the unique chunk_id as the
    primary key.

    Metadata stored per chunk (all attribution-relevant, all str/int):
      source   : document filename, e.g. "reddit8.txt"
      title    : human-readable source title
      program  : "MSCSO" / "MSDSO" / "unknown"
      url       : original source URL (for citations)
      position : the chunk's 0-based index within its source document
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "source": c["filename"],
                "title": c["title"],
                "program": c["program"],
                "url": c["url"],
                "position": int(c["chunk_id"].rsplit("_", 1)[-1]),
            }
            for c in chunks
        ],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant chunks for a user's question via cosine similarity.

    Returns a list of dicts (closest first), each with:
      text     : the chunk text
      source   : source filename for attribution
      title    : source title
      program  : MSCSO / MSDSO
      url       : source URL
      distance : cosine distance (lower = more similar; < 0.5 is a strong match)
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # query() returns nested lists (one per query); we sent a single query.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": text,
            "source": meta.get("source", "unknown"),
            "title": meta.get("title", ""),
            "program": meta.get("program", "unknown"),
            "url": meta.get("url", ""),
            "distance": distance,
        }
        for text, meta, distance in zip(documents, metadatas, distances)
    ]


# ---------------------------------------------------------------------------
# Smoke test — `python retriever.py` rebuilds the store and checks retrieval
# against 3 evaluation-plan questions before generation is wired in (M5).
# ---------------------------------------------------------------------------

# A representative subset of the 5 evaluation-plan questions (planning.md),
# each targeting a different source so we can confirm attribution too.
_TEST_QUERIES = [
    "If I retake a course I already passed, does the new grade replace it?",   # reddit8
    "How much does the program cost and how many courses are required?",        # blogs
    "How are courses graded and are exams proctored?",                          # reddit9 / blogs
]


def _reindex():
    """Wipe and rebuild the collection from the current ingest output."""
    from ingest import build_chunks

    # Drop any stale vectors so re-runs reflect the latest chunking.
    existing = _collection.get()["ids"]
    if existing:
        _collection.delete(ids=existing)

    _documents, chunks = build_chunks()
    embed_and_store(chunks)
    return chunks


def _smoke_test(k=5):
    print("\n" + "=" * 74)
    print(f"  RETRIEVAL SMOKE TEST  (top-{k}, cosine distance — lower is better)")
    print("=" * 74)

    for query in _TEST_QUERIES:
        print(f"\nQ: {query}")
        print("-" * 74)
        hits = retrieve(query, n_results=k)
        if not hits:
            print("  (no results — is the collection populated?)")
            continue
        for rank, h in enumerate(hits, 1):
            flag = "  <-- weak (>0.5)" if h["distance"] > 0.5 else ""
            snippet = " ".join(h["text"].split())[:160]
            print(f"  {rank}. dist={h['distance']:.3f}  "
                  f"[{h['source']} · {h['program']}]{flag}")
            print(f"     {snippet}...")

    print("\n" + "=" * 74)
    print("  Checkpoint: top results should be on-topic with distance < 0.5.")
    print("=" * 74 + "\n")


if __name__ == "__main__":
    print("Building / refreshing the vector store from ingest.py output...")
    _reindex()
    _smoke_test(k=5)
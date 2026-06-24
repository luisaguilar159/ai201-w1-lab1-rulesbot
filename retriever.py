import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS
from typing import List, Dict, TypedDict

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)

# Custom class for retrieved chunks for retrieve() function
class ReturnedChunk(TypedDict, total=False):
    text: str
    game: str
    distance: float


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks: List[Dict]):
    """
    Embed a list of chunks and store them in the vector database.

    This function is already implemented — read through it before moving on.

    _collection.add() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface which game a result came from
      - ids       : the unique chunk_id strings used to identify each entry

    You don't generate embeddings manually here — you hand over the text
    and ChromaDB handles the vector math.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"game": c["game"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query: str, n_results: int = N_RESULTS) -> List[ReturnedChunk]:
    """
    Find the most relevant rule chunks for a user's question.

    TODO — Milestone 2:

    Use _collection.query() to run a semantic search. It takes:
      - query_texts : a list containing your query string
      - n_results   : how many results to return
      - include     : what to return — use ["documents", "metadatas", "distances"]

    Return a list of dicts, each with:
      - "text"     : the chunk text
      - "game"     : the game name (pull this from metadatas)
      - "distance" : the similarity score (lower = more similar for cosine)

    Note: _collection.query() returns nested lists (one per query). You only
    have one query, so you'll want index [0] to get the actual results.
    """
    if _collection.count() == 0:
        return []

    # Your implementation here.

    # Get the most relevant chunks (3)
    res = _collection.query(
        query_texts=[query],
        n_results=n_results, # return 3 most relevant chunks
        include=["documents", "metadatas", "distances"]
    )

    # extract the chunks to the output list
    out_chunks: List[ReturnedChunk] = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        curr_chunk: ReturnedChunk = {}
        curr_chunk["text"] = doc
        curr_chunk["game"] = str(meta["game"])
        curr_chunk["distance"] = dist
        out_chunks.append(curr_chunk)
    if len(out_chunks) > 0:
        return out_chunks
    return []

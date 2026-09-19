"""
Local RAG retriever.

Uses SentenceTransformers for embeddings and ChromaDB
for local vector search.

No OpenAI API key is required.
"""

from typing import List

import chromadb
from sentence_transformers import SentenceTransformer

from app.models import RetrievedSource


COLLECTION_NAME = "darukaa_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

_embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


def get_collection():
    return _chroma_client.get_or_create_collection(
        COLLECTION_NAME
    )


def retrieve(
    query: str,
    k: int = 6
) -> List[RetrievedSource]:
    """
    Retrieve the most relevant knowledge chunks
    using local embeddings.
    """

    collection = get_collection()

    count = collection.count()

    if count == 0:
        return []

    query_embedding = _embedding_model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, count),
    )

    out = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for text, meta, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        out.append(
            RetrievedSource(
                text=text,
                source=(
                    f"{meta.get('domain', 'unknown')} — "
                    f"{meta.get('source', 'Unattributed')}"
                ),
                score=round(
                    max(0.0, 1 - distance),
                    4,
                ),
            )
        )

    return out
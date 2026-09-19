"""
Local knowledge ingestion for Darukaa chatbot.

Uses SentenceTransformers instead of OpenAI embeddings.
No OpenAI API key is required.
"""

import glob
import os
import re

import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "knowledge",
)

COLLECTION_NAME = "darukaa_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def parse_chunks(filepath: str):
    """Split a markdown knowledge file into chunks."""

    domain = os.path.splitext(os.path.basename(filepath))[0]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"^#.*\n", "", content, count=1).strip()

    raw_chunks = [
        chunk.strip()
        for chunk in content.split("\n\n")
        if chunk.strip()
    ]

    chunks = []

    for raw in raw_chunks:
        lines = raw.split("\n")

        source_line = ""
        body_lines = []

        for line in lines:
            if line.strip().startswith("Source:"):
                source_line = (
                    line.strip()
                    .replace("Source:", "")
                    .strip()
                )
            else:
                body_lines.append(line)

        text = " ".join(body_lines).strip()

        if text:
            chunks.append(
                {
                    "text": text,
                    "source": source_line or "Unattributed",
                    "domain": domain,
                }
            )

    return chunks


def run():
    print("Loading local embedding model...")

    model = SentenceTransformer(EMBEDDING_MODEL)

    chroma_client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        COLLECTION_NAME
    )

    all_chunks = []

    for filepath in sorted(
        glob.glob(
            os.path.join(KNOWLEDGE_DIR, "*.md")
        )
    ):
        all_chunks.extend(parse_chunks(filepath))

    print(
        f"Parsed {len(all_chunks)} knowledge chunks "
        f"from {os.path.abspath(KNOWLEDGE_DIR)}"
    )

    if not all_chunks:
        print("No knowledge files found.")
        return

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    print("Creating local embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.add(
        ids=[
            f"chunk-{i}"
            for i in range(len(all_chunks))
        ],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "source": chunk["source"],
                "domain": chunk["domain"],
            }
            for chunk in all_chunks
        ],
    )

    print(
        f"Successfully created local knowledge index "
        f"with {len(all_chunks)} chunks."
    )

    print(
        "OpenAI embeddings are NOT required."
    )


if __name__ == "__main__":
    run()
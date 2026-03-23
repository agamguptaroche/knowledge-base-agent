"""FAISS-based vector store for document chunk embeddings."""

import json
import numpy as np
import faiss
from pathlib import Path
from app.config import DATA_DIR

INDEX_PATH = DATA_DIR / "faiss.index"
METADATA_PATH = DATA_DIR / "metadata.json"


class VectorStore:
    def __init__(self):
        self.dimension = 1536  # text-embedding-3-small dimension
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []
        self._load()

    def _load(self):
        if INDEX_PATH.exists() and METADATA_PATH.exists():
            self.index = faiss.read_index(str(INDEX_PATH))
            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def _save(self):
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(METADATA_PATH, "w") as f:
            json.dump(self.metadata, f)

    def add(self, embeddings: list[list[float]], chunks: list[str], doc_id: str, filename: str):
        vectors = np.array(embeddings, dtype="float32")
        # Normalize for cosine similarity via inner product
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        for chunk in chunks:
            self.metadata.append({
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk,
            })
        self._save()

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        query_vec = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            entry = self.metadata[idx].copy()
            entry["score"] = float(score)
            results.append(entry)
        return results

    def delete_by_doc_id(self, doc_id: str):
        """Remove all vectors for a given document and rebuild the index."""
        keep_indices = [i for i, m in enumerate(self.metadata) if m["doc_id"] != doc_id]
        if len(keep_indices) == len(self.metadata):
            return  # nothing to delete

        if not keep_indices:
            # All vectors belong to this doc, reset
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            self._save()
            return

        # Reconstruct vectors for kept entries
        vectors = np.array(
            [self.index.reconstruct(i) for i in keep_indices], dtype="float32"
        )
        self.metadata = [self.metadata[i] for i in keep_indices]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)
        self._save()


# Singleton instance
vector_store = VectorStore()

import faiss
import os
import json
import numpy as np
from typing import List, Dict
from rag.embedder import get_embedding
import pathway as pw

class VectorStore:
    def __init__(self, index_path="vector_store/index.faiss", metadata_path="vector_store/metadata.json"):
        self.index_path = index_path
        self.metadata_path = metadata_path

        self.dimension = 384  # assuming embedding dim from get_embedding
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []  # Stores text
        self.metadata_store = []  # Stores dict metadata

        # Load existing index if available
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            with open(metadata_path, "r", encoding="utf-8") as f:
                store = json.load(f)
                self.documents = store["documents"]
                self.metadata_store = store["metadata"]
            print("✅ Loaded existing vector store from disk.")

    def add_embeddings(self, text: str, embeddings: List[List[float]], metadata: pw.Json | dict = None):
     if isinstance(metadata, pw.Json):
        metadata = metadata.unwrap()  # Convert pw.Json to plain Python dict

     self.data.append({
        "text": text,
        "embedding": embeddings[0],  # Single vector
        "metadata": metadata
    })


    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self.documents,
                "metadata": self.metadata_store
            }, f, ensure_ascii=False, indent=2)
        print("💾 Vector store saved.")

    def search(self, query: str, k=5):
        embedding = np.array([get_embedding(query)]).astype("float32")
        D, I = self.index.search(embedding, k)

        results = []
        for i in I[0]:
            if i < len(self.documents):
                results.append({
                    "text": self.documents[i],
                    "metadata": self.metadata_store[i]
                })
        return results

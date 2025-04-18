import sys
sys.path.append("/Users/priyaninagle/sports-chatbot/rag")
from helper import (
    embed_texts,
    build_documents,
    build_faiss_index,
    save_faiss_index,
    save_documents,
    load_faiss_index,
    load_documents,
    clear_vector_db,
    bm25_search,
    faiss_search,
    brute_force_metadata_search,
    combine_results
)

from sentence_transformers import SentenceTransformer
import numpy as np


class VectorDB:
    def __init__(self, faiss_path, docs_path):
        self.faiss_path = faiss_path
        self.docs_path = docs_path

        # Try to load existing index and documents
        self.index = load_faiss_index(faiss_path)
        self.documents = load_documents(docs_path)

        if self.index is None or not self.documents:
            print("⚠️ Vector DB not found or documents missing. Initializing new storage.")
            self.index = None
            self.documents = []
            self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Load model once
        else:
            print("✅ Existing vector database and documents loaded successfully.")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Still load model for searching

    def add_entry(self, summary, metadata):
        if not summary or not metadata:
            raise ValueError("❌ Both summary and metadata must be provided.")

        # Generate embedding for the new summary
        embeddings = self.model.encode([summary], convert_to_numpy=True)

        if embeddings.size == 0:
            raise ValueError("❌ Embedding generation failed for the input summary.")

        # Build a single document object
        new_documents = build_documents([summary], [metadata], embeddings)

        if not new_documents:
            raise ValueError("❌ Failed to create document object from summary and metadata.")

        self.documents.extend(new_documents)

        # Update or create FAISS index
        if self.index is None:
            self.index = build_faiss_index(embeddings)
        else:
            self.index.add(embeddings)

        print(f"✅ Added new entry to Vector DB. Total documents: {len(self.documents)}")

    def save(self):
        if self.index is None or not self.documents:
            raise RuntimeError("❌ Cannot save: Vector DB is empty or uninitialized.")

        save_documents(self.documents, self.docs_path)
        save_faiss_index(self.index, self.faiss_path)

        print(f"💾 Vector DB saved successfully:\n - Index: {self.faiss_path}\n - Documents: {self.docs_path}")

    def clear(self):
        clear_vector_db(self.faiss_path, self.docs_path)
        self.index = None
        self.documents = []
        print("🧹 Vector DB cleared.")

        

    def search(self, query, top_k=8):
        if self.index is None or not self.documents:
            raise RuntimeError("❌ Vector DB is empty. Add data before searching.")

        bm25_hits = bm25_search(query, self.documents, top_k)
        faiss_hits = faiss_search(query, self.model, self.index, self.documents, top_k)
        # metadata_hits = brute_force_metadata_search(query, self.documents, top_k)

        combined = combine_results(bm25_hits, faiss_hits)
        print(combined)
        return combined
    
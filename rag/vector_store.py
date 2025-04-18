import faiss
import json
import numpy as np
from typing import List
import os
from rag.embedder import get_embedding

class VectorStore:
    def __init__(self, 
                 dimension: int = 384, 
                 index_path: str = "faiss.index", 
                 static_doc_path: str = "static_data.json", 
                 dynamic_doc_path: str = "dynamic_data.jsonl",
                 mapping_doc_path: str = "document_mapping.json"):

        self.dimension = dimension
        self.index_path = index_path
        self.static_doc_path = static_doc_path
        self.dynamic_doc_path = dynamic_doc_path
        self.mapping_doc_path = mapping_doc_path
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

        # Load existing index and document mapping
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            print(f"✅ Loaded existing index from {self.index_path}")
        
        if os.path.exists(self.mapping_doc_path):
            with open(self.mapping_doc_path, "r") as f:
                self.documents = json.load(f)
            print(f"✅ Loaded {len(self.documents)} documents from mapping.")

    def _embed_and_add(self, docs: List[str]):
        """Embeds and adds documents to index + updates mapping."""
        # Filter out empty or invalid documents
        valid_docs = [doc for doc in docs if isinstance(doc, str) and doc.strip()]
        
        if not valid_docs:
            print("⚠️ No valid documents to embed.")
            return
        embeddings = np.array([get_embedding(doc) for doc in valid_docs], dtype=np.float32)
        self.index.add(embeddings)
        self.documents.extend(valid_docs)
        print(f"📌 Embedded and added {len(valid_docs)} valid documents.")


    def index_static_documents(self):
        if not self.documents:  # Only embed if mapping is empty (initial case)
            print("📥 Indexing static documents...")
            static_docs = self._load_json_file(self.static_doc_path)
            self._embed_and_add(static_docs)
            self._save_state()
        else:
            print("⚠️ Static documents already indexed. Skipping.")

    def index_dynamic_documents(self):
        print("📥 Indexing new dynamic documents...")
        dynamic_docs = self._load_json_file(self.dynamic_doc_path)

        # Avoid adding duplicates
        new_docs = [doc for doc in dynamic_docs if doc not in self.documents]
        if new_docs:
            self._embed_and_add(new_docs)
            self._save_state()
        else:
            print("✅ No new dynamic documents to add.")

    def search(self, query: str, top_k: int = 5) -> List[str]:
        query_embedding = np.array([get_embedding(query)], dtype=np.float32)
        distances, indices = self.index.search(query_embedding, top_k)
        print("🔍 Search distances + indices:", distances, indices)
        print("📊 Total vectors in index:", self.index.ntotal)
        return [self.documents[idx] for idx in indices[0] if idx < len(self.documents)]

    def _load_json_file(self, path: str) -> List[str]:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            documents = []
            with open(path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())  # Read each line as a JSON object
                        if isinstance(data, dict) and "text" in data:
                            documents.append(data["text"])  # Extract the "text" field
                        else:
                            print(f"⚠️ Invalid format in line: {line}")
                    except json.JSONDecodeError:
                        print(f"⚠️ Error decoding JSON in line: {line}")
            return documents
        else:
            print(f"⚠️ {path} does not exist or is empty.")
            return []



    def _save_state(self):
        """Save index and mapping to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.mapping_doc_path, "w") as f:
            json.dump(self.documents, f)
        print(f"💾 Saved index to {self.index_path} and document map to {self.mapping_doc_path}")

    def add_embeddings(self, new_docs: List[str]):
        """Public method to add new documents (used by Pathway UDF)."""
        # Only embed documents that are not already in self.documents
        unique_docs = [doc for doc in new_docs if doc not in self.documents]
        if unique_docs:
            self._embed_and_add(unique_docs)
        else:
            print("✅ No new documents to embed.")

    def save(self):
        """Public method to save index + document map (used by Pathway UDF)."""
        self._save_state()

    def print_all_documents(self):
        print("\n📚 Current FAISS document store:")
        for i, doc in enumerate(self.documents):
            print(f"{i}. {doc}")


 # Initialize the vector store
vector_store = VectorStore()

# Index dynamic documents
vector_store.index_dynamic_documents()

# Print all documents in the current FAISS document store
vector_store.print_all_documents()

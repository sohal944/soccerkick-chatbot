import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# === Step 1: Load JSONL with Summaries and Metadata ===
def load_summaries_with_metadata(jsonl_path):
    summaries = []
    metadata_list = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            summary = obj["summary"]
            metadata = {k: v for k, v in obj.items() if k != "summary"}
            summaries.append(summary)
            metadata_list.append(metadata)
    return summaries, metadata_list

# === Step 2: Embedding Generation ===
def embed_texts(texts, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    return model, np.array(embeddings, dtype="float32")

# === Step 3: Build Document Objects ===
def build_documents(summaries, metadata_list, embeddings):
    return [(summary, metadata, embedding) for summary, metadata, embedding in zip(summaries, metadata_list, embeddings)]

# === Step 4: FAISS Index Creation ===
def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

# === Saving Logic ===
def save_faiss_index(index, path):
    faiss.write_index(index, path)
    print(f"💾 FAISS index saved at {path}")

def save_documents(documents, path):
    serializable = [{"summary": s, "metadata": m, "embedding": e.tolist()} for s, m, e in documents]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    print(f"💾 Documents saved at {path}")

# === Loading Logic ===
def load_faiss_index(path):
    if os.path.exists(path):
        index = faiss.read_index(path)
        print(f"✅ FAISS index loaded from {path}")
        return index
    print("⚠️ No FAISS index found.")
    return None

def load_documents(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)
        documents = [(item["summary"], item["metadata"], np.array(item["embedding"], dtype="float32")) for item in raw_docs]
        print(f"✅ Loaded {len(documents)} documents from {path}")
        return documents
    print("⚠️ No documents file found.")
    return []

# === Clear Function to Delete FAISS Index and Documents ===
def clear_vector_db(faiss_path, docs_path):
    # Delete FAISS index file
    if os.path.exists(faiss_path):
        os.remove(faiss_path)
        print(f"✅ FAISS index file deleted from {faiss_path}")
    else:
        print("⚠️ FAISS index file does not exist.")

    # Delete Documents JSON file
    if os.path.exists(docs_path):
        os.remove(docs_path)
        print(f"✅ Documents file deleted from {docs_path}")
    else:
        print("⚠️ Documents file does not exist.")

# === Search Methods ===
def bm25_search(query, documents, top_k=2):
    corpus = [doc[0].split() for doc in documents]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query.split())
    ranked = sorted(zip(scores, documents), reverse=True, key=lambda x: x[0])
    return [{"summary": doc[0]} for score, doc in ranked[:top_k]]

def faiss_search(query, model, index, documents, top_k=3):
    q_emb = model.encode([query]).astype("float32")
    distances, idxs = index.search(q_emb, top_k)
    return [{"summary": documents[idx][0], "distance": dist, "source": "FAISS"}
            for dist, idx in zip(distances[0], idxs[0])]

def brute_force_metadata_search(query, documents, top_k=2):
    query_lower = query.lower()
    results = []
    for doc in documents:
        metadata_str = " ".join(str(v).lower() for v in doc[1].values())
        if query_lower in metadata_str:
            relevance = metadata_str.count(query_lower)
            results.append({"summary": doc[0], "metadata": doc[1], "relevance": relevance, "source": "Metadata"})
    return sorted(results, key=lambda x: x['relevance'], reverse=True)[:top_k]

def combine_results(bm25_results, faiss_results):
    combined = bm25_results + faiss_results
    combined.sort(key=lambda x: (x.get("distance", float("inf")), -x.get("score", 0), -x.get("relevance", 0)))
    return combined

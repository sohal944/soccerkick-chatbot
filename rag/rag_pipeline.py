# rag_pipeline.py

from transformers import pipeline
from rag.vector_store import VectorStore
from rank_bm25 import BM25Okapi
import numpy as np
import json

# Load the QA model (Flan-T5 for generation)
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

# Initialize Vector Store (handles static + dynamic documents)
vector_store = VectorStore(dimension=384)

# Load static data from final file for BM25 (not mock data)
with open("static_data.json", "r") as f:
    static_documents = json.load(f)

# Prepare static texts for BM25 search
static_texts = [doc['text'] for doc in static_documents]
bm25 = BM25Okapi([text.split() for text in static_texts])


def rag_pipeline(query: str, top_k: int = 5) -> str:
    """
    Retrieves top-k relevant documents using hybrid search (BM25 + vector search)
    and returns them for inspection (generation is commented out).
    """
    # 🔍 Step 1: BM25 search over static texts
    bm25_results = bm25.get_top_n(query.split(), static_texts, n=top_k)

    # 🔍 Step 2: FAISS vector search (static + dynamic)
    vector_results = vector_store.search(query, top_k=top_k)

    # 🧠 Merge results — keeping only vector search results for now
    combined_results = vector_results  # later we’ll do: list(set(bm25_results + vector_results))

    print("📥 Vector Search Results:")
    for i, res in enumerate(combined_results, 1):
        print(f"{i}. {res}")

    # 🛑 Generation step left commented for now
    # context = " ".join(combined_results)
    # prompt = f"Context: {context} \nQuestion: {query} \nAnswer:"
    # generated_response = qa_pipeline(prompt)[0]["generated_text"]
    # return generated_response

    return "📝 (Generation is currently disabled. See printed results above.)"


if __name__ == "__main__":
    query = "Priyani from USA"
    response = rag_pipeline(query)
    print("\nGenerated Answer:\n", response)

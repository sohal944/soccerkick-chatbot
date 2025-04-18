import sys
sys.path.append("/Users/priyaninagle/sports-chatbot/rag")
sys.path.append("/Users/priyaninagle/sports-chatbot/llm")

from rag.vectordb import VectorDB
from sentence_transformers import SentenceTransformer
from rag.helper import load_documents, load_faiss_index
from llm.generrator import LLMAnswerGenerator   # ✅ Add this

if __name__ == "__main__":
    # Step 1: Load VectorDB
    vector_db = VectorDB(
        faiss_path="/Users/priyaninagle/sports-chatbot/faiss_index.index",
        docs_path="/Users/priyaninagle/sports-chatbot/document_store.json"
    )

    # Step 2: Load FAISS + Embeddings + Model
    faiss_path = "/Users/priyaninagle/sports-chatbot/faiss_index.index"
    docs_path = "/Users/priyaninagle/sports-chatbot/document_store.json"
    index = load_faiss_index(faiss_path)
    documents = load_documents(docs_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Step 3: Search
    query = "which is leading la liga?"
    top_docs = vector_db.search(query)

    # Step 4: Generate Answer using LLM
    llm = LLMAnswerGenerator(model_name="google/flan-t5-base")
    answer = llm.generate_answer(query, top_docs)

    # Step 5: Print final response
    print("🔍 Query:", query)
    print("🤖 Answer:", answer)

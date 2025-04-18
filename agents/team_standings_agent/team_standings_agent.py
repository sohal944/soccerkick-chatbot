import sys
sys.path.append("/Users/priyaninagle/sports-chatbot/rag")
sys.path.append("/Users/priyaninagle/sports-chatbot/llm")

from rag.vectordb import VectorDB
from sentence_transformers import SentenceTransformer
from rag.helper import load_documents, load_faiss_index
from llm.generrator import LLMAnswerGenerator


# === 🧠 Load once globally ===
faiss_path = "/Users/priyaninagle/sports-chatbot/standings_faiss_index.index"
docs_path = "/Users/priyaninagle/sports-chatbot/standings_document_store.json"

# Load FAISS index and documents
index = load_faiss_index(faiss_path)
documents = load_documents(docs_path)

# Load SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize vector DB
vector_db = VectorDB(
    faiss_path=faiss_path,
    docs_path=docs_path
)

# Initialize LLM
llm = LLMAnswerGenerator(model_name="mistral")


# === ⚡️ Agent Entry Point ===
def handle_query(query: str) -> str:
    top_docs = vector_db.search(query)
    answer = llm.generate_answer(query, top_docs)
    return answer


# === 🧪 Local Test (Optional) ===
if __name__ == "__main__":
    query = "Give me team standings for la liga of season 2022-2023"
    result = handle_query(query)
    print("🔍 Query:", query)
    print("🤖 Answer:", result)

import sys
sys.path.append("/Users/priyaninagle/sports-chatbot/rag")
sys.path.append("/Users/priyaninagle/sports-chatbot/llm")

from rag.vectordb import VectorDB
from sentence_transformers import SentenceTransformer
from llm.generrator import LLMAnswerGenerator

# === 🧠 Load once globally ===
faiss_path="/Users/priyaninagle/sports-chatbot/player_stats_faiss_index.index",
docs_path="/Users/priyaninagle/sports-chatbot/player_stats_document_store.json"
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
    query = "List all live matches happening now"
    result = handle_query(query)
    print("🔍 Query:", query)
    print("🤖 Answer:", result)

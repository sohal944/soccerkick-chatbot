import pathway as pw
from rag.embedder import get_embedding
from rag.vector_store import VectorStore
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Use existing vector store (handles static + dynamic storage)
vector_store = VectorStore()

# Define schema
class DataSchema(pw.Schema):
    text: str
    

# Read dynamic data (streaming mode)
table = pw.io.jsonlines.read(
    "/Users/priyaninagle/sports-chatbot/dynamic_data.jsonl", schema=DataSchema, mode="streaming", autocommit_duration_ms=50
)

# Embed each text (as string) and add to vector store
@pw.udf
def embed_and_store(text: str) -> str:
    logging.info(f"[Pathway UDF] Embedding and storing: {text}")
    vector_store.add_embeddings([text])
    vector_store.save()
    return text

# Apply the embedding function
embedded_table = table.select(
    text=embed_and_store(table.text)
)

# Optional: Write embedded output for debug tracking
pw.io.jsonlines.write(embedded_table, "ingestion/debug_output.jsonl")

# Run the ingestion pipeline
pw.run()

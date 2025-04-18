import pathway as pw
from rag.embedder import get_embedding
from rag.vector_store import VectorStore

# Use existing vector store for indexing
vector_store = VectorStore()
print("hello")
# Define schema
class DataSchema(pw.Schema):
    text: str
    metadata: dict

# Read dynamic data (streaming mode)
table = pw.io.jsonlines.read(
    "dynamic_data.jsonl", schema=DataSchema, mode="streaming", 
    # autocommit_duration_ms=50
)

# Embed each text and insert into vector store
@pw.udf
def embed_and_add(text: str) -> str:
    print("hello",text)
    vector_store.add_embeddings([text])
    vector_store.save()
    return text

# Apply the embedding function
embedded_table = table.select(
    text=embed_and_add(table.text)
)

# (Optional) Print dynamic data into terminal for debugging
# This writes to stdout and lets you see what's being processed
pw.io.jsonlines.write(embedded_table, "ingestion/debug_output.jsonl")

# Run the dataflow
pw.run()

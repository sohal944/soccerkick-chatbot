from sentence_transformers import SentenceTransformer
from typing import List

# Load the MiniLM model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> List[float]:
    return model.encode(text, convert_to_tensor=False).tolist()

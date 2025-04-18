# api.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from classifier import classify_and_handle_query

# === 🚀 FastAPI Setup ===
app = FastAPI()

# CORS for Streamlit or any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class QueryInput(BaseModel):
    query: str
    match: str  # From UI, can be logged or used for future enhancement

# API Endpoint
@app.post("/query")
def query_api(data: QueryInput):
    print(f"🟡 Incoming query: {data.query} | Match: {data.match}")
    response = classify_and_handle_query(data.query)
    return {"response": response}

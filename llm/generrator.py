import requests

class LLMAnswerGenerator:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"

    def generate_answer(self, query, retrieved_docs):
        # Step 1: Prepare context
        context = "\n".join([doc["summary"] for doc in retrieved_docs])

        # Step 2: Construct prompt
        prompt = f"""You are a football assistant. Based on the following match updates, answer the user's query.

Match Data:
{context}

User Question: {query}
Answer:"""

        # Step 3: Send prompt to Ollama API
        response = requests.post(self.api_url, json={
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        })

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: {response.status_code} - {response.text}"

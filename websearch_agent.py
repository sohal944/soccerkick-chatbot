import requests

# === 🔧 SERP API KEY ===
SERPAPI_KEY = "a1d7e4fbb3c007588da3defb236237051883206ccd054a52990b333c6c2c2aed"  # replace with your key

# === 🦆 DuckDuckGo Fast Instant Answer ===
def duckduckgo_instant_answer(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("AbstractText"):
        return data["AbstractText"]
    elif data.get("Answer"):
        return data["Answer"]
    else:
        return None

# === 🌐 SerpAPI Fallback Search ===
def web_search_fallback(query):
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google"
    }
    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code != 200:
        return []

    results = response.json().get("organic_results", [])
    return results[:3]

# === 📃 Format SERP Results ===
def display_serp_results(results):
    if not results:
        return "No useful information found online."

    output = ""
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        snippet = result.get("snippet", "No description")
        link = result.get("link", "#")
        output += f"{i}. {title}\nSnippet: {snippet}\nLink: {link}\n\n"
    return output

# === 🧠 Integrate with Mistral Model (Ollama) ===
def generate_answer_with_mistral(query, context):
    url = "http://localhost:11434/api/generate"
    prompt = f"""You are a football assistant. Based on the following data, answer the user's question.

Match Data / Web Results:
{context}

User Question: {query}
Answer:"""

    response = requests.post(url, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        return f"Ollama Error: {response.status_code}"

# === 🎯 Unified Search Function ===
def smart_sports_query(query):
    print(f"\n🔍 Searching for: {query}")

    # Try fast DuckDuckGo first
    duck_result = duckduckgo_instant_answer(query)
    if duck_result:
        print("✅ Answer from DuckDuckGo")
        return duck_result

    # Fallback to SerpAPI
    print("⚠️ DuckDuckGo failed, using SerpAPI...")
    serp_results = web_search_fallback(query)
    context = display_serp_results(serp_results)

    # Generate final answer using Mistral
    return generate_answer_with_mistral(query, context)

# === 🚀 Run and Test ===
if __name__ == "__main__":
    user_query = input("Ask a sports-related question: ")
    answer = smart_sports_query(user_query)
    print("\n🧠 Final Answer:\n", answer)
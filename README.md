# ⚽ SoccerKick Chatbot

An advanced AI-powered chatbot that delivers real-time football insights, built using **Pathway**, **FAISS**, **Ollama**, and a custom **RAG pipeline** with both **semantic search** and **BM25** ranking.

Whether it's live scores, player stats, team standings, or upcoming fixtures — SoccerKick answers it all, intelligently.

---
#Interface
<img width="1470" alt="Screenshot 2025-04-18 at 5 37 13 AM" src="https://github.com/user-attachments/assets/46cc0304-781b-426d-a597-9f8e9180e5f7" />


## 🧠 Key Features

- 📡 **Live Football Data** (via scrapers + ingestion pipelines)
- 🧠 **RAG Pipeline**: Combines BM25 + semantic search using FAISS
- 🤖 **Ollama Model Integration** (local LLMs like Mistral, LLaMA)
- 🔌 **Pathway Connectors** for real-time streaming + data syncing
- 🏆 Query:
  - Live Scores
  - Team Standings
  - Player Stats
  - Fixtures
- 🌐 Modular Agent Framework (LangChain-style)

#Using Pathway
<img width="1145" alt="Screenshot 2025-04-18 at 3 44 43 AM" src="https://github.com/user-attachments/assets/a2559a6c-2b75-49fb-85a6-6c4191b9127e" />

---

## 🧰 Tech Stack

| Tool/Library     | Purpose                            |
|------------------|------------------------------------|
| **Python**       | Core language                      |
| **Pathway**      | Real-time data pipeline & streaming|
| **Ollama**       | Run LLMs locally (e.g. Mistral)    |
| **FAISS**        | Semantic vector search             |
| **BM25**         | Classic keyword-based retrieval    |
| **Pandas**       | Data processing                    |
| **BeautifulSoup**| Web scraping                       |

---


---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Priyani-dsai/soccerkick-chatbot.git
cd soccerkick-chatbot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

ollama run mistral


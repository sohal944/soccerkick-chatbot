import logging
import importlib
from websearch_agent import smart_sports_query

# === 🪵 Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === 🧠 Agent Mappings ===
AGENT_MAP = {
    "live_score": "agents.live_score_agent.live_score_agent",
    "player_stats": "agents.player_standings_agent.player_standings_agent",
    "team_stats": "agents.team_standings_agent.team_standings_agent",
    "fixture": "agents.fixtures_agent.fixtures_agent"
}

# === 🔍 Keyword-Based Classifier ===
def keyword_classifier(query: str) -> str:
    query_lower = query.lower()

    if any(word in query_lower for word in ["live score", "current score", "score update", "score now"]):
        return "live_score"
    elif any(word in query_lower for word in ["player", "top scorer", "player stats", "goals by", "assists"]):
        return "player_stats"
    elif any(word in query_lower for word in ["team", "standings", "table", "points", "league table"]):
        return "team_stats"
    elif any(word in query_lower for word in ["fixture", "schedule", "next match", "upcoming match"]):
        return "fixture"
    else:
        return "web_search"

# === 🚦 Route Query to Correct Agent ===
def route_query_to_agent(query: str) -> str:
    logging.info(f"[Router] Received query: {query}")
    intent = keyword_classifier(query)
    logging.info(f"[Classifier] Detected intent: {intent}")

    if intent in AGENT_MAP:
        try:
            module = importlib.import_module(AGENT_MAP[intent])
            if hasattr(module, "handle_query"):
                return module.handle_query(query)
            else:
                return f"[Error] Agent '{intent}' missing handle_query function."
        except ImportError as e:
            return f"[Error] Failed to load agent module for '{intent}': {e}"
    else:
        logging.info("[Router] Falling back to web search.")
        return smart_sports_query(query)

# === 📞 Entry Point ===
def classify_and_handle_query(query: str) -> str:
    return route_query_to_agent(query)

# Optional CLI test
if __name__ == "__main__":
    user_query = input("Ask a football question: ")
    response = classify_and_handle_query(user_query)
    print("Answer:", response)

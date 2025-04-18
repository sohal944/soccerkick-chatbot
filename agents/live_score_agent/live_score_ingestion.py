import sys
sys.path.append("/Users/priyaninagle/sports-chatbot/rag")
import pathway as pw
import logging
from rag.vectordb import VectorDB

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize VectorDB once (Pathway UDFs should call methods, not create the object each time!)
vector_db = VectorDB(
    faiss_path="/Users/priyaninagle/sports-chatbot/fiass_index.index",
    docs_path="/Users/priyaninagle/sports-chatbot/document_store.json"
)

# Define schema for live score data
class DataSchema(pw.Schema):
    MatchTime: str
    HomeTeam: str
    ScoreHome: int
    ScoreAway: int
    AwayTeam: str
    # ScrapedAt: str

# Read dynamic live score data (streaming mode)
live_score_data = pw.io.csv.read(
    "/Users/priyaninagle/sports-chatbot/final_data/live_score/live_scores.csv",
    schema=DataSchema,
    mode="streaming",
    autocommit_duration_ms=50
)

# Function to generate match summary (now combined with metadata)
@pw.udf
def generate_summary(home_team: str, score_home: int, away_team: str, score_away: int, match_time: str) -> str:
    # Intent and Method Metadata for goal scoring, points, ranking, etc.
    home_score_metadata = {
        "intent": ["ranking", "sorting", "position", "order", "standings", "hierarchy", "classification", "goals", "points", "score", "goal difference"],
        "method": ["top", "best", "highest", "leading", "champion", "first", "ascend", "ranked", "goal count", "leading scorer"]
    }
    away_score_metadata = {
        "intent": ["ranking", "sorting", "position", "order", "standings", "hierarchy", "classification", "goals", "points", "score", "goal difference"],
        "method": ["ascending", "bottom", "lowest", "last", "ranked", "order", "increment", "score difference"]
    }

    # Full summary text that includes match details and metadata
    summary = (
        f"At {match_time}, {home_team} is playing against {away_team}. "
        f"The current score is {score_home}-{score_away}. "
        f"The home team's ranking is based on {', '.join(home_score_metadata['method'])} methods and goal count. "
        f"The away team's ranking follows a {', '.join(away_score_metadata['method'])} method, factoring in score and goal difference."
    )

    return summary

# Embed and add hybrid metadata directly inside the embedding function
@pw.udf
def embed_and_store(summary: str, home_team: str, score_home: int, away_team: str, score_away: int, match_time: str) -> str:
    try:
        # Creating metadata for the match details with hardcoded semantics
        metadata = {
            "type": "live match stats",
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            "MatchTime": match_time,
            "HomeScoreMetadata": {
                "intent": ["ranking", "position", "goals", "score", "points", "goal difference", "winning", "scorer", "champion"],
                "method": ["top", "leading", "ascend", "highest scorer", "goal count"]
            },
            "AwayScoreMetadata": {
                "intent": ["ranking", "position", "goals", "score", "points", "goal difference", "losing", "ranked"],
                "method": ["ascending", "bottom", "lowest", "score difference"]
            }
        }
        
        # Logging the embedding process
        logging.info(f"Embedding summary: {summary} with metadata: {metadata}")

        # Adding the summary with metadata directly to the vector database
        vector_db.add_entry(summary, metadata)  # Store the summary for search
        vector_db.save()

        return "Added to VectorDB"
    except Exception as e:
        return f"Error: {e}"

# Process the live score data: Generate summaries and add hybrid metadata
live_score_summary_table = live_score_data.select(
    summary=generate_summary(
        live_score_data.HomeTeam,
        live_score_data.ScoreHome,
        live_score_data.AwayTeam,
        live_score_data.ScoreAway,
        live_score_data.MatchTime
    ),
    home_team=live_score_data.HomeTeam,
    score_home=live_score_data.ScoreHome,
    away_team=live_score_data.AwayTeam,
    score_away=live_score_data.ScoreAway,
    match_time=live_score_data.MatchTime
)

# Apply the embedding and storing function
embedded_table = live_score_summary_table.select(
    status=embed_and_store(
        live_score_summary_table.summary,
        live_score_summary_table.home_team,
        live_score_summary_table.score_home,
        live_score_summary_table.away_team,
        live_score_summary_table.score_away,
        live_score_summary_table.match_time
    )
)

# Write debug outputs for monitoring
pw.io.jsonlines.write(
    live_score_summary_table,
    "/Users/priyaninagle/sports-chatbot/ingestion/debug_output.jsonl"
)

pw.io.jsonlines.write(
    embedded_table,
    "/Users/priyaninagle/sports-chatbot/ingestion/embedded_output.jsonl"
)

# Run the pipeline
pw.run()
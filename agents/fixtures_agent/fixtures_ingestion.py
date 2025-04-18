import pathway as pw
import logging
from rag.vectordb import VectorDB

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize your vector store (update paths if needed)
vector_db = VectorDB(
    faiss_path="/Users/priyaninagle/sports-chatbot/fixtures_faiss_index.index",
    docs_path="/Users/priyaninagle/sports-chatbot/fixtures_document_store.json"
)

# Define schema for fixture data
class FixtureSchema(pw.Schema):
    Wk: str
    Day: str
    Date: str
    Time: str
    Home: str
    Away: str
    Score: str
    season: str

# Read the fixture data (assumed to be in CSV format)
fixtures_table = pw.io.csv.read(
    "/Users/priyaninagle/sports-chatbot/static_data",  # <-- Update path if needed
    schema=FixtureSchema,
    mode="static"
)

# Optional: Generate summary (simple example)
@pw.udf
def fixture_summary(wk, date, time, home, away, score, season):
    return (
        f"In Week {wk} of the {season} season, {home} played against {away} "
        f"on {date} at {time}. The final score was {score}."
    )

# Embed and store summary in vector DB
@pw.udf
def embed_and_store_fixture(summary, wk, date, time, home, away, score, season):
    try:
        metadata = {
            "type": "fixture",
            "Wk": wk,
            "Date": date,
            "Time": time,
            "Home": home,
            "Away": away,
            "Score": score,
            "season": season
        }
        logging.info(f"Embedding fixture: {summary} with metadata: {metadata}")
        vector_db.add_entry(summary, metadata)
        vector_db.save()
        return "Added to VectorDB"
    except Exception as e:
        logging.error(f"Error embedding fixture: {e}")
        return f"Error: {e}"

# Generate summary table
summary_table = fixtures_table.select(
    summary=fixture_summary(
        fixtures_table.Wk,
        fixtures_table.Date,
        fixtures_table.Time,
        fixtures_table.Home,
        fixtures_table.Away,
        fixtures_table.Score,
        fixtures_table.season
    ),
    wk=fixtures_table.Wk,
    date=fixtures_table.Date,
    time=fixtures_table.Time,
    home=fixtures_table.Home,
    away=fixtures_table.Away,
    score=fixtures_table.Score,
    season=fixtures_table.season
)

# Store summary + metadata into VectorDB
embedded_fixtures_table = summary_table.select(
    status=embed_and_store_fixture(
        summary_table.summary,
        summary_table.wk,
        summary_table.date,
        summary_table.time,
        summary_table.home,
        summary_table.away,
        summary_table.score,
        summary_table.season
    )
)

# Save the summaries for inspection/debugging (optional)
pw.io.jsonlines.write(
    summary_table,
    "/Users/priyaninagle/sports-chatbot/debugger/fixture_summary_output.jsonl"
)
pw.io.jsonlines.write(
    embedded_fixtures_table,
    "/Users/priyaninagle/sports-chatbot/debugger/embedded_fixture_output.jsonl"
)

# Run the Pathway pipeline
pw.run()

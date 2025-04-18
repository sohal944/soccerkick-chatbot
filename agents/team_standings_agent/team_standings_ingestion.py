import pathway as pw
import logging
from rag.vectordb import VectorDB

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize VectorDB once
vector_db = VectorDB(
    faiss_path="/Users/priyaninagle/sports-chatbot/standings_faiss_index.index",
    docs_path="/Users/priyaninagle/sports-chatbot/standings_document_store.json"
)

# Define schema for the standings data
class StandingsSchema(pw.Schema):
    Team: str
    MP: int
    W: int
    D: int
    L: int
    GF: int
    GA: int
    GD: int
    Pts: int
    League: str
    Season: str

# Read static standings data (batch mode)
team_standings_data = pw.io.csv.read(
    "/Users/priyaninagle/sports-chatbot/static_data/team_standings",
    schema=StandingsSchema,
    mode="static"
)

# Generate natural language summary from the table data
@pw.udf
def generate_standing_summary(team, mp, w, d, l, gf, ga, gd, pts, league, season):
    return (
        f"In the {league} {season} season, {team} played {mp} matches with "
        f"{w} wins, {d} draws, and {l} losses. They scored {gf} goals and conceded {ga}, "
        f"ending with a goal difference of {gd} and a total of {pts} points."
    )

# Embedding and storing the summary + rich metadata
@pw.udf
def embed_and_store_standing(summary, team, mp, w, d, l, gf, ga, gd, pts, league, season):
    try:
        metadata = {
            "type": "team standings",
            "Team": team,
            "League": league,
            "Season": season,
            "MP": mp,
            "W": w,
            "D": d,
            "L": l,
            "GF": gf,
            "GA": ga,
            "GD": gd,
            "Pts": pts,
            "MPMetadata": {
                "intent": ["matches played", "game count", "fixtures completed"],
                "method": ["count", "aggregate", "progress"]
            },
            "WMetadata": {
                "intent": ["wins", "victories", "successes"],
                "method": ["sort descending", "count"]
            },
            "DMetadata": {
                "intent": ["draws", "ties", "equal results"],
                "method": ["count"]
            },
            "LMetadata": {
                "intent": ["losses", "defeats", "failures"],
                "method": ["count", "sort descending"]
            },
            "GFMetadata": {
                "intent": ["goals for", "offensive strength", "attack performance"],
                "method": ["sum", "sort descending"]
            },
            "GAMetadata": {
                "intent": ["goals against", "defensive weakness", "defense performance"],
                "method": ["sum", "sort ascending"]
            },
            "GDMetadata": {
                "intent": ["goal difference", "net goals", "strength indicator"],
                "method": ["compute difference", "sort descending"]
            },
            "PtsMetadata": {
                "intent": ["points", "league standings", "success measure"],
                "method": ["tally", "sort descending"]
            }
        }

        logging.info(f"Embedding summary: {summary} with metadata: {metadata}")
        vector_db.add_entry(summary, metadata)
        vector_db.save()
        return "Added to VectorDB"

    except Exception as e:
        logging.error(f"Error embedding standing: {e}")
        return f"Error: {e}"

# Process standings data: generate summary + attach metadata + embed
standings_summary_table = team_standings_data.select(
    summary=generate_standing_summary(
        team_standings_data.Team,
        team_standings_data.MP,
        team_standings_data.W,
        team_standings_data.D,
        team_standings_data.L,
        team_standings_data.GF,
        team_standings_data.GA,
        team_standings_data.GD,
        team_standings_data.Pts,
        team_standings_data.League,
        team_standings_data.Season
    ),
    team=team_standings_data.Team,
    mp=team_standings_data.MP,
    w=team_standings_data.W,
    d=team_standings_data.D,
    l=team_standings_data.L,
    gf=team_standings_data.GF,
    ga=team_standings_data.GA,
    gd=team_standings_data.GD,
    pts=team_standings_data.Pts,
    league=team_standings_data.League,
    season=team_standings_data.Season
)

embedded_standings_table = standings_summary_table.select(
    status=embed_and_store_standing(
        standings_summary_table.summary,
        standings_summary_table.team,
        standings_summary_table.mp,
        standings_summary_table.w,
        standings_summary_table.d,
        standings_summary_table.l,
        standings_summary_table.gf,
        standings_summary_table.ga,
        standings_summary_table.gd,
        standings_summary_table.pts,
        standings_summary_table.league,
        standings_summary_table.season
    )
)

# Optional: write debug outputs
pw.io.jsonlines.write(
    standings_summary_table,
    "/Users/priyaninagle/sports-chatbot/debugger/standings_summary_output.jsonl"
)
pw.io.jsonlines.write(
    embedded_standings_table,
    "/Users/priyaninagle/sports-chatbot/debugger/embedded_standings_output.jsonl"
)

# Run the Pathway pipeline
pw.run()
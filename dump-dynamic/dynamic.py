import pathway as pw
import logging
from datetime import datetime
from rag.vectordb import VectorDB


vector_db=VectorDB(
    faiss_path="/mnt/c/Users/tonys/sports_chatbot/faiss_team_standing.index",
    docs_path="/mnt/c/Users/tonys/sports_chatbot/document_store_team_standing.json"
)

logging.basicConfig(level=logging.INFO)

# Define schema (updated Scraped_At to ScrapedAt, no underscore)
class TeamStandingSchema(pw.Schema):
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
    ScrapedAt: str  # Assuming ScrapedAt is in string format

# Read dynamic team standings data (streaming mode)
team_standings_data = pw.io.csv.read(
    "./final_data/team_standings/",
    schema=TeamStandingSchema,
    mode="streaming",
    autocommit_duration_ms=50
)


@pw.udf
def generate_standing_summary(
    team: str, mp: int, w: int, d: int, l: int, gf: int, ga: int, gd: int, 
    pts: int, league: str, season: str
) -> str:
    return (
        f" team {team} is currently in the {league} league in the {season} season. "
        f"They have played {mp} matches, won {w}, drawn {d}, and lost {l}. "
        f"Goals scored: {gf}, goals conceded: {ga}, goal difference: {gd}. "
        f"They have accumulated {pts} points so far this season."
    )

# Generate standings summary table
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
    season=team_standings_data.Season,
    scrapedat=team_standings_data.ScrapedAt
)

# Embed and store summaries with detailed metadata
@pw.udf
def embed_and_store_standing(
    summary: str, team: str, mp: int, w: int, d: int, l: int, gf: int, ga: int, gd: int, 
    pts: int, league: str, season: str,scraped_at: str
) -> str:
    try:
        metadata = {
            "type": "team standings",
            "Team": team,
            "ScrapedAt": scraped_at,
            "MP": mp,
            "W": w,
            "D": d,
            "L": l,
            "GF": gf,
            "GA": ga,
            "GD": gd,
            "Pts": pts,
            "League": league,
            "Season": season,
            "PositionMetadata": {
                "intent": ["ranking", "position", "standings", "order", "league place", "hierarchy"],
                "method": ["sorted", "best to worst", "ascending", "descending"]
            },
            "PlayedMetadata": {
                "intent": ["progress", "total matches", "schedule", "fixtures completed"],
                "method": ["match count", "season progress"]
            },
            "WonMetadata": {
                "intent": ["victories", "successes", "achievements", "win count", "performance", "ranking"],
                "method": ["high to low", "success rate", "sort descending"]
            },
            "DrawnMetadata": {
                "intent": ["ties", "equal outcomes", "undecided matches"]
            },
            "LostMetadata": {
                "intent": ["defeats", "losses", "failures", "shortcomings"],
                "method": ["counting", "negative performance"]
            },
            "GFMetadata": {
                "intent": ["goals scored", "offensive strength", "attack performance", "ranking"],
                "method": ["goal count", "high to low"]
            },
            "GAMetadata": {
                "intent": ["goals conceded", "defensive weakness", "defense performance"],
                "method": ["goal count", "low to high"]
            },
            "GDMetadata": {
                "intent": ["goal difference", "net goals", "strength indicator", "ranking"],
                "method": ["difference calculation", "sorted list"]
            },
            "PointsMetadata": {
                "intent": ["total points", "league progress", "success measure", "standings basis", "ranking"],
                "method": ["points tally", "sort descending", "highest first"]
            }
        }
        # Remove outdated entries from VectorDB (based on ScrapedAt)

        logging.info(f"Embedding summary for {team} with metadata: {metadata}")

        # Add the new entry to the VectorDB
        vector_db.add_entry(summary, metadata)
        vector_db.save()

        return "Added to VectorDB"
    except Exception as e:
        return f"Error: {e}"

# Embed and store the standings summary table (step 3)
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
        standings_summary_table.season,
        standings_summary_table.scrapedat
    )
)

# Write the embedded_standings_table (step 3)
pw.io.jsonlines.write(
    embedded_standings_table,
    "/mnt/c/Users/tonys/sports_chatbot/final_data/embedded_standings.jsonl"
)

# Run the Pathway pipeline
pw.run()
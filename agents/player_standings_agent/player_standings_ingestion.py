import pathway as pw
import logging
from rag.vectordb import VectorDB

# === Setup Logging ===
logging.basicConfig(level=logging.INFO)

# === Initialize VectorDB ===
vector_db = VectorDB(
    faiss_path="/Users/priyaninagle/sports-chatbot/player_stats_faiss_index.index",
    docs_path="/Users/priyaninagle/sports-chatbot/player_stats_document_store.json"
)

# === Simplified Schema ===
class PlayerStats(pw.Schema):
    Player: str
    Nation: str
    Pos: str
    Squad: str
    Gls: str
    Ast: str

# === Read CSV ===
player_data = pw.io.csv.read(
    "/Users/priyaninagle/sports-chatbot/static_data",
    schema=PlayerStats,
    mode="static"
)

# === Summary Generator ===
@pw.udf
def generate_summary(player, nation, pos, squad, gls, ast):
    return f"{player} from {nation}, played as a {pos} for {squad}, scored {gls} goals and assisted {ast} times."

# === Embed & Store in Vector DB ===
@pw.udf
def embed_and_store(summary, player, nation, pos, squad, gls, ast):
    try:
        metadata = {
            "Player": player,
            "Nation": nation,
            "Position": pos,
            "Squad": squad,
            "Goals": gls,
            "Assists": ast
        }
        logging.info(f"Embedding: {summary}")
        vector_db.add_entry(summary, metadata)
        vector_db.save()
        return "✅ Embedded"
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return f"Error: {e}"

# === Summary Table ===
summary_table = player_data.select(
    summary=generate_summary(
        player_data.Player,
        player_data.Nation,
        player_data.Pos,
        player_data.Squad,
        player_data.Gls,
        player_data.Ast
    ),
    player=player_data.Player,
    nation=player_data.Nation,
    pos=player_data.Pos,
    squad=player_data.Squad,
    gls=player_data.Gls,
    ast=player_data.Ast
)

# === Embed Table ===
embedded_table = summary_table.select(
    status=embed_and_store(
        summary_table.summary,
        summary_table.player,
        summary_table.nation,
        summary_table.pos,
        summary_table.squad,
        summary_table.gls,
        summary_table.ast
    )
)

pw.io.jsonlines.write(
    summary_table,
    "/Users/priyaninagle/sports-chatbot/debugger/player_summary_output.jsonl"
)

pw.io.jsonlines.write(
    embedded_table,
    "/Users/priyaninagle/sports-chatbot/debugger/embedded_player_output.jsonl"
)

# === Run the Pipeline ===
pw.run()

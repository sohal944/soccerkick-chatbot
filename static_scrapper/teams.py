import pandas as pd
import os

# Map league names to FBref competition IDs
LEAGUE_IDS = {
    "Premier League": "9",
    "La Liga": "12",
    "Bundesliga": "20",
    "Serie A": "11",
    "Ligue 1": "13"
}

def build_urls(league_name, season):
    comp_id = LEAGUE_IDS.get(league_name)
    if not comp_id:
        raise ValueError(f"Unsupported league: {league_name}")
    base_url = f"https://fbref.com/en/comps/{comp_id}/{season}/{season}-{league_name.replace(' ', '-')}-Stats"
    return base_url

def get_team_standings(url, league, season):
    tables = pd.read_html(url)
    for table in tables:
        if "W" in table.columns and "Pts" in table.columns:
            standings = table
            break
    else:
        raise ValueError("League standings table not found!")

    standings = standings[['Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']]
    standings.columns = ['Team', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']

    # Add extra columns
    standings["League"] = league
    standings["Season"] = season

    return standings

def save_to_csv(df, league, season, save_dir="static_data/team_standings"):
    dir_path = os.path.join(save_dir, league)
    os.makedirs(dir_path, exist_ok=True)
    file_name = f"{league.replace(' ', '_')}_{season}_standings.csv"
    file_path = os.path.join(dir_path, file_name)
    df.to_csv(file_path, index=False)
    print(f"✅ Data saved as CSV to {file_path}")

def run_for_league_and_seasons(league, seasons):
    for season in seasons:
        try:
            url = build_urls(league, season)
            print(f"\n📥 Fetching data for {league} {season} from: {url}")
            standings = get_team_standings(url, league, season)
            print(standings.head())  # Optional: show first few rows
            save_to_csv(standings, league, season)
        except Exception as e:
            print(f"❌ Failed to process {league} {season}: {e}")

# Example usage
if __name__ == "__main__":
    league_input = "Ligue 1"
    seasons_input = ["2020-2021", "2021-2022", "2022-2023", "2023-2024"]
    run_for_league_and_seasons(league_input, seasons_input)

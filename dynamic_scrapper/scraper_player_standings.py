import pandas as pd
import os
import time

# Map league names to FBref competition IDs
LEAGUE_IDS = {
    "Premier League": "9",
    "La Liga": "12",
    "Bundesliga": "20",
    "Serie A": "11",
    "Ligue 1": "13"
}

# List of seasons to process
SEASONS = ["2024-2025", "2023-2024", "2022-2023", "2021-2022", "2020-2021"]

def build_urls(league_name, season):
    comp_id = LEAGUE_IDS.get(league_name)
    if not comp_id:
        raise ValueError(f"Unsupported league: {league_name}")
    base_url = f"https://fbref.com/en/comps/{comp_id}/{season}/{season}-{league_name.replace(' ', '-')}-Stats"
    player_stats_url = f"https://fbref.com/en/comps/{comp_id}/{season}/stats/{season}-{league_name.replace(' ', '-')}-Stats"
    return base_url, player_stats_url

def get_team_standings(url):
    tables = pd.read_html(url)
    for table in tables:
        if "W" in table.columns and "Pts" in table.columns:
            standings = table
            break
    else:
        raise ValueError("League standings table not found!")

    standings = standings[['Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']]
    standings.columns = ['Team', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
    return standings

def save_to_json(df, league, season, save_dir="final_data/team_standings"):
    dir_path = os.path.join(save_dir, league)
    os.makedirs(dir_path, exist_ok=True)  # Create directory if it doesn't exist
    file_name = f"{league.replace(' ', '_')}_{season}_standings.json"
    file_path = os.path.join(dir_path, file_name)
    df.to_json(file_path, orient='records', indent=2)
    print(f"\n✅ Data saved as JSON to {file_path}")

def run_for_league_season(league, season):
    try:
        base_url, player_stats_url = build_urls(league, season)
        print(f"\nFetching team data from: {base_url}")
        print(f"Fetching player data from: {player_stats_url}")

        print(f"\n📊 Team Standings for {league} {season}:")
        standings = get_team_standings(base_url)
        print(standings)

        save_to_json(standings, league, season)
    except Exception as e:
        print(f"❌ Failed to process {league} {season}: {e}")

def start_live_updating(seasons=SEASONS, interval_per_league=60, cooldown_between_cycles=300):
    leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]

    while True:
        for season in seasons:
            print(f"\n🔄 Starting update for season {season}...")

            for league in leagues:
                print(f"\n📊 Processing {league} - {season}...")
                run_for_league_season(league, season)
                print(f"⏳ Waiting {interval_per_league} seconds before updating next league...\n")
                time.sleep(interval_per_league)

            print(f"\n🔁 All leagues for {season} updated. Waiting {cooldown_between_cycles // 60} minutes before next full cycle...\n")
            time.sleep(cooldown_between_cycles)

if __name__ == "__main__":
    start_live_updating()

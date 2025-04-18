import pandas as pd
import os
import time
from urllib.error import HTTPError

# League metadata dictionary
LEAGUE_INFO = {
    'Premier League': {'url_name': 'Premier-League', 'id': '9'},
    'La Liga': {'url_name': 'La-Liga', 'id': '12'},
    'Serie A': {'url_name': 'Serie-A', 'id': '11'},
    'Ligue 1': {'url_name': 'Ligue-1', 'id': '13'},
    'Bundesliga': {'url_name': 'Bundesliga', 'id': '20'},
}

# Function to fetch and save fixture data
def get_fixture_data(league_name, league_url_name, league_id, season):
    print(f'📅 Fetching fixture data for {league_name}, Season: {season}')
    
    url = f'https://fbref.com/en/comps/{league_id}/{season}/schedule/{season}-{league_url_name}-Scores-and-Fixtures'
    
    try:
        tables = pd.read_html(url)
    except Exception as e:
        print(f"❌ Failed to read tables from URL: {url}")
        print(e)
        return

    try:
        fixtures = tables[0][['Wk', 'Day', 'Date', 'Time', 'Home', 'Away', 'xG', 'xG.1', 'Score']].dropna()
    except KeyError:
        print("❌ Expected columns not found in fixture table.")
        return

    fixtures['season'] = season
    fixtures['game_id'] = fixtures.index

    output_dir = os.path.join("static_data", "fixtures", league_url_name)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f'{league_url_name}_{season}_fixture_data.csv')

    # Only save if data has changed
    if os.path.exists(output_path):
        try:
            old_data = pd.read_csv(output_path)
            if fixtures.equals(old_data):
                print(f'⏩ No changes for {league_name} ({season}), skipping save.')
                return
        except:
            print("⚠️ Error reading existing file, will overwrite.")

    fixtures.to_csv(output_path, index=False)
    print(f'✅ CSV Saved: {output_path}')

# Wrapper function for one league and one season
def run_for_league_season(league_name, season):
    if league_name not in LEAGUE_INFO:
        print(f"❌ League {league_name} not recognized.")
        return
    
    league = LEAGUE_INFO[league_name]
    try:
        get_fixture_data(league_name, league['url_name'], league['id'], season)
    except HTTPError:
        print(f"⚠️ HTTPError for {league_name} - {season}, skipping.")
        time.sleep(5)

# Main driver
if __name__ == "__main__":
    # ✅ USER INPUT HERE
    league_name = "Serie A"
    seasons = ["2021-2022", "2022-2023", "2023-2024", "2024-2025"]

    for season in seasons:
        run_for_league_season(league_name, season)

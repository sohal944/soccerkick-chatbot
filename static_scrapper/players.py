import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import os
import time
from datetime import datetime

# Define the dictionary for league IDs
LEAGUE_IDS = {
    "Premier League": "9",
    "La_Liga": "12",
    "Bundesliga": "20",
    "Serie A": "11",
    "Ligue 1": "13"
}

# Define a function to scrape data for a given league and season
def scrape_league_data(league_name, season):
    league_id = LEAGUE_IDS.get(league_name)
    if not league_id:
        print(f"❌ Invalid league name: {league_name}")
        return
    
    url = f"https://fbref.com/en/comps/{league_id}/{season}/stats/{season}-{league_name.replace(' ', '-')}-Stats"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    outer_div = soup.find('div', {'id': 'all_stats_standard', 'class': 'table_wrapper'})

    if outer_div:
        print(f"✅ Found outer div for {league_name} {season}")

        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            if 'div_stats_standard' in comment:
                comment_soup = BeautifulSoup(comment, 'html.parser')
                inner_div = comment_soup.find('div', {'id': 'div_stats_standard', 'class': 'table_container'})

                if inner_div:
                    table = inner_div.find('table', {'id': 'stats_standard'})
                    if table:
                        print(f"✅ Found table for {league_name} {season}")

                        header_row = table.find_all('tr')[1]
                        columns = [col.get_text(strip=True) for col in header_row.find_all('th')]

                        df = pd.read_html(str(table))[0]
                        df.columns = columns
                        df = df[df['Player'] != 'Player']
                        df.reset_index(drop=True, inplace=True)
                        df = df.iloc[:, :-11]
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        df["League"] = league_name
                        df["Season"] = season
                        df["ScrapedAt"] = current_time
                        if 'Rk' in df.columns:
                            df.drop(columns=['Rk'], inplace=True)

                        df['Gls'] = pd.to_numeric(df['Gls'], errors='coerce')
                        df = df.sort_values(by='Gls', ascending=False)

                        # Create league-specific directory
                        save_dir = os.path.join("final_data", "player_standings", league_name)
                        os.makedirs(save_dir, exist_ok=True)

                        filename = f"{league_name}_{season}_Stats.csv"
                        filepath = os.path.join(save_dir, filename)

                        # Save only if data has changed
                        if os.path.exists(filepath):
                            old_df = pd.read_csv(filepath)
                            if df.equals(old_df):
                                print(f"⏩ No changes for {league_name} {season}, skipping save.\n")
                                return

                        df.to_csv(filepath, index=False)
                        print(f"✅ Saved to {filepath}\n")

                    else:
                        print(f"❌ Table not found for {league_name} {season}")
                else:
                    print(f"❌ Inner div not found for {league_name} {season}")
    else:
        print(f"❌ Outer div not found for {league_name} {season}")


# Automatically run for all leagues for season 2024-2025 at intervals
def start_auto_scraping(season="2024-2025", interval_hours=0.1):
    try:
        while True:
            print(f"\n🔁 Starting new scraping cycle for {season}...\n")
            for league in LEAGUE_IDS.keys():
                print(f"➡️ Scraping {league}...")
                scrape_league_data(league, season)
                print(f"⏳ Done with {league}, moving on...\n")

            print(f"⏸️ Sleeping for {interval_hours} hours before next cycle...\n")
            time.sleep(interval_hours * 100)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting gracefully.")


if __name__ == "__main__":
    start_auto_scraping()
from bs4 import BeautifulSoup
import requests
import csv
import time
import os
from datetime import datetime

def scrape_from_livescore():
    print('Fetching markup from livescores.com ..')

    try:
        livescore_html = requests.get('https://www.livescores.com/football/live/?tz=5.5')
        livescore_html.raise_for_status()
    except Exception as e:
        return print('An error occurred: ', e)

    print("Feeding markup to BeautifulSoup ..")
    parsed_markup = BeautifulSoup(livescore_html.text, 'html.parser')

    root_div = parsed_markup.find("div", {"id": "__livescore"})
    if root_div:
        print("✅ Found root div '__livescore'")

        match_sections = root_div.find_all("div", {"class": "Le Pe Oe"})
        print(f"🔍 Found {len(match_sections)} match sections.")

        # Define and create the directory
        save_dir = "final_data/live_score"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, "live_scores.csv")

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write header only if file is empty
            file.seek(0, 2)
            if file.tell() == 0:
                writer.writerow(["HomeTeam", "ScoreHome", "ScoreAway", "AwayTeam", "MatchTime"])

            for match in match_sections:
                match_time = match.find("span", {"class": "tg"})
                match_time = match_time.get_text(strip=True) if match_time else "N/A"

                home_team = match.find("span", {"class": "Zh"})
                home_team = home_team.get_text(strip=True) if home_team else "N/A"

                away_team = match.find_all("span", {"class": "Zh"})[-1]
                away_team = away_team.get_text(strip=True) if away_team else "N/A"

                score_home = match.find("span", {"class": "Uh"})
                score_away = match.find("span", {"class": "di"})

                if score_home and score_away:
                    score_awayx = score_away.get_text(strip=True)
                    score_homex = score_home.get_text(strip=True).split('-')[0]
                else:
                    score_awayx = "N/A"
                    score_homex = "N/A"

                # Add current timestamp
                match_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                writer.writerow([home_team, score_homex, score_awayx, away_team, match_time])
                print(f"➡️ {home_team} {score_homex} {score_awayx} {away_team} | Scraped at: {match_time}")

    else:
        print("❌ Root div '__livescore' not found!")

def run_scraper():
    while True:
        scrape_from_livescore()
        print("⏳ Waiting 60 seconds before the next update...\n")
        time.sleep(20)

if __name__ == "__main__":
    run_scraper()

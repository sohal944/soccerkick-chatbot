from bs4 import BeautifulSoup
import requests
import csv
import time
import os

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

        # Define a dictionary to store the live matches
        live_matches = {}

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

            # Store each match and its score in the dictionary
            live_matches[f"{home_team} vs {away_team}"] = f"{score_homex} - {score_awayx}"
        
        return live_matches  # Return the dictionary

    else:
        print("❌ Root div '__livescore' not found!")
        return {}

# Function to continuously scrape and update live scores (optional)
def run_scraper():
    while True:
        live_matches = scrape_from_livescore()
        if live_matches:
            print(live_matches)
        print("⏳ Waiting 60 seconds before the next update...\n")
        time.sleep(60)

if __name__ == "__main__":
    run_scraper()
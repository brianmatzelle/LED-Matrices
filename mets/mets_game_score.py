import requests
from datetime import datetime
import pytz

def get_mets_game_score():
    # Set the date to July 12, 2025
    target_date = "2025-07-12"
    
    # API endpoint for MLB schedule
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={target_date}"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        # Find the Mets game
        mets_team_id = 121  # New York Mets team ID
        for game in data.get("dates", [{}])[0].get("games", []):
            home_team = game["teams"]["home"]["team"]["id"]
            away_team = game["teams"]["away"]["team"]["id"]
            
            if home_team == mets_team_id or away_team == mets_team_id:
                # Get game status
                game_status = game["status"]["detailedState"]
                home_team_name = game["teams"]["home"]["team"]["name"]
                away_team_name = game["teams"]["away"]["team"]["name"]
                home_score = game["teams"]["home"]["score"]
                away_score = game["teams"]["away"]["score"]
                
                # Check if the game is in progress
                if game_status in ["In Progress", "Delayed"]:
                    return f"{away_team_name} {away_score} - {home_team_name} {home_score} (Game in Progress)"
                elif game_status == "Final":
                    return f"{away_team_name} {away_score} - {home_team_name} {home_score} (Final)"
                elif game_status in ["Scheduled", "Warmup", "Pre-Game"]:
                    return f"No current game score available. Mets game against {away_team_name if home_team == mets_team_id else home_team_name} is {game_status.lower()}."
                else:
                    return f"No current game score available. Mets game status: {game_status}."
        
        return "No New York Mets game found for July 12, 2025."
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

if __name__ == "__main__":
    print(get_mets_game_score())

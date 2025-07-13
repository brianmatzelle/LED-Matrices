# SPDX-FileCopyrightText: 2025 Brian Matzelle
# SPDX-License-Identifier: MIT

# Mets Game Score Display
# For Metro M4 Airlift with RGB Matrix shield, 64 x 32 RGB LED Matrix display

"""
This program displays the Mets logo and current game score on an LED matrix display.
It queries the MLB API to get current game information and updates periodically.
"""

from os import getenv
import time
import board
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
import mets_game_graphics  # Custom graphics module for game display

# Get WiFi details, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")

if None in [ssid, password]:
    raise RuntimeError(
        "WiFi settings are kept in settings.toml, "
        "please add them there. The settings file must contain "
        "'CIRCUITPY_WIFI_SSID', 'CIRCUITPY_WIFI_PASSWORD'."
    )

# Mets team ID in MLB API
METS_TEAM_ID = 121

# Get today's date for the API call
import rtc

def get_today_date():
    """Get today's date in YYYY-MM-DD format"""
    try:
        # Get current time from RTC (should be set by network.get_local_time())
        current_time = rtc.RTC().datetime
        year = current_time.tm_year
        month = current_time.tm_mon
        day = current_time.tm_mday
        return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        # Fallback to a default date if RTC isn't available
        return "2024-07-12"

# Set up API endpoint for MLB schedule
def get_data_source():
    date = get_today_date()
    return f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

DATA_LOCATION = ["dates", 0, "games"]
UPDATE_INTERVAL = 300  # Update every 5 minutes (300 seconds)

# --- Display setup ---
matrix = Matrix()
network = Network(status_neopixel=board.NEOPIXEL, debug=True)
gfx = mets_game_graphics.MetsGameGraphics(matrix.display)

print("Mets game display loaded")

localtime_refresh = None
game_refresh = None

def find_mets_game(games_data):
    """Find the Mets game from the games data"""
    if not games_data:
        return None
    
    for game in games_data:
        home_team = game["teams"]["home"]["team"]["id"]
        away_team = game["teams"]["away"]["team"]["id"]
        
        if home_team == METS_TEAM_ID or away_team == METS_TEAM_ID:
            return game
    
    return None

def parse_game_data(game):
    """Parse game data into a format for display"""
    if not game:
        return {
            "status": "No Game",
            "home_team": "Mets",
            "away_team": "No Game",
            "home_score": 0,
            "away_score": 0,
            "inning": "",
            "is_mets_home": True
        }
    
    home_team = game["teams"]["home"]["team"]["name"]
    away_team = game["teams"]["away"]["team"]["name"]
    home_score = game["teams"]["home"].get("score", 0)
    away_score = game["teams"]["away"].get("score", 0)
    game_status = game["status"]["detailedState"]
    
    # Check if Mets are home team
    is_mets_home = game["teams"]["home"]["team"]["id"] == METS_TEAM_ID
    
    # Get inning information if available
    inning = ""
    if "linescore" in game and game["linescore"]:
        inning_num = game["linescore"].get("currentInning", "")
        inning_half = game["linescore"].get("inningHalf", "")
        if inning_num:
            inning = f"{inning_half} {inning_num}" if inning_half else f"Inning {inning_num}"
    
    return {
        "status": game_status,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "inning": inning,
        "is_mets_home": is_mets_home
    }

while True:
    # Only query the online time once per hour (and on first run)
    if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 3600:
        try:
            print("Getting time from internet!")
            network.get_local_time()
            localtime_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occurred getting time, retrying! -", e)
            continue

    # Only query the game data every 5 minutes (and on first run)
    if (not game_refresh) or (time.monotonic() - game_refresh) > UPDATE_INTERVAL:
        try:
            print("Getting game data...")
            DATA_SOURCE = get_data_source()
            print(f"API URL: {DATA_SOURCE}")
            
            value = network.fetch_data(DATA_SOURCE, json_path=DATA_LOCATION)
            print("Raw game data:", value)
            
            # Find the Mets game
            mets_game = find_mets_game(value)
            parsed_game = parse_game_data(mets_game)
            
            print("Parsed game data:", parsed_game)
            gfx.display_game(parsed_game)
            game_refresh = time.monotonic()
            
        except RuntimeError as e:
            print("Some error occurred getting game data, retrying! -", e)
            continue
        except Exception as e:
            print("Unexpected error:", e)
            # Display error state
            error_game = {
                "status": "Error",
                "home_team": "Mets",
                "away_team": "Error",
                "home_score": 0,
                "away_score": 0,
                "inning": "",
                "is_mets_home": True
            }
            gfx.display_game(error_game)
            continue

    # Small delay to prevent overwhelming the system
    time.sleep(1)

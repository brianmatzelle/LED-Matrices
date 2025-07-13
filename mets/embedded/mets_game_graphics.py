# SPDX-FileCopyrightText: 2024 Brian Matzelle
#
# SPDX-License-Identifier: MIT

import time
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# Colors for different elements
METS_BLUE = 0x002D72
METS_ORANGE = 0xFF5910
SCORE_COLOR = 0xFFFFFF
TEAM_COLOR = 0x00D3FF
STATUS_COLOR = 0x9000FF
INNING_COLOR = 0xCCCCCC
ERROR_COLOR = 0xFF0000

# Get the current working directory
cwd = ("/" + __file__).rsplit("/", 1)[0]

class MetsGameGraphics(displayio.Group):
    def __init__(self, display):
        super().__init__()
        self.display = display
        
        # Create the root group structure
        self.root_group = displayio.Group()
        self.root_group.append(self)
        
        # Create sub-groups for different display elements
        self._logo_group = displayio.Group()
        self.append(self._logo_group)
        
        self._score_group = displayio.Group()
        self.append(self._score_group)
        
        self._info_group = displayio.Group()
        self.append(self._info_group)
        
        # Load fonts (using smaller fonts for the compact display)
        try:
            # Try to load fonts from the fonts directory
            # small_font_path = "fonts/Arial-12.bdf"
            # medium_font_path = "fonts/Arial-14.bdf"
            small_font_path = "fonts/Roboto-Medium-5pt.bdf"
            medium_font_path = "fonts/Roboto-Medium-6pt.bdf"
            self.small_font = bitmap_font.load_font(small_font_path)
            self.medium_font = bitmap_font.load_font(medium_font_path)
            print("Custom fonts loaded successfully")
        except Exception as e:
            # Fallback to built-in font if fonts aren't available
            print(f"Font loading failed: {e}, using built-in font")
            self.small_font = displayio.FONT
            self.medium_font = displayio.FONT
        
        # Pre-load common glyphs
        if hasattr(self.small_font, 'load_glyphs'):
            glyphs = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: "
            self.small_font.load_glyphs(glyphs)
            self.medium_font.load_glyphs(glyphs)
        
        # Initialize logo
        self._load_logo()
        
        # Initialize text labels
        self._create_text_labels()
        
        # Show initial loading state
        self._show_loading()
        
    def _load_logo(self):
        """Load and display the Mets logo"""
        try:
            logo_bitmap = displayio.OnDiskBitmap("logo.bmp")
            logo_sprite = displayio.TileGrid(
                logo_bitmap,
                pixel_shader=logo_bitmap.pixel_shader
            )
            # Position logo in the top-left corner
            logo_sprite.x = 0
            logo_sprite.y = 0
            self._logo_group.append(logo_sprite)
            print("Logo loaded successfully")
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Create a placeholder text if logo fails to load
            logo_text = Label(self.small_font, text="NYM", color=METS_BLUE)
            logo_text.x = 2
            logo_text.y = 8
            self._logo_group.append(logo_text)
    
    def _create_text_labels(self):
        """Create text labels for game information"""
        # Score display - positioned to the right of the logo
        self.score_label = Label(self.medium_font, text="0-0", color=SCORE_COLOR)
        self.score_label.x = 20  # Moved left from 24
        self.score_label.y = 8
        self._score_group.append(self.score_label)
        
        # Team matchup display
        self.teams_label = Label(self.small_font, text="vs TBD", color=TEAM_COLOR)
        self.teams_label.x = 20  # Moved left from 24
        self.teams_label.y = 20
        self._info_group.append(self.teams_label)
        
        # Status/inning display
        self.status_label = Label(self.small_font, text="Loading...", color=STATUS_COLOR)
        self.status_label.x = 2
        self.status_label.y = 28
        self._info_group.append(self.status_label)
    
    def _show_loading(self):
        """Show loading state"""
        self.score_label.text = "..."
        self.teams_label.text = "Loading"
        self.status_label.text = "Getting data..."
        self.display.root_group = self.root_group
    
    def display_game(self, game_data):
        """Display game information on the matrix"""
        try:
            print(f"Displaying game: {game_data}")
            
            # Update score display
            home_score = game_data.get("home_score", 0)
            away_score = game_data.get("away_score", 0)
            
            # Ensure scores are integers
            if home_score is None:
                home_score = 0
            if away_score is None:
                away_score = 0
            
            if game_data["is_mets_home"]:
                # Mets are home team
                score_text = f"{away_score}-{home_score}"
            else:
                # Mets are away team
                score_text = f"{home_score}-{away_score}"
                
            print(f"Setting score text to: '{score_text}'")
            self.score_label.text = score_text
            
            # Update team matchup
            opponent = game_data["away_team"] if game_data["is_mets_home"] else game_data["home_team"]
            # Shorten team names for display
            opponent_short = self._shorten_team_name(opponent)
            home_away = "vs" if game_data["is_mets_home"] else "@"
            teams_text = f"{home_away} {opponent_short}"
            print(f"Setting teams text to: '{teams_text}'")
            self.teams_label.text = teams_text
            
            # Update status
            status = game_data["status"]
            inning = game_data.get("inning", "")
            
            if status == "Final":
                status_text = "Final"
                self.status_label.color = METS_ORANGE
            elif status in ["In Progress", "Delayed"]:
                if inning:
                    status_text = inning
                else:
                    status_text = "Live"
                self.status_label.color = METS_ORANGE
            elif status in ["Scheduled", "Warmup", "Pre-Game"]:
                status_text = "Today"
                self.status_label.color = STATUS_COLOR
            elif status == "No Game":
                status_text = "No Game"
                self.status_label.color = INNING_COLOR
            elif status == "Error":
                status_text = "Error"
                self.status_label.color = ERROR_COLOR
            else:
                status_text = status[:9]  # Truncate long status
                self.status_label.color = STATUS_COLOR
            
            print(f"Setting status text to: '{status_text}'")
            self.status_label.text = status_text
            
            # Update the display
            self.display.root_group = self.root_group
            
        except Exception as e:
            print(f"Error displaying game: {e}")
            # Show error state
            self.score_label.text = "ERR"
            self.teams_label.text = "Error"
            self.status_label.text = "Display Error"
            self.status_label.color = ERROR_COLOR
            self.display.root_group = self.root_group
    
    def _shorten_team_name(self, team_name):
        """Shorten team names for display on small screen"""
        # Dictionary of team name abbreviations
        team_abbrevs = {
            "New York Yankees": "NYY",
            "Boston Red Sox": "BOS",
            "Tampa Bay Rays": "TB",
            "Baltimore Orioles": "BAL",
            "Toronto Blue Jays": "TOR",
            "Chicago White Sox": "CWS",
            "Cleveland Guardians": "CLE",
            "Detroit Tigers": "DET",
            "Kansas City Royals": "KC",
            "Minnesota Twins": "MIN",
            "Houston Astros": "HOU",
            "Los Angeles Angels": "LAA",
            "Oakland Athletics": "OAK",
            "Seattle Mariners": "SEA",
            "Texas Rangers": "TEX",
            "Atlanta Braves": "ATL",
            "Miami Marlins": "MIA",
            "Philadelphia Phillies": "PHI",
            "Washington Nationals": "WSH",
            "Chicago Cubs": "CHC",
            "Cincinnati Reds": "CIN",
            "Milwaukee Brewers": "MIL",
            "Pittsburgh Pirates": "PIT",
            "St. Louis Cardinals": "STL",
            "Arizona Diamondbacks": "ARI",
            "Colorado Rockies": "COL",
            "Los Angeles Dodgers": "LAD",
            "San Diego Padres": "SD",
            "San Francisco Giants": "SF",
            "New York Mets": "NYM"
        }
        
        return team_abbrevs.get(team_name, team_name[:3].upper()) 
"""
File path configuration for the College Football Heavyweight Championship tracker.
"""
from pathlib import Path

# Base directories
# Since config is in src/config/, go up TWO levels to get to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent  # config -> src -> project root
DATA_DIR = PROJECT_ROOT / 'data'
WEB_DIR = PROJECT_ROOT / 'web'

# Data subdirectories
GAMES_DIR = DATA_DIR / 'games'
TEAMS_DIR = DATA_DIR / 'teams'
REPORTS_DIR = DATA_DIR / 'reports'

# Web subdirectories
ASSETS_DIR = WEB_DIR / 'assets'

# Main output files
HTML_FILE = WEB_DIR / 'cfbHeavyweights.html'

# Report files
ALL_TIME_RANKINGS_FILE = REPORTS_DIR / 'allTimeRankings.txt'
TOP_25_ACTIVE_FILE = REPORTS_DIR / 'top25Active.txt'
ALL_BOUTS_FILE = REPORTS_DIR / 'allBouts.txt'
LONGEST_REIGNS_FILE = REPORTS_DIR / 'longestReigns.txt'
SCHOOL_BY_SCHOOL_FILE = REPORTS_DIR / 'schoolBySchool.txt'
YEARLY_BELT_WINNERS_FILE = REPORTS_DIR / 'yearlyBeltWinners.txt'

# Helper functions
def get_games_file(year):
    """Get the path for a specific year's games file."""
    return GAMES_DIR / f'{year}Games.csv'

def get_teams_file(year):
    """Get the path for a specific year's teams file."""
    return TEAMS_DIR / f'{year}Teams.csv'

# Ensure directories exist
def ensure_directories():
    """Create all necessary directories if they don't exist."""
    for directory in [DATA_DIR, GAMES_DIR, TEAMS_DIR, REPORTS_DIR, WEB_DIR, ASSETS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
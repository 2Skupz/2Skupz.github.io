"""
Configuration package for the College Football Heavyweight Championship tracker.
"""
from .config import *
from .paths import *

__all__ = [
    # From config.py
    'START_YEAR',
    'SKIPPED_YEARS',
    'CSS_FILE',
    'LOGO_FILE',
    'TOP_N_ACTIVE',
    'DATE_FORMAT',
    'POINTS_PER_REIGN',
    'POINTS_PER_WIN',
    'WIN_PERCENTAGE_WEIGHT',
    
    # From paths.py
    'PROJECT_ROOT',
    'DATA_DIR',
    'WEB_DIR',
    'GAMES_DIR',
    'TEAMS_DIR',
    'REPORTS_DIR',
    'ASSETS_DIR',
    'HTML_FILE',
    'ALL_TIME_RANKINGS_FILE',
    'TOP_25_ACTIVE_FILE',
    'ALL_BOUTS_FILE',
    'LONGEST_REIGNS_FILE',
    'SCHOOL_BY_SCHOOL_FILE',
    'YEARLY_BELT_WINNERS_FILE',
    'get_games_file',
    'get_teams_file',
    'ensure_directories',
]
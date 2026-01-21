"""
General configuration settings for the College Football Heavyweight Championship tracker.
"""

# Season configuration
START_YEAR = 1869
SKIPPED_YEARS = [1871]  # Years with no games

# Web configuration
CSS_FILE = 'cfbHeavyweights.css'
LOGO_FILE = 'theChamp.jpeg'

# Report configuration
TOP_N_ACTIVE = 25  # Number of teams in active rankings

# Display configuration
DATE_FORMAT = '%Y-%m-%d'

# Ranking configuration
POINTS_PER_REIGN = 100
POINTS_PER_WIN = 10000
WIN_PERCENTAGE_WEIGHT = 0.001  # Dividing factor for win percentage contribution
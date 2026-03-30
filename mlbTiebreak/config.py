#==============================================================================
# Centralized configuration for file paths and season settings.
#==============================================================================
import os
from datetime import date

def getProjectRoot():
    return os.path.dirname(os.path.abspath(__file__))

def getSeason():
    today=date.today()
    return today.year if today.month>3 else today.year-1

def getTeamsPath(season):
    return os.path.join(getProjectRoot(), "data", "teams", f"{season}teams.csv")

def getGamesPath(season):
    return os.path.join(getProjectRoot(), "data", "games", f"{season}games.csv")

def getTiebreakersPath():
    return os.path.join(getProjectRoot(), "data", "tiebreakers.json")

def getGridsPath():
    return os.path.join(getProjectRoot(), "data", "tiebreaker_grids.txt")
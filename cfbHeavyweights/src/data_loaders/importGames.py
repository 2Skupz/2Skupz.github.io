import csv
from datetime import datetime

from .teamNameMap import toHeavyweightsName
from ..config import get_games_file, get_teams_file, ensure_directories, SPORTS_REPO_DIR
from ..utils.helpers import getCurrentSeason

# KPI publishes its daily Massey-sourced FBS fetch here (see KPI/sports_repo_publish.py)
# so this project never needs to know about KPI's own internal data layout.
RAW_CFB_DIR = SPORTS_REPO_DIR / 'cfb' / 'raw'


def raw_games_file(year):
    return RAW_CFB_DIR / 'games' / f'{year}Games.csv'


def raw_teams_file(year):
    return RAW_CFB_DIR / 'teams' / f'{year}Teams.csv'


def main():
    """Import the current season's FBS games/teams from sportsRepo."""
    ensure_directories()
    year = getCurrentSeason()
    importSeason(year)


def importSeason(year):
    gameList = readRawGames(year)
    writeGamesFile(get_games_file(year), gameList)
    teamList = readRawTeams(year)
    writeTeamsFile(get_teams_file(year), teamList)


def readRawGames(year):
    """Read KPI's raw Massey-sourced games file and map team names."""
    games = []
    with open(raw_games_file(year), 'r') as f:
        for row in csv.reader(f):
            gYear, month, day, winner, winnerScore, loser, loserScore = row
            games.append((
                int(gYear), int(month), int(day),
                toHeavyweightsName(winner), int(winnerScore),
                toHeavyweightsName(loser), int(loserScore),
            ))
    games.sort(key=lambda g: (g[0], g[1], g[2]))
    return games


def readRawTeams(year):
    """Read KPI's raw Massey-sourced team list and map team names."""
    with open(raw_teams_file(year), 'r') as f:
        return [toHeavyweightsName(row[0]) for row in csv.reader(f) if row]


def writeGamesFile(fileName, gameList):
    """Write a games file in cfbHeavyweights' existing schema."""
    fileName.parent.mkdir(parents=True, exist_ok=True)
    with open(fileName, 'w') as f:
        writer = csv.writer(f)
        for gameID, (gYear, month, day, winner, winnerScore, loser, loserScore) in enumerate(gameList):
            date = datetime(gYear, month, day).strftime('%b %-d, %Y')
            # week (col 1) and the away-win flag (col 7) aren't used downstream; placeholders.
            writer.writerow([gameID, 0, date, winner, winnerScore, loser, loserScore, 0])


def writeTeamsFile(fileName, teamList):
    """Write a teams file in cfbHeavyweights' existing schema."""
    fileName.parent.mkdir(parents=True, exist_ok=True)
    with open(fileName, 'w') as f:
        writer = csv.writer(f)
        for teamID, name in enumerate(teamList):
            writer.writerow([teamID, name, ''])


if __name__ == '__main__':
    main()

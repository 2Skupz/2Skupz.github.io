from utils.team import Team
from datetime import date
import csv
import os

def main():
    season = findCurrentSeason()
    leagueGames = createSchedule(season)
    writeGames(leagueGames, season)
    print(f"Success! Wrote {len(leagueGames)} completed games for {season}.")

def createSchedule(season):
    """Fetch all completed games from all teams, deduplicate"""
    leagueGames = []
    processedTeams = []
    teamList = createTeamList(season)
    
    for team in teamList:
        teamGames = team.getCurrentYearSchedule(season, teamList)
        for game in teamGames:
            if gameIsOk(game, processedTeams):
                leagueGames.append(game)
        processedTeams.append(team.abbr)
    
    return leagueGames

def gameIsOk(game, processedTeams):
    """Check if game hasn't been seen yet (avoid duplicates)"""
    return game.away not in processedTeams and game.home not in processedTeams

def findCurrentSeason():
    today = date.today()
    year = today.year
    month = today.month
    return year - 1 if month < 4 else year

def createTeamList(season, confirm=False):
    teamFile = getTeamFile(season)
    teamList = []
    
    try:
        with open(teamFile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                abbr, city, nickname, league, division = row
                newTeam = Team(abbr, city, nickname, league, division)
                teamList.append(newTeam)
                if confirm:
                    print(f"{newTeam} added to team list.")
    except FileNotFoundError:
        print(f"Team file {teamFile} not found.")
    
    return teamList

def getTeamFile(season):
    return f"data/teams/{season}teams.csv"

def getGameFile(season):
    os.makedirs('data/games', exist_ok=True)
    return f'data/games/{season}games.csv'

def writeGames(gameList, season):
    gameFile = getGameFile(season)
    gameList.sort(key=lambda g: g.date)
    
    with open(gameFile, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Day', 'Date', 'Away', 'Home', 'RA', 'RH', 'Inn'])
        for game in gameList:
            writer.writerow([game.day, game.date, game.away, game.home, game.ra, game.rh, game.inn])
    
    print(f"Wrote to {gameFile}")

if __name__ == "__main__":
    main()

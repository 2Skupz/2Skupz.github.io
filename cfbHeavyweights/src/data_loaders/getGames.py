import os
import csv
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

from ..models.heavyweightClasses import Game
from ..config import (
    SKIPPED_YEARS,
    get_games_file,
    get_teams_file,
    ensure_directories
)
from ..utils.helpers import getCurrentSeason


class Team:
    """Simple Team class for data loading."""
    def __init__(self, teamID, name, conference, wins=0, losses=0):
        self.teamID = teamID
        self.name = name
        self.conference = conference
        self.wins = wins
        self.losses = losses


def main():
    """Main function for updating game data."""
    ensure_directories()
    year = getCurrentSeason()
    for season in range(year, year + 1):
        if season in SKIPPED_YEARS:
            continue
        gameList = readGamesFromWeb(season)
        writePlayedGamesFile(get_games_file(season), gameList)
        teamList = readTeamsFromWeb(season)
        writeTeamFile(get_teams_file(season), teamList)


def readTeamsFromWeb(year):
    """Pull teams from sports reference site."""
    print("Team file does not exist. Reading team list from web.")
    teamID = 0
    year = str(year)
    teamList = []
    
    url = "https://www.sports-reference.com/cfb/years/" + year + "-standings.html"
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    
    for tr in soup.find_all('tr')[2:]:
        tds = tr.find_all('td')
        if len(tds) > 0:
            name = convertTeamName(tds[0].text)
            conference = tds[1].text
            createdTeam = Team(teamID, name, conference, 0, 0)
            teamList.append(createdTeam)
            teamID += 1
    
    return teamList


def readGamesFromWeb(year):
    """Read games from sports reference."""
    print("Reading games from the web.")
    gameID = 0
    year = str(year)
    url = "https://www.sports-reference.com/cfb/years/%s-schedule.html" % str(year)
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    gameList = []
    
    if int(year) > 2012:
        for tr in soup.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) > 0:
                week = tds[0].text
                date = tds[1].text
                winner = stripRank(tds[4].text)
                winPoints = tds[5].text
                awayWin = tds[6].text
                loser = stripRank(tds[7].text)
                loserPoints = tds[8].text
                if winPoints == "":
                    pass
                elif awayWin == '@':
                    createdGame = Game(winner, loser, int(winPoints), int(loserPoints), date)
                    createdGame.gameID = gameID
                    createdGame.week = week
                    gameList.append(createdGame)
                    gameID += 1
                else:
                    createdGame = Game(loser, winner, int(loserPoints), int(winPoints), date)
                    createdGame.gameID = gameID
                    createdGame.week = week
                    gameList.append(createdGame)
                    gameID += 1
    else:
        for tr in soup.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) > 0:
                week = tds[0].text
                date = tds[1].text
                winner = stripRank(tds[3].text)
                winPoints = tds[4].text
                awayWin = tds[5].text
                loser = stripRank(tds[6].text)
                loserPoints = tds[7].text
                if winPoints == "":
                    pass
                elif awayWin == '@':
                    createdGame = Game(winner, loser, int(winPoints), int(loserPoints), date)
                    createdGame.gameID = gameID
                    createdGame.week = week
                    gameList.append(createdGame)
                    gameID += 1
                else:
                    createdGame = Game(loser, winner, int(loserPoints), int(winPoints), date)
                    createdGame.gameID = gameID
                    createdGame.week = week
                    gameList.append(createdGame)
                    gameID += 1
    return gameList


def writePlayedGamesFile(fileName, gameList):
    """Write a file of all games played."""
    os.makedirs(os.path.dirname(fileName), exist_ok=True)
    if os.path.exists(fileName):
        os.remove(fileName)
    print("Writing game file %s" % fileName)
    with open(fileName, "w") as f:
        writer = csv.writer(f)
        for game in gameList:
            if game == None:
                pass
            else:
                awayWin = 1 if game.scoreA > game.scoreB else 0
                if awayWin == 1:
                    gameFileList = [game.gameID, game.week, game.date, game.teamA, 
                                    game.scoreA, game.teamB, game.scoreB, awayWin]
                else:
                    gameFileList = [game.gameID, game.week, game.date, game.teamB, 
                                    game.scoreB, game.teamA, game.scoreA, awayWin]
                writer.writerow(gameFileList)
    f.close()
    print("Game File Written: %s" % fileName)


def writeTeamFile(fileName, teamList):
    """Write a file of all teams for a given year."""
    os.makedirs(os.path.dirname(fileName), exist_ok=True)
    if os.path.exists(fileName):
        os.remove(fileName)
    print("Writing team file %s" % fileName)
    with open(fileName, "w") as f:
        writer = csv.writer(f)
        for team in teamList:
            writer.writerow([team.teamID, team.name, team.conference])
    f.close()
    print("Team File Written: %s" % fileName)


def stripRank(teamName):
    """Strip ranking from team name."""
    if len(teamName) > 0 and teamName[0] == '(':
        return convertTeamName(teamName[teamName.find(')') + 2:])
    else:
        return convertTeamName(teamName)


def convertTeamName(teamName):
    """Convert team names from sports reference to standard names."""
    if len(teamName) == 0:
        return teamName
    if teamName[len(teamName) - 1] == ';':
        return teamName[0:len(teamName) - 1]
    elif teamName == "Miami (FL)":
        return "Miami"
    elif teamName == "Middle Tennessee State":
        return "Middle Tennessee"
    elif teamName == "Florida International":
        return "Florida Int'l"
    elif teamName == "Southern California":
        return "USC"
    elif teamName == "Louisiana State":
        return "LSU"
    elif teamName == "Texas-El Paso":
        return "UTEP"
    elif teamName == "Bowling Green State":
        return "Bowling Green"
    elif teamName == "Brigham Young":
        return "BYU"
    elif teamName == "Texas Christian":
        return "TCU"
    elif teamName == "Mississippi":
        return "Ole Miss"
    elif teamName == "Nevada-Las Vegas":
        return "UNLV"
    elif teamName == "Pittsburgh":
        return "Pitt"
    elif teamName == "Central Florida":
        return "UCF"
    elif teamName == "Southern Methodist":
        return "SMU"
    elif teamName == "Alabama-Birmingham":
        return "UAB"
    elif teamName == "North Carolina State":
        return "NC State"
    elif teamName == "Southern Mississippi":
        return "Southern Miss"
    elif teamName == "Texas-San Antonio":
        return "UTSA"
    elif teamName == "Virginia Military Institute":
        return "VMI"
    else:
        return teamName


if __name__ == "__main__":
    main()
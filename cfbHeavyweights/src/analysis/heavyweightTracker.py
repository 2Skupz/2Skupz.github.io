import csv
import os
from datetime import datetime

from ..models.heavyweightClasses import Team, Game
from ..utils.helpers import findTeam, getCurrentSeason
from ..data_loaders import getGames

def createMasterFile():
    """Create lists of bouts, historical teams, and active teams."""
    historyTeamList = []
    boutList = []
    champ = None
    lastYear = getCurrentSeason()
    
    # Update file if needed
    if updateMostRecentGames(lastYear):
        getGamesAndTeams(lastYear)
    
    # Create master files
    for season in range(1869, lastYear + 1):
        if season == 1871:
            continue
        gameFile = "data/games/%sGames.csv" % season
        teamFile = "data/teams/%sTeams.csv" % season
        seasonTeamList = findSeasonTeams(teamFile)
        for team in seasonTeamList:
            checkHistoryList(historyTeamList, season, team)
        seasonGameList = processGameFile(season, gameFile, seasonTeamList)
        champ = findBouts(boutList, seasonGameList, champ)
    
    activeTeams = activeHistoryTeams(historyTeamList, seasonTeamList)
    return boutList, historyTeamList, activeTeams

def updateTeams(boutList, historyTeamList, champList):
    """Update team statistics with bout information."""
    processBouts(boutList, historyTeamList)
    setStats(historyTeamList)
    updateTeamTitles(champList, historyTeamList)

def yearlyNationalChamps(boutList):
    """Determine the national champion for each year."""
    champList = []
    currYear = 1869
    currChamp = None
    for bout in boutList:
        season = getSeason(bout)
        winner = boutChamp(bout, currChamp)
        if season > currYear:
            champList.append((currYear, currChamp))
            currYear = season
        currChamp = winner
    
    # Manual addition for 2024
    title2024 = (2024, 'Florida')
    if title2024 not in champList:
        import inspect
        currLine = inspect.currentframe().f_lineno
        print(f"Manually adding Florida's 2024 title at line {currLine}")
        champList.append(title2024)
    
    return champList

def boutChamp(bout, currChamp):
    """Determine who holds the belt after a bout."""
    if bout.checkTie():
        return currChamp
    else:
        winner, loser = bout.getWinnerLoser()
        return winner

def getSeason(bout):
    """Extract the season from a bout's date."""
    date = bout.date
    dayYear = date.split(",")
    monthDay = dayYear[0].split(" ")
    month = monthDay[0].strip()
    year = dayYear[1].strip()
    if month == "Jan":
        return int(year) - 1
    else:
        return int(year)

def updateTeamTitles(champList, teamList):
    """Add national titles to teams."""
    for season in champList:
        champ = findTeam(teamList, season[1])
        if champ:
            champ.addNationalTitle(season[0])

def updateMostRecentGames(year):
    """Check if games need to be updated (currently disabled)."""
    return False

def getGamesAndTeams(year):
    """Fetch games and teams from the web."""
    gameList = getGames.readGamesFromWeb(year)
    getGames.writePlayedGamesFile(f"data/games/{year}Games.csv", gameList)
    if not os.path.exists(f"data/teams/{year}Teams.csv"):
        teamList = getGames.readTeamsFromWeb(year)
        getGames.writeTeamFile(f"data/teams/{year}Teams.csv", teamList)

def dropInactiveTeamsWithNoHistory(active, historical):
    """Remove inactive teams that never participated in a bout."""
    return [team for team in active] + [
        team for team in historical 
        if team not in active and len(team.challenges) > 0
    ]

def createOtherLinks(boutList, activeTeamList, historyTeamList, champList):
    """Create various report files."""
    topN(historyTeamList, len(historyTeamList), "data/reports/allTimeRankings.txt")
    topN(activeTeamList, 25, "data/reports/top25Active.txt")
    printAllBouts(boutList, "data/reports/allBouts.txt")
    longestReigns(historyTeamList, "data/reports/longestReigns.txt")
    writeSchoolBySchool("data/reports/schoolBySchool.txt", historyTeamList)

def writeSchoolBySchool(page, teamList):
    """Write school-by-school belt history."""
    data = ""
    for team in teamList:
        cW, cL, cT, dW, dL, dT, numReigns, titles = team.records()
        data += "*******\n"
        data += f"{team.name} Belt History"
        data += f"\n\tNational Titles: {titles}"
        if titles == 0:
            data += f"\n"
        else:
            data += f" - {team.getTitleString()}\n"
        data += f"\tNumber of Reigns: {numReigns}\n"
        data += f"\tRecord in Bouts: {cW+dW}-{cL+dL}-{cT+dT}\n"
        data += f"\t\tAs Belt Holder: {dW}-{dL}-{dT}\n"
        data += f"\t\tAs Challenger : {cW}-{cL}-{cT}\n"
        data += "\n\n"
    printFile(data, page)

def longestReigns(teamList, outputFile=None):
    """Generate report of longest reigns."""
    reignList = createReignList(teamList)
    sortedReignList = sorted(reignList, key=lambda x: x[0], reverse=True)
    sortedReignList = [x for x in sortedReignList if x[0] >= 10]
    data = f"{'Games':<7}{'Team':<22}{'Start':<16}{'End':<16}\n"
    for r in sortedReignList:
        data += f"{r[0]:<7}{r[1]:<22}{r[2]:<16}{r[3]:<12}\n"
    printFile(data, outputFile)

def createReignList(teamList):
    """Create a list of all reigns."""
    reignList = []
    for team in teamList:
        if team.currentReign:
            reignList.append(team.currentReign.quickSum())
        for reign in team.reigns:
            reignList.append(reign.quickSum())
    return reignList

def topN(historyTeamList, num=25, outputFile=None):
    """Generate top N rankings."""
    tableStr = f"All-Time Heavyweight Rankings\n"
    historyTeamList.sort(key=lambda x: x.rankingPoints, reverse=True)
    for i in range(min(num, len(historyTeamList))):
        tableStr += historyTeamList[i].rankSummary(i) + "\n"
    printFile(tableStr, outputFile)

def printFile(data, outputFile):
    """Print data to file or console."""
    if outputFile:
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        with open(outputFile, "w") as file:
            file.write(data)
    else:
        print(data)

def printAllBouts(boutList, outputFile=None):
    """Print all bouts to file."""
    data = "Date            Defending           Challenger              Score      Beltholder\n"
    for game in boutList:
        data += game.beltSum() + "\n"
    printFile(data, outputFile)

def processBouts(boutList, historyTeamList):
    """Process all bouts and update team records."""
    for game in boutList:
        defending = game.defending
        if defending == None:
            vacantBelt(historyTeamList, game)
        else:
            if game.checkTie():
                champDefendsWithTie(historyTeamList, game)
            else:
                winner, loser = game.getWinnerLoser()
                if winner == defending or winner == "TIE":
                    champDefends(historyTeamList, game)
                else:
                    newChamp(historyTeamList, game)

def vacantBelt(historyTeamList, game):
    """Handle vacant belt scenario."""
    winner, loser = game.getWinnerLoser()
    belt = findTeam(historyTeamList, winner)
    challenger = findTeam(historyTeamList, loser)
    belt.startReign(game)
    belt.addChallenge(game)
    challenger.addChallenge(game)

def champDefends(historyTeamList, game):
    """Handle successful championship defense."""
    belt, challenger = getBeltAndChallenge(historyTeamList, game)
    belt.addToReign(game)
    challenger.addChallenge(game)

def champDefendsWithTie(historyTeamList, game):
    """Handle championship defense with tie."""
    belt, challenger = getBeltAndChallenge(historyTeamList, game)
    belt.addToReign(game)
    challenger.addChallenge(game)

def newChamp(historyTeamList, game):
    """Handle new champion scenario."""
    belt, challenger = getBeltAndChallenge(historyTeamList, game)
    belt.endReign(game)
    challenger.startReign(game)
    challenger.addChallenge(game)

def getBeltAndChallenge(historyTeamList, game):
    """Get belt holder and challenger from a game."""
    return findTeam(historyTeamList, game.defending), findTeam(historyTeamList, game.challenger)

def getBeltTeam(boutList, teamList):
    """Get the current belt holder."""
    lastBout = boutList[-1]
    winner, loser = lastBout.getWinnerLoser()
    return findTeam(teamList, winner)

def setStats(historyTeamList):
    """Set statistics for all teams."""
    for team in historyTeamList:
        team.setStats()

def checkHistoryList(teamList, season, team):
    """Check and update history list with team."""
    teamNames = getTeamNames(teamList)
    if team not in teamNames:
        newTeam = Team(team)
        newTeam.seasonsPlayed.append(season)
        teamList.append(newTeam)
    else:
        theTeam = findTeam(teamList, team)
        theTeam.seasonsPlayed.append(season)

def findBouts(boutList, gameList, champ):
    """Find and process bouts in game list."""
    for game in gameList:
        game.addStakes(champ)
        champ = checkBouts(boutList, game, champ)
    return champ

def checkBouts(boutList, game, champ):
    """Check if a game is a bout."""
    if champ == None:
        game.titleFight()
    elif game.teamA == champ or game.teamB == champ:
        game.titleFight()
    if game.bout:
        boutList.append(game)
        if game.checkTie():
            return champ
        else:
            winner, loser = game.getWinnerLoser()
            return winner
    else:
        return champ

def processGameFile(season, gameFile, teamList):
    """Process a game file and return list of games."""
    gameList = []
    with open(gameFile, 'r') as g:
        reader = csv.reader(g)
        for row in reader:
            newGame = readGameFromRow(row)
            if bothTeamsOnList(teamList, newGame):
                gameList.append(newGame)
    return gameList

def readGameFromRow(row):
    """Read a game from a CSV row."""
    gameID = row[0]
    week = row[1]
    date = row[2]
    teamA = row[3]
    scoreA = int(row[4])
    teamB = row[5]
    scoreB = int(row[6])
    return Game(teamA, teamB, scoreA, scoreB, date)

def bothTeamsOnList(teamList, game):
    """Check if both teams are on the list."""
    if (game.teamA in teamList) and (game.teamB in teamList):
        return True
    else:
        return False

def getTeamNames(teamList):
    """Get list of team names."""
    return [x.name for x in teamList]

def findSeasonTeams(teamFile):
    """Find teams for a season from file."""
    teamList = []
    with open(teamFile, 'r') as t:
        reader = csv.reader(t)
        for row in reader:
            teamList.append(row[1])
    return teamList

def activeHistoryTeams(allTime, season):
    """Get teams that are both in history and active."""
    return [x for x in allTime if x.name in season]
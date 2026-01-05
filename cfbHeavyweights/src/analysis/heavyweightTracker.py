import csv
import os
from datetime import datetime
from collections import Counter

from ..models.heavyweightClasses import Team, Game
from ..utils.helpers import findTeam, getCurrentSeason
from ..data_loaders import getGames
from ..config import (
    START_YEAR, SKIPPED_YEARS, TOP_N_ACTIVE,
    get_games_file, get_teams_file,
    ALL_TIME_RANKINGS_FILE, TOP_25_ACTIVE_FILE, ALL_BOUTS_FILE,
    LONGEST_REIGNS_FILE, SCHOOL_BY_SCHOOL_FILE, YEARLY_BELT_WINNERS_FILE
)

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
    for season in range(START_YEAR, lastYear + 1):
        if season in SKIPPED_YEARS:
            continue
        gameFile = get_games_file(season)
        teamFile = get_teams_file(season)
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
    currYear = START_YEAR
    currChamp = None
    for bout in boutList:
        season = getSeason(bout)
        winner = boutChamp(bout, currChamp)
        if season > currYear:
            champList.append((currYear, currChamp))
            currYear = season
        currChamp = winner
    
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
    getGames.writePlayedGamesFile(get_games_file(year), gameList)
    if not os.path.exists(get_teams_file(year)):
        teamList = getGames.readTeamsFromWeb(year)
        getGames.writeTeamFile(get_teams_file(year), teamList)

def dropInactiveTeamsWithNoHistory(active, historical):
    """Remove inactive teams that never participated in a bout."""
    return [team for team in active] + [
        team for team in historical 
        if team not in active and len(team.challenges) > 0
    ]

def createOtherLinks(boutList, activeTeamList, historyTeamList, champList):
    """Create various report files."""
    topN(historyTeamList, len(historyTeamList), ALL_TIME_RANKINGS_FILE)
    topN(activeTeamList, TOP_N_ACTIVE, TOP_25_ACTIVE_FILE)
    printAllBouts(boutList, ALL_BOUTS_FILE)
    longestReigns(historyTeamList, LONGEST_REIGNS_FILE)
    writeSchoolBySchool(SCHOOL_BY_SCHOOL_FILE, historyTeamList)
    writeYearlyBeltWinners(champList, YEARLY_BELT_WINNERS_FILE)

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

def writeYearlyBeltWinners(champList, outputFile):
    """Write yearly belt winners to file with summary and year-by-year listing."""
    # Count titles per team
    title_counts = Counter(champ for year, champ in champList)
    
    # Sort by titles (descending), then alphabetically
    sorted_teams = sorted(title_counts.items(), key=lambda x: (-x[1], x[0]))
    
    # Build the output
    data = "The team that ends the season with the belt becomes the National Champion. "
    data += "Sometimes, like Michigan in 2023, the belt winner wins the real National Championship. "
    data += "Sometimes, like in 1994 when 6-6 Wyoming won the championship, the winning team doesn't even play in a Bowl Game. "
    data += "Below is the all time list of Champions. First by most titles, then the year-by-year titles.\n\n"
    
    # Header for team summary
    data += f"{'Team':<25}{'Titles':<10}Years\n"
    
    # Write each team's summary
    for team, count in sorted_teams:
        # Get all years for this team
        years = [str(year) for year, champ in champList if champ == team]
        years_str = ", ".join(years)
        data += f"{team:<25}{count:<10}{years_str}\n"
    
    data += "\n"
    
    # Write year-by-year listing
    for year, champ in champList:
        data += f"{year} {champ}\n"
    
    printFile(data, outputFile)

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
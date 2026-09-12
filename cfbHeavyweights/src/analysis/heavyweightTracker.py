import csv
import os
from datetime import datetime
from collections import Counter

from ..models.heavyweightClasses import Team, Game
from ..utils.helpers import findTeam, getCurrentSeason
from ..utils.htmlReport import writeHtmlReportPage, dateSortKey
from ..config import (
    START_YEAR, SKIPPED_YEARS, TOP_N_ACTIVE,
    get_games_file, get_teams_file,
    ALL_TIME_RANKINGS_FILE, TOP_25_ACTIVE_FILE, ALL_BOUTS_FILE,
    LONGEST_REIGNS_FILE, SCHOOL_BY_SCHOOL_FILE, YEARLY_BELT_WINNERS_FILE,
    BELT_LINEAGE_FILE
)

def createMasterFile():
    """Create lists of bouts, historical teams, and active teams."""
    historyTeamList = []
    boutList = []
    champ = None
    lastYear = getCurrentSeason()

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

def dropInactiveTeamsWithNoHistory(active, historical):
    """Remove inactive teams that never participated in a bout."""
    return [team for team in active] + [
        team for team in historical 
        if team not in active and len(team.challenges) > 0
    ]

def createOtherLinks(boutList, activeTeamList, historyTeamList, champList):
    """Create various report files."""
    topN(historyTeamList, len(historyTeamList), ALL_TIME_RANKINGS_FILE, "All-Time Heavyweight Rankings")
    topN(activeTeamList, TOP_N_ACTIVE, TOP_25_ACTIVE_FILE, "Top 25 Active FBS Teams")
    printAllBouts(boutList, ALL_BOUTS_FILE)
    longestReigns(historyTeamList, LONGEST_REIGNS_FILE)
    writeSchoolBySchool(SCHOOL_BY_SCHOOL_FILE, historyTeamList)
    writeYearlyBeltWinners(champList, YEARLY_BELT_WINNERS_FILE)
    writeBeltLineage(boutList, BELT_LINEAGE_FILE)

def writeSchoolBySchool(page, teamList):
    """Write school-by-school belt history."""
    data = ""
    rows = []
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

        titlesStr = f"{titles} ({team.getTitleString()})" if titles else "0"
        rows.append((
            team.name, numReigns, titlesStr,
            f"{cW+dW}-{cL+dL}-{cT+dT}", f"{dW}-{dL}-{dT}", f"{cW}-{cL}-{cT}",
        ))
    printFile(data, page)

    writeHtmlReportPage(
        page.with_suffix('.html'),
        "School-by-School Belt History",
        [{
            'headers': ['School', 'Reigns', 'National Titles', 'Overall Record',
                        'As Belt Holder', 'As Challenger'],
            'rows': rows,
            'numericCols': {1},
        }],
    )

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
    summaryRows = []
    for team, count in sorted_teams:
        # Get all years for this team
        years = [str(year) for year, champ in champList if champ == team]
        years_str = ", ".join(years)
        data += f"{team:<25}{count:<10}{years_str}\n"
        summaryRows.append((team, count, years_str))

    data += "\n"

    # Write year-by-year listing
    yearRows = []
    for year, champ in champList:
        data += f"{year} {champ}\n"
        yearRows.append((year, champ))

    printFile(data, outputFile)

    writeHtmlReportPage(
        outputFile.with_suffix('.html'),
        "Yearly National Champions",
        [
            {
                'heading': 'Titles by Team',
                'headers': ['Team', 'Titles', 'Years'],
                'rows': summaryRows,
                'numericCols': {1},
            },
            {
                'heading': 'Year by Year',
                'headers': ['Year', 'Champion'],
                'rows': yearRows,
                'numericCols': {0},
            },
        ],
        description=(
            "The team that ends the season with the belt becomes the National Champion. "
            "Sometimes the belt winner also wins the real National Championship; sometimes "
            "(like 6-6 Wyoming in 1994) the winning team doesn't even play in a Bowl Game."
        ),
    )

def longestReigns(teamList, outputFile=None):
    """Generate report of longest reigns."""
    reignList = createReignList(teamList)
    sortedReignList = sorted(reignList, key=lambda x: x[0], reverse=True)
    sortedReignList = [x for x in sortedReignList if x[0] >= 10]
    data = f"{'Games':<7}{'Team':<22}{'Start':<16}{'End':<16}\n"
    for r in sortedReignList:
        data += f"{r[0]:<7}{r[1]:<22}{r[2]:<16}{r[3]:<12}\n"
    printFile(data, outputFile)

    if outputFile:
        rows = [
            (games, team, (start, dateSortKey(start)), (end, dateSortKey(end)))
            for games, team, start, end in sortedReignList
        ]
        writeHtmlReportPage(
            outputFile.with_suffix('.html'),
            "Longest Championship Reigns",
            [{
                'headers': ['Games', 'Team', 'Start', 'End'],
                'rows': rows,
                'numericCols': {0, 2, 3},
            }],
            description="Reigns of 10 or more games, longest first.",
        )

def createReignList(teamList):
    """Create a list of all reigns."""
    reignList = []
    for team in teamList:
        if team.currentReign:
            reignList.append(team.currentReign.quickSum())
        for reign in team.reigns:
            reignList.append(reign.quickSum())
    return reignList

def topN(historyTeamList, num=25, outputFile=None, htmlTitle=None):
    """Generate top N rankings."""
    tableStr = f"All-Time Heavyweight Rankings\n"
    historyTeamList.sort(key=lambda x: x.rankingPoints, reverse=True)
    rows = []
    for i in range(min(num, len(historyTeamList))):
        team = historyTeamList[i]
        tableStr += team.rankSummary(i) + "\n"
        team.overallWLT()
        record = f"{team.w}-{team.l}-{team.t}" if team.t else f"{team.w}-{team.l}"
        rows.append((i + 1, team.name, team.numReigns, record))
    printFile(tableStr, outputFile)

    if outputFile:
        writeHtmlReportPage(
            outputFile.with_suffix('.html'),
            htmlTitle or "Rankings",
            [{
                'headers': ['Rank', 'Team', 'Reigns', 'Record'],
                'rows': rows,
                'numericCols': {0, 2},
            }],
        )

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
    rows = []
    for game in boutList:
        data += game.beltSum() + "\n"
        rows.append(boutRow(game))
    printFile(data, outputFile)

    if outputFile:
        writeHtmlReportPage(
            outputFile.with_suffix('.html'),
            "All Bouts",
            [{
                'headers': ['Date', 'Defending', 'Challenger', 'Score', 'Beltholder'],
                'rows': rows,
                'numericCols': {0},
            }],
        )

def boutRow(game):
    """Build a (date, defending, challenger, score, beltholder) row for a bout."""
    if not game.checkTie():
        winner, _ = game.getWinnerLoser()
    if game.defending is None:
        defending, challenger = game.teamA, game.teamB
        score = f"{game.scoreA}-{game.scoreB}"
        beltholder = winner
    elif game.checkTie():
        if game.defending == game.teamA:
            defending, challenger, score = game.teamA, game.teamB, f"{game.scoreA}-{game.scoreB}"
        else:
            defending, challenger, score = game.teamB, game.teamA, f"{game.scoreB}-{game.scoreA}"
        beltholder = game.defending
    else:
        defending, challenger = game.defending, game.challenger
        score = f"{game.scoreA}-{game.scoreB}" if game.defending == game.teamA else f"{game.scoreB}-{game.scoreA}"
        beltholder = winner
    return ((game.date, dateSortKey(game.date)), defending, challenger, score, beltholder)

def computeBeltLineage(boutList):
    """Walk all bouts and record every moment the belt changed hands."""
    lineage = []
    champ = None
    for game in boutList:
        if game.checkTie():
            continue  # champion retains the belt on a tie; no lineage change
        winner, loser = game.getWinnerLoser()
        if winner == champ:
            continue  # successful defense; no lineage change
        score = (game.scoreA, game.scoreB) if game.teamA == winner else (game.scoreB, game.scoreA)
        lineage.append({
            'date': game.date,
            'champ': winner,
            'previous': champ,
            'opponent': loser,
            'score': score,
        })
        champ = winner
    return lineage

def writeBeltLineage(boutList, outputFile):
    """Write the full belt-lineage timeline: every moment the title changed hands."""
    lineage = computeBeltLineage(boutList)

    entries_html = []
    for i, event in enumerate(lineage):
        champ = event['champ']
        opponent = event['opponent']
        scoreFor, scoreAgainst = event['score']
        if event['previous'] is None:
            detail = f"defeated {opponent} {scoreFor}-{scoreAgainst} to claim the vacant belt"
        else:
            detail = f"defeated {event['previous']} {scoreFor}-{scoreAgainst} to take the belt"
        entries_html.append(
            f'            <div class="timeline-entry">'
            f'<div class="timeline-year">#{i + 1} — {event["date"]}</div>'
            f'<div class="timeline-detail"><strong>{champ}</strong> {detail}</div></div>\n'
        )

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Belt Lineage</title>
    <link rel="stylesheet" href="../../web/assets/cfbHeavyweights.css">
</head>
<body>
    <div class="report-page">
        <a class="back-link" href="../../web/cfbHeavyweights.html">&larr; Back to Championship Page</a>
        <h1>Belt Lineage</h1>
        <p class="description">Every moment the College Football Heavyweight Championship changed hands — {len(lineage)} title changes across over 150 years.</p>
        <div class="timeline">
{''.join(entries_html)}        </div>
    </div>
</body>
</html>
"""
    outputFile.parent.mkdir(parents=True, exist_ok=True)
    with open(outputFile, 'w') as f:
        f.write(content)

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
"""
College Football Heavyweight Championship Tracker
Main module for generating championship webpage and reports.
"""

import os
from datetime import datetime
from pathlib import Path

from .data_loaders.getGames import readGamesFromWeb, writePlayedGamesFile, readTeamsFromWeb, writeTeamFile
from .models.heavyweightClasses import Team, Game, Reign
from .utils.helpers import findTeam, getCurrentSeason, findNth
from .analysis.heavyweightTracker import (
    createMasterFile, updateTeams, yearlyNationalChamps,
    dropInactiveTeamsWithNoHistory, createOtherLinks,
    getBeltTeam
)

# Configuration constants
WEB_DIR = Path('web')
HTML_FILE = WEB_DIR / 'cfbHeavyweights.html'
ASSETS_DIR = WEB_DIR / 'assets'
CSS_FILE = 'cfbHeavyweights.css'
LOGO_FILE = 'theChamp.jpeg'


def main():
    """Main entry point for the College Football Heavyweight Championship tracker."""
    print("Starting College Football Heavyweight Championship Tracker...")
    
    # Load and process data
    print("Loading game and team data...")
    boutList, historyTeamList, activeTeamList = createMasterFile()
    
    print("Calculating yearly champions...")
    champList = yearlyNationalChamps(boutList)
    
    print("Updating team statistics...")
    updateTeams(boutList, historyTeamList, champList)
    
    print("Filtering teams...")
    historyTeamList = dropInactiveTeamsWithNoHistory(activeTeamList, historyTeamList)
    
    print("Creating reports...")
    createOtherLinks(boutList, activeTeamList, historyTeamList, champList)
    
    print("Generating webpage...")
    beltTeam = getBeltTeam(boutList, historyTeamList)
    createWebpage(HTML_FILE, boutList, activeTeamList, historyTeamList, champList)
    
    print(f"\n✓ Complete! Current champion: {beltTeam.getName()}")
    print(f"✓ Webpage created at: {HTML_FILE}")
    print(f"✓ Reports created in: data/reports/")


def createWebpage(webpage, boutList, activeTeamList, historyTeamList, champList):
    """
    Create the main HTML webpage.
    
    Args:
        webpage: Path to output HTML file
        boutList: List of all championship bouts
        activeTeamList: List of currently active teams
        historyTeamList: List of all teams in history
        champList: List of yearly champions
    """
    beltTeam = getBeltTeam(boutList, historyTeamList)
    
    writeHTMLHeader(webpage, historyTeamList, beltTeam)
    writeChampInfo(webpage, beltTeam)
    writeCurrentReign(webpage, beltTeam)
    writePreviousReigns(webpage, beltTeam)
    writeChallenges(webpage, beltTeam)
    writeReportsSection(webpage)
    writeHTMLFooter(webpage)


def writeHTMLHeader(page, historyTeamList, beltTeam):
    """Write the HTML header, CSS link, and preamble."""
    numReigns = getTotalReigns(historyTeamList)
    numReigns = findNth(numReigns)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Football Heavyweight Championship</title>
    <link rel="stylesheet" href="{ASSETS_DIR.name}/{CSS_FILE}">
</head>
<body>
    <div class="container">
        <div class="center-image">
            <img src="{ASSETS_DIR.name}/{LOGO_FILE}" alt="Championship Image">
        </div>
        <div class="preamble">
            In boxing (and other sports), one becomes the champ by beating the champ. And they remain the champ until someone takes it from them. 
            What if college football did this? On November 6, 1869 Rutgers defeated Princeton 6-4 (in a game that more closely resembled soccer than 
            what we'd call football, but we're counting it anyway), winning the first College Football Heavyweight Bout. Princeton would win the 
            rematch 8-0 to take back the Belt. Since then, I've tracked the progress of the Belt and all the challenges for it. The {numReigns} (and current) 
            Heavyweight Champion of College Football is {beltTeam.getName()}.
        </div>
"""
    os.makedirs(os.path.dirname(page), exist_ok=True)
    with open(page, 'w') as file:
        file.write(html_content)


def writeChampInfo(webpage, beltTeam):
    """
    Write the current champion information table.
    
    Args:
        webpage: Path to HTML file
        beltTeam: Current belt holder Team object
    """
    cW, cL, cT, dW, dL, dT, numReigns, natties = beltTeam.records()
    
    with open(webpage, 'a') as file:
        file.write("        <!-- Current Champion Table -->\n")
        file.write("        <div class=\"small-table-container\">\n")
        file.write("            <div class=\"champ-header\">Current Champ</div>\n")
        file.write("            <div class=\"text-content\">\n")
        file.write("                <table class=\"table\">\n")
        
        # School name
        file.write("                    <tr>\n")
        file.write("                        <th>School</th>\n")
        file.write(f"                        <td>{beltTeam.getName()}</td>\n")
        file.write("                    </tr>\n")
        
        # Number of reigns
        file.write("                    <tr>\n")
        file.write("                        <th>Number of Reigns</th>\n")
        file.write(f"                        <td>{beltTeam.numReigns}</td>\n")
        file.write("                    </tr>\n")
        
        # National titles
        file.write("                    <tr>\n")
        file.write("                        <th>National Titles</th>\n")
        if natties > 0:
            file.write(f"                        <td>{natties} — ({beltTeam.getTitleString()})</td>\n")
        else:
            file.write("                        <td>0</td>\n")
        file.write("                    </tr>\n")
        
        # Records
        file.write("                    <tr>\n")
        file.write("                        <th>Record in Bouts</th>\n")
        file.write(f"                        <td>{dW+cW}-{dL+cL}-{dT+cT}</td>\n")
        file.write("                    </tr>\n")
        
        file.write("                    <tr>\n")
        file.write("                        <th>As Belt Holder</th>\n")
        file.write(f"                        <td>{dW}-{dL}-{dT}</td>\n")
        file.write("                    </tr>\n")
        
        file.write("                    <tr>\n")
        file.write("                        <th>As Challenger</th>\n")
        file.write(f"                        <td>{cW}-{cL}-{cT}</td>\n")
        file.write("                    </tr>\n")
        
        file.write("                </table>\n")
        file.write("            </div>\n")
        file.write("        </div>\n")


def writeCurrentReign(webpage, beltTeam):
    """
    Write the current reign section.
    
    Args:
        webpage: Path to HTML file
        beltTeam: Current belt holder Team object
    """
    currentReign = beltTeam.currentReign
    reignLength = len(currentReign.games)
    gs = "game" if reignLength == 1 else "games"
    
    with open(webpage, 'a') as file:
        file.write("<div class=\"content-section\">\n")
        file.write("    <h3>***Current Reign***</h3>\n")
        file.write(f"    <p>{reignLength} {gs}</p>\n")
        file.write("    <ul>\n")
        for game in currentReign.games:
            file.write(f"        <li>{str(game)}</li>\n")
        file.write("    </ul>\n")
        file.write("</div>\n\n")


def writePreviousReigns(webpage, beltTeam):
    """
    Write the previous reigns section.
    
    Args:
        webpage: Path to HTML file
        beltTeam: Current belt holder Team object
    """
    reigns = beltTeam.reigns
    
    if not reigns:
        return  # Skip if no previous reigns
    
    numReigns = len(reigns)
    
    with open(webpage, 'a') as file:
        file.write("<div class=\"content-section\">\n")
        file.write("    <h3>Previous Reigns:</h3>\n")
        
        for reign in reversed(reigns):
            reignGames = reign.games
            file.write(f"    <h4>Reign #{numReigns}</h4>\n")
            file.write("    <ul>\n")
            for game in reignGames:
                file.write(f"        <li>{str(game)}</li>\n")
            file.write("    </ul>\n")
            numReigns -= 1
        
        file.write("</div>\n\n")


def writeChallenges(webpage, beltTeam):
    """
    Write the challenges section.
    
    Args:
        webpage: Path to HTML file
        beltTeam: Current belt holder Team object
    """
    challenges = beltTeam.challenges
    numChall = len(challenges)
    gs = "time" if numChall == 1 else "times"
    numWins = beltTeam.numReigns
    
    with open(webpage, 'a') as file:
        file.write("<div class=\"content-section\">\n")
        file.write("    <h3>Challenges:</h3>\n")
        file.write(f"    <p>{beltTeam.getName()} has challenged {numChall} {gs}, winning {numWins}:</p>\n")
        file.write("    <ul>\n")
        
        for game in challenges:
            winner = game.winnerWas(beltTeam.getName())
            if winner:
                file.write(f"        <li><strong>{str(game)}</strong></li>\n")
            else:
                file.write(f"        <li>{str(game)}</li>\n")
        
        file.write("    </ul>\n")
        file.write("</div>\n\n")


def writeReportsSection(webpage):
    """
    Write the links to other reports.
    
    Args:
        webpage: Path to HTML file
    """
    column1_links = [
        ('All-Time Rankings', '../data/reports/allTimeRankings.txt'),
        ('School Reports', '../data/reports/schoolBySchool.txt'),
        ('Longest Reigns', '../data/reports/longestReigns.txt')
    ]
    column2_links = [
        ('Top 25 (Active FBS)', '../data/reports/top25Active.txt'),
        ('Yearly National Champions', '../data/reports/yearlyBeltWinners.txt'),
        ('All Bouts', '../data/reports/allBouts.txt')
    ]
    
    with open(webpage, 'a') as file:
        file.write("<div class=\"content-section\">\n")
        file.write("    <h3>Reports:</h3>\n")
        file.write("    <div class=\"links-container\">\n")
        
        # First column
        file.write("        <div class=\"links-column\">\n")
        for text, href in column1_links:
            file.write(f"            <a href=\"{href}\">{text}</a>\n")
        file.write("        </div>\n")
        
        # Second column
        file.write("        <div class=\"links-column\">\n")
        for text, href in column2_links:
            file.write(f"            <a href=\"{href}\">{text}</a>\n")
        file.write("        </div>\n")
        
        file.write("    </div>\n")
        file.write("</div>\n")


def writeHTMLFooter(webpage):
    """
    Write the HTML footer with compilation date.
    
    Args:
        webpage: Path to HTML file
    """
    with open(webpage, 'a') as file:
        file.write(f"    <p style=\"text-align: center; margin-top: 20px;\">")
        file.write(f"Compiled {datetime.now().strftime('%Y-%m-%d')}</p>\n")
        file.write("    </div>\n")  # Close container
        file.write("</body>\n")
        file.write("</html>\n")


def getTotalReigns(teamList):
    """
    Calculate total number of reigns across all teams.
    
    Args:
        teamList: List of Team objects
        
    Returns:
        int: Total number of reigns
    """
    return sum(team.numReigns for team in teamList)


if __name__ == "__main__":
    main()
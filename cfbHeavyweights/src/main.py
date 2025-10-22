import csv
import os
from datetime import datetime

from .data_loaders.getGames import readGamesFromWeb, writePlayedGamesFile, readTeamsFromWeb, writeTeamFile
from .models.heavyweightClasses import Team, Game, Reign
from .utils.helpers import findTeam, getCurrentSeason, findNth
from .analysis.heavyweightTracker import (
    createMasterFile, updateTeams, yearlyNationalChamps,
    dropInactiveTeamsWithNoHistory, createOtherLinks,
    getBeltTeam
)

def main():
    """Main entry point for the College Football Heavyweight Championship tracker."""
    boutList, historyTeamList, activeTeamList = createMasterFile()
    champList = yearlyNationalChamps(boutList)
    updateTeams(boutList, historyTeamList, champList)
    historyTeamList = dropInactiveTeamsWithNoHistory(activeTeamList, historyTeamList)
    createOtherLinks(boutList, activeTeamList, historyTeamList, champList)
    beltTeam = getBeltTeam(boutList, historyTeamList)
    createWebpage('web/cfbHeavyweights.html', boutList, activeTeamList, historyTeamList, champList)

def createWebpage(webpage, boutList, activeTeamList, historyTeamList, champList):
    """Create the main HTML webpage."""
    beltTeam = getBeltTeam(boutList, historyTeamList)
    
    writePreamble(webpage, historyTeamList, beltTeam)
    writeChampInfo(webpage, beltTeam)
    writeCurrentReign(webpage, beltTeam)
    writePreviousReigns(webpage, beltTeam)
    writeChallenges(webpage, beltTeam)
    otherLinks(webpage)

def writePreamble(page, historyTeamList, beltTeam):
    """Write the HTML preamble with styling."""
    numReigns = getTotalReigns(historyTeamList)
    numReigns = findNth(numReigns)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Football Heavyweight Championship</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
        }}
        .container {{
            max-width: 80%;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .center-image {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .center-image img {{
            width: 400px;
            height: 300px;
            object-fit: contain;
        }}
        .preamble {{
            text-align: justify;
            margin-top: 20px;
        }}
        .small-table-container {{
            max-width: 40%;
            margin: 0 auto;
        }}
        .champ-header {{
            text-align: center;
            padding: 10px 0;
            background-color: #2c3e50; /* Subtle navy */
            color: #ecf0f1; /* Light gray text */
            margin-bottom: 10px;
            font-size: 1.3em;
            letter-spacing: 1px;
            width: 100%;
            box-sizing: border-box;
        }}
        .table {{
            margin: 10px 0;
            border-collapse: collapse;
            width: 100%;
        }}
        .table th, .table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .table th {{
            background-color: #f2f2f2;
        }}
        .links-container {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }}
        .links-column {{
            width: 45%;
        }}
        .links-column a {{
            display: block;
            margin-bottom: 10px;
            text-decoration: none;
            color: #34495e; /* Dark, muted blue */
            font-weight: bold;
            transition: color 0.3s;
        }}
        .links-column a:hover {{
            color: #2980b9; /* Brighter blue on hover */
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="center-image">
            <img src="assets/theChamp.jpeg" alt="Championship Image">
        </div>
        <div class="preamble">
            In boxing (and other sports), one becomes the champ by beating the champ. And they remain the champ until someone takes it from them. 
            What if college football did this? On November 6, 1869 Rutgers defeated Princeton 6-4 (in a game that more closely resembled soccer than 
            what we'd call football, but we're counting it anyway), winning the first College Football Heavyweight Bout. Princeton would win the 
            rematch 8-0 to take back the Belt. Since then, I've tracked the progress of the Belt and all the challenges for it. The {numReigns} (and current) 
            Heavyweight Champion of College Football is {beltTeam.getName()}.
        </div>
    </div>
</body>
</html>"""
    os.makedirs(os.path.dirname(page), exist_ok=True)
    with open(page, 'w') as file:
        file.write(html_content)

def preamble(preamblePage, outpage):
    """Copy preamble to output page - NOT USED ANYMORE."""
    pass

def writeCurrentReign(webpage, beltTeam):
    """Write the current reign section."""
    currentReign = beltTeam.currentReign
    reignLength = len(currentReign.games)
    gs = "game" if reignLength == 1 else "games"
    with open(webpage, 'a') as file:
        file.write("<h3>***Current Reign***</h3\n")
        file.write(f"        <p>{reignLength} {gs}</p>\n")
        file.write("        <ul>\n")
        for game in currentReign.games:
            file.write(f"            <li>{str(game)}</li>\n")
        file.write("        </ul>\n\n")

def writePreviousReigns(webpage, beltTeam):
    """Write the previous reigns section."""
    reigns = beltTeam.reigns
    numReigns = len(reigns)
    with open(webpage, 'a') as file:
        file.write("<h3>Previous Reigns:</h3>\n")
        for reign in reversed(reigns):
            reignGames = reign.games
            file.write(f"        <h4>Reign #{numReigns}</h4>\n")
            file.write("        <ul>\n")
            for game in reignGames:
                file.write(f"            <li>{str(game)}</li>\n")
            file.write("        </ul>\n\n")
            numReigns -= 1

def writeChallenges(webpage, beltTeam):
    """Write the challenges section."""
    challenges = beltTeam.challenges
    numChall = len(challenges)
    gs = "time" if numChall == 1 else "times"
    numWins = beltTeam.numReigns
    with open(webpage, 'a') as file:
        file.write("    <h3>Challenges:</h3>\n")
        file.write(f"    <p>{beltTeam.getName()} has challenged {numChall} {gs}, winning {numWins}:</p>\n")
        file.write("        <ul>\n")
        for game in challenges:
            winner = game.winnerWas(beltTeam.getName())
            if winner:
                file.write(f"        <li><strong>{str(game)}</strong></li>\n")
            else:
                file.write(f"        <li>{str(game)}</li>\n")
        file.write("    </ul>\n\n")

def otherLinks(webpage):
    """Write the links to other reports and close HTML."""
    column1Links = [
        ('All-Time Rankings', '../data/reports/allTimeRankings.txt'),
        ('School Reports', '../data/reports/schoolBySchool.txt'),
        ('Longest Reigns', '../data/reports/longestReigns.txt')
    ]
    column2Links = [
        ('Top 25 (Active FBS)', '../data/reports/top25Active.txt'),
        ('Yearly National Champions', '../data/reports/yearlyBeltWinners.txt'),
        ('All Bouts', '../data/reports/allBouts.txt')
    ]
    with open(webpage, 'a') as file:
        file.write("\n<h3>Reports:</h3>    <!-- Links in Two Columns -->\n")
        file.write("    <div class=\"links-container\">\n")
        file.write("        <div class=\"links-column\">\n")
        for text, href in column1Links:
            file.write(f"            <a href=\"{href}\">{text}</a>\n")
        file.write("        </div>\n")
        file.write("        <div class=\"links-column\">\n")
        for text, href in column2Links:
            file.write(f"            <a href=\"{href}\">{text}</a>\n")
        file.write("        </div>\n")
        file.write("    </div>\n\n")
        file.write(f"Compiled {datetime.now().strftime('%Y-%m-%d')}")

def writeChampInfo(webpage, beltTeam):
    """Write the current champion information table."""
    cW, cL, cT, dW, dL, dT, numReigns, natties = beltTeam.records()
    with open(webpage, 'a') as file:
        file.write("        <!-- Smaller Table Container -->        <div class=\"small-table-container\">\n")
        file.write("            <!-- Champ Header above the table -->            <div class=\"champ-header\">                Current Champ            </div>\n")
        file.write("            <!-- Text Content -->            <div class=\"text-content\">\n")
        file.write("                <table class=\"table\">")
        file.write("                    <tr>                        <th>School</th>")
        file.write(f"                        <td>{beltTeam.getName()}</td>                    </tr>")
        file.write("                    <tr>                        <th>Number of Reigns</th>")
        file.write(f"                        <td>{beltTeam.numReigns}</td>                    </tr>")
        file.write("                    <tr>                        <th>National Titles</th>")
        if natties > 0:
            file.write(f"                        <td>{natties} — ({beltTeam.getTitleString()})</td>                    </tr>")
        else:
            file.write(f"                        <td>0</td>                    </tr>")
        file.write("                    <tr>                        <th>Record in Bouts</th>")
        file.write(f"                        <td>{dW+cW}-{dL+cL}-{dT+cT}</td>                    </tr>")
        file.write("                    <tr>                        <th>As Belt Holder</th>")
        file.write(f"                        <td>{dW}-{dL}-{dT}</td>                    </tr>")
        file.write("                    <tr>                        <th>As Challenger</th>")
        file.write(f"                        <td>{cW}-{cL}-{cT}</td>                    </tr>                </table>\n")
        file.write("            </div>\n")
        file.write("        </div>")

def getTotalReigns(teamList):
    """Calculate total number of reigns across all teams."""
    return sum(team.numReigns for team in teamList)

if __name__ == "__main__":
    main()
#02.22.24
#getGames
#copied from cfbKpi, including date. Probably should there as well but uncertain of consequences
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
from Game import Game
from Team import Team
import os
import csv

def main():
	year=getCurrentSeason(datetime.now())
	for season in range(year,year+1):
		if season==1871:
			continue
		gameList=readGamesFromWeb(season)
		writePlayedGamesFile("Games/%sGames.csv" % season,gameList)
		teamList=readTeamsFromWeb(season)
		writeTeamFile("Teams/%sTeams.csv" % season,teamList)


def getCurrentSeason(date):
	if date.month<9:
		return date.year-1
	else:
		return date.year

#------------------------------------------------------------------------------
# readTeamsFromWeb(int)
# pull teams off of sports reference site
#------------------------------------------------------------------------------
def readTeamsFromWeb(year):
	print("Team file does not exist. Reading team list from web.")
	teamID = 0 #initialize teamID
	year = str(year)
	teamList=[]

	#create url and open page
	url = "https://www.sports-reference.com/cfb/years/" + year + "-standings.html"
	html = urlopen(url)
	soup = BeautifulSoup(html, "html.parser")
	#print soup
	for tr in soup.find_all('tr')[2:]:
		tds = tr.find_all('td')
		if len(tds) > 0:
			name = convertTeamName(tds[0].text)
			conference = tds[1].text
			createdTeam = Team(teamID,name,conference,0,0)
			teamList.append(createdTeam)
			teamID += 1
	#addFCSTeam() #to catch teams that are not included on the team list
	return teamList

#------------------------------------------------------------------------------
# readGamesFromFile(int)
# for quicker access, read a file
#------------------------------------------------------------------------------
def readGamesFromFile(readFile,year):
	if not os.path.exists(readFile):
		readGamesFromWeb(year)
	else:
		print("Reading games from file.")
		with open(readFile,'r') as r:
			reader = csv.reader(r)
			for row in reader:
				gameID = int(row[0])
				week = int(row[1])
				winner = row[2]
				winPoints=int(row[3])
				loser=row[4]
				loserPoints=int(row[5])
				awayWin =row[6]
				if awayWin == 1:
					createdGame = Game(gameID,week,loser,loserPoints,winner,winPoints)
					gameList.append(createdGame)
				else:
					createdGame = Game(gameID,week,loser,loserPoints,winner,winPoints)
					gameList.append(createdGame)

#------------------------------------------------------------------------------
# readGamesFromWeb(int)
#------------------------------------------------------------------------------
def readGamesFromWeb(year):
	print("Reading games from the web.")
	gameID = 0
	year = str(year)
	url = "https://www.sports-reference.com/cfb/years/%s-schedule.html" % str(year)
	html = urlopen(url)
	soup = BeautifulSoup(html,"html.parser")
	gameList=[]

	#sport-reference includes the time of the game from 2013 on
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
				elif(awayWin == '@'):
					createdGame = Game(gameID,week,date,winner,winPoints,loser,loserPoints)
					gameList.append(createdGame)
					gameID += 1
				else:
					createdGame = Game(gameID,week,date,loser,loserPoints,winner,winPoints)
					gameList.append(createdGame)
					gameID += 1
	else:
		for tr in soup.find_all('tr')[1:]:
			tds = tr.find_all('td')
			if len(tds) > 0:
				week = tds[0].text
				date=tds[1].text
				winner = stripRank(tds[3].text)
				winPoints = tds[4].text
				awayWin = tds[5].text
				loser = stripRank(tds[6].text)
				loserPoints = tds[7].text
				if winPoints == "":
					pass
				elif(awayWin == '@'):
					createdGame = Game(gameID,week,date,winner,winPoints,loser,loserPoints)
					gameList.append(createdGame)
					gameID += 1
				else:
					createdGame = Game(gameID,week,date,loser,loserPoints,winner,winPoints)
					gameList.append(createdGame)
					gameID += 1
	return gameList
#------------------------------------------------------------------------------
# writePlayedGameFile(string)
# write a file of all games played
# fileName represents path within directory
#------------------------------------------------------------------------------
def writePlayedGamesFile(fileName,gameList):
	if os.path.exists(fileName): os.remove(fileName)
	print("Writing game file %s" % fileName)
	with open(fileName,"w") as f:
		writer = csv.writer(f)
		for game in gameList:
			if game == None:
				pass
			else:
				awayWin =1 if game.awayScore>game.homeScore else 0
				if awayWin == 1:
					gameFileList=[game.gameID,game.week,game.date,game.away,game.awayScore,game.home,game.homeScore,awayWin]
				else:
					gameFileList=game.gameID,game.week,game.date,game.home,game.homeScore,game.away,game.awayScore,awayWin
			writer.writerow(gameFileList)
	f.close()
	print("Game File Written: %s" % fileName)

#------------------------------------------------------------------------------
# writeTeamFile(string)
# write a file of all teams for a given year
# fileName represents path within directory
#------------------------------------------------------------------------------
def writeTeamFile(fileName,teamList):
	if os.path.exists(fileName): os.remove(fileName)
	print("Writing team file %s" % fileName)
	with open(fileName,"w") as f:
		writer = csv.writer(f)
		for team in teamList:
			writer.writerow([team.teamID,team.name,team.conference])
	f.close()
	print("Team File Written: %s" % fileName)

#------------------------------------------------------------------------------
# stripRank(string)
# sports reference gives us the team rank with its game data, this strips it
# for example, if a team is ranked #3, it will take (3) UCLA and return UCLA
#------------------------------------------------------------------------------
def stripRank(teamName):
	if teamName[0] == '(':
		return convertTeamName(teamName[teamName.find(')')+2:])
	else:
		return convertTeamName(teamName)

#------------------------------------------------------------------------------
# convertTeamName(string)
# converts team names from sports reference name to my name
# example: Louisiana State becomes LSU, Miami (FL) becomes Miami
# handles names case by case
#------------------------------------------------------------------------------
def convertTeamName(teamName):
	if teamName[len(teamName)-1] == ';': return teamName[0:len(teamName)-1]
	elif teamName == "Miami (FL)": return "Miami"
	elif teamName == "Middle Tennessee State": return "Middle Tennessee"
	elif teamName == "Florida International": return "Florida Int'l"
	elif teamName == "Southern California": return "USC"
	elif teamName == "Louisiana State": return "LSU"
	elif teamName == "Texas-El Paso": return "UTEP"
	elif teamName == "Bowling Green State": return "Bowling Green"
	elif teamName == "Brigham Young": return "BYU"
	elif teamName == "Texas Christian": return "TCU"
	elif teamName == "Mississippi": return "Ole Miss"
	elif teamName == "Nevada-Las Vegas": return "UNLV"
	elif teamName == "Pittsburgh": return "Pitt"
	elif teamName == "Central Florida": return "UCF"
	elif teamName == "Southern Methodist": return "SMU"
	elif teamName == "Alabama-Birmingham": return "UAB"
	elif teamName == "North Carolina State": return "NC State"
	elif teamName == "Pittsburgh": return "Pitt"
	elif teamName == "Southern Mississippi": return "Southern Miss"
	elif teamName == "Texas-San Antonio": return "UTSA"
	else: return teamName

if __name__=="__main__":
	main()
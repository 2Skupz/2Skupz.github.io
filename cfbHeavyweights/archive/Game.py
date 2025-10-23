
#Ken Schroeder
#10.30.15
#Home, Cyan PDX, Portland, OR
#Rainy
#Class for storing Games
#Updated 3/18/17
#Game.py

#-----------------------------------------------------------------------------
# getPointDiff(int,int)
# returns point differential, home team - away team (an away win is negative)
#-----------------------------------------------------------------------------
def getPointDiff(homeScore, awayScore):
	return homeScore - awayScore

#-----------------------------------------------------------------------------
# gameResult(list<int>)
# determines if the game was a win, loss, or tie
#-----------------------------------------------------------------------------
def gameResult(score):
	if score[0] == score[1]:
		return 't'
	elif int(score[0]) > int(score[1]):
		return 'W'
	else:
		return 'L'

#-----------------------------------------------------------------------------
# Game
# variables:
#   gameID (int): ID of the game
#   week (int): week the game was played
#   away (Team): who the away team is
#   awayScore (int): how many points the away team scored
#   home (Team): who the home team is
#   homeScore (int): how many points the home teams cored
#   point diff(int): home points - away points
#-----------------------------------------------------------------------------
class Game:
	def __init__(self, gameID, week, date,away, awayScore, home, homeScore):
		self.gameID = gameID
		self.week = week
		self.date = date
		self.away = away
		self.awayScore = awayScore
		self.home = home
		self.homeScore = homeScore
		self.pointDiff = getPointDiff(int(homeScore), int(awayScore))

#-----------------------------------------------------------------------------
# toString
# prints game results screen
#-----------------------------------------------------------------------------
	def toString(self):
		points = int(self.pointDiff)
		gameID = (str(self.gameID) + ". ").rjust(4) + "\t"
		if (points == 0):
			pass
		elif (points < 0):
			print(gameID + self.away + " defeats " + self.home + " by " + str(-1*points))
		else:
			print(gameID + self.home + " defeats " + self.away + " by " + str(points))

#-----------------------------------------------------------------------------
# toCSV
# returns CSV version of game
#-----------------------------------------------------------------------------
	def toCSV(self):
		return (self.gameID,self.week,self.date,self.away,self.awayScore,self.home,self.homeScore)

#-----------------------------------------------------------------------------
# toUpsetString
# prints game results screen
#-----------------------------------------------------------------------------
	def toUpsetString(self):
		points = int(self.pointDiff)
		gameID = (str(self.gameID)+".").ljust(7)
		print(gameID + self.home.ljust(25) + self.away.ljust(25)+str(points))

#-----------------------------------------------------------------------------
# oneWayScheduleString(string)
# print the game vital stats from one teams perspective
#-----------------------------------------------------------------------------
	def oneWayScheduleString(self,teamName):
		week = str(self.week).ljust(4)
		gameID = str(self.gameID).ljust(5)
		away = "@ " if self.away==teamName else ""
		opponent = away + (self.away if self.home==teamName else self.home)
		opponent=opponent.ljust(20)
		teamPts = self.awayScore if away=="@ " else self.homeScore
		oppPts = str(self.homeScore if away=="@ " else self.awayScore)
		result = "W" if int(teamPts) > int(oppPts) else "L"
		result = result.ljust(8)
		score = "%s-%s" % (teamPts,oppPts)
		if teamPts == oppPts: result = "T"
		print(week + gameID + opponent + result + score)

#-----------------------------------------------------------------------------
# toScheduleString
# print the game vital stats
#-----------------------------------------------------------------------------
	def toScheduleString(self):
		week = str(self.week).ljust(4)
		gameID = str(self.gameID).ljust(5)
		away = str(self.away).ljust(20)
		awayPts = str(self.awayScore).ljust(4)
		home = str(self.home).ljust(20)
		homePts = str(self.homeScore).ljust(4)
		print(week + gameID + away + awayPts + home + homePts)


#-----------------------------------------------------------------------------
# toGameScoreString(team,list<int>)
# prints a string of the game results
#-----------------------------------------------------------------------------
	def toGameScoreString(self, opponent, score):
		week = str(self.week).ljust(4)
		gameID = str(self.gameID).ljust(5)
		oppName = str(opponent.name).ljust(20)
		scoreString = str(score[0]).rjust(3) + "-" + str(score[1]).ljust(3)
		result = str(gameResult(score)) +","
		return week + gameID + oppName + result + scoreString

#-----------------------------------------------------------------------------
# testTheGame
# test that all new features are incorporated correctly
#-----------------------------------------------------------------------------
def testTheGame():
	testGame = Game(1, 1, "Oregon", 21, "California", 17)
	print(testGame.gameID)
	print(testGame.week)
	print(testGame.away)
	print(testGame.awayScore)
	print(testGame.home)
	print(testGame.homeScore)
	print(testGame.pointDiff)

#-----------------------------------------------------------------------------
# main
# just testing everything is working
#-----------------------------------------------------------------------------
if __name__ == "__main__":
	print("Testing the game class")
	testTheGame()

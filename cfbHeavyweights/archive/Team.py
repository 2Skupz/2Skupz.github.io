#Ken Schroeder
#10.31.15
#Home, Cyan PDX, Portland, OR
#Perfectly Halloweeny
#A program that takes a series of games and prints out rankings
#Team.py

def winLossString(wins, losses, ties, tiesExist):
	if int(tiesExist) > 0:
		return winLossTieString(wins,losses,ties)
	winString = str(wins).rjust(3)
	lossString = str(losses).ljust(3)
	return winString + "-" + lossString

def winLossTieString(wins, losses, ties):
	firstBlank = " "
	winString = str(wins).rjust(3)
	lossString = str(losses).rjust(3)
	tieString = str(ties).rjust(3)
	return " " + winString + lossString + tieString
	
class Team:
	def __init__(self, id, name, conference, wins, losses):
		self.teamID = id
		self.name = name
		self.conference = conference
		self.wins = wins
		self.losses = losses
		self.ties = 0
		self.setWRS(0)
		self.setSRS(0)
		self.setKRS(0)
		self.setSOS(0)

	def clear(self):
		self.wins = 0
		self.losses = 0
		self.ties = 0
		self.setWRS(0)
		self.setSRS(0)
		self.setKRS(0)
		self.setSOS(0)

	def addWin(self):
		self.wins =int(self.wins) + 1

	def addLoss(self):
		self.losses = int(self.losses) + 1

	def addTie(self):
		self.ties = int(self.ties) + 1

	def setWRS(self, rating):
		self.WRSRating = rating

	def setSRS(self, rating):
		self.srsRating = rating

	def setKRS(self, rating):
		self.krsRating = rating

	def setSOS(self, sos):
		self.sos = sos

	def setWRSRank(self, rank):
		self.WRSRank = rank

	def setSRSRank(self,rank):
		self.srsRank = rank

	def setKRSRank(self,rank):
		self.krsRank = rank

	def setSOSRank(self,rank):
		self.sosRank = rank

	def calculateWP(self):
		if int(self.wins) or int(self.losses) or int(self.ties)> 0:
			numerator = float(self.wins) + float(self.ties)/2
			denomenator = float(self.wins) + float(self.ties) + float(self.losses)
			self.winPerc = round(numerator/denomenator,3)
		else:
			self.winPerc = .499999999999

	def getWRSPercent(self, min, max):
		if min == max:
			return .5
		else:
			numerator = float(self.WRSRating - min)
			denominator = float(max - min)
			return float(numerator / denominator)

	def getSRSPercent(self, min, max):
		if min == max:
			return .5
		else:
			numerator = float(self.srsRating - min)
			denominator = float(max - min)
			return float(numerator / denominator)

	def toListString(self, tiesAllowed):
		teamName = str(self.name).ljust(20)
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		wrs = str(self.WRSRating).rjust(7)
		srs = str(self.srsRating).rjust(8)
		krs = str(self.krsRating).rjust(8)
		cString = str(self.WRSRank).rjust(5)
		sString = str(self.srsRank).rjust(5)
		kString = str(self.krsRank).rjust(5)
		schedString = str(self.sosRank).rjust(4)
		print(teamName + winLoss + wrs + srs + krs + cString + sString + kString, end=' ')
		print(schedString)

	def nameWithRank(self):
		teamName = str(self.name).ljust(20)
		teamRank = str("#" + str(self.krsRank) + " ").rjust(5)
		return teamRank +  teamName

	def wlString(self, tiesAllowed):
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		return winLoss

	def toWRSString(self, tiesAllowed):
		rankString = str(self.WRSRank) + ". "
		rankString = str(rankString).rjust(5)
		teamName = str(self.name).ljust(20)
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		wrs = str(self.WRSRating).rjust(9)
		conf = str("  " + str(self.conference)).ljust(16)
		return rankString + teamName + winLoss + wrs + conf
		
	def toSRSString(self, tiesAllowed):
		rankString = str(self.srsRank) + ". "
		rankString = str(rankString).rjust(5)
		teamName = str(self.name).ljust(20)
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		srs = str(self.srsRating).rjust(9)
		conf = str("  " + str(self.conference)).ljust(16)
		return rankString + teamName + winLoss + srs + conf

	def toKRSString(self, tiesAllowed):
		teamName = str(self.name).ljust(20)
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		krs = str(self.krsRating).rjust(7)
		wrs = str(self.WRSRating).rjust(7)
		srs = str(self.srsRating).rjust(9)
		conf = str("  " + str(self.conference)).ljust(16)
		return teamName + winLoss + krs + srs + wrs + conf

	def toSOSString(self, tiesAllowed):
		teamName = str(self.name).ljust(20)
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		sos = str(self.sos).rjust(6)
		conf = str("  " + str(self.conference)).ljust(16)
		return teamName + winLoss + sos + conf

	def rankString(self, tiesAllowed):
		teamName = str(self.name).ljust(20)
		krs = str(self.krsRank).rjust(5)
		srs = str(self.srsRank).rjust(5)
		wrs = str(self.WRSRank).rjust(5)
		sos = str(self.sosRank).rjust(5)
		conf = str("  " + str(self.conference).ljust(16))
		winLoss = winLossString(self.wins, self.losses, self.ties, tiesAllowed)
		print(teamName + winLoss + krs + srs + wrs + sos + conf)

	def toConfStandingsString(self, tiesAllowed):
		winLoss = self.wlString(tiesAllowed)
		teamName = " " + str(self.name).ljust(20)
		krs = str(self.krsRating).rjust(7)
		krsRank = str(self.krsRank).rjust(5)
		return teamName + winLoss + krs + krsRank

	def records(self):
		return (self.challengeWins,self.challengeLosses,self.challengeTies,self.beltWins,self.beltLosses,self.beltTies,len(self.nationalTitles))

	'''
	Other ideas:
	WRS Rating
	SRS Rating
	SRS SOS
	Win Percentage
	KCS Rating
		(<WRS Percentile> + <SRS Percentile> + <Win Percentage>)/3

'''
def testTheTeam():
	team = Team(1,"Portland St", "Big Sky", 23, 7, 7.5)
	print(team.teamID)
	print(team.name)
	print(team.conference)
	print(team.wins)
	print(team.losses)
	print(team.rating)

if __name__ == "__main__":
	print("Testing the team class")
	testTheTeam()
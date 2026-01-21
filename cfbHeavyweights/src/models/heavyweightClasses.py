class Team:
    def __init__(self,name):
        self.name=name
        self.reigns=[]
        self.currentReign=[]
        self.beltWins=0
        self.challengeWins=0
        self.beltLosses=0
        self.challengeLosses=0
        self.beltTies=0
        self.challengeTies=0
        self.overallWLT()
        self.rankingPoints=0
        self.defenses=0
        self.numReigns=0
        self.challenges=[]
        self.seasonsPlayed=[]
        self.nationalTitles=[]
        self.currentReign=None

    def getName(self,just=1):
        return self.name.ljust(just)

    def startReign(self,game):
        self.currentReign=Reign(self.getName())
        self.addToReign(game)

    def addToReign(self,game):
        self.currentReign.add(game)

    def endReign(self,game):
        self.addToReign(game)
        self.reigns.append(self.currentReign)
        self.currentReign=None

    def addChallenge(self,game):
        self.challenges.append(game)

    def addNationalTitle(self,year):
        self.nationalTitles.append(year)

    def overallWLT(self):
        self.w=self.beltWins+self.challengeWins
        self.l=self.beltLosses+self.challengeLosses
        self.t=self.beltTies+self.challengeTies

    def setStats(self):
        self.numReigns=len(self.reigns)
        if self.currentReign!=None:
            self.numReigns+=1
        self.numChallenges=len(self.challenges)
        self.getBeltRecord()
        self.setRankingPoints()

    def setRankingPoints(self):
        self.overallWLT()
        self.beltGP=self.w+self.t+self.l
        self.beltWP=(self.w+self.t/2)/(self.beltGP) if self.beltGP>0 else 0
        self.rankingPoints+=100*self.numReigns
        self.rankingPoints+=10000*self.w
        self.rankingPoints+=(self.beltWP/1000)
        if self.w==0:
            self.rankingPoints=self.t+self.l/1000

    def getBeltRecord(self):
        if self.currentReign!=None:
            for idx, game in enumerate(self.currentReign.games):
                if idx == 0:
                    continue  # Skip the first game - it was a challenge, not a defense
                self.beltWins+=1

        for reign in self.reigns:
            for idx, game in enumerate(reign.games):
                if idx == 0:
                    continue  # Skip the first game - it was a challenge, not a defense

                if game.checkTie():
                    self.beltTies+=1
                else:
                    winner,loser=game.getWinnerLoser()
                    if winner==self.name:
                        self.beltWins+=1
                    elif loser==self.name:
                        self.beltLosses+=1
                    else:
                        print("ERROR")
                        print(game)

        for game in self.challenges:
            if game.checkTie():
                self.challengeTies+=1
            else:
                winner,loser=game.getWinnerLoser()
                if loser==self.name:
                    self.challengeLosses+=1
                elif winner==self.name:
                    self.challengeWins+=1


    def basicStatSum(self):
        print("Team: %s" % self.name)
        print("\tNum Reigns: %d" % self.numReigns)
        titlesString=self.getTitleString()
        print(f"\tNational Titles: {len(self.nationalTitles)} - ({titlesString})")
        print("\tOverall: %d-%d-%d" % (self.beltWins,self.beltLosses,self.beltTies))
        dW=self.beltWins-self.challengeWins
        dL=self.beltLosses-self.challengeLosses
        dT=self.beltTies-self.challengeTies
        print(f"\tAs Belt Holder: {dW}-{dL}-{dT}")
        print("\tAs Challenger: %d-%d-%d" % (self.challengeWins,self.challengeLosses,self.challengeTies))


    def getTitleString(self,delimiter=", "):
        return delimiter.join(map(str,self.nationalTitles))

    def printAllReigns(self):
        num=len(self.reigns)
        for reign in reversed(self.reigns):
            print(f"Reign #{num}")
            reign.printGames()
            num-=1
            print()

    def rankSummary(self,rank):
        rank=str(rank+1).rjust(3)
        name=self.name.ljust(32)
        numReigns=str(self.numReigns).ljust(8)
        self.overallWLT()
        wlt=self.wlString('overall')
        return ("%s %s%s%s" % (rank,name,numReigns,wlt.ljust(12)))

    def getLastReign(self):
        if self.currentReign!=None:
            return self.currentReign
        return self.reigns[-1]

    def printChallenges(self):
        print(f"{self.getName()} has challenged {len(self.challenges)} times for the belt, winning {self.numReigns}.")
        for game in self.challenges:
            if not game.checkTie():
                w,l=game.getWinnerLoser()
                prepend="*".rjust(6) if w==self.getName() else " "
            print(f"{prepend}\t{game}")

    def records(self):
        return (self.challengeWins,self.challengeLosses,self.challengeTies,self.beltWins,self.beltLosses,self.beltTies,self.numReigns,len(self.nationalTitles))

    def wlString(self,series):
        if series=='overall':
            if self.t!=0:
                return f"{self.w}-{self.l}-{self.t}"
            else:
                return f"{self.w}-{self.l}"


    def __str__(self):
        return self.getName()

class Reign:
    def __init__(self,team):
        self.team=team
        self.games=[]
        self.w=0
        self.l=0

    def add(self,game):
        self.games.append(game)

    def length(self):
        return len(self.games)

    def printGames(self):
        print(f"{self.length()} games")
        for game in self.games:
            print(f"..{game}")

    def quickSum(self):
        firstBout=self.games[0]
        lastBout=self.games[-1]
        return [self.length(),self.team,firstBout.date,lastBout.date]

    def __str__(self):
        return f"Reign lasted {len(self.games)} games."


class Game:
    def __init__(self,teamA,teamB,scoreA,scoreB,date,bout=False):
        self.teamA=teamA
        self.teamB=teamB
        self.scoreA=scoreA
        self.scoreB=scoreB
        self.date=date
        self.bout=bout

    def titleFight(self,fightBool=True):
        self.bout=fightBool

    def checkTie(self):
        return self.scoreA==self.scoreB

    def getWinnerLoser(self):
        if self.scoreA>self.scoreB:
            return self.teamA,self.teamB
        elif self.scoreB>self.scoreA:
            return self.teamB,self.teamA


    def addStakes(self,defending):
        if defending==None:
            self.defending=None
            self.challenger=None
        elif self.teamA==defending:
            self.defending=self.teamA
            self.challenger=self.teamB
        elif self.teamB==defending:
            self.defending=self.teamB
            self.challenger=self.teamA

    def beltSum(self):
        date=self.date.ljust(16)
        score=str("%d-%d" % (self.scoreA,self.scoreB)).ljust(11)
        if not self.checkTie(): winner,loser=self.getWinnerLoser()
        if self.defending==None:
            return "%s%s%s%s%s" % (date,self.teamA.ljust(20),self.teamB.ljust(24),score,winner)
        elif self.checkTie():
            if self.defending==self.teamA:
                return "%s%s%s%s%s" % (date,self.teamA.ljust(20),self.teamB.ljust(24),score,self.defending)                
            else:
                return "%s%s%s%s%s" % (date,self.teamB.ljust(20),self.teamA.ljust(24),score,self.defending)
        else:
            return "%s%s%s%s%s" % (date,self.defending.ljust(20),self.challenger.ljust(24),score,winner)

    def winnerWas(self,name):
        if self.checkTie():
            return False
        w,l=self.getWinnerLoser()
        return w==name

    def __str__(self):
        return "%s %s %d:%d %s" % (self.date.ljust(14),self.teamA,self.scoreA,self.scoreB,self.teamB)
from pybaseball import schedule_and_record as teamSched
from utils import game

class Team:
    def __init__(self, abbr, city, nickname, league, division):
        self.abbr = abbr
        self.city = city
        self.nickname = nickname
        self.league = league
        self.division = division
        self.w = 0
        self.l = 0
        self.rf = 0
        self.ra = 0
        self.rd = 0
        self.sched = []

    def __str__(self):
        return f"{self.city} {self.nickname}"

    def __repr__(self):
        return f"{self.nickname} ({self.abbr})"

    def standingsStr(self):
        return f"{self.abbr:<20} {self.w:<4} {self.l:<4} {self.rd:<5}"

    def getCurrentYearSchedule(self, season, teamList):
        """Fetch schedule from pybaseball and return completed games"""
        playedGames = []
        try:
            schedule = teamSched(season, self.abbr)
            pandaList = schedule.values.tolist()
            for gameList in pandaList:
                # Check if game has a decision (W/L value at index 4)
                dec = gameList[4]
                if dec is not None:
                    newGame = game.createGameFromPandaList(season, gameList)
                    playedGames.append(newGame)
        except Exception as e:
            print(f"Error fetching schedule for {self.abbr}: {e}")
        
        return playedGames

    def reset(self):
        self.w = 0
        self.l = 0
        self.rf = 0
        self.ra = 0

    def addGame(self, game):
        self.sched.append(game)

    def addWin(self, game):
        self.addGame(game)
        self.w += 1
        self.rf += game.winRun
        self.ra += game.lossRun

    def addLoss(self, game):
        self.addGame(game)
        self.l += 1
        self.rf += game.lossRun
        self.ra += game.winRun

    def calcWp(self):
        self.gp = self.w + self.l
        if self.gp == 0:
            self.wp = 0
        else:
            self.wp = self.w / self.gp

    def setRD(self):
        self.rd = self.rf - self.ra
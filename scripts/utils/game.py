from datetime import datetime

def getResult(runsAway, runsHome, awayTeam, homeTeam):
    if runsHome > runsAway:
        return homeTeam, awayTeam, runsHome, runsAway
    elif runsAway > runsHome:
        return awayTeam, homeTeam, runsAway, runsHome
    else:
        return None, None, None, None

def createGameFromPandaList(season, pandaList):
    """Create Game from pybaseball schedule list"""
    day = pandaList[0]
    team1 = pandaList[1]
    team1Site = pandaList[2]
    team2 = pandaList[3]
    team1Runs = pandaList[5]
    team2Runs = pandaList[6]
    inn = pandaList[7]
    weekday, yearday = formatDay(season, day)
    runsAway, runsHome, awayTeam, homeTeam = sortTeams(team1, team1Site, team2, team1Runs, team2Runs)
    return Game(weekday, yearday, awayTeam, homeTeam, runsAway, runsHome, inn)

def formatDay(season, day):
    """Parse day string and return (weekday_int, day_of_year)"""
    weekdayStr, datePart = day.split(', ')
    if "(" in datePart:
        datePart = datePart.split('(')[0]
    weekdayMap = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    weekdayInt = weekdayMap[weekdayStr]
    dateObj = datetime.strptime(datePart + f' {season}', '%b %d %Y')
    dayOfYear = dateObj.timetuple().tm_yday
    return weekdayInt, dayOfYear

def sortTeams(team1, team1Site, team2, team1Runs, team2Runs):
    """Determine away/home teams and sort runs accordingly"""
    if team1Site == 'Home':
        return team2Runs, team1Runs, team2, team1
    else:
        return team1Runs, team2Runs, team1, team2

def createGameFromList(gameData):
    """Create Game from CSV row data"""
    day = int(gameData[0])
    date = int(gameData[1])
    away = gameData[2]
    home = gameData[3]
    ra = int(gameData[4])
    rh = int(gameData[5])
    inn = int(gameData[6])
    return Game(day, date, away, home, ra, rh, inn)

class Game:
    def __init__(self, day, date, away, home, ra, rh, inn=9):
        self.day = day
        self.date = date
        self.away = away
        self.home = home
        self.ra = int(ra)
        self.rh = int(rh)
        self.inn = int(inn)
        self.winner, self.loser, self.winRun, self.lossRun = getResult(self.ra, self.rh, self.away, self.home)

    def __str__(self):
        return f'{self.day} {self.date:<4} {self.away} {self.ra:<3} {self.home} {self.rh:<3} ({self.inn})'

    def getGameKey(self):
        """Unique identifier for deduplication"""
        return (self.date, self.away, self.home)
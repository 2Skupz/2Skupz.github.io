from datetime import datetime

def findTeam(teamList, team):
    """Find a team in the team list by name."""
    theTeam = [x for x in teamList if x.name == team]
    if len(theTeam) == 0:
        return None
    return theTeam[0]

def getCurrentSeason():
    """Get the current college football season."""
    today = datetime.now()
    if today.month < 9:
        return today.year - 1
    else:
        return today.year

def findNth(num):
    """Convert number to ordinal (1st, 2nd, 3rd, etc)."""
    if 11 <= num % 100 <= 13:
        return f"{num}th"
    lastDigit = num % 10
    if lastDigit == 1:
        return f"{num}st"
    elif lastDigit == 2:
        return f"{num}nd"
    elif lastDigit == 3:
        return f"{num}rd"
    else:
        return f"{num}th"

def ordinalSuffix(n):
    """Convert number to ordinal suffix."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        last_digit = n % 10
        if last_digit == 1:
            suffix = 'st'
        elif last_digit == 2:
            suffix = 'nd'
        elif last_digit == 3:
            suffix = 'rd'
        else:
            suffix = 'th'
    return f"{n}{suffix}"
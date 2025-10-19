"""
scripts/utils/rules.py
"""

class Standing:
    """Represents a team's record"""
    def __init__(self, team_abbr, w=0, l=0):
        self.team = team_abbr
        self.w = w
        self.l = l
    
    def __str__(self):
        return f"{self.w}-{self.l}"
    
    def record_str(self):
        return f"{self.w}-{self.l}"

def get_h2h_record(games, team1, team2):
    """Calculate head-to-head record for team1 vs team2"""
    w = l = 0
    for game in games:
        if game.away == team1 and game.home == team2:
            if game.winner == team1:
                w += 1
            else:
                l += 1
        elif game.home == team1 and game.away == team2:
            if game.winner == team1:
                w += 1
            else:
                l += 1
    return Standing(team1, w, l)

def get_division_record(games, team1, team2_list):
    """Calculate team1's record vs all teams in team2_list"""
    w = l = 0
    for game in games:
        if game.away == team1 and game.home in team2_list:
            if game.winner == team1:
                w += 1
            else:
                l += 1
        elif game.home == team1 and game.away in team2_list:
            if game.winner == team1:
                w += 1
            else:
                l += 1
    return Standing(team1, w, l)

def get_league_record(games, team1, league_teams):
    """Calculate team1's record vs all teams in league_teams"""
    w = l = 0
    for game in games:
        if game.away == team1 and game.home in league_teams:
            if game.winner == team1:
                w += 1
            else:
                l += 1
        elif game.home == team1 and game.away in league_teams:
            if game.winner == team1:
                w += 1
            else:
                l += 1
    return Standing(team1, w, l)

def determine_tiebreaker_winner(record1, record2):
    """Compare two records, return winner or None if tied"""
    if record1.w > record2.w:
        return record1.team
    elif record2.w > record1.w:
        return record2.team
    else:
        return None  # Tied, need further tiebreaker
"""
scripts/generate_tiebreaker_grid.py
Generates a grid showing tiebreaker winners for each league
Includes summary statistics of tiebreaker wins per team
"""
import json
import csv
from collections import defaultdict


def load_teams_for_league(season, league):
    """Load and sort teams for a given league"""
    teams = []
    try:
        with open(f'data/teams/{season}teams.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                abbr, city, nickname, team_league, division = row
                if team_league == league:
                    teams.append(abbr)
    except FileNotFoundError:
        print(f"Teams file not found: data/teams/{season}teams.csv")
        return []
    
    return sorted(teams)


def load_tiebreakers(season):
    """Load tiebreakers from JSON"""
    try:
        with open('data/tiebreakers.json', 'r') as f:
            data = json.load(f)
            return data.get(str(season), {})
    except FileNotFoundError:
        print("Tiebreakers file not found: data/tiebreakers.json")
        return {}


def build_matchup_dict(tiebreakers, league):
    """Build a dictionary for quick lookup: (team1, team2) -> winner"""
    matchups = {}
    league_data = tiebreakers.get(league, [])
    
    for matchup in league_data:
        team1 = matchup['team1']
        team2 = matchup['team2']
        winner = matchup['tiebreak_winner']
        matchups[(team1, team2)] = winner
    
    return matchups


def count_tiebreak_records(tiebreakers, league):
    """Count tiebreaker wins and losses for each team (each matchup counted once)"""
    records = defaultdict(lambda: {'wins': 0, 'losses': 0})
    league_data = tiebreakers.get(league, [])
    seen_matchups = set()
    
    for matchup in league_data:
        team1 = matchup['team1']
        team2 = matchup['team2']
        winner = matchup['tiebreak_winner']
        
        # Create a canonical matchup key to avoid counting twice
        matchup_key = tuple(sorted([team1, team2]))
        
        if matchup_key not in seen_matchups and winner:
            seen_matchups.add(matchup_key)
            records[winner]['wins'] += 1
            loser = team2 if winner == team1 else team1
            records[loser]['losses'] += 1
    
    return records


def generate_grid(season, league):
    """Generate tiebreaker grid for a league"""
    teams = load_teams_for_league(season, league)
    tiebreakers = load_tiebreakers(season)
    matchups = build_matchup_dict(tiebreakers, league)
    
    if not teams:
        print(f"No teams found for {league}")
        return ""
    
    # Build header row
    lines = []
    header = "-".ljust(8)
    for team in teams:
        header += f"{team:>8}"
    lines.append(header)
    
    # Build data rows
    for team1 in teams:
        row = f"{team1:<8}"
        for team2 in teams:
            if team1 == team2:
                row += "-".rjust(8)
            elif team1 < team2:
                # Look up (team1, team2)
                winner = matchups.get((team1, team2), "?")
                row += f"{winner:>8}"
            else:
                # Look up (team2, team1) and reverse the result
                winner = matchups.get((team2, team1), "?")
                row += f"{winner:>8}"
        lines.append(row)
    
    return "\n".join(lines)


def generate_summary(season, league):
    """Generate a summary of tiebreaker records by team"""
    tiebreakers = load_tiebreakers(season)
    records = count_tiebreak_records(tiebreakers, league)
    
    lines = []
    lines.append(f"\n{league} TIEBREAKER RECORD SUMMARY")
    lines.append("-" * 40)
    
    # Sort teams by win-loss record (wins descending, then losses ascending), then alphabetically
    sorted_teams = sorted(records.items(), key=lambda x: (-x[1]['wins'], x[1]['losses'], x[0]))
    
    if not sorted_teams:
        lines.append("No tiebreaker data available")
        return "\n".join(lines)
    
    for team, record in sorted_teams:
        wins = record['wins']
        losses = record['losses']
        lines.append(f"{team:<6} {wins:>2}-{losses:<2}")
    
    return "\n".join(lines)


def main():
    season = 2025
    
    # Generate AL grid and summary
    print("Generating tiebreaker grids for 2025...\n")
    al_grid = generate_grid(season, 'AL')
    al_summary = generate_summary(season, 'AL')
    
    nl_grid = generate_grid(season, 'NL')
    nl_summary = generate_summary(season, 'NL')
    
    # Write to file
    with open('data/tiebreaker_grids.txt', 'w') as f:
        f.write("=" * 130 + "\n")
        f.write(f"MLB TIEBREAKER WINNERS - {season}\n")
        f.write("=" * 130 + "\n\n")
        
        f.write("AMERICAN LEAGUE\n")
        f.write("-" * 130 + "\n")
        f.write(al_grid)
        f.write(al_summary)
        f.write("\n\n")
        
        f.write("NATIONAL LEAGUE\n")
        f.write("-" * 130 + "\n")
        f.write(nl_grid)
        f.write(nl_summary)
        f.write("\n")
    
    print(f"Wrote grids to data/tiebreaker_grids.txt")
    print(f"\nAL Grid (15x15):\n{al_grid}\n")
    print(al_summary)
    print(f"\nNL Grid (15x15):\n{nl_grid}\n")
    print(nl_summary)


if __name__ == "__main__":
    main()
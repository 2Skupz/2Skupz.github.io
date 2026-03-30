"""
scripts/generate_tiebreakers.py
"""
import csv
import json
from utils.game import createGameFromList
from utils.rules import get_h2h_record, get_division_record, get_league_record, determine_tiebreaker_winner


def load_teams(season):
    """Load team data from CSV and build division/league mappings"""
    divisions = {}
    leagues = {'AL': [], 'NL': []}
    team_to_div = {}
    team_to_league = {}
    
    try:
        with open(f'data/teams/{season}teams.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                abbr, city, nickname, league, division = row
                
                # Build division key (e.g., "AL_WEST")
                div_key = f"{league}_{division}"
                
                # Add to divisions
                if div_key not in divisions:
                    divisions[div_key] = []
                divisions[div_key].append(abbr)
                
                # Add to leagues
                if abbr not in leagues[league]:
                    leagues[league].append(abbr)
                
                # Build mappings
                team_to_div[abbr] = div_key
                team_to_league[abbr] = league
    except FileNotFoundError:
        print(f"Teams file not found: data/teams/{season}teams.csv")
        return None, None, None, None
    
    return divisions, leagues, team_to_div, team_to_league


def load_games(season):
    """Load games from CSV"""
    games = []
    try:
        with open(f'data/games/{season}games.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                game = createGameFromList(row)
                games.append(game)
    except FileNotFoundError:
        print(f"Games file not found: data/games/{season}games.csv")
        return []
    
    return games


def calculate_matchup(games, team1, team2, divisions, team_to_div, team_to_league):
    """Calculate tiebreaker matchup between two teams"""
    league = team_to_league[team1]
    div1 = team_to_div[team1]
    div2 = team_to_div[team2]
    
    # Get all teams in this league
    league_teams = []
    for div_key, teams in divisions.items():
        if div_key.startswith(league):
            league_teams.extend(teams)
    
    # Get head-to-head record
    h2h_rec_1 = get_h2h_record(games, team1, team2)
    h2h_rec_2 = get_h2h_record(games, team2, team1)
    h2h_winner = determine_tiebreaker_winner(h2h_rec_1, h2h_rec_2)
    
    # Get division records
    div_teams_1 = divisions[div1]
    div_teams_2 = divisions[div2]
    div_rec_1 = get_division_record(games, team1, div_teams_1)
    div_rec_2 = get_division_record(games, team2, div_teams_2)
    div_winner = determine_tiebreaker_winner(div_rec_1, div_rec_2)
    
    # Get league records
    league_rec_1 = get_league_record(games, team1, league_teams)
    league_rec_2 = get_league_record(games, team2, league_teams)
    league_winner = determine_tiebreaker_winner(league_rec_1, league_rec_2)
    
    # Determine overall tiebreaker winner based on sequence: h2h -> div -> league
    tiebreak_winner = None
    tiebreak_method = None
    
    if h2h_winner:
        tiebreak_winner = h2h_winner
        tiebreak_method = 'h2h'
    elif div_winner:
        tiebreak_winner = div_winner
        tiebreak_method = 'div'
    elif league_winner:
        tiebreak_winner = league_winner
        tiebreak_method = 'league'
    
    return {
        'team1': team1,
        'team1_division': div1,
        'team2': team2,
        'team2_division': div2,
        'h2h_record_1': h2h_rec_1.record_str(),
        'h2h_record_2': h2h_rec_2.record_str(),
        'h2h_record_winner': h2h_winner,
        'div_record_1': div_rec_1.record_str(),
        'div_record_2': div_rec_2.record_str(),
        'div_record_winner': div_winner,
        'league_record_1': league_rec_1.record_str(),
        'league_record_2': league_rec_2.record_str(),
        'league_record_winner': league_winner,
        'tiebreak_winner': tiebreak_winner,
        'tiebreak_method': tiebreak_method,
    }


def generate_tiebreakers(season):
    """Generate all tiebreaker matchups for a season"""
    games = load_games(season)
    if not games:
        print("No games loaded!")
        return {}
    
    divisions, leagues, team_to_div, team_to_league = load_teams(season)
    if not divisions:
        print("No teams loaded!")
        return {}
    
    results = {
        'AL': [],
        'NL': []
    }
    
    # Generate all AL matchups (both orderings)
    al_teams = sorted(leagues['AL'])
    for i, team1 in enumerate(al_teams):
        for team2 in al_teams[i+1:]:
            matchup = calculate_matchup(games, team1, team2, divisions, team_to_div, team_to_league)
            results['AL'].append(matchup)
            # Add reverse matchup
            reverse_matchup = calculate_matchup(games, team2, team1, divisions, team_to_div, team_to_league)
            results['AL'].append(reverse_matchup)
    
    # Generate all NL matchups (both orderings)
    nl_teams = sorted(leagues['NL'])
    for i, team1 in enumerate(nl_teams):
        for team2 in nl_teams[i+1:]:
            matchup = calculate_matchup(games, team1, team2, divisions, team_to_div, team_to_league)
            results['NL'].append(matchup)
            # Add reverse matchup
            reverse_matchup = calculate_matchup(games, team2, team1, divisions, team_to_div, team_to_league)
            results['NL'].append(reverse_matchup)
    
    return results


def write_tiebreakers(tiebreakers, season):
    """Write tiebreakers to JSON"""
    output = {season: tiebreakers}
    
    with open('data/tiebreakers.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Wrote tiebreakers to data/tiebreakers.json")
    print(f"  AL: {len(tiebreakers['AL'])} matchups")
    print(f"  NL: {len(tiebreakers['NL'])} matchups")


def main():
    season = 2025
    print(f"Generating tiebreakers for {season}...")
    tiebreakers = generate_tiebreakers(season)
    write_tiebreakers(tiebreakers, season)


if __name__ == "__main__":
    main()
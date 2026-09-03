# PairwiseStandings/generatePairwiseStandings.py
#
# Turns mlbTiebreak's pairwise tiebreaker winners into a standings-shaped view:
# "if every team in this league ended the season tied, who wins the tiebreaker
# chain against whom." Each team's record is its tiebreak record against the
# ENTIRE league (all other teams), same number as
# mlbTiebreak/scripts/generateTiebreakGrid.py's summary. Division and wild
# card tables just group/order that same record - when two teams share a
# tiebreak record, whichever one directly owns the head-to-head (or
# division/league fallback) tiebreaker over the other is ranked ahead, exactly
# like real MLB standings order a head-to-head tie.
#
# This is a standalone sibling project: it reads mlbTiebreak's already-
# generated data/tiebreakers.json and data/teamFiles/{season}teams.csv
# directly (no shared Python code), so run mlbTiebreak/main.py first to
# refresh those before running this.
#
# Note: this uses a simple pairwise comparator, so a 3-way (or 4-way) cycle
# among equally-tied teams isn't resolved with the full multi-team rules in
# mlbTiebreak/mlbTiebreakFileTree.txt - only the two-team head-to-head chain.
import csv
import json
import os
from functools import cmp_to_key

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MLB_TIEBREAK_DATA_DIR = os.path.join(THIS_DIR, '..', 'mlbTiebreak', 'data')
TIEBREAKERS_FILE = os.path.join(MLB_TIEBREAK_DATA_DIR, 'tiebreakers.json')
TEAM_FILES_DIR = os.path.join(MLB_TIEBREAK_DATA_DIR, 'teamFiles')
OUTPUT_FILE = os.path.join(THIS_DIR, 'pairwiseStandings.json')

DIVISION_ORDER = ['EAST', 'CENTRAL', 'WEST']


def load_tiebreakers():
    """Read mlbTiebreak's data/tiebreakers.json - {season: {season: {...}}}."""
    with open(TIEBREAKERS_FILE, 'r') as f:
        data = json.load(f)
    season = next(iter(data))
    return season, data[season]


def load_teams(season):
    teams_path = os.path.join(TEAM_FILES_DIR, f"{season}teams.csv")
    teams = {}
    with open(teams_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            abbr, city, nickname, league, division = row
            teams[abbr] = {
                'abbr': abbr, 'city': city, 'nickname': nickname,
                'name': f"{city} {nickname}", 'league': league, 'division': division,
            }
    return teams


def fmt_pct(w, l):
    gp = w + l
    if gp == 0:
        return '.000'
    pct = w / gp
    return f"{pct:.3f}".lstrip('0') if pct < 1 else '1.000'


def fmt_gb(leader, team):
    gb = ((leader['w'] - team['w']) + (team['l'] - leader['l'])) / 2
    if gb <= 0:
        return '-'
    return f"{gb:.1f}".rstrip('0').rstrip('.') if gb == int(gb) else f"{gb:.1f}"


def build_winner_lookup(matchups):
    """(team1, team2) -> tiebreak_winner (or None if unresolved) for one league."""
    return {(m['team1'], m['team2']): m['tiebreak_winner'] for m in matchups}


def tally_vs_league(league_abbrs, winner_lookup):
    """Each team's tiebreak wins/losses against every other team in the league."""
    record = {abbr: {'tb_w': 0, 'tb_l': 0} for abbr in league_abbrs}
    for team1 in league_abbrs:
        for team2 in league_abbrs:
            if team1 == team2:
                continue
            winner = winner_lookup.get((team1, team2))
            if winner == team1:
                record[team1]['tb_w'] += 1
            elif winner == team2:
                record[team1]['tb_l'] += 1
    return record


def build_team_entry(abbr, teams, record):
    info = teams[abbr]
    w, l = record['tb_w'], record['tb_l']
    return {
        'abbr': abbr,
        'name': info['name'],
        'city': info['city'],
        'nickname': info['nickname'],
        'division': info['division'],
        'tb_w': w,
        'tb_l': l,
        'tb_pct': fmt_pct(w, l),
        'w': w, 'l': l,
    }


def make_comparator(winner_lookup):
    """Rank by tiebreak wins; break ties with the direct pairwise tiebreak winner."""
    def compare(a, b):
        if a['tb_w'] != b['tb_w']:
            return b['tb_w'] - a['tb_w']
        winner = winner_lookup.get((a['abbr'], b['abbr']))
        if winner == a['abbr']:
            return -1
        if winner == b['abbr']:
            return 1
        return 0
    return compare


def rank_group(entries, comparator):
    ordered = sorted(entries, key=cmp_to_key(comparator))
    leader = ordered[0]
    for i, team in enumerate(ordered):
        team['rank'] = i + 1
        team['gb'] = fmt_gb(leader, team) if i > 0 else '-'
    return ordered


def generate_pairwise_standings():
    season, tiebreak_data = load_tiebreakers()
    teams = load_teams(season)

    result = {}
    for league in ('AL', 'NL'):
        winner_lookup = build_winner_lookup(tiebreak_data[league])
        comparator = make_comparator(winner_lookup)
        league_teams = {a: t for a, t in teams.items() if t['league'] == league}
        league_record = tally_vs_league(list(league_teams.keys()), winner_lookup)

        divisions_out = {}
        wc_pool = []
        for division in DIVISION_ORDER:
            abbrs = [a for a, t in league_teams.items() if t['division'] == division]
            if not abbrs:
                continue
            entries = [build_team_entry(a, teams, league_record[a]) for a in abbrs]
            div_table = rank_group(entries, comparator)
            divisions_out[division] = div_table

            # everyone except that division's own tiebreak-standings leader
            wc_pool.extend(team['abbr'] for team in div_table[1:])

        wc_entries = [build_team_entry(a, teams, league_record[a]) for a in wc_pool]
        wc_ordered = rank_group(wc_entries, comparator)
        for i, team in enumerate(wc_ordered):
            team['wc_rank'] = team.pop('rank')
            team['wcgb'] = team.pop('gb')
            team['in_wc'] = i < 3

        result[league] = {
            'divisions': divisions_out,
            'wildcard': wc_ordered,
        }

    return season, result


def write_pairwise_standings(season, data):
    output = {str(season): data}
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Wrote pairwise standings to {OUTPUT_FILE}")


def main():
    print(f"Reading tiebreakers from {TIEBREAKERS_FILE}...")
    season, data = generate_pairwise_standings()
    write_pairwise_standings(season, data)


if __name__ == "__main__":
    main()

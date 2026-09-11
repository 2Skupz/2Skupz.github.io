# PairwiseStandings/generatePairwiseStandings.py
#
# Turns mlbTiebreak's pairwise tiebreaker winners into a standings-shaped view:
# "if every team in this league ended the season tied, who wins the tiebreaker
# chain against whom." Each team's record is its tiebreak record against the
# ENTIRE league (all other teams), same number as
# mlbTiebreak/scripts/generateTiebreakGrid.py's summary. Division and wild
# card tables just group/order that same record - when several teams share a
# tiebreak record, they're ordered using the two/three/four-team cascade in
# mlbTiebreak/README.md (see tiebreakRules.py), and a plain-language note
# explaining the resolution is attached to the group.
#
# This is a standalone sibling project: it reads mlbTiebreak's already-
# generated data/tiebreakers.json and data/teamFiles/{season}teams.csv
# directly (no shared Python code), so run mlbTiebreak/main.py first to
# refresh those before running this.
import csv
import json
import os

from tiebreakRules import build_stats, resolve_group, pct as calc_pct

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
    if w + l == 0:
        return '.000'
    p = calc_pct(w, l)
    return f"{p:.3f}".lstrip('0') if p < 1 else '1.000'


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


def rank_and_resolve_ties(entries, h2h, div_stats, league_stats):
    """Sort by tiebreak record, then resolve any group sharing a record with
    the two/three/four-team cascade. Returns (ordered_entries, ties) where
    ties is a list of {teams, record, note} for every group of 2+."""
    by_abbr = {e['abbr']: e for e in entries}
    entries_sorted = sorted(entries, key=lambda e: (-e['tb_w'], e['tb_l']))

    groups = []
    for entry in entries_sorted:
        if groups and groups[-1][0]['tb_w'] == entry['tb_w'] and groups[-1][0]['tb_l'] == entry['tb_l']:
            groups[-1].append(entry)
        else:
            groups.append([entry])

    ordered = []
    ties = []
    for group in groups:
        abbrs = [e['abbr'] for e in group]
        if len(abbrs) == 1:
            ordered.append(group[0])
            continue
        resolved_abbrs, note = resolve_group(abbrs, h2h, div_stats, league_stats)
        ordered.extend(by_abbr[a] for a in resolved_abbrs)
        ties.append({
            'teams': resolved_abbrs,
            'record': f"{group[0]['tb_w']}-{group[0]['tb_l']}",
            'note': note,
        })

    leader = ordered[0]
    for i, team in enumerate(ordered):
        team['rank'] = i + 1
        team['gb'] = fmt_gb(leader, team) if i > 0 else '-'

    return ordered, ties


def generate_pairwise_standings():
    season, tiebreak_data = load_tiebreakers()
    teams = load_teams(season)

    result = {}
    for league in ('AL', 'NL'):
        matchups = tiebreak_data[league]
        winner_lookup = build_winner_lookup(matchups)
        h2h, div_stats, league_stats = build_stats(matchups)
        league_teams = {a: t for a, t in teams.items() if t['league'] == league}
        league_record = tally_vs_league(list(league_teams.keys()), winner_lookup)

        divisions_out = {}
        division_ties = {}
        wc_pool = []
        for division in DIVISION_ORDER:
            abbrs = [a for a, t in league_teams.items() if t['division'] == division]
            if not abbrs:
                continue
            entries = [build_team_entry(a, teams, league_record[a]) for a in abbrs]
            div_table, ties = rank_and_resolve_ties(entries, h2h, div_stats, league_stats)
            divisions_out[division] = div_table
            division_ties[division] = ties

            # everyone except that division's own tiebreak-standings leader
            wc_pool.extend(team['abbr'] for team in div_table[1:])

        wc_entries = [build_team_entry(a, teams, league_record[a]) for a in wc_pool]
        wc_ordered, wc_ties = rank_and_resolve_ties(wc_entries, h2h, div_stats, league_stats)
        for i, team in enumerate(wc_ordered):
            team['wc_rank'] = team.pop('rank')
            team['wcgb'] = team.pop('gb')
            team['in_wc'] = i < 3

        result[league] = {
            'divisions': divisions_out,
            'division_ties': division_ties,
            'wildcard': wc_ordered,
            'wildcard_ties': wc_ties,
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

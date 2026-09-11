# PairwiseStandings/tiebreakRules.py
#
# Implements the multi-team tiebreaker cascade documented in
# mlbTiebreak/README.md (two-team, three-team, and four-team rules), using
# only head-to-head / intradivision / intraleague records - the same three
# criteria mlbTiebreak/scripts/generateTiebreakers.py already computes for
# every pair. The "last half of intraleague games" criteria (steps 4-5 for
# two teams, c-d and 5-6 for three/four) aren't implemented: mlbTiebreak
# doesn't track a second-half split, and the existing two-team cascade in
# generateTiebreakers.py already stops at league record for the same reason.
# When a tie survives every criterion this module does implement, it's
# reported as unresolved rather than guessed at.
#
# Ties of 5+ teams aren't covered by the documented rules at all; they're
# ordered by combined record among the group as a reasonable stand-in, and
# flagged as such.


def parse_record(record_str):
    w, l = record_str.split('-')
    return int(w), int(l)


def pct(w, l):
    gp = w + l
    return w / gp if gp else 0.0


def build_stats(matchups):
    """From one league's tiebreakers.json matchups: pairwise H2H + each team's
    division/league record (team-level, so any matchup row for that team
    carries the same value)."""
    h2h = {}
    div_stats = {}
    league_stats = {}
    for m in matchups:
        a = m['team1']
        h2h[(a, m['team2'])] = parse_record(m['h2h_record_1'])
        div_stats[a] = parse_record(m['div_record_1'])
        league_stats[a] = parse_record(m['league_record_1'])
    return h2h, div_stats, league_stats


def _order_by_division_then_league(teams, div_stats, league_stats):
    """Fallback used when a 3- or 4-team group is exactly identical head-to-head."""
    div_pcts = {t: pct(*div_stats[t]) for t in teams}
    if len(set(div_pcts.values())) > 1:
        return sorted(teams, key=lambda t: -div_pcts[t]), 'intradivision win%'

    league_pcts = {t: pct(*league_stats[t]) for t in teams}
    if len(set(league_pcts.values())) > 1:
        return sorted(teams, key=lambda t: -league_pcts[t]), 'intraleague win%'

    return teams, 'unresolved (identical in every tracked category)'


def resolve_two(a, b, h2h, div_stats, league_stats):
    wa, la = h2h[(a, b)]
    if wa != la:
        winner, loser = (a, b) if wa > la else (b, a)
        w, l = (wa, la) if wa > la else (la, wa)
        return [winner, loser], f"{winner} over {loser} on head-to-head ({w}-{l})"

    da, db = div_stats[a], div_stats[b]
    pa, pb = pct(*da), pct(*db)
    if pa != pb:
        winner, loser = (a, b) if pa > pb else (b, a)
        return [winner, loser], f"{winner} over {loser} on intradivision record"

    ea, eb = league_stats[a], league_stats[b]
    qa, qb = pct(*ea), pct(*eb)
    if qa != qb:
        winner, loser = (a, b) if qa > qb else (b, a)
        return [winner, loser], f"{winner} over {loser} on intraleague record"

    return [a, b], f"{a}/{b} unresolved (tied on head-to-head, division, and league record)"


def resolve_three(teams, h2h, div_stats, league_stats):
    a, b, c = teams

    def combined(x):
        others = [t for t in teams if t != x]
        w = sum(h2h[(x, o)][0] for o in others)
        l = sum(h2h[(x, o)][1] for o in others)
        return w, l

    combined_pct = {t: pct(*combined(t)) for t in teams}

    if len(set(combined_pct.values())) == 1:
        order, method = _order_by_division_then_league(teams, div_stats, league_stats)
        return order, f"identical head-to-head among the three - ranked by {method}"

    def beats(x, y):
        w, l = h2h[(x, y)]
        return w > l

    dominant = [x for x in teams if all(beats(x, o) for o in teams if o != x)]
    if len(dominant) == 1:
        leader = dominant[0]
        rest = [t for t in teams if t != leader]
        rest_order, rest_note = resolve_two(rest[0], rest[1], h2h, div_stats, league_stats)
        return [leader] + rest_order, f"{leader} beat both others head-to-head; {rest_note}"

    distinct_vals = sorted(set(combined_pct.values()), reverse=True)
    groups_by_val = {}
    for t in teams:
        groups_by_val.setdefault(combined_pct[t], []).append(t)

    order = []
    notes = []
    for val in distinct_vals:
        members = groups_by_val[val]
        if len(members) == 1:
            order.extend(members)
        else:
            sub_order, sub_note = resolve_two(members[0], members[1], h2h, div_stats, league_stats)
            order.extend(sub_order)
            notes.append(sub_note)

    note = "ranked by combined head-to-head record among the three"
    if notes:
        note += "; " + "; ".join(notes)
    return order, note


def resolve_four(teams, h2h, div_stats, league_stats):
    def beats(x, y):
        w, l = h2h[(x, y)]
        return w > l

    dominant = [x for x in teams if all(beats(x, o) for o in teams if o != x)]
    if len(dominant) == 1:
        leader = dominant[0]
        rest = [t for t in teams if t != leader]
        rest_order, rest_note = resolve_three(rest, h2h, div_stats, league_stats)
        return [leader] + rest_order, f"{leader} beat all three others head-to-head; {rest_note}"

    def combined(x):
        others = [t for t in teams if t != x]
        w = sum(h2h[(x, o)][0] for o in others)
        l = sum(h2h[(x, o)][1] for o in others)
        return w, l

    combined_pct = {t: pct(*combined(t)) for t in teams}
    distinct_vals = sorted(set(combined_pct.values()), reverse=True)

    if len(distinct_vals) == 1:
        order, method = _order_by_division_then_league(teams, div_stats, league_stats)
        return order, f"identical combined record among the four - ranked by {method}"

    groups_by_val = {}
    for t in teams:
        groups_by_val.setdefault(combined_pct[t], []).append(t)

    order = []
    notes = []
    for val in distinct_vals:
        members = groups_by_val[val]
        if len(members) == 1:
            order.extend(members)
        elif len(members) == 2:
            sub_order, sub_note = resolve_two(members[0], members[1], h2h, div_stats, league_stats)
            order.extend(sub_order)
            notes.append(sub_note)
        else:
            sub_order, sub_note = resolve_three(members, h2h, div_stats, league_stats)
            order.extend(sub_order)
            notes.append(sub_note)

    note = "ranked by combined head-to-head record among the four"
    if notes:
        note += "; " + "; ".join(notes)
    return order, note


def resolve_many(teams, h2h, div_stats, league_stats):
    """5+ team tie: not covered by the documented rules. Order by combined
    record among the group as a reasonable stand-in, recursing into the real
    rules for any sub-group of 4 or fewer."""
    def combined(x):
        others = [t for t in teams if t != x]
        w = sum(h2h[(x, o)][0] for o in others)
        l = sum(h2h[(x, o)][1] for o in others)
        return w, l

    combined_pct = {t: pct(*combined(t)) for t in teams}
    distinct_vals = sorted(set(combined_pct.values()), reverse=True)
    groups_by_val = {}
    for t in teams:
        groups_by_val.setdefault(combined_pct[t], []).append(t)

    order = []
    notes = []
    for val in distinct_vals:
        members = groups_by_val[val]
        if len(members) > 1:
            sub_order, sub_note = resolve_group(members, h2h, div_stats, league_stats)
            order.extend(sub_order)
            notes.append(sub_note)
        else:
            order.extend(members)

    note = f"{len(teams)}-way tie isn't covered by the documented rules - ranked by combined record among the group"
    if notes:
        note += "; " + "; ".join(notes)
    return order, note


def resolve_group(abbrs, h2h, div_stats, league_stats):
    n = len(abbrs)
    if n <= 1:
        return abbrs, None
    if n == 2:
        return resolve_two(abbrs[0], abbrs[1], h2h, div_stats, league_stats)
    if n == 3:
        return resolve_three(abbrs, h2h, div_stats, league_stats)
    if n == 4:
        return resolve_four(abbrs, h2h, div_stats, league_stats)
    return resolve_many(abbrs, h2h, div_stats, league_stats)

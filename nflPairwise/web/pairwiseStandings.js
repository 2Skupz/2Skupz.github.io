// web/pairwiseStandings.js
// Renders the AFC and NFC pairwise standings from data/pairwiseStandings.js
// (window.NFL_PAIRWISE_STANDINGS, written by main.py).

let standings = null;
let showTies = false; // set per conference while it renders: T column only if ties exist

const DIVISION_LABELS = {
    East: 'East',
    North: 'North',
    South: 'South',
    West: 'West',
};

const LEAGUE_LABELS = {
    AFC: 'American Football Conference',
    NFC: 'National Football Conference',
};

const BRACKET_TITLES = ['Wild Card', 'Divisional', 'Conf. Championship'];

document.addEventListener('DOMContentLoaded', () => {
    loadStandings();
    render();
    document.getElementById('rulesLink').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('rulesDialog').showModal();
    });
    document.getElementById('rulesClose').addEventListener('click', () => {
        document.getElementById('rulesDialog').close();
    });
});

function loadStandings() {
    const data = window.NFL_PAIRWISE_STANDINGS;
    if (!data) {
        console.error('No standings data. Run main.py to generate data/pairwiseStandings.js.');
        return;
    }
    standings = data;
    document.getElementById('seasonLabel').textContent = `${data.season} Season`;
    document.getElementById('footnote').textContent = `Generated ${data.generated}`;
}

function getLogoPath(team) {
    return `../data/logos/${team.abbr}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    if (!standings) {
        root.innerHTML = '';
        return;
    }

    // Brackets sit in their own row so the AFC and NFC brackets start at the same height.
    root.innerHTML = `
        <div class="pairwise-leagues">
            ${renderLeagueColumn('AFC')}
            ${renderLeagueColumn('NFC')}
        </div>
        <div class="pairwise-brackets">
            ${renderBracket('AFC', standings.AFC.playoffs)}
            ${renderBracket('NFC', standings.NFC.playoffs)}
        </div>
    `;
}

function renderLeagueColumn(league) {
    const leagueData = standings[league];
    if (!leagueData) return '';

    showTies = leagueData.has_ties;
    const isNFC = league === 'NFC';

    const divisionsHtml = Object.entries(leagueData.divisions)
        .map(([division, teams]) => renderDivisionTable(league, division, teams))
        .join('');

    return `
        <div class="league-column ${isNFC ? 'nl' : ''}">
            <h2 class="league-heading ${isNFC ? 'nl' : ''}">${LEAGUE_LABELS[league]}</h2>
            ${divisionsHtml}
            <div class="section-divider"><span>Playoff Picture</span></div>
            ${renderLeadersTable(league, leagueData.division_leaders)}
            ${renderWildcardTable(league, leagueData.wildcard)}
            ${renderTieExplainer(leagueData.ties)}
        </div>
    `;
}

// Columns: W, L, (T only when the conference has any tie), PCT
function rowClass() {
    return showTies ? 'with-ties' : '';
}

function renderHeaderRow() {
    return `
        <div class="standings-row tb-row standings-header ${rowClass()}">
            <div class="col-team">Team</div>
            <div class="col-num">W</div>
            <div class="col-num">L</div>
            ${showTies ? '<div class="col-num">T</div>' : ''}
            <div class="col-num">PCT</div>
        </div>
    `;
}

function renderTeamRow(team, extraClass) {
    const marker = team.tie_number ? `<sup class="tie-marker">${team.tie_number}</sup>` : '';
    return `
        <div class="standings-row tb-row ${rowClass()} ${extraClass || ''}">
            <div class="col-team">
                <span class="rank">${team.wc_rank || team.rank}</span>
                <img class="team-logo-sm" src="${getLogoPath(team)}" alt="${team.name}">
                <span class="team-name">${team.name}${marker}</span>
                <span class="team-abbr">${team.abbr}${marker}</span>
            </div>
            <div class="col-num">${team.tb_w}</div>
            <div class="col-num">${team.tb_l}</div>
            ${showTies ? `<div class="col-num">${team.tb_t}</div>` : ''}
            <div class="col-num">${team.tb_pct}</div>
        </div>
    `;
}

function renderDivisionTable(league, division, teams) {
    const label = DIVISION_LABELS[division] || division;
    const rows = teams
        .map(team => renderTeamRow(team, team.rank === 1 ? 'row-leader' : (team.in_wc ? 'row-clinch' : '')))
        .join('');

    return `
        <div class="standings-table">
            <div class="standings-title">${league} ${label}</div>
            ${renderHeaderRow()}
            ${rows}
        </div>
    `;
}

function renderLeadersTable(league, teams) {
    if (!teams || !teams.length) return '';

    const rows = teams
        .map(team => renderTeamRow(team, team.rank === 1 ? 'row-leader' : ''))
        .join('');

    return `
        <div class="standings-table">
            <div class="standings-title">${league} Division Leaders</div>
            ${renderHeaderRow()}
            ${rows}
        </div>
    `;
}

// Three wild card spots per conference. The divider sits below the last spot.
function renderWildcardTable(league, teams) {
    if (!teams || !teams.length) return '';

    const rows = teams.map((team, i) => {
        const rowClassName = team.in_wc ? 'row-clinch' : '';
        const divider = i === 3 ? '<div class="wc-divider"></div>' : '';
        return divider + renderTeamRow(team, rowClassName);
    }).join('');

    return `
        <div class="standings-table standings-wildcard">
            <div class="standings-title">${league} Wild Card</div>
            ${renderHeaderRow()}
            ${rows}
        </div>
    `;
}

function renderBracketTeam(team, winnerAbbr) {
    const isWinner = team.abbr === winnerAbbr;
    return `
        <div class="bracket-team ${isWinner ? 'winner' : 'loser'}">
            <span class="bracket-seed">${team.seed}</span>
            <img class="bracket-logo" src="${getLogoPath(team)}" alt="${team.name}">
            <span class="bracket-team-name">${team.abbr}</span>
        </div>
    `;
}

// Bracket geometry. Every conference uses the same numbers, so the AFC and NFC
// brackets line up with each other. Card positions are in px inside .bracket.
const BRACKET_CARD_H = 136;   // height of one game card
const BRACKET_GAP = 12;       // space between wild card cards
const BRACKET_TOP = 30;       // room for the round titles above the cards

function renderBracketGame(game, y) {
    return `
        <div class="bracket-game" style="top:${BRACKET_TOP + y}px;height:${BRACKET_CARD_H}px">
            ${renderBracketTeam(game.teams[0], game.winner.abbr)}
            ${renderBracketTeam(game.teams[1], game.winner.abbr)}
            <div class="bracket-note">${game.note}</div>
        </div>
    `;
}

// Wild card games stack at fixed spacing. Each later-round game is centered
// between the two games feeding it, and the championship between the two
// divisional games. Positions are y offsets of the card's top edge.
function bracketPositions(wildCardCount) {
    const wc = Array.from({ length: wildCardCount }, (_, i) => i * (BRACKET_CARD_H + BRACKET_GAP));
    const div = [];
    for (let i = 0; i + 1 < wc.length; i++) div.push((wc[i] + wc[i + 1]) / 2);
    const champ = [(div[0] + div[1]) / 2];
    return { wild_card: wc, divisional: div, championship: champ };
}

function renderBracket(league, playoffs) {
    if (!playoffs) return '';

    const pos = bracketPositions(playoffs.wild_card.length);
    const rounds = [
        { games: playoffs.wild_card, ys: pos.wild_card },
        { games: playoffs.divisional, ys: pos.divisional },
        { games: playoffs.championship, ys: pos.championship },
    ];
    const height = BRACKET_TOP + playoffs.wild_card.length * BRACKET_CARD_H +
        (playoffs.wild_card.length - 1) * BRACKET_GAP;

    return `
        <div class="standings-table bracket-card">
            <div class="standings-title">${league} Simulated Playoffs</div>
            <div class="bracket" style="height:${height}px">
                ${rounds.map((r, i) => `
                    <div class="bracket-round bracket-round-${i + 1}">
                        <div class="bracket-round-title">${BRACKET_TITLES[i]}</div>
                        ${r.games.map((g, j) => renderBracketGame(g, r.ys[j])).join('')}
                    </div>`).join('')}
            </div>
            <div class="bracket-champion">${league} Champion: ${playoffs.champion.name}</div>
        </div>
    `;
}

function renderTieExplainer(ties) {
    if (!ties || !ties.length) return '';

    const items = ties.map(tie => `
        <div class="tie-entry">
            <div class="tie-entry-header">
                <span class="tie-entry-number">${tie.number}</span>
                ${tie.label}: ${tie.teams.join('/')}
                <span class="tie-entry-record">(${tie.record})</span>
            </div>
            <div class="tie-entry-steps">
                ${tie.steps.map(step => `<div class="tie-entry-step">${step}</div>`).join('')}
            </div>
        </div>
    `).join('');

    return `
        <div class="tie-explainer">
            <div class="tie-explainer-title">Tiebreakers</div>
            ${items}
        </div>
    `;
}

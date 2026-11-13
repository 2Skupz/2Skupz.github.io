let standings = null;
let season = null;

const DIVISION_LABELS = {
    EAST: 'East',
    CENTRAL: 'Central',
    WEST: 'West',
};

const LEAGUE_LABELS = {
    AL: 'American League',
    NL: 'National League',
};

document.addEventListener('DOMContentLoaded', () => {
    loadStandings();
    render();
});

// Data comes from pairwiseStandingsData.js (window.MLB_PAIRWISE_STANDINGS,
// written by generatePairwiseStandings.py) rather than fetch(), so the page
// works when opened straight from disk.
function loadStandings() {
    const data = window.MLB_PAIRWISE_STANDINGS;
    if (!data) {
        console.error('No standings data. Run refresh.sh to generate pairwiseStandingsData.js.');
        return;
    }
    season = data.season;
    standings = data;
    document.getElementById('seasonLabel').textContent = `${season} Season`;
    document.getElementById('footnote').textContent = `Generated ${data.generated}`;
}

function getLogoPath(team) {
    const fileName = `${team.city}${team.nickname}`.replace(/[.\s]+/g, '');
    return `../mlbTiebreak/data/logos/${fileName}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    if (!standings) {
        root.innerHTML = '<p class="subtitle">No standings data found. Run refresh.sh to generate pairwiseStandingsData.js.</p>';
        return;
    }

    root.innerHTML = `
        ${renderSection('Standings', renderStandingsColumn)}
        ${renderSection('Playoff Picture', renderPictureColumn)}
        ${renderSection('Simulated Playoffs', renderBracketColumn)}
    `;
}

// Each section is a full-width labeled divider followed by an AL | NL pair, so
// the two leagues start level with each other in every section.
function renderSection(title, renderColumn) {
    return `
        <div class="section-divider"><span>${title}</span></div>
        <div class="pairwise-leagues">
            ${renderColumn('AL')}
            ${renderColumn('NL')}
        </div>
    `;
}

function columnClass(league) {
    return `league-column ${league === 'NL' ? 'nl' : ''}`;
}

function renderStandingsColumn(league) {
    const leagueData = standings[league];
    if (!leagueData) return '';

    const divisionsHtml = Object.entries(leagueData.divisions)
        .map(([division, teams]) => renderDivisionTable(league, division, teams))
        .join('');

    return `
        <div class="${columnClass(league)}">
            <h2 class="league-heading ${league === 'NL' ? 'nl' : ''}">${LEAGUE_LABELS[league]}</h2>
            ${divisionsHtml}
        </div>
    `;
}

function renderPictureColumn(league) {
    const leagueData = standings[league];
    if (!leagueData) return '';

    return `
        <div class="${columnClass(league)}">
            ${renderLeadersTable(league, leagueData.division_leaders)}
            ${renderWildcardTable(league, leagueData.wildcard)}
            ${renderTieExplainer(league, leagueData.ties)}
        </div>
    `;
}

function renderBracketColumn(league) {
    const leagueData = standings[league];
    if (!leagueData) return '';

    return `
        <div class="${columnClass(league)}">
            ${renderBracket(league, leagueData.playoffs)}
        </div>
    `;
}

function renderHeaderRow() {
    return `
        <div class="standings-row tb-row standings-header">
            <div class="col-team">Team</div>
            <div class="col-num">W</div>
            <div class="col-num">L</div>
            <div class="col-num">PCT</div>
        </div>
    `;
}

function renderTeamRow(team, extraClass) {
    const marker = team.tie_number ? `<sup class="tie-marker">${team.tie_number}</sup>` : '';
    return `
        <div class="standings-row tb-row ${extraClass || ''}">
            <div class="col-team">
                <span class="rank">${team.wc_rank || team.rank}</span>
                <img class="team-logo-sm" src="${getLogoPath(team)}" alt="${team.name}">
                <span class="team-name">${team.name}${marker}</span>
                <span class="team-abbr">${team.abbr}${marker}</span>
            </div>
            <div class="col-num">${team.tb_w}</div>
            <div class="col-num">${team.tb_l}</div>
            <div class="col-num">${team.tb_pct}</div>
        </div>
    `;
}

function renderDivisionTable(league, division, teams) {
    const label = DIVISION_LABELS[division] || division;
    const rows = teams
        .map(team => renderTeamRow(team, team.rank === 1 ? 'row-leader' : team.in_wc ? 'row-clinch' : ''))
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
            <div class="standings-title">${league} Leaders</div>
            ${renderHeaderRow()}
            ${rows}
        </div>
    `;
}

function renderWildcardTable(league, teams) {
    if (!teams || !teams.length) return '';

    const rows = teams.map((team, i) => {
        const rowClass = team.in_wc ? 'row-clinch' : '';
        const divider = i === 3 ? '<div class="wc-divider"></div>' : '';
        return divider + renderTeamRow(team, rowClass);
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

// A slot names where a game card sits in the bracket (positions are fixed in
// CSS, so the AL and NL brackets are identical and line up): 'top' and
// 'bottom' are the two rows, 'mid' is centered between them. Each Wild Card
// game sits level with the Division Series game it feeds, and the pennant
// game is centered between the two Division Series games.
function renderBracketGame(game, slot) {
    return `
        <div class="bracket-game slot-${slot}">
            ${renderBracketTeam(game.teams[0], game.winner.abbr)}
            ${renderBracketTeam(game.teams[1], game.winner.abbr)}
            <div class="bracket-note">${game.note}</div>
        </div>
    `;
}

function renderBracketRound(title, games, slots, roundNumber) {
    return `
        <div class="bracket-round bracket-round-${roundNumber}">
            <div class="bracket-round-title">${title}</div>
            ${games.map((game, i) => renderBracketGame(game, slots[i])).join('')}
        </div>
    `;
}

function renderBracket(league, playoffs) {
    if (!playoffs) return '';

    return `
        <div class="standings-table bracket-card">
            <div class="standings-title">${league} Simulated Playoffs</div>
            <div class="bracket">
                ${renderBracketRound('Wild Card', playoffs.wild_card, ['top', 'bottom'], 1)}
                ${renderBracketRound('Division Series', playoffs.division_series, ['top', 'bottom'], 2)}
                ${renderBracketRound(league === 'AL' ? 'ALCS' : 'NLCS', playoffs.championship, ['mid'], 3)}
            </div>
            <div class="bracket-champion">${league} Pennant: ${playoffs.champion.name}</div>
        </div>
    `;
}

function renderTieExplainer(league, ties) {
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
            <div class="tie-explainer-title">${league} Tiebreakers</div>
            ${items}
        </div>
    `;
}

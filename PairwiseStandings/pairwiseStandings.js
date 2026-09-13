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

document.addEventListener('DOMContentLoaded', async () => {
    await loadStandings();
    render();
});

async function loadStandings() {
    try {
        const response = await fetch('pairwiseStandings.json');
        const data = await response.json();
        season = Object.keys(data)[0];
        standings = data[season];
        document.getElementById('seasonLabel').textContent = `${season} Season`;
    } catch (error) {
        console.error('Error loading pairwise standings:', error);
    }
}

function getLogoPath(team) {
    const fileName = `${team.city}${team.nickname}`.replace(/[.\s]+/g, '');
    return `../mlbTiebreak/data/logos/${fileName}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    if (!standings) {
        root.innerHTML = '';
        return;
    }

    root.innerHTML = `
        <div class="pairwise-leagues">
            ${renderLeagueColumn('AL')}
            ${renderLeagueColumn('NL')}
        </div>
    `;
}

function renderLeagueColumn(league) {
    const leagueData = standings[league];
    if (!leagueData) return '';

    const divisionsHtml = Object.entries(leagueData.divisions)
        .map(([division, teams]) => renderDivisionTable(league, division, teams))
        .join('');

    return `
        <div class="league-column ${league === 'NL' ? 'nl' : ''}">
            <h2 class="league-heading ${league === 'NL' ? 'nl' : ''}">${LEAGUE_LABELS[league]}</h2>
            ${divisionsHtml}
            ${renderLeadersTable(league, leagueData.division_leaders)}
            ${renderWildcardTable(league, leagueData.wildcard)}
            ${renderTieExplainer(leagueData.ties)}
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
        .map(team => renderTeamRow(team, team.rank === 1 ? 'row-leader' : ''))
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

function renderBracketGame(game) {
    return `
        <div class="bracket-game">
            ${renderBracketTeam(game.teams[0], game.winner.abbr)}
            ${renderBracketTeam(game.teams[1], game.winner.abbr)}
            <div class="bracket-note">${game.note}</div>
        </div>
    `;
}

function renderBracket(league, playoffs) {
    if (!playoffs) return '';

    return `
        <div class="standings-table bracket-card">
            <div class="standings-title">${league} Simulated Playoffs</div>
            <div class="bracket">
                <div class="bracket-round">
                    <div class="bracket-round-title">Wild Card</div>
                    ${playoffs.wild_card.map(renderBracketGame).join('')}
                </div>
                <div class="bracket-round">
                    <div class="bracket-round-title">Division Series</div>
                    ${playoffs.division_series.map(renderBracketGame).join('')}
                </div>
                <div class="bracket-round">
                    <div class="bracket-round-title">${league === 'AL' ? 'ALCS' : 'NLCS'}</div>
                    ${playoffs.championship.map(renderBracketGame).join('')}
                </div>
            </div>
            <div class="bracket-champion">${league} Pennant: ${playoffs.champion.name}</div>
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

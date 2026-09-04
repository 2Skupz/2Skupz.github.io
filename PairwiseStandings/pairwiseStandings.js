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
        <div class="league-column">
            <h2 class="league-heading ${league === 'NL' ? 'nl' : ''}">${LEAGUE_LABELS[league]}</h2>
            ${divisionsHtml}
            ${renderWildcardTable(league, leagueData.wildcard)}
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
    return `
        <div class="standings-row tb-row ${extraClass || ''}">
            <div class="col-team">
                <span class="rank">${team.wc_rank || team.rank}</span>
                <img class="team-logo-sm" src="${getLogoPath(team)}" alt="${team.name}">
                <span class="team-name">${team.name}</span>
                <span class="team-abbr">${team.abbr}</span>
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

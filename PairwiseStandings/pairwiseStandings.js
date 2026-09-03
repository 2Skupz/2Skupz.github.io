let currentLeague = 'AL';
let standings = null;
let season = null;

const DIVISION_LABELS = {
    EAST: 'East',
    CENTRAL: 'Central',
    WEST: 'West',
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

function switchLeague(league) {
    currentLeague = league;
    document.getElementById('leagueAL').classList.toggle('active', league === 'AL');
    document.getElementById('leagueNL').classList.toggle('active', league === 'NL');
    document.getElementById('leagueNL').classList.toggle('nl', league === 'NL');
    render();
}

function getLogoPath(team) {
    const fileName = `${team.city}${team.nickname}`.replace(/[.\s]+/g, '');
    return `../mlbTiebreak/data/logos/${fileName}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    if (!standings || !standings[currentLeague]) {
        root.innerHTML = '';
        return;
    }

    const leagueData = standings[currentLeague];
    const divisionsHtml = Object.entries(leagueData.divisions)
        .map(([division, teams]) => renderDivisionTable(division, teams))
        .join('');

    root.innerHTML = `
        <div class="standings-divisions">${divisionsHtml}</div>
        ${renderWildcardTable(leagueData.wildcard)}
    `;
}

function renderHeaderRow(gbLabel) {
    return `
        <div class="standings-row tb-row standings-header">
            <div class="col-team">Team</div>
            <div class="col-num">W</div>
            <div class="col-num">L</div>
            <div class="col-num">PCT</div>
            <div class="col-num">${gbLabel}</div>
        </div>
    `;
}

function renderTeamRow(team, gb, extraClass) {
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
            <div class="col-num">${gb}</div>
        </div>
    `;
}

function renderDivisionTable(division, teams) {
    const label = DIVISION_LABELS[division] || division;
    const rows = teams
        .map(team => renderTeamRow(team, team.gb, team.rank === 1 ? 'row-leader' : ''))
        .join('');

    return `
        <div class="standings-table">
            <div class="standings-title">${currentLeague} ${label}</div>
            ${renderHeaderRow('GB')}
            ${rows}
        </div>
    `;
}

function renderWildcardTable(teams) {
    if (!teams || !teams.length) return '';

    const rows = teams.map((team, i) => {
        const rowClass = team.in_wc ? 'row-clinch' : '';
        const divider = i === 3 ? '<div class="wc-divider"></div>' : '';
        return divider + renderTeamRow(team, team.wcgb, rowClass);
    }).join('');

    return `
        <div class="standings-table standings-wildcard">
            <div class="standings-title">${currentLeague} Wild Card</div>
            ${renderHeaderRow('WCGB')}
            ${rows}
        </div>
    `;
}

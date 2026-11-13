let currentLeague = 'AL';
let standings = null;
let season = null;

const DIVISION_LABELS = {
    EAST: 'East',
    CENTRAL: 'Central',
    WEST: 'West',
};

document.addEventListener('DOMContentLoaded', () => {
    loadStandings();
    render();
});

// Data comes from ../data/standings.js (window.MLB_STANDINGS, written by
// scripts/generateStandings.py) rather than fetch(), so the page works when
// opened straight from disk.
function loadStandings() {
    const data = window.MLB_STANDINGS;
    if (!data) {
        console.error('No standings data. Run main.py to generate data/standings.js.');
        return;
    }
    season = Object.keys(data)[0];
    standings = data[season];
    document.getElementById('seasonLabel').textContent = `${season} Season`;
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
    return `../data/logos/${fileName}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    if (!standings || !standings[currentLeague]) {
        root.innerHTML = '<p class="subtitle">No standings data found. Run main.py to generate data/standings.js.</p>';
        return;
    }

    const leagueData = standings[currentLeague];
    const divisionsHtml = Object.entries(leagueData.divisions)
        .map(([division, teams]) => renderDivisionTable(division, teams))
        .join('');

    root.innerHTML = `
        <div class="${currentLeague === 'NL' ? 'nl' : ''}">
            <div class="standings-divisions">${divisionsHtml}</div>
            ${renderWildcardTable(leagueData.wildcard)}
            ${renderTieExplainer(currentLeague, leagueData.ties)}
        </div>
    `;
}

function renderHeaderRow(gbLabel) {
    return `
        <div class="standings-row standings-header">
            <div class="col-team">Team</div>
            <div class="col-num">W</div>
            <div class="col-num">L</div>
            <div class="col-num">PCT</div>
            <div class="col-num">${gbLabel}</div>
            <div class="col-num">STRK</div>
            <div class="col-num">L10</div>
            <div class="col-record">HOME</div>
            <div class="col-record">AWAY</div>
            <div class="col-num">DIFF</div>
        </div>
    `;
}

function renderTeamRow(team, gb, extraClass) {
    const streakClass = team.streak.startsWith('W') ? 'streak-win' : 'streak-loss';
    const marker = team.tie_number ? `<sup class="tie-marker">${team.tie_number}</sup>` : '';
    return `
        <div class="standings-row ${extraClass || ''}">
            <div class="col-team">
                <span class="rank">${team.wc_rank || team.rank}</span>
                <img class="team-logo-sm" src="${getLogoPath(team)}" alt="${team.name}">
                <span class="team-name">${team.name}${marker}</span>
                <span class="team-abbr">${team.abbr}${marker}</span>
            </div>
            <div class="col-num">${team.w}</div>
            <div class="col-num">${team.l}</div>
            <div class="col-num">${team.pct}</div>
            <div class="col-num">${gb}</div>
            <div class="col-num ${streakClass}">${team.streak}</div>
            <div class="col-num">${team.last10}</div>
            <div class="col-record">${team.home}</div>
            <div class="col-record">${team.away}</div>
            <div class="col-num">${team.diff}</div>
        </div>
    `;
}

function renderDivisionTable(division, teams) {
    const label = DIVISION_LABELS[division] || division;
    const rows = teams
        .map(team => renderTeamRow(team, team.gb, team.rank === 1 ? 'row-leader' : team.in_wc ? 'row-clinch' : ''))
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

// web/nflStandings.js
// Real NFL standings for one conference at a time, in the style of the
// mlbTiebreak standings page. Data: data/nflStandings.js (window.NFL_STANDINGS).

let currentConf = 'AFC';
let showTies = false; // T column only when the conference has a tie
const DATA = window.NFL_STANDINGS;

const DIVISION_LABELS = { East: 'East', North: 'North', South: 'South', West: 'West' };

document.addEventListener('DOMContentLoaded', () => {
    if (!DATA) {
        document.getElementById('seasonLabel').textContent =
            'No data found. Run main.py to generate data/nflStandings.js.';
        return;
    }
    document.getElementById('seasonLabel').textContent = `${DATA.season} Season`;
    document.getElementById('footnote').textContent = `Generated ${DATA.generated}`;
    render();
    document.getElementById('rulesLink').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('rulesDialog').showModal();
    });
    document.getElementById('rulesClose').addEventListener('click', () => {
        document.getElementById('rulesDialog').close();
    });
});

function switchConference(c) {
    currentConf = c;
    document.getElementById('leagueAFC').classList.toggle('active', c === 'AFC');
    document.getElementById('leagueNFC').classList.toggle('active', c === 'NFC');
    document.getElementById('leagueNFC').classList.toggle('nfc', c === 'NFC');
    render();
}

function getLogoPath(team) {
    return `../data/logos/${team.abbr}.png`;
}

function render() {
    const root = document.getElementById('standingsRoot');
    const data = DATA && DATA[currentConf];
    if (!data) {
        root.innerHTML = '';
        return;
    }
    showTies = data.has_ties;

    const divisionsHtml = Object.entries(data.divisions)
        .map(([d, teams]) => renderDivisionTable(d, teams)).join('');

    root.innerHTML = `
        <div class="standings-divisions">${divisionsHtml}</div>
        <div class="section-divider"><span>Playoff Picture</span></div>
        <div class="standings-divisions">
            ${renderLeadersTable(data.division_leaders)}
            ${renderWildcardTable(data.wildcard)}
        </div>
        ${renderTieExplainer(data.ties)}
    `;
}

// Columns after the team name: W, L, [T], PCT, GB, STRK, DIV, CONF, DIFF
function columnCount() {
    return showTies ? 9 : 8;
}

function renderHeaderRow(gbLabel) {
    return `
        <div class="standings-row std-row std-header" style="--cols:${columnCount()}">
            <div class="col-team">Team</div>
            <div class="col-num">W</div>
            <div class="col-num">L</div>
            ${showTies ? '<div class="col-num">T</div>' : ''}
            <div class="col-num">PCT</div>
            <div class="col-num">${gbLabel}</div>
            <div class="col-num">STRK</div>
            <div class="col-num">DIV</div>
            <div class="col-num">CONF</div>
            <div class="col-num">DIFF</div>
        </div>
    `;
}

function renderTeamRow(team, gb, extraClass) {
    const streakClass = team.streak.startsWith('W') ? 'streak-win'
        : team.streak.startsWith('L') ? 'streak-loss' : '';
    const marker = team.tie_number ? `<sup class="tie-marker">${team.tie_number}</sup>` : '';
    return `
        <div class="standings-row std-row ${extraClass || ''}" style="--cols:${columnCount()}">
            <div class="col-team">
                <span class="rank">${team.wc_rank || team.rank}</span>
                <img class="team-logo-sm" src="${getLogoPath(team)}" alt="${team.name}">
                <span class="team-name">${team.name}${marker}</span>
                <span class="team-abbr">${team.abbr}${marker}</span>
            </div>
            <div class="col-num">${team.w}</div>
            <div class="col-num">${team.l}</div>
            ${showTies ? `<div class="col-num">${team.t}</div>` : ''}
            <div class="col-num">${team.pct}</div>
            <div class="col-num">${gb}</div>
            <div class="col-num ${streakClass}">${team.streak}</div>
            <div class="col-num std-small">${team.div}</div>
            <div class="col-num std-small">${team.conf}</div>
            <div class="col-num">${team.diff}</div>
        </div>
    `;
}

function renderDivisionTable(division, teams) {
    const rows = teams
        .map(team => renderTeamRow(team, team.gb, team.rank === 1 ? 'row-leader' : (team.in_wc ? 'row-wildcard' : '')))
        .join('');
    return `
        <div class="standings-table">
            <div class="standings-title">${currentConf} ${DIVISION_LABELS[division] || division}</div>
            ${renderHeaderRow('GB')}
            ${rows}
        </div>
    `;
}

function renderLeadersTable(teams) {
    if (!teams || !teams.length) return '';
    const rows = teams
        .map(team => renderTeamRow(team, '', team.rank === 1 ? 'row-leader' : ''))
        .join('');
    return `
        <div class="standings-table">
            <div class="standings-title">${currentConf} Division Leaders</div>
            ${renderHeaderRow('')}
            ${rows}
        </div>
    `;
}

// Three wild card spots per conference, shaded yellow. Divider below the last one.
function renderWildcardTable(teams) {
    if (!teams || !teams.length) return '';
    const rows = teams.map((team, i) => {
        const cls = team.in_wc ? 'row-wildcard' : '';
        const divider = i === 3 ? '<div class="wc-divider"></div>' : '';
        return divider + renderTeamRow(team, team.wcgb, cls);
    }).join('');
    return `
        <div class="standings-table standings-wildcard">
            <div class="standings-title">${currentConf} Wild Card</div>
            ${renderHeaderRow('WCGB')}
            ${rows}
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

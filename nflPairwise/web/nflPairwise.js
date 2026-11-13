// web/nflPairwise.js
// Renders the matchup comparison, tiebreaker grid, and summary from
// data/tiebreakers.js (window.NFL_TIEBREAK_DATA, written by main.py).

let currentConf = 'AFC';
const DATA = window.NFL_TIEBREAK_DATA;

document.addEventListener('DOMContentLoaded', () => {
    if (!DATA) {
        document.getElementById('seasonLabel').textContent =
            'No data found. Run main.py to generate data/tiebreakers.js.';
        return;
    }
    document.getElementById('seasonLabel').textContent = `${DATA.season} Season`;
    populateSelectors();
    renderAll();
});

function logoPath(abbr) {
    return `../data/logos/${abbr}.png`;
}

function conf() {
    return DATA.conferences[currentConf];
}

function teamByAbbr(abbr) {
    return conf().teams.find(t => t.abbr === abbr);
}

// Matchups are stored once per pair (team1 < team2 alphabetically).
// Return the pair in the order asked for, flipping the sides if needed.
function getMatchup(a, b) {
    const direct = conf().matchups.find(m => m.team1 === a && m.team2 === b);
    if (direct) return { m: direct, flipped: false };
    const reversed = conf().matchups.find(m => m.team1 === b && m.team2 === a);
    if (reversed) return { m: reversed, flipped: true };
    return null;
}

function populateSelectors() {
    const teams = [...conf().teams].sort((x, y) => x.abbr.localeCompare(y.abbr));
    const options = '<option value="">Select a team...</option>' +
        teams.map(t => `<option value="${t.abbr}">${t.name} (${t.abbr})</option>`).join('');
    document.getElementById('team1').innerHTML = options;
    document.getElementById('team2').innerHTML = options;
    document.getElementById('results').classList.add('hidden');
}

function switchConference(c) {
    currentConf = c;
    document.getElementById('leagueAFC').classList.toggle('active', c === 'AFC');
    document.getElementById('leagueNFC').classList.toggle('active', c === 'NFC');
    document.getElementById('leagueNFC').classList.toggle('nfc', c === 'NFC');
    populateSelectors();
    renderAll();
}

function showMatchup() {
    const a = document.getElementById('team1').value;
    const b = document.getElementById('team2').value;
    if (!a || !b || a === b) return;

    const found = getMatchup(a, b);
    if (!found) return;
    displayMatchup(a, b, found);
}

function displayMatchup(a, b, { m, flipped }) {
    // Left column is always the team the user picked as Team 1.
    const left = a, right = b;
    const tLeft = teamByAbbr(left), tRight = teamByAbbr(right);

    document.getElementById('team1Logo').src = logoPath(left);
    document.getElementById('team1Logo').alt = `${tLeft.name} logo`;
    document.getElementById('team2Logo').src = logoPath(right);
    document.getElementById('team2Logo').alt = `${tRight.name} logo`;
    document.getElementById('team1Name').textContent = tLeft.name;
    document.getElementById('team1Abbr').textContent = left;
    document.getElementById('team1Record').textContent = `${tLeft.record} overall`;
    document.getElementById('team2Name').textContent = tRight.name;
    document.getElementById('team2Abbr').textContent = right;
    document.getElementById('team2Record').textContent = `${tRight.record} overall`;

    document.getElementById('matchupType').textContent = m.type === 'division'
        ? `Division matchup (${m.division}): divisional rules apply`
        : 'Conference matchup: conference rules apply';

    // Step rows, in the order they were evaluated. Values are stored with
    // team1 on the left; swap when the user's Team 1 is the stored team2.
    const rows = m.steps.map(step => {
        const leftVal = flipped ? step.team2 : step.team1;
        const rightVal = flipped ? step.team1 : step.team2;
        const leftWins = step.winner === left;
        const rightWins = step.winner === right;
        const cls = step.applied ? '' : ' step-na';
        const note = !step.applied && step.team1 !== 'not tracked' ? ' <span class="step-note">not applied (no games, or below minimum)</span>' : '';
        const naNote = step.team1 === 'not tracked' ? '<span class="step-note">not in data</span>' : '';
        return `
            <div class="tiebreaker-row${cls}">
                <div class="record ${leftWins ? 'winner' : ''}">${leftVal === 'not tracked' ? '—' : leftVal}${naNote}</div>
                <div class="label">${step.step}${note}</div>
                <div class="record ${rightWins ? 'winner' : ''}">${rightVal === 'not tracked' ? '—' : rightVal}</div>
            </div>`;
    }).join('');
    document.getElementById('stepRows').innerHTML = rows;

    document.getElementById('winnerLabel').textContent = m.winner ? 'Tiebreaker Winner' : 'Result';
    document.getElementById('winnerName').textContent = m.winner
        ? `${teamByAbbr(m.winner).name} (${m.winner})`
        : 'Tie';
    document.getElementById('winnerMethod').innerHTML = m.winner
        ? `Decided by <strong>${m.decided_by}</strong>`
        : `No criterion separates them. ${m.decided_by}.`;

    document.getElementById('results').classList.remove('hidden');
}

function renderAll() {
    renderTiebreakerMatrix();
    document.getElementById('footnote').textContent = `Generated ${DATA.generated}`;
}

function renderTiebreakerMatrix() {
    const matrix = document.getElementById('tiebreakerMatrix');
    const teams = [...conf().teams].sort((x, y) => x.abbr.localeCompare(y.abbr));
    const cols = teams.length + 1;
    matrix.style.gridTemplateColumns = `repeat(${cols}, minmax(0, 1fr))`;

    let html = '<div class="matrix-cell matrix-corner">vs</div>';
    html += teams.map(t => `
        <div class="matrix-cell matrix-team-header" title="${t.name}">
            <img src="${logoPath(t.abbr)}" alt="${t.name} logo" class="matrix-logo">
            <span>${t.abbr}</span>
        </div>`).join('');

    teams.forEach(row => {
        html += `
        <div class="matrix-cell matrix-side-header" title="${row.name}">
            <img src="${logoPath(row.abbr)}" alt="${row.name} logo" class="matrix-logo">
            <span>${row.abbr}</span>
        </div>`;
        teams.forEach(col => {
            if (row.abbr === col.abbr) {
                html += '<div class="matrix-cell matrix-diagonal">—</div>';
                return;
            }
            const found = getMatchup(row.abbr, col.abbr);
            if (!found) {
                html += '<div class="matrix-cell matrix-empty">n/a</div>';
                return;
            }
            const { m } = found;
            const winner = m.winner;
            const tip = `${row.abbr} vs ${col.abbr}: ` +
                (winner ? `${winner} wins, decided by ${m.decided_by}` : `tie (${m.decided_by})`);
            const label = winner ? winner : 'Tie';
            const cls = winner === row.abbr ? 'row-wins' : (winner ? 'col-wins' : 'tie');
            html += `<div class="matrix-cell matrix-winner-cell ${cls}" title="${tip}">${label}</div>`;
        });
    });

    matrix.innerHTML = html;
}


let currentLeague = 'AL';
let teams = [];
let tiebreakers = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadTeams();
    await loadTiebreakers();
    populateSelectors();
    renderTiebreakerMatrix();
});

async function loadTeams() {
    try {
        const response = await fetch('../data/teamFiles/2026teams.csv');
        const csv = await response.text();
        const lines = csv.split('\n').map(line => line.trim()).filter(line => line);
        
        teams = lines.map(line => {
            const parts = line.split(',');
            if (parts.length < 5) return null;
            return {
                abbr: parts[0].trim(),
                city: parts[1].trim(),
                nickname: parts[2].trim(), // "Blue Jays"
                league: parts[3].trim(),
                division: parts[4].trim()
            };
        }).filter(t => t !== null);
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

async function loadTiebreakers() {
    try {
        const response = await fetch('../data/tiebreakers.json');
        const data = await response.json();
        tiebreakers = data['2026'];
    } catch (error) {
        console.error('Error loading tiebreakers:', error);
    }
}

function populateSelectors() {
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    const leagueTeams = teams.filter(t => t.league === currentLeague).sort((a, b) => a.abbr.localeCompare(b.abbr));
    
    const options = '<option value="">Select a team...</option>' + 
        leagueTeams.map(t => `<option value="${t.abbr}">${t.city} ${t.nickname} (${t.abbr})</option>`).join('');
    
    team1Select.innerHTML = options;
    team2Select.innerHTML = options;
    document.getElementById('results').classList.add('hidden');
}

function switchLeague(league) {
    currentLeague = league;
    document.getElementById('leagueAL').classList.toggle('active', league === 'AL');
    document.getElementById('leagueNL').classList.toggle('active', league === 'NL');
    document.getElementById('leagueNL').classList.toggle('nl', league === 'NL');
    populateSelectors();
    renderTiebreakerMatrix();
}

function showMatchup() {
    const t1Abbr = document.getElementById('team1').value;
    const t2Abbr = document.getElementById('team2').value;
    
    if (!t1Abbr || !t2Abbr || t1Abbr === t2Abbr) return;
    
    const matchup = getMatchup(t1Abbr, t2Abbr);

    if (matchup) displayMatchup(matchup);
}

function getMatchup(team1Abbr, team2Abbr) {
    const leagueData = tiebreakers?.[currentLeague];

    if (!leagueData) return null;

    const direct = leagueData.find(m => m.team1 === team1Abbr && m.team2 === team2Abbr);
    if (direct) return direct;

    const reversed = leagueData.find(m => m.team1 === team2Abbr && m.team2 === team1Abbr);
    if (!reversed) return null;

    return {
        team1: reversed.team2,
        team2: reversed.team1,
        h2h_record_1: reversed.h2h_record_2,
        h2h_record_2: reversed.h2h_record_1,
        h2h_record_winner: swapWinner(reversed.h2h_record_winner, reversed.team1, reversed.team2),
        div_record_1: reversed.div_record_2,
        div_record_2: reversed.div_record_1,
        div_record_winner: swapWinner(reversed.div_record_winner, reversed.team1, reversed.team2),
        league_record_1: reversed.league_record_2,
        league_record_2: reversed.league_record_1,
        league_record_winner: swapWinner(reversed.league_record_winner, reversed.team1, reversed.team2),
        tiebreak_winner: swapWinner(reversed.tiebreak_winner, reversed.team1, reversed.team2),
        tiebreak_method: reversed.tiebreak_method
    };
}

function swapWinner(winner, originalTeam1, originalTeam2) {
    if (winner === originalTeam1) return originalTeam2;
    if (winner === originalTeam2) return originalTeam1;
    return null;
}

function getTeam(abbr) {
    return teams.find(team => team.abbr === abbr);
}

function getLogoPath(team) {
    const fileName = `${team.city}${team.nickname}`.replace(/[.\s]+/g, '');
    return `../data/logos/${fileName}.png`;
}

function getTeamDisplayName(team) {
    return `${team.city} ${team.nickname}`;
}

function renderTiebreakerMatrix() {
    const matrix = document.getElementById('tiebreakerMatrix');
    const leagueTeams = teams
        .filter(team => team.league === currentLeague)
        .sort((a, b) => a.abbr.localeCompare(b.abbr));

    if (!matrix || !leagueTeams.length || !tiebreakers?.[currentLeague]) {
        if (matrix) matrix.innerHTML = '';
        return;
    }

    const headerCells = leagueTeams.map(team => `
        <div class="matrix-cell matrix-team-header" title="${getTeamDisplayName(team)} (${team.abbr})">
            <img src="${getLogoPath(team)}" alt="${getTeamDisplayName(team)} logo" class="matrix-logo">
            <span>${team.abbr}</span>
        </div>
    `).join('');

    const rows = leagueTeams.map(rowTeam => {
        const rowHeader = `
            <div class="matrix-cell matrix-side-header" title="${getTeamDisplayName(rowTeam)} (${rowTeam.abbr})">
                <img src="${getLogoPath(rowTeam)}" alt="${getTeamDisplayName(rowTeam)} logo" class="matrix-logo">
                <span>${rowTeam.abbr}</span>
            </div>
        `;

        const cells = leagueTeams.map(columnTeam => {
            if (rowTeam.abbr === columnTeam.abbr) {
                return '<div class="matrix-cell matrix-diagonal">-</div>';
            }

            const matchup = getMatchup(rowTeam.abbr, columnTeam.abbr);
            const winner = matchup ? getTeam(matchup.tiebreak_winner) : null;

            if (!winner) {
                return '<div class="matrix-cell matrix-empty">TBD</div>';
            }

            return `
                <button
                    type="button"
                    class="matrix-cell matrix-winner-cell"
                    title="${getTeamDisplayName(rowTeam)} vs ${getTeamDisplayName(columnTeam)}: ${getTeamDisplayName(winner)} owns the tiebreaker"
                    onclick="selectMatchup('${rowTeam.abbr}', '${columnTeam.abbr}')"
                >
                    <img src="${getLogoPath(winner)}" alt="${getTeamDisplayName(winner)} logo" class="matrix-logo winner-logo">
                </button>
            `;
        }).join('');

        return rowHeader + cells;
    }).join('');

    matrix.style.gridTemplateColumns = `96px repeat(${leagueTeams.length}, minmax(0, 1fr))`;
    matrix.innerHTML = `
        <div class="matrix-cell matrix-corner">Row team vs column team</div>
        ${headerCells}
        ${rows}
    `;
}

function selectMatchup(team1Abbr, team2Abbr) {
    document.getElementById('team1').value = team1Abbr;
    document.getElementById('team2').value = team2Abbr;
    showMatchup();
}

function displayMatchup(matchup) {
    const t1 = getTeam(matchup.team1);
    const t2 = getTeam(matchup.team2);
    
    document.getElementById('team1Name').textContent = getTeamDisplayName(t1);
    document.getElementById('team1Abbr').textContent = t1.abbr;
    document.getElementById('team2Name').textContent = getTeamDisplayName(t2);
    document.getElementById('team2Abbr').textContent = t2.abbr;
    
    const logo1 = document.getElementById('team1Logo');
    const logo2 = document.getElementById('team2Logo');

    logo1.src = getLogoPath(t1);
    logo2.src = getLogoPath(t2);
    logo1.style.display = 'block';
    logo2.style.display = 'block';

    const format = (rec, isWin) => `<span class="${isWin ? 'winner' : ''}">${rec}</span>`;
    document.getElementById('h2h1').innerHTML = format(matchup.h2h_record_1, matchup.h2h_record_winner === t1.abbr);
    document.getElementById('h2h2').innerHTML = format(matchup.h2h_record_2, matchup.h2h_record_winner === t2.abbr);
    document.getElementById('div1').innerHTML = format(matchup.div_record_1, matchup.div_record_winner === t1.abbr);
    document.getElementById('div2').innerHTML = format(matchup.div_record_2, matchup.div_record_winner === t2.abbr);
    document.getElementById('league1').innerHTML = format(matchup.league_record_1, matchup.league_record_winner === t1.abbr);
    document.getElementById('league2').innerHTML = format(matchup.league_record_2, matchup.league_record_winner === t2.abbr);
    
    const winner = getTeam(matchup.tiebreak_winner);
    document.getElementById('winnerName').textContent = `${getTeamDisplayName(winner)} (${winner.abbr})`;
    document.getElementById('winnerMethod').innerHTML = `Won on <strong>${matchup.tiebreak_method.toUpperCase()}</strong>`;
    document.getElementById('results').classList.remove('hidden');
}

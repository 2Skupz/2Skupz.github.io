let currentLeague = 'AL';
let teams = [];
let tiebreakers = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadTeams();
    await loadTiebreakers();
    populateSelectors();
});

async function loadTeams() {
    try {
        const response = await fetch('mlbTiebreakTeams.csv');
        const csv = await response.text();
        const lines = csv.split('\n').filter(line => line.trim());
        
        teams = lines.map(line => {
            const [abbr, city, nickname, league, division] = line.split(',');
            return {
                abbr: abbr.trim(),
                city: city.trim(),
                nickname: nickname.trim(),
                league: league.trim(),
                division: division.trim()
            };
        });
        console.log('Loaded teams:', teams.length);
    } catch (error) {
        console.error('Error loading teams:', error);
        alert('Could not load teams. Make sure mlbTiebreakTeams.csv exists.');
    }
}

async function loadTiebreakers() {
    try {
        const response = await fetch('tiebreakers.json');
        tiebreakers = await response.json();
        console.log('Loaded tiebreakers:', Object.keys(tiebreakers));
    } catch (error) {
        console.error('Error loading tiebreakers:', error);
        alert('Could not load tiebreakers. Make sure tiebreakers.json exists.');
    }
}

function populateSelectors() {
    const leagueTeams = teams.filter(t => t.league === currentLeague).sort((a, b) => a.abbr.localeCompare(b.abbr));
    
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    
    const options = '<option value="">Select a team...</option>' + 
        leagueTeams.map(t => `<option value="${t.abbr}">${t.city} ${t.nickname} (${t.abbr})</option>`).join('');
    
    team1Select.innerHTML = options;
    team2Select.innerHTML = options;
    
    // Reset selections
    team1Select.value = '';
    team2Select.value = '';
    
    // Hide results
    document.getElementById('results').classList.add('hidden');
}

function switchLeague(league) {
    currentLeague = league;
    
    // Update button states
    document.getElementById('leagueAL').classList.toggle('active', league === 'AL');
    document.getElementById('leagueNL').classList.toggle('active', league === 'NL');
    document.getElementById('leagueNL').classList.toggle('nl', league === 'NL');
    
    populateSelectors();
}

function showMatchup() {
    const team1 = document.getElementById('team1').value;
    const team2 = document.getElementById('team2').value;
    
    if (!team1 || !team2) {
        alert('Please select both teams');
        return;
    }
    
    if (team1 === team2) {
        alert('Please select different teams');
        return;
    }
    
    // Find matchup in tiebreakers
    const leagueData = tiebreakers['2025'][currentLeague];
    let matchup = null;

    // 1️⃣ Try to find an exact match first
    matchup = leagueData.find(m => m.team1 === team1 && m.team2 === team2);

    // 2️⃣ If not found, look for reversed matchup
    if (!matchup) {
        const reversed = leagueData.find(m => m.team1 === team2 && m.team2 === team1);
        if (reversed) {
            matchup = {
                team1: reversed.team2,
                team2: reversed.team1,
                h2h_record_1: reversed.h2h_record_2,
                h2h_record_2: reversed.h2h_record_1,
                h2h_record_winner: reversed.h2h_record_winner === reversed.team1 ? reversed.team2 :
                                   (reversed.h2h_record_winner === reversed.team2 ? reversed.team1 : null),
                div_record_1: reversed.div_record_2,
                div_record_2: reversed.div_record_1,
                div_record_winner: reversed.div_record_winner === reversed.team1 ? reversed.team2 :
                                   (reversed.div_record_winner === reversed.team2 ? reversed.team1 : null),
                league_record_1: reversed.league_record_2,
                league_record_2: reversed.league_record_1,
                league_record_winner: reversed.league_record_winner === reversed.team1 ? reversed.team2 :
                                      (reversed.league_record_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_winner: reversed.tiebreak_winner === reversed.team1 ? reversed.team2 :
                                 (reversed.tiebreak_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_method: reversed.tiebreak_method
            };
        }
    }

    if (!matchup) {
        alert('Matchup not found');
        return;
    }

    console.log('=== DEBUG ===');
    console.log('Selected team1:', team1);
    console.log('Selected team2:', team2);
    console.log('Matchup found:', matchup);
    console.log('Matchup.team1:', matchup.team1, 'Matchup.team2:', matchup.team2);
    console.log('H2H winner:', matchup.h2h_record_winner);
    console.log('Tiebreak winner:', matchup.tiebreak_winner);
    console.log('=== END DEBUG ===');
    
    displayMatchup(matchup);
}

function displayMatchup(matchup) {
    const getTeamName = (abbr) => {
        const t = teams.find(tm => tm.abbr === abbr);
        return t ? `${t.city} ${t.nickname}` : abbr;
    };
    
    // Team info
    document.getElementById('team1Name').textContent = getTeamName(matchup.team1);
    document.getElementById('team1Abbr').textContent = matchup.team1;
    document.getElementById('team2Name').textContent = getTeamName(matchup.team2);
    document.getElementById('team2Abbr').textContent = matchup.team2;
    
    // Records with bold styling for winners
    const formatRecord = (record, isWinner) => {
        return `<span class="${isWinner ? 'winner' : ''}">${record}</span>`;
    };
    
    document.getElementById('h2h1').innerHTML = formatRecord(matchup.h2h_record_1, matchup.h2h_record_winner === matchup.team1);
    document.getElementById('h2h2').innerHTML = formatRecord(matchup.h2h_record_2, matchup.h2h_record_winner === matchup.team2);
    
    document.getElementById('div1').innerHTML = formatRecord(matchup.div_record_1, matchup.div_record_winner === matchup.team1);
    document.getElementById('div2').innerHTML = formatRecord(matchup.div_record_2, matchup.div_record_winner === matchup.team2);
    
    document.getElementById('league1').innerHTML = formatRecord(matchup.league_record_1, matchup.league_record_winner === matchup.team1);
    document.getElementById('league2').innerHTML = formatRecord(matchup.league_record_2, matchup.league_record_winner === matchup.team2);
    
    // Winner
    document.getElementById('winnerName').textContent = `${getTeamName(matchup.tiebreak_winner)} (${matchup.tiebreak_winner})`;
    document.getElementById('winnerMethod').innerHTML = `Won on <strong>${matchup.tiebreak_method.toUpperCase()}</strong>`;
    
    // Show results
    document.getElementById('results').classList.remove('hidden');
}
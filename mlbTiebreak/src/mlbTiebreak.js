#==========================================================================
# MLB Tiebreaker Logic and UI Controller
#==========================================================================

let currentLeague = 'AL';
let teams = [];
let tiebreakers = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadTeams();
    await loadTiebreakers();
    populateSelectors();
});

#==========================================================================
# Fetch and parse team data from CSV
#==========================================================================
async function loadTeams() {
    try {
        const response = await fetch('../data/teams/2025teams.csv');
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
    }
}

#==========================================================================
# Load tiebreaker JSON data
#==========================================================================
async function loadTiebreakers() {
    try {
        const response = await fetch('../data/tiebreakers.json');
        tiebreakers = await response.json();
    } catch (error) {
        console.error('Error loading tiebreakers:', error);
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
    
    team1Select.value = '';
    team2Select.value = '';
    
    document.getElementById('results').classList.add('hidden');
}

function switchLeague(league) {
    currentLeague = league;
    document.getElementById('leagueAL').classList.toggle('active', league === 'AL');
    document.getElementById('leagueNL').classList.toggle('active', league === 'NL');
    populateSelectors();
}

#==========================================================================
# Find and process the matchup from the tiebreaker data
#==========================================================================
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
    
    const leagueData = tiebreakers['2025'][currentLeague];
    let matchup = leagueData.find(m => m.team1 === team1 && m.team2 === team2);

    if (!matchup) {
        const reversed = leagueData.find(m => m.team1 === team2 && m.team2 === team1);
        if (reversed) {
            matchup = {
                team1: reversed.team2,
                team2: reversed.team1,
                h2h_record_1: reversed.h2h_record_2,
                h2h_record_2: reversed.h2h_record_1,
                h2h_record_winner: reversed.h2h_record_winner === reversed.team1 ? reversed.team2 : (reversed.h2h_record_winner === reversed.team2 ? reversed.team1 : null),
                div_record_1: reversed.div_record_2,
                div_record_2: reversed.div_record_1,
                div_record_winner: reversed.div_record_winner === reversed.team1 ? reversed.team2 : (reversed.div_record_winner === reversed.team2 ? reversed.team1 : null),
                league_record_1: reversed.league_record_2,
                league_record_2: reversed.league_record_1,
                league_record_winner: reversed.league_record_winner === reversed.team1 ? reversed.team2 : (reversed.league_record_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_winner: reversed.tiebreak_winner === reversed.team1 ? reversed.team2 : (reversed.tiebreak_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_method: reversed.tiebreak_method
            };
        }
    }

    if (matchup) {
        displayMatchup(matchup);
    } else {
        alert('Matchup data not found.');
    }
}

#==========================================================================
# Update the UI with records, names, and dynamic logos
#==========================================================================
function displayMatchup(matchup) {
    const getTeamObj = (abbr) => teams.find(tm => tm.abbr === abbr);
    
    const t1 = getTeamObj(matchup.team1);
    const t2 = getTeamObj(matchup.team2);
    
    // Update Text Info
    document.getElementById('team1Name').textContent = `${t1.city} ${t1.nickname}`;
    document.getElementById('team1Abbr').textContent = matchup.team1;
    document.getElementById('team2Name').textContent = `${t2.city} ${t2.nickname}`;
    document.getElementById('team2Abbr').textContent = matchup.team2;
    
    // Update Logos (Format: CityNickname.png)
    const logo1 = document.getElementById('team1Logo');
    const logo2 = document.getElementById('team2Logo');
    
    logo1.src = `../data/logos/${t1.city}${t1.nickname}.png`;
    logo2.src = `../data/logos/${t2.city}${t2.nickname}.png`;
    
    // Update Records
    const formatRecord = (record, isWinner) => `<span class="${isWinner ? 'winner' : ''}">${record}</span>`;
    
    document.getElementById('h2h1').innerHTML = formatRecord(matchup.h2h_record_1, matchup.h2h_record_winner === matchup.team1);
    document.getElementById('h2h2').innerHTML = formatRecord(matchup.h2h_record_2, matchup.h2h_record_winner === matchup.team2);
    
    document.getElementById('div1').innerHTML = formatRecord(matchup.div_record_1, matchup.div_record_winner === matchup.team1);
    document.getElementById('div2').innerHTML = formatRecord(matchup.div_record_2, matchup.div_record_winner === matchup.team2);
    
    document.getElementById('league1').innerHTML = formatRecord(matchup.league_record_1, matchup.league_record_winner === matchup.team1);
    document.getElementById('league2').innerHTML = formatRecord(matchup.league_record_2, matchup.league_record_winner === matchup.team2);
    
    // Update Winner Box
    const winner = getTeamObj(matchup.tiebreak_winner);
    document.getElementById('winnerName').textContent = `${winner.city} ${winner.nickname} (${matchup.tiebreak_winner})`;
    document.getElementById('winnerMethod').innerHTML = `Won on <strong>${matchup.tiebreak_method.toUpperCase()}</strong>`;
    
    document.getElementById('results').classList.remove('hidden');
}
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
        const response = await fetch('../data/teams/2025teams.csv');
        const csv = await response.text();
        const lines = csv.split('\n').map(line => line.trim()).filter(line => line);
        
        teams = lines.map(line => {
            const parts = line.split(',');
            if (parts.length < 5) return null;
            return {
                abbr: parts[0].trim(),
                city: parts[1].trim(),
                nickname: parts[2].trim(),
                league: parts[3].trim(),
                division: parts[4].trim()
            };
        }).filter(t => t !== null);
        
        console.log('Loaded teams:', teams.length);
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

async function loadTiebreakers() {
    try {
        const response = await fetch('../data/tiebreakers.json');
        const data = await response.json();
        // Access the 2025 object specifically from your JSON structure
        tiebreakers = data['2025'];
        console.log('Loaded tiebreakers');
    } catch (error) {
        console.error('Error loading tiebreakers:', error);
    }
}

function populateSelectors() {
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    
    const leagueTeams = teams.filter(t => t.league === currentLeague)
                             .sort((a, b) => a.abbr.localeCompare(b.abbr));
    
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

function showMatchup() {
    const t1Abbr = document.getElementById('team1').value;
    const t2Abbr = document.getElementById('team2').value;
    
    if (!t1Abbr || !t2Abbr) {
        alert('Please select both teams');
        return;
    }
    
    if (t1Abbr === t2Abbr) {
        alert('Please select different teams');
        return;
    }
    
    if (!tiebreakers || !tiebreakers[currentLeague]) {
        alert('Tiebreaker data not loaded. Ensure you are using a local server.');
        return;
    }
    
    const leagueData = tiebreakers[currentLeague];
    let matchup = leagueData.find(m => m.team1 === t1Abbr && m.team2 === t2Abbr);

    if (!matchup) {
        const reversed = leagueData.find(m => m.team1 === t2Abbr && m.team2 === t1Abbr);
        if (reversed) {
            matchup = {
                team1: reversed.team2, team2: reversed.team1,
                h2h_record_1: reversed.h2h_record_2, h2h_record_2: reversed.h2h_record_1,
                h2h_record_winner: reversed.h2h_record_winner === reversed.team1 ? reversed.team2 : (reversed.h2h_record_winner === reversed.team2 ? reversed.team1 : null),
                div_record_1: reversed.div_record_2, div_record_2: reversed.div_record_1,
                div_record_winner: reversed.div_record_winner === reversed.team1 ? reversed.team2 : (reversed.div_record_winner === reversed.team2 ? reversed.team1 : null),
                league_record_1: reversed.league_record_2, league_record_2: reversed.league_record_1,
                league_record_winner: reversed.league_record_winner === reversed.team1 ? reversed.team2 : (reversed.league_record_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_winner: reversed.tiebreak_winner === reversed.team1 ? reversed.team2 : (reversed.tiebreak_winner === reversed.team2 ? reversed.team1 : null),
                tiebreak_method: reversed.tiebreak_method
            };
        }
    }

    if (matchup) {
        displayMatchup(matchup);
    } else {
        alert('Matchup not found');
    }
}

function displayMatchup(matchup) {
    const getTeam = (abbr) => teams.find(t => t.abbr === abbr);
    const t1 = getTeam(matchup.team1);
    const t2 = getTeam(matchup.team2);
    
    document.getElementById('team1Name').textContent = `${t1.city} ${t1.nickname}`;
    document.getElementById('team1Abbr').textContent = t1.abbr;
    document.getElementById('team2Name').textContent = `${t2.city} ${t2.nickname}`;
    document.getElementById('team2Abbr').textContent = t2.abbr;
    
    // Logic for Logos from your FileTree [cite: 1]
    const logo1 = document.getElementById('team1Logo');
    const logo2 = document.getElementById('team2Logo');
    logo1.src = `../data/logos/${t1.city}${t1.nickname}.png`;
    logo2.src = `../data/logos/${t2.city}${t2.nickname}.png`;
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
    document.getElementById('winnerName').textContent = `${winner.city} ${winner.nickname} (${winner.abbr})`;
    document.getElementById('winnerMethod').innerHTML = `Won on <strong>${matchup.tiebreak_method.toUpperCase()}</strong>`;
    
    document.getElementById('results').classList.remove('hidden');
}
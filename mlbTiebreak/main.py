#==============================================================================
# Main entry point for the MLB Tiebreak project.
#==============================================================================
import sys
import os

# Add the scripts directory to the path so it can find utils
projectRoot = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(projectRoot, 'scripts'))

import config
from scripts.getGames import createSchedule, writeGames
from scripts.generateTiebreakers import generate_tiebreakers, write_tiebreakers
from scripts.generateTiebreakGrid import generate_grid, generate_summary

def runTiebreakPipeline():
    season = config.getSeason()
    
    # 1. Update Game Data
    print(f"--- Step 1: Updating game data for {season} ---")
    leagueGames = createSchedule(season)
    writeGames(leagueGames, season)
    
    # 2. Process Tiebreaker Logic
    print(f"\n--- Step 2: Calculating tiebreaker matchups ---")
    tiebreakerData = generate_tiebreakers(season)
    write_tiebreakers(tiebreakerData, season)
    
    # 3. Generate Visual Reports
    print(f"\n--- Step 3: Generating text grids and summaries ---")
    alGrid = generate_grid(season, 'AL')
    alSummary = generate_summary(season, 'AL')
    nlGrid = generate_grid(season, 'NL')
    nlSummary = generate_summary(season, 'NL')
    
    reportPath = config.getGridsPath()
    with open(reportPath, 'w') as f:
        f.write("=" * 130 + "\n")
        f.write(f"MLB TIEBREAKER WINNERS - {season}\n")
        f.write("=" * 130 + "\n\n")
        f.write("AMERICAN LEAGUE\n" + "-" * 130 + "\n")
        f.write(alGrid + "\n" + alSummary + "\n\n")
        f.write("NATIONAL LEAGUE\n" + "-" * 130 + "\n")
        f.write(nlGrid + "\n" + nlSummary + "\n")
        
    print(f"\nPipeline complete! View results in: {reportPath}")

if __name__ == "__main__":
    runTiebreakPipeline()
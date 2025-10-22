# College Football Heavyweight Championship Tracker

A Python application that tracks the "Heavyweight Championship" of college football - a traveling championship that follows the principle: you become the champ by beating the champ.

## Concept

Starting with the first college football game (Rutgers vs Princeton, November 6, 1869), this program tracks who holds the "belt" through history. The belt changes hands only when the current champion loses a game.

## Project Structure

```
cfbHeavyweights2/
├── data/
│   ├── games/          # CSV files with game data by season
│   ├── teams/          # CSV files with team data by season
│   └── reports/        # Generated text reports
├── src/
│   ├── main.py         # Main entry point
│   ├── data_loaders/
│   │   └── getGames.py # Web scraping for games/teams
│   ├── models/
│   │   └── heavyweightClasses.py  # Core classes (Team, Game, Reign)
│   ├── utils/
│   │   └── helpers.py  # Helper functions
│   └── analysis/
│       └── heavyweightTracker.py  # Analysis logic
├── web/
│   ├── index.html      # Generated webpage
│   └── assets/
│       ├── style.css   # Webpage styling
│       └── theChamp.jpeg
└── tests/
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- BeautifulSoup4
- urllib3

Create a `requirements.txt` file with:
```
beautifulsoup4==4.12.2
urllib3==2.0.7
```

## Usage

Run the main program:
```bash
python -m src.main
```

This will:
1. Load historical game data from CSV files
2. Process all bouts (games where the belt is at stake)
3. Calculate team statistics
4. Generate reports in `data/reports/`
5. Create the main webpage at `web/index.html`

## Features

- **Historical Tracking**: Tracks the belt from 1869 to present
- **Team Statistics**: Records for each team as belt holder and challenger
- **Multiple Reports**:
  - All-time rankings
  - Top 25 active teams
  - Longest reigns
  - School-by-school histories
  - Complete bout listing
  - Yearly champions

## Data Sources

Game data is scraped from Sports Reference (sports-reference.com/cfb)

## Key Concepts

- **Bout**: A game where the heavyweight belt is at stake
- **Reign**: A continuous period where a team holds the belt
- **Challenge**: Any game where a team plays for the belt (as holder or challenger)
- **Defensive Record**: Games played while holding the belt (excludes the challenge win that earned the belt)

## Notes

- The year 1871 is skipped (no games played)
- Games in January count toward the previous season
- Ties: The belt holder retains the belt in case of a tie
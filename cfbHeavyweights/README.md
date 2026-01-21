# Ken Schroeder
# Version 2 of my College Football Heavyweight Championship Tracker
# Written October 20, 2025

# College Football Heavyweight Championship Tracker

A Python application that tracks the "Heavyweight Championship" of college football - a traveling championship belt that follows boxing's principle: **you become the champ by beating the champ**.

## Concept

Starting with the first college football game on November 6, 1869 (Rutgers vs Princeton), this program tracks who holds the "belt" throughout history. The championship changes hands only when the current champion loses a game. If the champion ties, they retain the belt.

## Features

- **Historical Tracking**: Complete belt history from 1869 to present
- **Comprehensive Statistics**: 
  - Team records as belt holder vs. challenger
  - Number of reigns per team
  - Longest reigns
  - National championship correlations
- **Multiple Reports**:
  - All-time rankings
  - Top 25 active FBS teams
  - School-by-school histories
  - Complete bout listing
  - Yearly champions
  - Longest championship reigns
- **Web Interface**: Generates a clean, styled HTML page showing current champion and full history

## Project Structure

```
cfbHeavyweights2/
├── data/
│   ├── games/          # CSV files with game data by season (1869-present)
│   ├── teams/          # CSV files with team data by season
│   └── reports/        # Generated text reports
├── src/
│   ├── main.py                      # Main entry point
│   ├── data_loaders/
│   │   └── getGames.py              # Web scraping from Sports Reference
│   ├── models/
│   │   └── heavyweightClasses.py   # Core classes (Team, Game, Reign)
│   ├── utils/
│   │   └── helpers.py               # Helper functions
│   └── analysis/
│       └── heavyweightTracker.py    # Analysis and tracking logic
├── web/
│   ├── cfbHeavyweights.html         # Generated webpage
│   └── assets/
│       ├── cfbHeavyweights.css      # Styling
│       └── theChamp.jpeg            # Championship logo
├── requirements.txt
└── README.md
```

## Installation

1. **Clone or download the repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Ensure you have Python 3.7+**:
```bash
python3 --version
```

## Usage

Run the program from the project root directory:

```bash
python3 -m src.main
```

This will:
1. Load historical game data from CSV files in `data/games/` and `data/teams/`
2. Process all bouts (games where the belt is at stake)
3. Calculate comprehensive team statistics
4. Generate text reports in `data/reports/`
5. Create the main webpage at `web/cfbHeavyweights.html`

### Viewing Results

Open `web/cfbHeavyweights.html` in your browser to see:
- Current belt holder
- Their complete reign and challenge history
- Links to all statistical reports

## Key Concepts

### Belt Terminology

- **Bout**: A game where the heavyweight belt is at stake (champion is playing)
- **Reign**: A continuous period where a team holds the belt
- **Challenge**: Any game where a team plays for the belt (as holder or challenger)
- **Defensive Record**: Games played while holding the belt
  - *Note: The first game of each reign (the challenge victory that won the belt) is NOT counted as a defensive game*

### Rules

- The belt starts with Rutgers (winner of first game, Nov 6, 1869)
- Belt changes hands when the champion loses
- Champion retains belt in case of a tie
- Games in January count toward the previous season
- The year 1871 is skipped (no games played)

## Data Sources

Game and team data is scraped from [Sports Reference](https://www.sports-reference.com/cfb/) when needed.

## Generated Reports

All reports are created in `data/reports/`:

1. **allTimeRankings.txt**: All teams ranked by a points system (reigns + wins + win percentage)
2. **top25Active.txt**: Top 25 currently active FBS teams
3. **schoolBySchool.txt**: Complete history for every team
4. **longestReigns.txt**: Championship reigns of 10+ games
5. **allBouts.txt**: Complete list of every belt game ever played
6. **yearlyBeltWinners.txt**: Who held the belt at the end of each season

## Statistics Calculation

Teams are ranked using a points system:
- 100 points per reign
- 10,000 points per bout win
- Bonus points for winning percentage

Records are broken down into:
- **As Belt Holder**: Defensive games (excluding the challenge win that earned the belt)
- **As Challenger**: Games attempting to win the belt

## Requirements

- Python 3.7+
- BeautifulSoup4 (for web scraping)

See `requirements.txt` for specific versions.

## Troubleshooting

**Import errors**: Make sure you're running from the project root with `python3 -m src.main`

**Missing game files**: The program will attempt to download them from Sports Reference if they don't exist

**Path issues**: All paths are relative to the project root directory

## Future Enhancements

Potential features to add:
- Automatic weekly updates during football season
- Interactive web visualization
- Conference-based statistics
- Era-based analysis
- Championship drought tracking

## Author

Created to answer the question: "What if college football had a traveling championship like boxing?"

## License

Feel free to use and modify as you wish!

---

## Version Updates:
- V2: A few bug fixes in counting wins, etc. Centered webpage. Mostly structural changes
*Last Updated: 2025*
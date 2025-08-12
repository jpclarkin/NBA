# NBA Data Science Infrastructure

A comprehensive data pipeline for NBA analytics including data ingestion, feature engineering, ML model training, and analysis.

## Features

- **Data Ingestion**: Fetch data from NBA.com API
- **Database Models**: Comprehensive SQLAlchemy models for teams, players, games, and statistics
- **Feature Engineering**: Build features for ML models
- **ML Integration**: Ready for MLflow and Feast integration
- **Analysis Tools**: Historical analysis and visualization capabilities

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to the NBA directory
cd NBA

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the NBA directory:

```bash
# Optional: NBA API key (if you have one)
NBA_API_KEY=your_api_key_here

# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite:///nba.sqlite3
```

### 3. Initialize Database

```bash
python main.py init-db
```

### 4. Ingest Data

```bash
# Ingest teams
python main.py ingest-teams

# Ingest games for a specific season
python main.py ingest-games --season 2023 --season-type "Regular Season"

# Ingest team statistics
python main.py ingest-team-stats --season 2023 --season-type "Regular Season"

# Ingest players
python main.py ingest-players --season 2023

# Ingest player statistics
python main.py ingest-player-stats --season 2023 --season-type "Regular Season"

# Ingest historical data (multiple years)
python main.py ingest-historical --start-year 2020 --end-year 2023 --data-types teams games team_stats
```

## Data Models

### Teams
- Basic team information (name, abbreviation, city, state)
- Conference and division
- Arena information
- Team colors and logos

### Players
- Player details (name, position, height, weight)
- Birth information and college
- Draft information
- Current team and status

### Games
- Game metadata (date, season, type)
- Team matchups and results
- Arena and attendance
- Game context (rest days, back-to-back)

### Statistics
- Team statistics (offensive, defensive, advanced metrics)
- Player statistics (per-game averages, percentages)
- Game-level statistics
- Historical trends

## API Integration

The infrastructure uses the NBA.com API to fetch data. Key endpoints include:

- **Teams**: `commonteamroster` - Team information and rosters
- **Games**: `scoreboard` - Game schedules and results
- **Team Stats**: `leaguedashteamstats` - Team statistics
- **Player Stats**: `leaguedashplayerstats` - Player statistics
- **Game Stats**: `boxscoretraditionalv2` - Detailed game statistics

## Database Schema

The database uses SQLAlchemy with the following main tables:

- `teams` - Team information
- `players` - Player information
- `games` - Game metadata and results
- `team_stats` - Team statistics by season
- `player_season_stats` - Player statistics by season
- `game_stats` - Game-level team statistics
- `player_game_stats` - Game-level player statistics
- `betting_lines` - Betting information (placeholder)

## CLI Commands

### Data Ingestion

```bash
# Initialize database
python main.py init-db

# Ingest teams
python main.py ingest-teams

# Ingest games
python main.py ingest-games --season 2023 --season-type "Regular Season"

# Ingest players
python main.py ingest-players --season 2023

# Ingest team statistics
python main.py ingest-team-stats --season 2023 --season-type "Regular Season"

# Ingest player statistics
python main.py ingest-player-stats --season 2023 --season-type "Regular Season"

# Ingest historical data
python main.py ingest-historical --start-year 2020 --end-year 2023
```

### Analysis

```bash
# Run analysis (coming soon)
python main.py analyze --season 2023 --analysis-type team_performance
```

## Project Structure

```
NBA/
├── nba/                    # Main package
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── db/                # Database models and session
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   └── session.py     # Database session management
│   ├── ingest/            # Data ingestion modules
│   │   ├── __init__.py
│   │   ├── teams_ingest.py
│   │   ├── games_ingest.py
│   │   ├── players_ingest.py
│   │   └── stats_ingest.py
│   ├── sources/           # Data sources
│   │   ├── __init__.py
│   │   └── nba_client.py  # NBA API client
│   ├── ml/                # ML modules (coming soon)
│   └── analysis/          # Analysis modules (coming soon)
├── data/                  # Data storage
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks
├── scripts/               # Utility scripts
├── main.py               # CLI interface
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Development

### Adding New Data Sources

1. Create a new client in `nba/sources/`
2. Implement the required methods
3. Create corresponding ingestion modules in `nba/ingest/`
4. Add CLI commands in `main.py`

### Adding New Models

1. Define new SQLAlchemy models in `nba/db/models.py`
2. Create migration scripts if needed
3. Update ingestion modules to handle new data

### Adding Analysis Features

1. Create analysis modules in `nba/analysis/`
2. Implement analysis functions
3. Add CLI commands in `main.py`

## Integration with ML Infrastructure

This NBA infrastructure is designed to integrate with the existing ML infrastructure:

- **MLflow**: For experiment tracking and model management
- **Feast**: For feature store integration
- **Optuna**: For hyperparameter optimization

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Include docstrings for all functions
4. Test your changes thoroughly
5. Update documentation as needed

## License

This project is part of the larger Data Science infrastructure and follows the same licensing terms.

## Support

For questions or issues, please refer to the main Data Science infrastructure documentation or create an issue in the project repository.

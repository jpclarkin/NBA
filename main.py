#!/usr/bin/env python3
"""
NBA Data Science Pipeline

This CLI interface provides comprehensive capabilities for:
- Historical data ingestion from NBA API
- Feature engineering and ML model training
- Historical analysis and visualization
- Integration with MLflow and Feast
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nba.config import get_settings
from nba.db.session import create_all_tables, get_session_factory
from nba.ingest.teams_ingest import ingest_teams
from nba.ingest.games_ingest import ingest_games
from nba.ingest.players_ingest import ingest_players
from nba.ingest.stats_ingest import ingest_team_stats, ingest_player_stats


def ensure_directories() -> None:
    """Ensure necessary directories exist."""
    Path("data").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("analysis").mkdir(exist_ok=True)
    Path("visualizations").mkdir(exist_ok=True)


def cli() -> None:
    """CLI interface for NBA data pipeline."""
    parser = argparse.ArgumentParser(description="NBA Data Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ===== DATA INGESTION COMMANDS =====
    
    # Teams ingestion
    p_teams = subparsers.add_parser("ingest-teams", help="Ingest team information")
    
    # Games ingestion
    p_games = subparsers.add_parser("ingest-games", help="Ingest game data")
    p_games.add_argument("--season", type=int, required=True, help="NBA season year (e.g., 2023 for 2023-24)")
    p_games.add_argument("--season-type", type=str, default="Regular Season", 
                        choices=["Regular Season", "Playoffs", "All-Star"],
                        help="Season type")
    
    # Players ingestion
    p_players = subparsers.add_parser("ingest-players", help="Ingest player data")
    p_players.add_argument("--season", type=int, help="NBA season year")
    p_players.add_argument("--team-id", type=str, help="Specific team ID to ingest players for")
    
    # Team stats ingestion
    p_team_stats = subparsers.add_parser("ingest-team-stats", help="Ingest team statistics")
    p_team_stats.add_argument("--season", type=int, required=True, help="NBA season year")
    p_team_stats.add_argument("--season-type", type=str, default="Regular Season",
                             choices=["Regular Season", "Playoffs", "All-Star"],
                             help="Season type")
    
    # Player stats ingestion
    p_player_stats = subparsers.add_parser("ingest-player-stats", help="Ingest player statistics")
    p_player_stats.add_argument("--season", type=int, required=True, help="NBA season year")
    p_player_stats.add_argument("--season-type", type=str, default="Regular Season",
                               choices=["Regular Season", "Playoffs", "All-Star"],
                               help="Season type")
    p_player_stats.add_argument("--team-id", type=str, help="Specific team ID to ingest stats for")
    
    # Historical data ingestion
    p_historical = subparsers.add_parser("ingest-historical", help="Ingest historical data")
    p_historical.add_argument("--start-year", type=int, default=2020, help="Start year for ingestion")
    p_historical.add_argument("--end-year", type=int, default=None, help="End year for ingestion")
    p_historical.add_argument("--data-types", nargs="+", 
                             choices=["teams", "games", "players", "team_stats", "player_stats"],
                             default=["teams", "games", "team_stats"],
                             help="Types of data to ingest")
    p_historical.add_argument("--season-type", type=str, default="Regular Season",
                             choices=["Regular Season", "Playoffs", "All-Star"],
                             help="Season type for games and stats")

    # ===== DATABASE COMMANDS =====
    
    p_db = subparsers.add_parser("init-db", help="Initialize database tables")
    
    # ===== ANALYSIS COMMANDS =====
    
    p_analyze = subparsers.add_parser("analyze", help="Run analysis")
    p_analyze.add_argument("--season", type=int, help="Season to analyze")
    p_analyze.add_argument("--analysis-type", type=str, 
                          choices=["team_performance", "player_performance", "game_trends"],
                          default="team_performance",
                          help="Type of analysis to run")

    # Parse arguments
    args = parser.parse_args()

    # Ensure directories exist
    ensure_directories()

    # Execute commands
    if args.command == "init-db":
        print("Initializing database tables...")
        create_all_tables()
        print("Database tables created successfully!")
        
    elif args.command == "ingest-teams":
        print("Ingesting teams...")
        ingest_teams()
        
    elif args.command == "ingest-games":
        print(f"Ingesting games for {args.season} {args.season_type}...")
        ingest_games(args.season, args.season_type)
        
    elif args.command == "ingest-players":
        print("Ingesting players...")
        ingest_players(args.season, args.team_id)
        
    elif args.command == "ingest-team-stats":
        print(f"Ingesting team stats for {args.season} {args.season_type}...")
        ingest_team_stats(args.season, args.season_type)
        
    elif args.command == "ingest-player-stats":
        print(f"Ingesting player stats for {args.season} {args.season_type}...")
        ingest_player_stats(args.season, args.season_type, args.team_id)
        
    elif args.command == "ingest-historical":
        end_year = args.end_year or args.start_year
        print(f"Ingesting historical data from {args.start_year} to {end_year}...")
        
        for year in range(args.start_year, end_year + 1):
            print(f"\nProcessing year {year}...")
            
            if "teams" in args.data_types:
                print("  Ingesting teams...")
                ingest_teams()
                
            if "games" in args.data_types:
                print(f"  Ingesting games for {year} {args.season_type}...")
                ingest_games(year, args.season_type)
                
            if "players" in args.data_types:
                print(f"  Ingesting players for {year}...")
                ingest_players(year)
                
            if "team_stats" in args.data_types:
                print(f"  Ingesting team stats for {year} {args.season_type}...")
                ingest_team_stats(year, args.season_type)
                
            if "player_stats" in args.data_types:
                print(f"  Ingesting player stats for {year} {args.season_type}...")
                ingest_player_stats(year, args.season_type)
        
        print(f"\nHistorical data ingestion completed for {args.start_year}-{end_year}")
        
    elif args.command == "analyze":
        print(f"Running {args.analysis_type} analysis...")
        # TODO: Implement analysis functions
        print("Analysis functionality coming soon!")


if __name__ == "__main__":
    cli()

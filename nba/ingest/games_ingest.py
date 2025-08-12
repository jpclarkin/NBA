"""
Game data ingestion for NBA
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from nba.db.session import get_session_factory
from nba.db.models import Game, Team
from nba.sources.nba_api_client_fixed import NBAAPIClientFixed as NBAAPIClient


def ingest_games(season: int, season_type: str = "Regular Season", 
                session: Session = None) -> List[Game]:
    """
    Ingest game data from NBA API.
    
    Args:
        season: NBA season year (e.g., 2023 for 2023-24 season)
        season_type: Season type ('Regular Season', 'Playoffs', etc.)
        session: Database session. If None, creates a new session.
        
    Returns:
        List of ingested Game objects.
    """
    client = NBAAPIClient()
    
    # Use provided session or create new one
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        # Fetch games from API
        games_data = client.get_games(season, season_type)
        
        ingested_games = []
        
        for game_data in games_data:
            # Check if game already exists
            existing_game = session.query(Game).filter(
                Game.id == game_data["game_id"]
            ).first()
            
            if existing_game:
                # Update existing game
                for key, value in game_data.items():
                    if hasattr(existing_game, key):
                        setattr(existing_game, key, value)
                ingested_games.append(existing_game)
            else:
                # Get team references
                home_team = get_team_by_abbreviation(game_data["home_team_abbr"], session)
                away_team = get_team_by_abbreviation(game_data["away_team_abbr"], session)
                
                # Parse game date
                game_date = None
                if game_data.get("game_date"):
                    if isinstance(game_data["game_date"], str):
                        game_date = datetime.strptime(game_data["game_date"], "%Y-%m-%d").date()
                    elif isinstance(game_data["game_date"], date):
                        game_date = game_data["game_date"]
                
                # Determine home win
                home_win = None
                if game_data.get("home_score") is not None and game_data.get("away_score") is not None:
                    home_win = game_data["home_score"] > game_data["away_score"]
                
                # Create new game
                game = Game(
                    id=game_data["game_id"],
                    game_date=game_date,
                    season=season,
                    season_type=season_type,
                    home_team_id=home_team.id if home_team else None,
                    away_team_id=away_team.id if away_team else None,
                    home_team_abbr=game_data["home_team_abbr"],
                    away_team_abbr=game_data["away_team_abbr"],
                    home_score=game_data.get("home_score"),
                    away_score=game_data.get("away_score"),
                    home_win=home_win,
                    arena=game_data.get("arena"),
                    attendance=game_data.get("attendance"),
                    duration_minutes=game_data.get("duration_minutes")
                )
                session.add(game)
                ingested_games.append(game)
        
        session.commit()
        print(f"Successfully ingested {len(ingested_games)} games for {season} {season_type}")
        
        return ingested_games
        
    except Exception as e:
        session.rollback()
        print(f"Error ingesting games: {e}")
        raise
    finally:
        if should_close:
            session.close()


def get_team_by_abbreviation(abbreviation: str, session: Session) -> Optional[Team]:
    """
    Get team by abbreviation.
    
    Args:
        abbreviation: Team abbreviation (e.g., 'LAL', 'BOS')
        session: Database session
        
    Returns:
        Team object or None if not found.
    """
    return session.query(Team).filter(
        Team.abbreviation == abbreviation.upper()
    ).first()


def get_games_by_season(season: int, season_type: str = "Regular Season", 
                       session: Session = None) -> List[Game]:
    """
    Get all games for a specific season.
    
    Args:
        season: NBA season year
        season_type: Season type
        session: Database session. If None, creates a new session.
        
    Returns:
        List of Game objects.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        games = session.query(Game).filter(
            Game.season == season,
            Game.season_type == season_type
        ).all()
        return games
    finally:
        if should_close:
            session.close()


def get_games_by_date_range(start_date: date, end_date: date, 
                           session: Session = None) -> List[Game]:
    """
    Get games within a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        session: Database session. If None, creates a new session.
        
    Returns:
        List of Game objects.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        games = session.query(Game).filter(
            Game.game_date >= start_date,
            Game.game_date <= end_date
        ).all()
        return games
    finally:
        if should_close:
            session.close()

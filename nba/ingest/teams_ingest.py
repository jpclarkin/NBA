"""
Team data ingestion for NBA
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from nba.db.session import get_session_factory
from nba.db.models import Team
from nba.sources.nba_api_client_fixed import NBAAPIClientFixed as NBAAPIClient


def ingest_teams(session: Session = None) -> List[Team]:
    """
    Ingest team data from NBA API.
    
    Args:
        session: Database session. If None, creates a new session.
        
    Returns:
        List of ingested Team objects.
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
        # Fetch teams from API
        teams_data = client.get_teams()
        
        ingested_teams = []
        
        for team_data in teams_data:
            # Check if team already exists
            existing_team = session.query(Team).filter(
                Team.team_id == team_data["team_id"]
            ).first()
            
            if existing_team:
                # Update existing team
                for key, value in team_data.items():
                    if hasattr(existing_team, key):
                        setattr(existing_team, key, value)
                ingested_teams.append(existing_team)
            else:
                # Create new team
                team = Team(
                    team_id=team_data["team_id"],
                    name=team_data["name"],
                    abbreviation=team_data["abbreviation"],
                    city=team_data.get("city"),
                    state=team_data.get("state"),
                    conference=team_data.get("conference"),
                    division=team_data.get("division")
                )
                session.add(team)
                ingested_teams.append(team)
        
        session.commit()
        print(f"Successfully ingested {len(ingested_teams)} teams")
        
        return ingested_teams
        
    except Exception as e:
        session.rollback()
        print(f"Error ingesting teams: {e}")
        raise
    finally:
        if should_close:
            session.close()


def get_team_by_abbreviation(abbreviation: str, session: Session = None) -> Team:
    """
    Get team by abbreviation.
    
    Args:
        abbreviation: Team abbreviation (e.g., 'LAL', 'BOS')
        session: Database session. If None, creates a new session.
        
    Returns:
        Team object or None if not found.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        team = session.query(Team).filter(
            Team.abbreviation == abbreviation.upper()
        ).first()
        return team
    finally:
        if should_close:
            session.close()


def get_all_teams(session: Session = None) -> List[Team]:
    """
    Get all teams from database.
    
    Args:
        session: Database session. If None, creates a new session.
        
    Returns:
        List of all Team objects.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        teams = session.query(Team).all()
        return teams
    finally:
        if should_close:
            session.close()

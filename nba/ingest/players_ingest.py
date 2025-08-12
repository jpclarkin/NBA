"""
Player data ingestion for NBA
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from nba.db.session import get_session_factory
from nba.db.models import Player, Team
from nba.sources.nba_client import NBAAPIClient


def ingest_players(season: Optional[int] = None, team_id: Optional[str] = None,
                  session: Session = None) -> List[Player]:
    """
    Ingest player data from NBA API.
    
    Args:
        season: NBA season year (e.g., 2023 for 2023-24 season)
        team_id: Specific team ID to ingest players for
        session: Database session. If None, creates a new session.
        
    Returns:
        List of ingested Player objects.
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
        # Fetch players from API
        players_data = client.get_players(season, team_id)
        
        ingested_players = []
        
        for player_data in players_data:
            # Check if player already exists
            existing_player = session.query(Player).filter(
                Player.player_id == player_data.get("PLAYER_ID")
            ).first()
            
            if existing_player:
                # Update existing player
                update_player_data(existing_player, player_data)
                ingested_players.append(existing_player)
            else:
                # Create new player
                player = create_player_from_data(player_data, session)
                if player:
                    session.add(player)
                    ingested_players.append(player)
        
        session.commit()
        print(f"Successfully ingested {len(ingested_players)} players")
        
        return ingested_players
        
    except Exception as e:
        session.rollback()
        print(f"Error ingesting players: {e}")
        raise
    finally:
        if should_close:
            session.close()


def create_player_from_data(player_data: Dict[str, Any], session: Session) -> Optional[Player]:
    """
    Create a Player object from API data.
    
    Args:
        player_data: Player data from API
        session: Database session
        
    Returns:
        Player object or None if invalid data.
    """
    try:
        # Get team reference
        team = None
        if player_data.get("TEAM_ID"):
            team = session.query(Team).filter(
                Team.team_id == str(player_data["TEAM_ID"])
            ).first()
        
        # Parse birth date
        birth_date = None
        if player_data.get("BIRTH_DATE"):
            try:
                birth_date = datetime.strptime(player_data["BIRTH_DATE"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        
        # Parse draft information
        draft_year = None
        draft_round = None
        draft_number = None
        
        if player_data.get("DRAFT_YEAR"):
            try:
                draft_year = int(player_data["DRAFT_YEAR"])
            except (ValueError, TypeError):
                pass
        
        if player_data.get("DRAFT_ROUND"):
            try:
                draft_round = int(player_data["DRAFT_ROUND"])
            except (ValueError, TypeError):
                pass
        
        if player_data.get("DRAFT_NUMBER"):
            try:
                draft_number = int(player_data["DRAFT_NUMBER"])
            except (ValueError, TypeError):
                pass
        
        # Parse weight
        weight = None
        if player_data.get("WEIGHT"):
            try:
                weight = int(player_data["WEIGHT"])
            except (ValueError, TypeError):
                pass
        
        # Split name into first and last
        full_name = player_data.get("PLAYER_NAME", "")
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        player = Player(
            player_id=str(player_data.get("PLAYER_ID", "")),
            name=full_name,
            first_name=first_name,
            last_name=last_name,
            team_id=team.id if team else None,
            position=player_data.get("POSITION"),
            height=player_data.get("HEIGHT"),
            weight=weight,
            birth_date=birth_date,
            birth_place=player_data.get("BIRTH_PLACE"),
            college=player_data.get("COLLEGE"),
            draft_year=draft_year,
            draft_round=draft_round,
            draft_number=draft_number,
            is_active=player_data.get("IS_ACTIVE", True),
            jersey_number=player_data.get("JERSEY_NUMBER")
        )
        
        return player
        
    except Exception as e:
        print(f"Error creating player from data: {e}")
        return None


def update_player_data(player: Player, player_data: Dict[str, Any]) -> None:
    """
    Update existing player with new data.
    
    Args:
        player: Existing Player object
        player_data: New player data from API
    """
    try:
        # Update basic information
        if player_data.get("PLAYER_NAME"):
            player.name = player_data["PLAYER_NAME"]
            name_parts = player.name.split(" ", 1)
            player.first_name = name_parts[0] if len(name_parts) > 0 else ""
            player.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        if player_data.get("POSITION"):
            player.position = player_data["POSITION"]
        
        if player_data.get("HEIGHT"):
            player.height = player_data["HEIGHT"]
        
        if player_data.get("WEIGHT"):
            try:
                player.weight = int(player_data["WEIGHT"])
            except (ValueError, TypeError):
                pass
        
        if player_data.get("JERSEY_NUMBER"):
            player.jersey_number = player_data["JERSEY_NUMBER"]
        
        if "IS_ACTIVE" in player_data:
            player.is_active = player_data["IS_ACTIVE"]
        
    except Exception as e:
        print(f"Error updating player data: {e}")


def get_players_by_team(team_id: int, session: Session = None) -> List[Player]:
    """
    Get all players for a specific team.
    
    Args:
        team_id: Team ID
        session: Database session. If None, creates a new session.
        
    Returns:
        List of Player objects.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        players = session.query(Player).filter(
            Player.team_id == team_id,
            Player.is_active == True
        ).all()
        return players
    finally:
        if should_close:
            session.close()


def get_player_by_id(player_id: str, session: Session = None) -> Optional[Player]:
    """
    Get player by NBA player ID.
    
    Args:
        player_id: NBA player ID
        session: Database session. If None, creates a new session.
        
    Returns:
        Player object or None if not found.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        player = session.query(Player).filter(
            Player.player_id == player_id
        ).first()
        return player
    finally:
        if should_close:
            session.close()


def get_active_players(session: Session = None) -> List[Player]:
    """
    Get all active players.
    
    Args:
        session: Database session. If None, creates a new session.
        
    Returns:
        List of active Player objects.
    """
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        should_close = True
    else:
        should_close = False
    
    try:
        players = session.query(Player).filter(
            Player.is_active == True
        ).all()
        return players
    finally:
        if should_close:
            session.close()

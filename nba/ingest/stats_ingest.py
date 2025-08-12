"""
Statistics data ingestion for NBA
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from nba.db.session import get_session_factory
from nba.db.models import TeamStats, PlayerSeasonStats, Team, Player
from nba.sources.nba_client import NBAAPIClient


def ingest_team_stats(season: int, season_type: str = "Regular Season",
                     session: Session = None) -> List[TeamStats]:
    """
    Ingest team statistics from NBA API.
    
    Args:
        season: NBA season year (e.g., 2023 for 2023-24 season)
        season_type: Season type ('Regular Season', 'Playoffs', etc.)
        session: Database session. If None, creates a new session.
        
    Returns:
        List of ingested TeamStats objects.
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
        # Fetch team stats from API
        stats_data = client.get_team_stats(season, season_type)
        
        ingested_stats = []
        
        for stat_data in stats_data:
            # Get team reference
            team = session.query(Team).filter(
                Team.team_id == str(stat_data.get("TEAM_ID", ""))
            ).first()
            
            if not team:
                print(f"Team not found for TEAM_ID: {stat_data.get('TEAM_ID')}")
                continue
            
            # Check if stats already exist
            existing_stats = session.query(TeamStats).filter(
                TeamStats.team_id == team.id,
                TeamStats.season == season,
                TeamStats.season_type == season_type
            ).first()
            
            if existing_stats:
                # Update existing stats
                update_team_stats(existing_stats, stat_data)
                ingested_stats.append(existing_stats)
            else:
                # Create new stats
                team_stats = create_team_stats_from_data(stat_data, team, season, season_type)
                if team_stats:
                    session.add(team_stats)
                    ingested_stats.append(team_stats)
        
        session.commit()
        print(f"Successfully ingested team stats for {len(ingested_stats)} teams")
        
        return ingested_stats
        
    except Exception as e:
        session.rollback()
        print(f"Error ingesting team stats: {e}")
        raise
    finally:
        if should_close:
            session.close()


def create_team_stats_from_data(stat_data: Dict[str, Any], team: Team, 
                               season: int, season_type: str) -> Optional[TeamStats]:
    """
    Create a TeamStats object from API data.
    
    Args:
        stat_data: Team statistics data from API
        team: Team object
        season: Season year
        season_type: Season type
        
    Returns:
        TeamStats object or None if invalid data.
    """
    try:
        # Parse numeric values
        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        team_stats = TeamStats(
            team_id=team.id,
            season=season,
            season_type=season_type,
            games_played=safe_int(stat_data.get("GP")),
            wins=safe_int(stat_data.get("W")),
            losses=safe_int(stat_data.get("L")),
            win_percentage=safe_float(stat_data.get("W_PCT")),
            points_per_game=safe_float(stat_data.get("PTS")),
            field_goal_percentage=safe_float(stat_data.get("FG_PCT")),
            three_point_percentage=safe_float(stat_data.get("FG3_PCT")),
            free_throw_percentage=safe_float(stat_data.get("FT_PCT")),
            offensive_rebounds_per_game=safe_float(stat_data.get("OREB")),
            defensive_rebounds_per_game=safe_float(stat_data.get("DREB")),
            assists_per_game=safe_float(stat_data.get("AST")),
            steals_per_game=safe_float(stat_data.get("STL")),
            blocks_per_game=safe_float(stat_data.get("BLK")),
            turnovers_per_game=safe_float(stat_data.get("TOV")),
            personal_fouls_per_game=safe_float(stat_data.get("PF")),
            pace=safe_float(stat_data.get("PACE")),
            offensive_rating=safe_float(stat_data.get("OFFRTG")),
            defensive_rating=safe_float(stat_data.get("DEFRTG")),
            net_rating=safe_float(stat_data.get("NETRTG"))
        )
        
        return team_stats
        
    except Exception as e:
        print(f"Error creating team stats from data: {e}")
        return None


def update_team_stats(team_stats: TeamStats, stat_data: Dict[str, Any]) -> None:
    """
    Update existing team stats with new data.
    
    Args:
        team_stats: Existing TeamStats object
        stat_data: New statistics data from API
    """
    try:
        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        # Update all fields
        team_stats.games_played = safe_int(stat_data.get("GP")) or team_stats.games_played
        team_stats.wins = safe_int(stat_data.get("W")) or team_stats.wins
        team_stats.losses = safe_int(stat_data.get("L")) or team_stats.losses
        team_stats.win_percentage = safe_float(stat_data.get("W_PCT")) or team_stats.win_percentage
        team_stats.points_per_game = safe_float(stat_data.get("PTS")) or team_stats.points_per_game
        team_stats.field_goal_percentage = safe_float(stat_data.get("FG_PCT")) or team_stats.field_goal_percentage
        team_stats.three_point_percentage = safe_float(stat_data.get("FG3_PCT")) or team_stats.three_point_percentage
        team_stats.free_throw_percentage = safe_float(stat_data.get("FT_PCT")) or team_stats.free_throw_percentage
        team_stats.offensive_rebounds_per_game = safe_float(stat_data.get("OREB")) or team_stats.offensive_rebounds_per_game
        team_stats.defensive_rebounds_per_game = safe_float(stat_data.get("DREB")) or team_stats.defensive_rebounds_per_game
        team_stats.assists_per_game = safe_float(stat_data.get("AST")) or team_stats.assists_per_game
        team_stats.steals_per_game = safe_float(stat_data.get("STL")) or team_stats.steals_per_game
        team_stats.blocks_per_game = safe_float(stat_data.get("BLK")) or team_stats.blocks_per_game
        team_stats.turnovers_per_game = safe_float(stat_data.get("TOV")) or team_stats.turnovers_per_game
        team_stats.personal_fouls_per_game = safe_float(stat_data.get("PF")) or team_stats.personal_fouls_per_game
        team_stats.pace = safe_float(stat_data.get("PACE")) or team_stats.pace
        team_stats.offensive_rating = safe_float(stat_data.get("OFFRTG")) or team_stats.offensive_rating
        team_stats.defensive_rating = safe_float(stat_data.get("DEFRTG")) or team_stats.defensive_rating
        team_stats.net_rating = safe_float(stat_data.get("NETRTG")) or team_stats.net_rating
        
    except Exception as e:
        print(f"Error updating team stats: {e}")


def ingest_player_stats(season: int, season_type: str = "Regular Season",
                       team_id: Optional[str] = None, session: Session = None) -> List[PlayerSeasonStats]:
    """
    Ingest player statistics from NBA API.
    
    Args:
        season: NBA season year (e.g., 2023 for 2023-24 season)
        season_type: Season type ('Regular Season', 'Playoffs', etc.)
        team_id: Specific team ID to ingest stats for
        session: Database session. If None, creates a new session.
        
    Returns:
        List of ingested PlayerSeasonStats objects.
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
        # Fetch player stats from API
        stats_data = client.get_player_stats(season, season_type, team_id)
        
        ingested_stats = []
        
        for stat_data in stats_data:
            # Get player reference
            player = session.query(Player).filter(
                Player.player_id == str(stat_data.get("PLAYER_ID", ""))
            ).first()
            
            if not player:
                print(f"Player not found for PLAYER_ID: {stat_data.get('PLAYER_ID')}")
                continue
            
            # Get team reference
            team = None
            if stat_data.get("TEAM_ID"):
                team = session.query(Team).filter(
                    Team.team_id == str(stat_data["TEAM_ID"])
                ).first()
            
            # Check if stats already exist
            existing_stats = session.query(PlayerSeasonStats).filter(
                PlayerSeasonStats.player_id == player.id,
                PlayerSeasonStats.season == season,
                PlayerSeasonStats.season_type == season_type
            ).first()
            
            if existing_stats:
                # Update existing stats
                update_player_stats(existing_stats, stat_data)
                ingested_stats.append(existing_stats)
            else:
                # Create new stats
                player_stats = create_player_stats_from_data(stat_data, player, team, season, season_type)
                if player_stats:
                    session.add(player_stats)
                    ingested_stats.append(player_stats)
        
        session.commit()
        print(f"Successfully ingested player stats for {len(ingested_stats)} players")
        
        return ingested_stats
        
    except Exception as e:
        session.rollback()
        print(f"Error ingesting player stats: {e}")
        raise
    finally:
        if should_close:
            session.close()


def create_player_stats_from_data(stat_data: Dict[str, Any], player: Player, team: Optional[Team],
                                 season: int, season_type: str) -> Optional[PlayerSeasonStats]:
    """
    Create a PlayerSeasonStats object from API data.
    
    Args:
        stat_data: Player statistics data from API
        player: Player object
        team: Team object (optional)
        season: Season year
        season_type: Season type
        
    Returns:
        PlayerSeasonStats object or None if invalid data.
    """
    try:
        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        player_stats = PlayerSeasonStats(
            player_id=player.id,
            team_id=team.id if team else None,
            season=season,
            season_type=season_type,
            games_played=safe_int(stat_data.get("GP")),
            games_started=safe_int(stat_data.get("GS")),
            minutes_per_game=safe_float(stat_data.get("MIN")),
            points_per_game=safe_float(stat_data.get("PTS")),
            rebounds_per_game=safe_float(stat_data.get("REB")),
            assists_per_game=safe_float(stat_data.get("AST")),
            steals_per_game=safe_float(stat_data.get("STL")),
            blocks_per_game=safe_float(stat_data.get("BLK")),
            turnovers_per_game=safe_float(stat_data.get("TOV")),
            personal_fouls_per_game=safe_float(stat_data.get("PF")),
            field_goal_percentage=safe_float(stat_data.get("FG_PCT")),
            three_point_percentage=safe_float(stat_data.get("FG3_PCT")),
            free_throw_percentage=safe_float(stat_data.get("FT_PCT")),
            true_shooting_percentage=safe_float(stat_data.get("TS_PCT")),
            effective_field_goal_percentage=safe_float(stat_data.get("EFG_PCT")),
            offensive_rebound_percentage=safe_float(stat_data.get("OREB_PCT")),
            defensive_rebound_percentage=safe_float(stat_data.get("DREB_PCT")),
            assist_percentage=safe_float(stat_data.get("AST_PCT")),
            turnover_percentage=safe_float(stat_data.get("TOV_PCT")),
            usage_percentage=safe_float(stat_data.get("USG_PCT")),
            player_efficiency_rating=safe_float(stat_data.get("PER"))
        )
        
        return player_stats
        
    except Exception as e:
        print(f"Error creating player stats from data: {e}")
        return None


def update_player_stats(player_stats: PlayerSeasonStats, stat_data: Dict[str, Any]) -> None:
    """
    Update existing player stats with new data.
    
    Args:
        player_stats: Existing PlayerSeasonStats object
        stat_data: New statistics data from API
    """
    try:
        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        # Update all fields
        player_stats.games_played = safe_int(stat_data.get("GP")) or player_stats.games_played
        player_stats.games_started = safe_int(stat_data.get("GS")) or player_stats.games_started
        player_stats.minutes_per_game = safe_float(stat_data.get("MIN")) or player_stats.minutes_per_game
        player_stats.points_per_game = safe_float(stat_data.get("PTS")) or player_stats.points_per_game
        player_stats.rebounds_per_game = safe_float(stat_data.get("REB")) or player_stats.rebounds_per_game
        player_stats.assists_per_game = safe_float(stat_data.get("AST")) or player_stats.assists_per_game
        player_stats.steals_per_game = safe_float(stat_data.get("STL")) or player_stats.steals_per_game
        player_stats.blocks_per_game = safe_float(stat_data.get("BLK")) or player_stats.blocks_per_game
        player_stats.turnovers_per_game = safe_float(stat_data.get("TOV")) or player_stats.turnovers_per_game
        player_stats.personal_fouls_per_game = safe_float(stat_data.get("PF")) or player_stats.personal_fouls_per_game
        player_stats.field_goal_percentage = safe_float(stat_data.get("FG_PCT")) or player_stats.field_goal_percentage
        player_stats.three_point_percentage = safe_float(stat_data.get("FG3_PCT")) or player_stats.three_point_percentage
        player_stats.free_throw_percentage = safe_float(stat_data.get("FT_PCT")) or player_stats.free_throw_percentage
        player_stats.true_shooting_percentage = safe_float(stat_data.get("TS_PCT")) or player_stats.true_shooting_percentage
        player_stats.effective_field_goal_percentage = safe_float(stat_data.get("EFG_PCT")) or player_stats.effective_field_goal_percentage
        player_stats.offensive_rebound_percentage = safe_float(stat_data.get("OREB_PCT")) or player_stats.offensive_rebound_percentage
        player_stats.defensive_rebound_percentage = safe_float(stat_data.get("DREB_PCT")) or player_stats.defensive_rebound_percentage
        player_stats.assist_percentage = safe_float(stat_data.get("AST_PCT")) or player_stats.assist_percentage
        player_stats.turnover_percentage = safe_float(stat_data.get("TOV_PCT")) or player_stats.turnover_percentage
        player_stats.usage_percentage = safe_float(stat_data.get("USG_PCT")) or player_stats.usage_percentage
        player_stats.player_efficiency_rating = safe_float(stat_data.get("PER")) or player_stats.player_efficiency_rating
        
    except Exception as e:
        print(f"Error updating player stats: {e}")

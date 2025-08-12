"""
NBA API Client - Fixed Version with NumPy Compatibility

This module provides a client for fetching NBA data using the nba_api library,
with NumPy compatibility issues resolved.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import pandas as pd

# nba_api imports
try:
    from nba_api.stats.endpoints import (
        commonteamroster,
        leaguedashteamstats,
        leaguedashplayerstats,
        boxscoretraditionalv2,
        leaguestandingsv3,
        playercareerstats,
        teamdashboardbyyearoveryear,
        playerdashboardbyyearoveryear,
        scoreboard
    )
    from nba_api.stats.static import players, teams
    from nba_api.live.nba.endpoints import scoreboard as live_scoreboard
    NBA_API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some NBA API endpoints not available: {e}")
    NBA_API_AVAILABLE = False
    # Fallback imports
    try:
        from nba_api.stats.static import players, teams
    except ImportError:
        players = None
        teams = None


@dataclass
class NBAAPIClientFixed:
    """Client for fetching NBA data using the nba_api library with NumPy compatibility."""
    
    rate_limit_sleep_seconds: float = 1.0
    timeout_seconds: int = 30
    max_retries: int = 3
    
    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        time.sleep(self.rate_limit_sleep_seconds)
    
    def _safe_api_call(self, api_call, *args, **kwargs) -> Any:
        """Safely make an API call with retry logic."""
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                result = api_call(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.rate_limit_sleep_seconds * (attempt + 1))
    
    def get_teams(self, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all NBA teams using static data."""
        try:
            if teams is None:
                print("Warning: Teams static data not available")
                return []
                
            teams_data = teams.get_teams()
            
            teams_list = []
            for team in teams_data:
                team_dict = {
                    "team_id": str(team['id']),
                    "name": team['full_name'],
                    "abbreviation": team['abbreviation'],
                    "city": team['city'],
                    "state": team['state'],
                    "conference": team.get('conference', ''),
                    "division": team.get('division', '')
                }
                teams_list.append(team_dict)
            
            return teams_list
            
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def get_players(self, season: Optional[int] = None, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NBA players using static data."""
        try:
            if players is None:
                print("Warning: Players static data not available")
                return []
                
            players_data = players.get_players()
            
            if season:
                players_data = [p for p in players_data if p.get('is_active', False)]
            
            players_list = []
            for player in players_data:
                player_dict = {
                    "player_id": str(player['id']),
                    "name": player['full_name'],
                    "first_name": player['first_name'],
                    "last_name": player['last_name'],
                    "position": player.get('position', ''),
                    "height": player.get('height', ''),
                    "weight": player.get('weight', 0),
                    "is_active": player.get('is_active', False),
                    "team_id": str(player.get('team_id', '')) if player.get('team_id') else None
                }
                players_list.append(player_dict)
            
            return players_list
            
        except Exception as e:
            print(f"Error fetching players: {e}")
            return []
    
    def get_games(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get NBA games for a specific season."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            # Use scoreboard endpoint for current games
            scoreboard_data = self._safe_api_call(
                scoreboard.ScoreBoard,
                game_date=None,
                league_id="00",
                day_offset=0
            )
            
            games = []
            if hasattr(scoreboard_data, 'get_data_frames'):
                df = scoreboard_data.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    game_dict = {
                        "game_id": str(row['GAME_ID']),
                        "game_date": row['GAME_DATE_EST'],
                        "season": season,
                        "season_type": season_type,
                        "home_team_abbr": row['HOME_TEAM_ABBREVIATION'],
                        "away_team_abbr": row['VISITOR_TEAM_ABBREVIATION'],
                        "home_score": int(row['HOME_TEAM_SCORE']) if pd.notna(row['HOME_TEAM_SCORE']) else 0,
                        "away_score": int(row['VISITOR_TEAM_SCORE']) if pd.notna(row['VISITOR_TEAM_SCORE']) else 0,
                        "home_win": False,  # Will be calculated
                        "arena": row['ARENA'] if pd.notna(row['ARENA']) else "",
                        "attendance": int(row['ATTENDANCE']) if pd.notna(row['ATTENDANCE']) else 0
                    }
                    
                    # Calculate home win
                    if pd.notna(row['HOME_TEAM_SCORE']) and pd.notna(row['VISITOR_TEAM_SCORE']):
                        game_dict["home_win"] = game_dict["home_score"] > game_dict["away_score"]
                    
                    games.append(game_dict)
            
            return games
            
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    def get_team_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get team statistics for a specific season."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            stats_data = self._safe_api_call(
                leaguedashteamstats.LeagueDashTeamStats,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            stats = []
            if hasattr(stats_data, 'get_data_frames'):
                df = stats_data.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    stat_dict = {
                        "team_id": str(row['TEAM_ID']),
                        "team_name": row['TEAM_NAME'],
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(row['GP']) if pd.notna(row['GP']) else 0,
                        "wins": int(row['W']) if pd.notna(row['W']) else 0,
                        "losses": int(row['L']) if pd.notna(row['L']) else 0,
                        "win_percentage": float(row['W_PCT']) if pd.notna(row['W_PCT']) else 0.0,
                        "points_per_game": float(row['PTS']) if pd.notna(row['PTS']) else 0.0,
                        "rebounds_per_game": float(row['REB']) if pd.notna(row['REB']) else 0.0,
                        "assists_per_game": float(row['AST']) if pd.notna(row['AST']) else 0.0,
                        "steals_per_game": float(row['STL']) if pd.notna(row['STL']) else 0.0,
                        "blocks_per_game": float(row['BLK']) if pd.notna(row['BLK']) else 0.0,
                        "turnovers_per_game": float(row['TOV']) if pd.notna(row['TOV']) else 0.0,
                        "field_goal_percentage": float(row['FG_PCT']) if pd.notna(row['FG_PCT']) else 0.0,
                        "three_point_percentage": float(row['FG3_PCT']) if pd.notna(row['FG3_PCT']) else 0.0,
                        "free_throw_percentage": float(row['FT_PCT']) if pd.notna(row['FT_PCT']) else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return []
    
    def get_player_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get player statistics for a specific season."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            stats_data = self._safe_api_call(
                leaguedashplayerstats.LeagueDashPlayerStats,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            stats = []
            if hasattr(stats_data, 'get_data_frames'):
                df = stats_data.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    stat_dict = {
                        "player_id": str(row['PLAYER_ID']),
                        "player_name": row['PLAYER_NAME'],
                        "team_id": str(row['TEAM_ID']) if pd.notna(row['TEAM_ID']) else None,
                        "team_name": row['TEAM_NAME'] if pd.notna(row['TEAM_NAME']) else "",
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(row['GP']) if pd.notna(row['GP']) else 0,
                        "games_started": int(row['GS']) if pd.notna(row['GS']) else 0,
                        "minutes_per_game": float(row['MIN']) if pd.notna(row['MIN']) else 0.0,
                        "points_per_game": float(row['PTS']) if pd.notna(row['PTS']) else 0.0,
                        "rebounds_per_game": float(row['REB']) if pd.notna(row['REB']) else 0.0,
                        "assists_per_game": float(row['AST']) if pd.notna(row['AST']) else 0.0,
                        "steals_per_game": float(row['STL']) if pd.notna(row['STL']) else 0.0,
                        "blocks_per_game": float(row['BLK']) if pd.notna(row['BLK']) else 0.0,
                        "turnovers_per_game": float(row['TOV']) if pd.notna(row['TOV']) else 0.0,
                        "field_goal_percentage": float(row['FG_PCT']) if pd.notna(row['FG_PCT']) else 0.0,
                        "three_point_percentage": float(row['FG3_PCT']) if pd.notna(row['FG3_PCT']) else 0.0,
                        "free_throw_percentage": float(row['FT_PCT']) if pd.notna(row['FT_PCT']) else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return []
    
    def get_standings(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get NBA standings for a specific season."""
        try:
            standings_data = self._safe_api_call(
                leaguestandingsv3.LeagueStandingsV3,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type=season_type
            )
            
            standings = []
            if hasattr(standings_data, 'get_data_frames'):
                df = standings_data.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    standing_dict = {
                        "team_id": str(row['TeamID']),
                        "team_name": row['TeamName'],
                        "season": season,
                        "season_type": season_type,
                        "conference": row['Conference'],
                        "division": row['Division'],
                        "wins": int(row['WINS']) if pd.notna(row['WINS']) else 0,
                        "losses": int(row['LOSSES']) if pd.notna(row['LOSSES']) else 0,
                        "win_percentage": float(row['WinPCT']) if pd.notna(row['WinPCT']) else 0.0,
                        "games_back": float(row['GB']) if pd.notna(row['GB']) else 0.0,
                        "conference_rank": int(row['ConferenceRank']) if pd.notna(row['ConferenceRank']) else 0,
                        "division_rank": int(row['DivisionRank']) if pd.notna(row['DivisionRank']) else 0
                    }
                    standings.append(standing_dict)
            
            return standings
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []
    
    def get_player_career_stats(self, player_id: str) -> Dict[str, Any]:
        """Get career statistics for a specific player."""
        try:
            career_data = self._safe_api_call(
                playercareerstats.PlayerCareerStats,
                player_id=player_id
            )
            
            if hasattr(career_data, 'get_data_frames'):
                df = career_data.get_data_frames()[0]
                
                career_stats = []
                for _, row in df.iterrows():
                    season_stats = {
                        "season": row['SEASON_ID'],
                        "team_id": str(row['TEAM_ID']) if pd.notna(row['TEAM_ID']) else None,
                        "team_name": row['TEAM_NAME'] if pd.notna(row['TEAM_NAME']) else None,
                        "games_played": int(row['GP']) if pd.notna(row['GP']) else 0,
                        "games_started": int(row['GS']) if pd.notna(row['GS']) else 0,
                        "minutes_per_game": float(row['MIN']) if pd.notna(row['MIN']) else 0.0,
                        "points_per_game": float(row['PTS']) if pd.notna(row['PTS']) else 0.0,
                        "rebounds_per_game": float(row['REB']) if pd.notna(row['REB']) else 0.0,
                        "assists_per_game": float(row['AST']) if pd.notna(row['AST']) else 0.0,
                        "steals_per_game": float(row['STL']) if pd.notna(row['STL']) else 0.0,
                        "blocks_per_game": float(row['BLK']) if pd.notna(row['BLK']) else 0.0,
                        "turnovers_per_game": float(row['TOV']) if pd.notna(row['TOV']) else 0.0,
                        "field_goal_percentage": float(row['FG_PCT']) if pd.notna(row['FG_PCT']) else 0.0,
                        "three_point_percentage": float(row['FG3_PCT']) if pd.notna(row['FG3_PCT']) else 0.0,
                        "free_throw_percentage": float(row['FT_PCT']) if pd.notna(row['FT_PCT']) else 0.0
                    }
                    career_stats.append(season_stats)
                
                return {
                    "player_id": player_id,
                    "career_stats": career_stats
                }
            
            return {"player_id": player_id, "career_stats": []}
            
        except Exception as e:
            print(f"Error fetching player career stats: {e}")
            return {"player_id": player_id, "career_stats": []}
    
    def get_live_games(self) -> List[Dict[str, Any]]:
        """Get currently live NBA games."""
        try:
            live_data = self._safe_api_call(live_scoreboard.ScoreBoard)
            
            games = []
            if hasattr(live_data, 'get_dict'):
                data = live_data.get_dict()
                
                if 'games' in data:
                    for game in data['games']:
                        game_dict = {
                            "game_id": str(game.get('gameId', '')),
                            "game_status": game.get('gameStatusText', ''),
                            "home_team": game.get('homeTeam', {}).get('teamName', ''),
                            "away_team": game.get('awayTeam', {}).get('teamName', ''),
                            "home_score": game.get('homeTeam', {}).get('score', 0),
                            "away_score": game.get('awayTeam', {}).get('score', 0),
                            "quarter": game.get('period', 0),
                            "time_remaining": game.get('gameStatusText', '')
                        }
                        games.append(game_dict)
            
            return games
            
        except Exception as e:
            print(f"Error fetching live games: {e}")
            return []

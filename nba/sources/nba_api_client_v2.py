"""
NBA API Client v2 - NumPy Compatible Version

This module provides a client for fetching NBA data using the nba_api library,
with workarounds for NumPy compatibility issues.
"""

from __future__ import annotations

import time
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

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
class NBAAPIClientV2:
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
    
    def _safe_get_dict(self, api_result) -> Dict[str, Any]:
        """Safely get dictionary from API result, avoiding pandas issues."""
        try:
            if hasattr(api_result, 'get_dict'):
                return api_result.get_dict()
            elif hasattr(api_result, 'get_data_frames'):
                # Try to get raw data without pandas
                return {"data": "available but pandas required"}
            else:
                return {"error": "No data available"}
        except Exception as e:
            return {"error": f"Failed to get data: {e}"}
    
    def _safe_get_json(self, api_result) -> str:
        """Safely get JSON from API result."""
        try:
            if hasattr(api_result, 'get_json'):
                return api_result.get_json()
            else:
                return json.dumps({"error": "No JSON available"})
        except Exception as e:
            return json.dumps({"error": f"Failed to get JSON: {e}"})
    
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
            # Use scoreboard endpoint
            scoreboard_data = self._safe_api_call(
                scoreboard.ScoreBoard,
                game_date=None,
                league_id="00",
                day_offset=0
            )
            
            # Get raw data without pandas
            data = self._safe_get_dict(scoreboard_data)
            
            if "error" in data:
                print(f"Error getting games data: {data['error']}")
                return []
            
            games = []
            if 'GameHeader' in data:
                for game in data['GameHeader']:
                    game_dict = {
                        "game_id": str(game.get('GAME_ID', '')),
                        "game_date": game.get('GAME_DATE_EST', ''),
                        "season": season,
                        "season_type": season_type,
                        "home_team_abbr": game.get('HOME_TEAM_ABBREVIATION', ''),
                        "away_team_abbr": game.get('VISITOR_TEAM_ABBREVIATION', ''),
                        "home_score": game.get('HOME_TEAM_SCORE', 0),
                        "away_score": game.get('VISITOR_TEAM_SCORE', 0),
                        "home_win": game.get('HOME_TEAM_SCORE', 0) > game.get('VISITOR_TEAM_SCORE', 0),
                        "arena": game.get('ARENA', ''),
                        "attendance": game.get('ATTENDANCE', 0)
                    }
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
            
            # Get raw data without pandas
            data = self._safe_get_dict(stats_data)
            
            if "error" in data:
                print(f"Error getting team stats data: {data['error']}")
                return []
            
            stats = []
            if 'LeagueDashTeamStats' in data:
                for team_stat in data['LeagueDashTeamStats']:
                    stat_dict = {
                        "team_id": str(team_stat.get('TEAM_ID', '')),
                        "team_name": team_stat.get('TEAM_NAME', ''),
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(team_stat.get('GP', 0)),
                        "wins": int(team_stat.get('W', 0)),
                        "losses": int(team_stat.get('L', 0)),
                        "win_percentage": float(team_stat.get('W_PCT', 0.0)),
                        "points_per_game": float(team_stat.get('PTS', 0.0)),
                        "rebounds_per_game": float(team_stat.get('REB', 0.0)),
                        "assists_per_game": float(team_stat.get('AST', 0.0)),
                        "steals_per_game": float(team_stat.get('STL', 0.0)),
                        "blocks_per_game": float(team_stat.get('BLK', 0.0)),
                        "turnovers_per_game": float(team_stat.get('TOV', 0.0)),
                        "field_goal_percentage": float(team_stat.get('FG_PCT', 0.0)),
                        "three_point_percentage": float(team_stat.get('FG3_PCT', 0.0)),
                        "free_throw_percentage": float(team_stat.get('FT_PCT', 0.0))
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
            
            # Get raw data without pandas
            data = self._safe_get_dict(stats_data)
            
            if "error" in data:
                print(f"Error getting player stats data: {data['error']}")
                return []
            
            stats = []
            if 'LeagueDashPlayerStats' in data:
                for player_stat in data['LeagueDashPlayerStats']:
                    stat_dict = {
                        "player_id": str(player_stat.get('PLAYER_ID', '')),
                        "player_name": player_stat.get('PLAYER_NAME', ''),
                        "team_id": str(player_stat.get('TEAM_ID', '')) if player_stat.get('TEAM_ID') else None,
                        "team_name": player_stat.get('TEAM_NAME', ''),
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(player_stat.get('GP', 0)),
                        "games_started": int(player_stat.get('GS', 0)),
                        "minutes_per_game": float(player_stat.get('MIN', 0.0)),
                        "points_per_game": float(player_stat.get('PTS', 0.0)),
                        "rebounds_per_game": float(player_stat.get('REB', 0.0)),
                        "assists_per_game": float(player_stat.get('AST', 0.0)),
                        "steals_per_game": float(player_stat.get('STL', 0.0)),
                        "blocks_per_game": float(player_stat.get('BLK', 0.0)),
                        "turnovers_per_game": float(player_stat.get('TOV', 0.0)),
                        "field_goal_percentage": float(player_stat.get('FG_PCT', 0.0)),
                        "three_point_percentage": float(player_stat.get('FG3_PCT', 0.0)),
                        "free_throw_percentage": float(player_stat.get('FT_PCT', 0.0))
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
            
            # Get raw data without pandas
            data = self._safe_get_dict(standings_data)
            
            if "error" in data:
                print(f"Error getting standings data: {data['error']}")
                return []
            
            standings = []
            if 'Standings' in data:
                for standing in data['Standings']:
                    standing_dict = {
                        "team_id": str(standing.get('TeamID', '')),
                        "team_name": standing.get('TeamName', ''),
                        "season": season,
                        "season_type": season_type,
                        "conference": standing.get('Conference', ''),
                        "division": standing.get('Division', ''),
                        "wins": int(standing.get('WINS', 0)),
                        "losses": int(standing.get('LOSSES', 0)),
                        "win_percentage": float(standing.get('WinPCT', 0.0)),
                        "games_back": float(standing.get('GB', 0.0)),
                        "conference_rank": int(standing.get('ConferenceRank', 0)),
                        "division_rank": int(standing.get('DivisionRank', 0))
                    }
                    standings.append(standing_dict)
            
            return standings
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []
    
    def get_live_games(self) -> List[Dict[str, Any]]:
        """Get currently live NBA games."""
        try:
            live_data = self._safe_api_call(live_scoreboard.ScoreBoard)
            
            data = self._safe_get_dict(live_data)
            
            if "error" in data:
                print(f"Error getting live games data: {data['error']}")
                return []
            
            games = []
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

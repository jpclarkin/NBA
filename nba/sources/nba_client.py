"""
NBA API Client

This module provides a client for fetching NBA data from various sources.
Currently supports NBA.com API and can be extended for other sources.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime, date
import requests

from nba.config import get_settings


NBA_BASE_URL = "https://stats.nba.com/stats"
NBA_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nba.com/",
}


class NBAAPIError(Exception):
    """Exception raised for NBA API errors."""
    pass


@dataclass
class NBAAPIClient:
    """Client for fetching NBA data from various sources."""
    
    api_key: Optional[str] = None
    rate_limit_sleep_seconds: float = 1.0
    timeout_seconds: int = 30
    max_retries: int = 5

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = get_settings().nba_api_key

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a GET request to the NBA API with retry logic."""
        url = f"{NBA_BASE_URL}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                resp = requests.get(
                    url, 
                    headers=NBA_API_HEADERS, 
                    params=params, 
                    timeout=self.timeout_seconds
                )
                
                if resp.status_code == 200:
                    return resp.json()
                    
                if resp.status_code in (429, 500, 502, 503, 504):
                    sleep_seconds = self.rate_limit_sleep_seconds * (attempt + 1)
                    time.sleep(sleep_seconds)
                    continue
                    
                raise NBAAPIError(f"NBA API GET {url} failed: {resp.status_code} {resp.text}")
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    sleep_seconds = self.rate_limit_sleep_seconds * (attempt + 1) * 2
                    time.sleep(sleep_seconds)
                    continue
                raise NBAAPIError(f"NBA API GET {url} timed out after {self.max_retries} retries")
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    sleep_seconds = self.rate_limit_sleep_seconds * (attempt + 1)
                    time.sleep(sleep_seconds)
                    continue
                raise NBAAPIError(f"NBA API GET {url} failed after {self.max_retries} retries: {e}")
                
        raise NBAAPIError(f"NBA API GET {url} failed after {self.max_retries} retries")

    def get_teams(self, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all NBA teams."""
        params = {
            "LeagueID": "00",  # NBA
            "Season": f"{season}-{str(season + 1)[-2:]}" if season else "2023-24",
            "IsOnlyCurrentSeason": "1"
        }
        
        response = self._get("commonteamroster", params)
        
        # Extract team information from response
        teams = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            team_data = response["resultSets"][0]["rowSet"]
            
            # Group by team
            team_dict = {}
            for row in team_data:
                team_id = row[0]
                if team_id not in team_dict:
                    team_dict[team_id] = {
                        "team_id": str(team_id),
                        "name": row[1],
                        "abbreviation": row[2],
                        "city": row[3],
                        "state": row[4],
                        "conference": row[5],
                        "division": row[6]
                    }
            
            teams = list(team_dict.values())
            
        return teams

    def get_games(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get games for a specific season and season type."""
        params = {
            "LeagueID": "00",
            "Season": f"{season}-{str(season + 1)[-2:]}",
            "SeasonType": season_type,
            "IsOnlyCurrentSeason": "0"
        }
        
        response = self._get("scoreboard", params)
        
        games = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            game_data = response["resultSets"][0]["rowSet"]
            
            for row in game_data:
                game = {
                    "game_id": row[2],
                    "game_date": row[0],
                    "season": season,
                    "season_type": season_type,
                    "home_team_abbr": row[6],
                    "away_team_abbr": row[3],
                    "home_score": row[8],
                    "away_score": row[5],
                    "arena": row[9],
                    "attendance": row[10],
                    "duration_minutes": row[11]
                }
                games.append(game)
                
        return games

    def get_team_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get team statistics for a season."""
        params = {
            "LeagueID": "00",
            "Season": f"{season}-{str(season + 1)[-2:]}",
            "SeasonType": season_type,
            "PerMode": "PerGame",
            "MeasureType": "Base"
        }
        
        response = self._get("leaguedashteamstats", params)
        
        team_stats = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            stats_data = response["resultSets"][0]["rowSet"]
            headers = response["resultSets"][0]["headers"]
            
            for row in stats_data:
                stats = dict(zip(headers, row))
                team_stats.append(stats)
                
        return team_stats

    def get_player_stats(self, season: int, season_type: str = "Regular Season", 
                        team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get player statistics for a season."""
        params = {
            "LeagueID": "00",
            "Season": f"{season}-{str(season + 1)[-2:]}",
            "SeasonType": season_type,
            "PerMode": "PerGame",
            "MeasureType": "Base"
        }
        
        if team_id:
            params["TeamID"] = team_id
            
        response = self._get("leaguedashplayerstats", params)
        
        player_stats = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            stats_data = response["resultSets"][0]["rowSet"]
            headers = response["resultSets"][0]["headers"]
            
            for row in stats_data:
                stats = dict(zip(headers, row))
                player_stats.append(stats)
                
        return player_stats

    def get_game_stats(self, game_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific game."""
        params = {
            "GameID": game_id,
            "StartPeriod": "0",
            "EndPeriod": "0",
            "StartRange": "0",
            "EndRange": "0",
            "RangeType": "0"
        }
        
        response = self._get("boxscoretraditionalv2", params)
        
        game_stats = {
            "game_id": game_id,
            "home_stats": {},
            "away_stats": {},
            "player_stats": []
        }
        
        if "resultSets" in response:
            for result_set in response["resultSets"]:
                name = result_set["name"]
                data = result_set["rowSet"]
                headers = result_set["headers"]
                
                if name == "PlayerStats":
                    for row in data:
                        player_stat = dict(zip(headers, row))
                        game_stats["player_stats"].append(player_stat)
                elif name == "TeamStats":
                    if data:
                        if len(data) >= 2:
                            game_stats["home_stats"] = dict(zip(headers, data[0]))
                            game_stats["away_stats"] = dict(zip(headers, data[1]))
                            
        return game_stats

    def get_players(self, season: Optional[int] = None, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get player information."""
        params = {
            "LeagueID": "00",
            "Season": f"{season}-{str(season + 1)[-2:]}" if season else "2023-24",
            "IsOnlyCurrentSeason": "1"
        }
        
        if team_id:
            params["TeamID"] = team_id
            
        response = self._get("commonteamroster", params)
        
        players = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            player_data = response["resultSets"][0]["rowSet"]
            headers = response["resultSets"][0]["headers"]
            
            for row in player_data:
                player = dict(zip(headers, row))
                players.append(player)
                
        return players

    def get_betting_lines(self, game_id: str) -> List[Dict[str, Any]]:
        """Get betting lines for a game (placeholder - would need betting API integration)."""
        # This is a placeholder - actual implementation would require
        # integration with a betting data provider API
        return []

    def get_standings(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get current standings."""
        params = {
            "LeagueID": "00",
            "Season": f"{season}-{str(season + 1)[-2:]}",
            "SeasonType": season_type,
            "StandingsType": "Conference"
        }
        
        response = self._get("leaguestandingsv3", params)
        
        standings = []
        if "resultSets" in response and len(response["resultSets"]) > 0:
            standings_data = response["resultSets"][0]["rowSet"]
            headers = response["resultSets"][0]["headers"]
            
            for row in standings_data:
                standing = dict(zip(headers, row))
                standings.append(standing)
                
        return standings

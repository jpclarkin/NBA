"""
NBA API Client v3 - Direct HTTP Requests

This module provides a client for fetching NBA data using direct HTTP requests,
completely bypassing the nba_api library to avoid NumPy compatibility issues.
"""

from __future__ import annotations

import time
import json
import requests
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date


@dataclass
class NBAAPIClientV3:
    """Client for fetching NBA data using direct HTTP requests."""
    
    rate_limit_sleep_seconds: float = 1.0
    timeout_seconds: int = 30
    max_retries: int = 3
    base_url: str = "https://stats.nba.com/stats"
    
    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        time.sleep(self.rate_limit_sleep_seconds)
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a direct HTTP request to the NBA API."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout_seconds)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.rate_limit_sleep_seconds * (attempt + 1))
        
        return {"error": "All retry attempts failed"}
    
    def get_teams(self, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all NBA teams using direct API call."""
        try:
            # Use the commonteamroster endpoint to get team list
            params = {
                'LeagueID': '00',
                'Season': '2023-24' if season else '2023-24'
            }
            
            data = self._make_request('commonteamroster', params)
            
            if 'error' in data:
                print(f"Error fetching teams: {data['error']}")
                return []
            
            teams = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                team_data = data['resultSets'][0]['rowSet']
                
                # Create a set to avoid duplicates
                seen_teams = set()
                
                for team_row in team_data:
                    team_id = str(team_row[0])
                    if team_id not in seen_teams:
                        team_dict = {
                            "team_id": team_id,
                            "name": team_row[1],  # Team name
                            "abbreviation": team_row[2],  # Team abbreviation
                            "city": team_row[1].split()[-1] if team_row[1] else "",  # Extract city
                            "state": "",  # Not available in this endpoint
                            "conference": "",  # Not available in this endpoint
                            "division": ""  # Not available in this endpoint
                        }
                        teams.append(team_dict)
                        seen_teams.add(team_id)
            
            return teams
            
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def get_players(self, season: Optional[int] = None, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NBA players using direct API call."""
        try:
            # Use the commonteamroster endpoint
            params = {
                'LeagueID': '00',
                'Season': '2023-24' if season else '2023-24'
            }
            
            if team_id:
                params['TeamID'] = team_id
            
            data = self._make_request('commonteamroster', params)
            
            if 'error' in data:
                print(f"Error fetching players: {data['error']}")
                return []
            
            players = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                player_data = data['resultSets'][0]['rowSet']
                
                for player_row in player_data:
                    player_dict = {
                        "player_id": str(player_row[12]),  # PLAYER_ID
                        "name": player_row[3],  # PLAYER
                        "first_name": player_row[3].split()[0] if player_row[3] else "",
                        "last_name": " ".join(player_row[3].split()[1:]) if player_row[3] and len(player_row[3].split()) > 1 else "",
                        "position": player_row[5],  # POSITION
                        "height": player_row[10],  # HEIGHT
                        "weight": int(player_row[11]) if player_row[11] else 0,  # WEIGHT
                        "is_active": True,  # Assume active if in roster
                        "team_id": str(player_row[0])  # TEAM_ID
                    }
                    players.append(player_dict)
            
            return players
            
        except Exception as e:
            print(f"Error fetching players: {e}")
            return []
    
    def get_team_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get team statistics for a specific season."""
        try:
            params = {
                'LeagueID': '00',
                'Season': f"{season}-{str(season + 1)[-2:]}",
                'SeasonType': season_type,
                'PerMode': 'PerGame',
                'MeasureType': 'Base',
                'PlusMinus': 'N',
                'PaceAdjust': 'N',
                'Rank': 'N',
                'Outcome': '',
                'Location': '',
                'Month': '0',
                'SeasonSegment': '',
                'DateFrom': '',
                'DateTo': '',
                'OpponentTeamID': '0',
                'VsConference': '',
                'VsDivision': '',
                'TeamID': '0',
                'Conference': '',
                'Division': '',
                'GameSegment': '',
                'Period': '0',
                'ShotClockRange': '',
                'LastNGames': '0'
            }
            
            data = self._make_request('leaguedashteamstats', params)
            
            if 'error' in data:
                print(f"Error fetching team stats: {data['error']}")
                return []
            
            stats = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                result_set = data['resultSets'][0]
                headers = result_set['headers']
                rows = result_set['rowSet']
                
                for row in rows:
                    stat_dict = {
                        "team_id": str(row[headers.index('TEAM_ID')]),
                        "team_name": row[headers.index('TEAM_NAME')],
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(row[headers.index('GP')]) if 'GP' in headers else 0,
                        "wins": int(row[headers.index('W')]) if 'W' in headers else 0,
                        "losses": int(row[headers.index('L')]) if 'L' in headers else 0,
                        "win_percentage": float(row[headers.index('W_PCT')]) if 'W_PCT' in headers else 0.0,
                        "points_per_game": float(row[headers.index('PTS')]) if 'PTS' in headers else 0.0,
                        "rebounds_per_game": float(row[headers.index('REB')]) if 'REB' in headers else 0.0,
                        "assists_per_game": float(row[headers.index('AST')]) if 'AST' in headers else 0.0,
                        "steals_per_game": float(row[headers.index('STL')]) if 'STL' in headers else 0.0,
                        "blocks_per_game": float(row[headers.index('BLK')]) if 'BLK' in headers else 0.0,
                        "turnovers_per_game": float(row[headers.index('TOV')]) if 'TOV' in headers else 0.0,
                        "field_goal_percentage": float(row[headers.index('FG_PCT')]) if 'FG_PCT' in headers else 0.0,
                        "three_point_percentage": float(row[headers.index('FG3_PCT')]) if 'FG3_PCT' in headers else 0.0,
                        "free_throw_percentage": float(row[headers.index('FT_PCT')]) if 'FT_PCT' in headers else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return []
    
    def get_player_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get player statistics for a specific season."""
        try:
            params = {
                'LeagueID': '00',
                'Season': f"{season}-{str(season + 1)[-2:]}",
                'SeasonType': season_type,
                'PerMode': 'PerGame',
                'MeasureType': 'Base',
                'PlusMinus': 'N',
                'PaceAdjust': 'N',
                'Rank': 'N',
                'Outcome': '',
                'Location': '',
                'Month': '0',
                'SeasonSegment': '',
                'DateFrom': '',
                'DateTo': '',
                'OpponentTeamID': '0',
                'VsConference': '',
                'VsDivision': '',
                'TeamID': '0',
                'Conference': '',
                'Division': '',
                'GameSegment': '',
                'Period': '0',
                'ShotClockRange': '',
                'LastNGames': '0',
                'GameScope': '',
                'PlayerExperience': '',
                'PlayerPosition': '',
                'StarterBench': '',
                'ActiveFlag': ''
            }
            
            data = self._make_request('leaguedashplayerstats', params)
            
            if 'error' in data:
                print(f"Error fetching player stats: {data['error']}")
                return []
            
            stats = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                result_set = data['resultSets'][0]
                headers = result_set['headers']
                rows = result_set['rowSet']
                
                for row in rows:
                    stat_dict = {
                        "player_id": str(row[headers.index('PLAYER_ID')]),
                        "player_name": row[headers.index('PLAYER_NAME')],
                        "team_id": str(row[headers.index('TEAM_ID')]) if 'TEAM_ID' in headers else None,
                        "team_name": row[headers.index('TEAM_NAME')] if 'TEAM_NAME' in headers else "",
                        "season": season,
                        "season_type": season_type,
                        "games_played": int(row[headers.index('GP')]) if 'GP' in headers else 0,
                        "games_started": int(row[headers.index('GS')]) if 'GS' in headers else 0,
                        "minutes_per_game": float(row[headers.index('MIN')]) if 'MIN' in headers else 0.0,
                        "points_per_game": float(row[headers.index('PTS')]) if 'PTS' in headers else 0.0,
                        "rebounds_per_game": float(row[headers.index('REB')]) if 'REB' in headers else 0.0,
                        "assists_per_game": float(row[headers.index('AST')]) if 'AST' in headers else 0.0,
                        "steals_per_game": float(row[headers.index('STL')]) if 'STL' in headers else 0.0,
                        "blocks_per_game": float(row[headers.index('BLK')]) if 'BLK' in headers else 0.0,
                        "turnovers_per_game": float(row[headers.index('TOV')]) if 'TOV' in headers else 0.0,
                        "field_goal_percentage": float(row[headers.index('FG_PCT')]) if 'FG_PCT' in headers else 0.0,
                        "three_point_percentage": float(row[headers.index('FG3_PCT')]) if 'FG3_PCT' in headers else 0.0,
                        "free_throw_percentage": float(row[headers.index('FT_PCT')]) if 'FT_PCT' in headers else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return []
    
    def get_standings(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get NBA standings for a specific season."""
        try:
            params = {
                'LeagueID': '00',
                'Season': f"{season}-{str(season + 1)[-2:]}",
                'SeasonType': season_type
            }
            
            data = self._make_request('leaguestandingsv3', params)
            
            if 'error' in data:
                print(f"Error fetching standings: {data['error']}")
                return []
            
            standings = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                result_set = data['resultSets'][0]
                headers = result_set['headers']
                rows = result_set['rowSet']
                
                for row in rows:
                    standing_dict = {
                        "team_id": str(row[headers.index('TeamID')]),
                        "team_name": row[headers.index('TeamName')],
                        "season": season,
                        "season_type": season_type,
                        "conference": row[headers.index('Conference')],
                        "division": row[headers.index('Division')],
                        "wins": int(row[headers.index('WINS')]),
                        "losses": int(row[headers.index('LOSSES')]),
                        "win_percentage": float(row[headers.index('WinPCT')]),
                        "games_back": float(row[headers.index('GB')]),
                        "conference_rank": int(row[headers.index('ConferenceRank')]),
                        "division_rank": int(row[headers.index('DivisionRank')])
                    }
                    standings.append(standing_dict)
            
            return standings
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []
    
    def get_games(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get NBA games for a specific season."""
        try:
            # Note: This endpoint might not work as expected for historical games
            # The scoreboard endpoint is primarily for current/live games
            params = {
                'GameDate': datetime.now().strftime('%m/%d/%Y'),
                'LeagueID': '00',
                'DayOffset': '0'
            }
            
            data = self._make_request('scoreboard', params)
            
            if 'error' in data:
                print(f"Error fetching games: {data['error']}")
                return []
            
            games = []
            if 'resultSets' in data and len(data['resultSets']) > 0:
                result_set = data['resultSets'][0]
                headers = result_set['headers']
                rows = result_set['rowSet']
                
                for row in rows:
                    game_dict = {
                        "game_id": str(row[headers.index('GAME_ID')]),
                        "game_date": row[headers.index('GAME_DATE_EST')],
                        "season": season,
                        "season_type": season_type,
                        "home_team_abbr": row[headers.index('HOME_TEAM_ABBREVIATION')],
                        "away_team_abbr": row[headers.index('VISITOR_TEAM_ABBREVIATION')],
                        "home_score": int(row[headers.index('HOME_TEAM_SCORE')]) if 'HOME_TEAM_SCORE' in headers else 0,
                        "away_score": int(row[headers.index('VISITOR_TEAM_SCORE')]) if 'VISITOR_TEAM_SCORE' in headers else 0,
                        "home_win": False,  # Will be calculated
                        "arena": row[headers.index('ARENA')] if 'ARENA' in headers else "",
                        "attendance": int(row[headers.index('ATTENDANCE')]) if 'ATTENDANCE' in headers else 0
                    }
                    
                    # Calculate home win
                    if 'HOME_TEAM_SCORE' in headers and 'VISITOR_TEAM_SCORE' in headers:
                        game_dict["home_win"] = game_dict["home_score"] > game_dict["away_score"]
                    
                    games.append(game_dict)
            
            return games
            
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []

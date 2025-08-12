"""
NBA API Client - Enhanced Version with Full Endpoint Coverage

This module provides a comprehensive client for fetching NBA data using the nba_api library,
with support for all major endpoints and advanced analytics.
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
        # Basic endpoints
        commonteamroster,
        leaguedashteamstats,
        leaguedashplayerstats,
        boxscoretraditionalv2,
        leaguestandingsv3,
        playercareerstats,
        scoreboard,
        
        # Advanced analytics
        leaguedashptstats,
        leaguedashoppptstats,
        leaguedashptdefend,
        leaguedashclutch,
        
        # Game details
        boxscoreadvancedv2,
        boxscorefourfactorsv2,
        boxscoremiscv2,
        boxscoreplayertrackv2,
        boxscorescoringv2,
        
        # Historical data
        alltimeleadersgrid,
        assistleaders,
        defensehub,
        draftboard,
        
        # Team/Player dashboards
        teamdashboardbyclutch,
        teamdashboardbygamesplits,
        teamdashboardbygeneralsplits,
        teamdashboardbylastngames,
        teamdashboardbyopponent,
        teamdashboardbyshootingsplits,
        teamdashboardbyteamperformance,
        
        # Player dashboards
        playerdashboardbyclutch,
        playerdashboardbygamesplits,
        playerdashboardbygeneralsplits,
        playerdashboardbylastngames,
        playerdashboardbyopponent,
        playerdashboardbyshootingsplits,
        playerdashboardbyteamperformance,
        
        # Additional endpoints
        commonallplayers,
        commonplayerinfo,
        commonplayoffseries,
        commonteamroster,
        commonteamyears,
        cumestatsplayer,
        cumestatsteam,
        defensehub,
        draftcombinestats,
        drafthistory,
        fantasywidget,
        franchisehistory,
        homepageleaders,
        homepagev2,
        infographicfanduelplayer,
        leaderstiles,
        leaguedashlineups,
        leaguedashplayerclutch,
        leaguedashplayerptshot,
        leaguedashplayershotlocations,
        leaguedashplayerstats,
        leaguedashptdefend,
        leaguedashptstats,
        leaguedashptteamdefend,
        leaguedashptteamptshot,
        leaguedashptteamshotlocations,
        leaguedashteamclutch,
        leaguedashteamlineups,
        leaguedashteamptshot,
        leaguedashteamshotlocations,
        leaguedashteamstats,
        leagueleaders,
        leaguestandings,
        leaguestandingsv3,
        playbyplay,
        playbyplayv2,
        playercareerstats,
        playercareerstatsv2,
        playercompare,
        playerdashboardbyclutch,
        playerdashboardbygamesplits,
        playerdashboardbygeneralsplits,
        playerdashboardbylastngames,
        playerdashboardbyopponent,
        playerdashboardbyshootingsplits,
        playerdashboardbyteamperformance,
        playerestimatedmetrics,
        playerfantasyprofile,
        playerfantasyprofilebargraph,
        playerfantasyprofilechart,
        playergamelog,
        playergamelogs,
        playerindex,
        playernextngames,
        playerprofilev2,
        playersvsplayers,
        playervsplayer,
        playoffpicture,
        scoreboard,
        scoreboardv2,
        shotchartdetail,
        shotchartlineupdetail,
        teamdashboardbyclutch,
        teamdashboardbygamesplits,
        teamdashboardbygeneralsplits,
        teamdashboardbylastngames,
        teamdashboardbyopponent,
        teamdashboardbyshootingsplits,
        teamdashboardbyteamperformance,
        teamestimatedmetrics,
        teamgamelog,
        teamgamelogs,
        teamhistoricalleaders,
        teaminfocommon,
        teamnextngames,
        teamvsplayer,
        teamyearbyyearstats,
        videodetails,
        videoevents,
        videostatus,
        winprobabilitypbp
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
class NBAAPIClientEnhanced:
    """Enhanced client for fetching NBA data using the nba_api library with full endpoint coverage."""
    
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
    
    # Basic endpoints (inherited from fixed client)
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
    
    # Enhanced endpoints - Advanced Analytics
    def get_player_tracking_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get player tracking statistics."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            stats_data = self._safe_api_call(
                leaguedashptstats.LeagueDashPtStats,
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
                        "minutes_per_game": float(row['MIN']) if pd.notna(row['MIN']) else 0.0,
                        "miles_per_game": float(row['MILES']) if pd.notna(row['MILES']) else 0.0,
                        "miles_per_hour": float(row['MILES_PER_HOUR']) if pd.notna(row['MILES_PER_HOUR']) else 0.0,
                        "avg_speed": float(row['AVG_SPEED']) if pd.notna(row['AVG_SPEED']) else 0.0,
                        "max_speed": float(row['MAX_SPEED']) if pd.notna(row['MAX_SPEED']) else 0.0,
                        "avg_speed_offense": float(row['AVG_SPEED_OFFENSE']) if pd.notna(row['AVG_SPEED_OFFENSE']) else 0.0,
                        "avg_speed_defense": float(row['AVG_SPEED_DEFENSE']) if pd.notna(row['AVG_SPEED_DEFENSE']) else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching player tracking stats: {e}")
            return []
    
    def get_clutch_stats(self, season: int, season_type: str = "Regular Season") -> List[Dict[str, Any]]:
        """Get clutch performance statistics."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            stats_data = self._safe_api_call(
                leaguedashclutch.LeagueDashClutch,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame",
                clutch_time="Last 5 Minutes",
                ahead_behind="Ahead or Behind",
                point_diff=5
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
                        "clutch_games": int(row['CLUTCH_GAMES']) if pd.notna(row['CLUTCH_GAMES']) else 0,
                        "clutch_minutes": float(row['CLUTCH_MIN']) if pd.notna(row['CLUTCH_MIN']) else 0.0,
                        "clutch_points": float(row['CLUTCH_PTS']) if pd.notna(row['CLUTCH_PTS']) else 0.0,
                        "clutch_rebounds": float(row['CLUTCH_REB']) if pd.notna(row['CLUTCH_REB']) else 0.0,
                        "clutch_assists": float(row['CLUTCH_AST']) if pd.notna(row['CLUTCH_AST']) else 0.0,
                        "clutch_plus_minus": float(row['CLUTCH_PLUS_MINUS']) if pd.notna(row['CLUTCH_PLUS_MINUS']) else 0.0
                    }
                    stats.append(stat_dict)
            
            return stats
            
        except Exception as e:
            print(f"Error fetching clutch stats: {e}")
            return []
    
    def get_team_dashboard(self, team_id: str, season: int, season_type: str = "Regular Season") -> Dict[str, Any]:
        """Get comprehensive team dashboard data."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return {}
            
        try:
            dashboard_data = {}
            
            # Team performance dashboard
            performance_data = self._safe_api_call(
                teamdashboardbyteamperformance.TeamDashboardByTeamPerformance,
                team_id=team_id,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            if hasattr(performance_data, 'get_data_frames'):
                dfs = performance_data.get_data_frames()
                if len(dfs) > 0:
                    dashboard_data['performance'] = dfs[0].to_dict('records')
            
            # Team shooting splits
            shooting_data = self._safe_api_call(
                teamdashboardbyshootingsplits.TeamDashboardByShootingSplits,
                team_id=team_id,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            if hasattr(shooting_data, 'get_data_frames'):
                dfs = shooting_data.get_data_frames()
                if len(dfs) > 0:
                    dashboard_data['shooting'] = dfs[0].to_dict('records')
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error fetching team dashboard: {e}")
            return {}
    
    def get_player_dashboard(self, player_id: str, season: int, season_type: str = "Regular Season") -> Dict[str, Any]:
        """Get comprehensive player dashboard data."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return {}
            
        try:
            dashboard_data = {}
            
            # Player performance dashboard
            performance_data = self._safe_api_call(
                playerdashboardbyteamperformance.PlayerDashboardByTeamPerformance,
                player_id=player_id,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            if hasattr(performance_data, 'get_data_frames'):
                dfs = performance_data.get_data_frames()
                if len(dfs) > 0:
                    dashboard_data['performance'] = dfs[0].to_dict('records')
            
            # Player shooting splits
            shooting_data = self._safe_api_call(
                playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits,
                player_id=player_id,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode_detailed="PerGame"
            )
            
            if hasattr(shooting_data, 'get_data_frames'):
                dfs = shooting_data.get_data_frames()
                if len(dfs) > 0:
                    dashboard_data['shooting'] = dfs[0].to_dict('records')
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error fetching player dashboard: {e}")
            return {}
    
    def get_game_details(self, game_id: str) -> Dict[str, Any]:
        """Get detailed game statistics."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return {}
            
        try:
            game_details = {}
            
            # Traditional box score
            traditional_data = self._safe_api_call(
                boxscoretraditionalv2.BoxScoreTraditionalV2,
                game_id=game_id
            )
            
            if hasattr(traditional_data, 'get_data_frames'):
                dfs = traditional_data.get_data_frames()
                if len(dfs) > 0:
                    game_details['traditional'] = dfs[0].to_dict('records')
            
            # Advanced box score
            advanced_data = self._safe_api_call(
                boxscoreadvancedv2.BoxScoreAdvancedV2,
                game_id=game_id
            )
            
            if hasattr(advanced_data, 'get_data_frames'):
                dfs = advanced_data.get_data_frames()
                if len(dfs) > 0:
                    game_details['advanced'] = dfs[0].to_dict('records')
            
            # Four factors box score
            four_factors_data = self._safe_api_call(
                boxscorefourfactorsv2.BoxScoreFourFactorsV2,
                game_id=game_id
            )
            
            if hasattr(four_factors_data, 'get_data_frames'):
                dfs = four_factors_data.get_data_frames()
                if len(dfs) > 0:
                    game_details['four_factors'] = dfs[0].to_dict('records')
            
            return game_details
            
        except Exception as e:
            print(f"Error fetching game details: {e}")
            return {}
    
    def get_league_leaders(self, season: int, season_type: str = "Regular Season", stat_category: str = "PTS") -> List[Dict[str, Any]]:
        """Get league leaders for various statistical categories."""
        if not NBA_API_AVAILABLE:
            print("Warning: NBA API endpoints not available")
            return []
            
        try:
            leaders_data = self._safe_api_call(
                leagueleaders.LeagueLeaders,
                season=f"{season}-{str(season + 1)[-2:]}",
                season_type_all_star=season_type,
                per_mode48="PerGame",
                stat_category_abbreviation=stat_category
            )
            
            leaders = []
            if hasattr(leaders_data, 'get_data_frames'):
                df = leaders_data.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    leader_dict = {
                        "rank": int(row['RANK']) if pd.notna(row['RANK']) else 0,
                        "player_id": str(row['PLAYER_ID']),
                        "player_name": row['PLAYER_NAME'],
                        "team_id": str(row['TEAM_ID']) if pd.notna(row['TEAM_ID']) else None,
                        "team_name": row['TEAM_NAME'] if pd.notna(row['TEAM_NAME']) else "",
                        "stat_value": float(row[stat_category]) if pd.notna(row[stat_category]) else 0.0,
                        "stat_category": stat_category,
                        "season": season,
                        "season_type": season_type
                    }
                    leaders.append(leader_dict)
            
            return leaders
            
        except Exception as e:
            print(f"Error fetching league leaders: {e}")
            return []
    
    # Inherit other methods from fixed client
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

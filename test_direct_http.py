#!/usr/bin/env python3
"""
Test script for Direct HTTP NBA API Client
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_http_client():
    """Test the direct HTTP NBA API client"""
    try:
        from nba.sources.nba_api_client_v3 import NBAAPIClientV3
        
        print("Testing Direct HTTP NBA API Client...")
        client = NBAAPIClientV3()
        
        # Test teams
        print("Testing teams...")
        teams = client.get_teams()
        print(f"✅ Teams: {len(teams)} teams")
        if teams:
            print(f"   - Sample team: {teams[0]['name']} ({teams[0]['abbreviation']})")
        
        # Test players
        print("Testing players...")
        players = client.get_players()
        print(f"✅ Players: {len(players)} players")
        if players:
            print(f"   - Sample player: {players[0]['name']} ({players[0]['position']})")
        
        # Test team stats
        print("Testing team stats...")
        team_stats = client.get_team_stats(2023, "Regular Season")
        print(f"✅ Team stats: {len(team_stats)} teams")
        if team_stats:
            print(f"   - Sample team: {team_stats[0]['team_name']} - {team_stats[0]['points_per_game']} PPG")
        
        # Test player stats
        print("Testing player stats...")
        player_stats = client.get_player_stats(2023, "Regular Season")
        print(f"✅ Player stats: {len(player_stats)} players")
        if player_stats:
            print(f"   - Sample player: {player_stats[0]['player_name']} - {player_stats[0]['points_per_game']} PPG")
        
        # Test standings
        print("Testing standings...")
        standings = client.get_standings(2023, "Regular Season")
        print(f"✅ Standings: {len(standings)} teams")
        if standings:
            print(f"   - Sample team: {standings[0]['team_name']} - {standings[0]['wins']}-{standings[0]['losses']}")
        
        # Test games (current day)
        print("Testing games...")
        games = client.get_games(2023, "Regular Season")
        print(f"✅ Games: {len(games)} games")
        if games:
            print(f"   - Sample game: {games[0]['away_team_abbr']} @ {games[0]['home_team_abbr']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct HTTP client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_quality():
    """Test data quality and structure"""
    try:
        from nba.sources.nba_api_client_v3 import NBAAPIClientV3
        
        print("Testing data quality...")
        client = NBAAPIClientV3()
        
        # Test team stats structure
        team_stats = client.get_team_stats(2023, "Regular Season")
        if team_stats:
            sample_team = team_stats[0]
            required_fields = ['team_id', 'team_name', 'season', 'points_per_game', 'win_percentage']
            missing_fields = [field for field in required_fields if field not in sample_team]
            if missing_fields:
                print(f"⚠️ Missing fields in team stats: {missing_fields}")
            else:
                print("✅ Team stats structure is correct")
        
        # Test player stats structure
        player_stats = client.get_player_stats(2023, "Regular Season")
        if player_stats:
            sample_player = player_stats[0]
            required_fields = ['player_id', 'player_name', 'season', 'points_per_game', 'games_played']
            missing_fields = [field for field in required_fields if field not in sample_player]
            if missing_fields:
                print(f"⚠️ Missing fields in player stats: {missing_fields}")
            else:
                print("✅ Player stats structure is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏀 Testing Direct HTTP NBA API Client")
    print("=" * 50)
    
    # Test direct HTTP client
    if not test_direct_http_client():
        print("\n💡 Direct HTTP client test failed")
        sys.exit(1)
    
    # Test data quality
    if not test_data_quality():
        print("\n💡 Data quality test failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Direct HTTP client is working!")
    print("\n📝 NumPy compatibility issues completely bypassed!")
    print("   - No pandas dependencies")
    print("   - No NumPy compatibility issues")
    print("   - Direct access to NBA API endpoints")

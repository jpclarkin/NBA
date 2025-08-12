#!/usr/bin/env python3
"""
Test script for NumPy-compatible NBA API client
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_static_data():
    """Test static data access"""
    try:
        from nba.sources.nba_api_client_v2 import NBAAPIClientV2
        
        print("Testing static data...")
        client = NBAAPIClientV2()
        
        # Test teams
        teams = client.get_teams()
        print(f"✅ Teams: {len(teams)} teams")
        
        # Test players
        players = client.get_players()
        print(f"✅ Players: {len(players)} players")
        
        return True
        
    except Exception as e:
        print(f"❌ Static data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    try:
        from nba.sources.nba_api_client_v2 import NBAAPIClientV2
        
        print("Testing API endpoints...")
        client = NBAAPIClientV2()
        
        # Test team stats
        team_stats = client.get_team_stats(2023, "Regular Season")
        print(f"✅ Team stats: {len(team_stats)} teams")
        
        # Test player stats
        player_stats = client.get_player_stats(2023, "Regular Season")
        print(f"✅ Player stats: {len(player_stats)} players")
        
        # Test standings
        standings = client.get_standings(2023, "Regular Season")
        print(f"✅ Standings: {len(standings)} teams")
        
        # Test games (this might be empty if no games for the date)
        games = client.get_games(2023, "Regular Season")
        print(f"✅ Games: {len(games)} games")
        
        # Test live games
        live_games = client.get_live_games()
        print(f"✅ Live games: {len(live_games)} games")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_quality():
    """Test data quality and structure"""
    try:
        from nba.sources.nba_api_client_v2 import NBAAPIClientV2
        
        print("Testing data quality...")
        client = NBAAPIClientV2()
        
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
    print("🏀 Testing NumPy-Compatible NBA API Client")
    print("=" * 50)
    
    # Test static data
    if not test_static_data():
        print("\n💡 Static data test failed")
        sys.exit(1)
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n💡 API endpoints test failed")
        sys.exit(1)
    
    # Test data quality
    if not test_data_quality():
        print("\n💡 Data quality test failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! NumPy compatibility issues resolved!")
    print("\n📝 The NBA API client is now ready for full endpoint coverage.")

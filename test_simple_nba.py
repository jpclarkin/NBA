#!/usr/bin/env python3
"""
Simple test script for NBA API integration that works around compatibility issues
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_static_data_only():
    """Test only the static data which should work"""
    try:
        # Test static data directly
        from nba_api.stats.static import teams, players
        
        teams_data = teams.get_teams()
        players_data = players.get_players()
        
        print(f"✅ Static data access successful:")
        print(f"   - Teams: {len(teams_data)}")
        print(f"   - Players: {len(players_data)}")
        
        # Show sample data
        if teams_data:
            sample_team = teams_data[0]
            print(f"   - Sample team: {sample_team['full_name']} ({sample_team['abbreviation']})")
        
        if players_data:
            sample_player = players_data[0]
            print(f"   - Sample player: {sample_player['full_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Static data access failed: {e}")
        return False

def test_our_client_static_only():
    """Test our client with static data only"""
    try:
        # Import our client
        from nba.sources.nba_api_client import NBAAPIClient
        
        client = NBAAPIClient()
        
        # Test teams (should work with static data)
        teams = client.get_teams()
        print(f"✅ Our client - Teams: {len(teams)}")
        
        # Test players (should work with static data)
        players = client.get_players()
        print(f"✅ Our client - Players: {len(players)}")
        
        # Show sample data
        if teams:
            print(f"   - Sample team: {teams[0]}")
        
        if players:
            print(f"   - Sample player: {players[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Our client failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏀 Testing NBA API Integration (Static Data Only)")
    print("=" * 50)
    
    # Test static data
    if not test_static_data_only():
        print("\n💡 Static data access failed")
        sys.exit(1)
    
    # Test our client
    if not test_our_client_static_only():
        print("\n💡 Our client failed")
        sys.exit(1)
    
    print("\n🎉 Static data tests passed! NBA API integration is working for static data.")
    print("\n📝 Note: Some endpoints are temporarily disabled due to NumPy compatibility issues.")
    print("   - Teams and players data is working")
    print("   - Games, stats, and other endpoints need NumPy compatibility fixes")

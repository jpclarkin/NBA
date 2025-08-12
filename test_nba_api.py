#!/usr/bin/env python3
"""
Test script for NBA API integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nba_api_installation():
    """Test if nba_api is properly installed"""
    try:
        import nba_api
        version = getattr(nba_api, '__version__', 'unknown')
        print(f"✅ nba_api installed (version: {version})")
        return True
    except ImportError as e:
        print(f"❌ nba_api not found: {e}")
        return False

def test_nba_api_static_data():
    """Test static data access"""
    try:
        from nba_api.stats.static import teams, players
        teams_data = teams.get_teams()
        players_data = players.get_players()
        print(f"✅ Static data access successful:")
        print(f"   - Teams: {len(teams_data)}")
        print(f"   - Players: {len(players_data)}")
        return True
    except Exception as e:
        print(f"❌ Static data access failed: {e}")
        return False

def test_nba_api_endpoints():
    """Test API endpoints"""
    try:
        from nba_api.stats.endpoints import leaguedashteamstats
        # Test a simple endpoint call
        stats = leaguedashteamstats.LeagueDashTeamStats(season="2023-24")
        print("✅ API endpoints working")
        return True
    except Exception as e:
        print(f"❌ API endpoints failed: {e}")
        return False

def test_our_client():
    """Test our NBA API client"""
    try:
        from nba.sources.nba_api_client import NBAAPIClient
        client = NBAAPIClient()
        
        # Test teams
        teams = client.get_teams()
        print(f"✅ Our client - Teams: {len(teams)}")
        
        # Test players
        players = client.get_players()
        print(f"✅ Our client - Players: {len(players)}")
        
        return True
    except Exception as e:
        print(f"❌ Our client failed: {e}")
        return False

if __name__ == "__main__":
    print("🏀 Testing NBA API Integration")
    print("=" * 40)
    
    # Test installation
    if not test_nba_api_installation():
        print("\n💡 Try installing nba_api with: pip install nba_api")
        sys.exit(1)
    
    # Test static data
    if not test_nba_api_static_data():
        print("\n💡 Static data access failed")
        sys.exit(1)
    
    # Test endpoints
    if not test_nba_api_endpoints():
        print("\n💡 API endpoints failed")
        sys.exit(1)
    
    # Test our client
    if not test_our_client():
        print("\n💡 Our client failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! NBA API integration is working.")

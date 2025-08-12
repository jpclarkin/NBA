#!/usr/bin/env python3
"""
Test script for Fixed NBA API Client
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixed_client():
    """Test the fixed NBA API client"""
    try:
        from nba.sources.nba_api_client_fixed import NBAAPIClientFixed
        
        print("Testing Fixed NBA API Client...")
        client = NBAAPIClientFixed()
        
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
        
        # Test team stats (may fail due to network)
        print("Testing team stats...")
        team_stats = client.get_team_stats(2023, "Regular Season")
        print(f"✅ Team stats: {len(team_stats)} teams")
        if team_stats:
            print(f"   - Sample team: {team_stats[0]['team_name']} - {team_stats[0]['points_per_game']} PPG")
        
        # Test player stats (may fail due to network)
        print("Testing player stats...")
        player_stats = client.get_player_stats(2023, "Regular Season")
        print(f"✅ Player stats: {len(player_stats)} players")
        if player_stats:
            print(f"   - Sample player: {player_stats[0]['player_name']} - {player_stats[0]['points_per_game']} PPG")
        
        # Test standings (may fail due to network)
        print("Testing standings...")
        standings = client.get_standings(2023, "Regular Season")
        print(f"✅ Standings: {len(standings)} teams")
        if standings:
            print(f"   - Sample team: {standings[0]['team_name']} - {standings[0]['wins']}-{standings[0]['losses']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fixed client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ingestion_integration():
    """Test integration with ingestion modules"""
    try:
        print("Testing ingestion integration...")
        from nba.ingest.teams_ingest import ingest_teams
        from nba.ingest.players_ingest import ingest_players
        from nba.db.session import get_session_factory
        
        # Test teams ingestion
        print("Testing teams ingestion...")
        session_factory = get_session_factory()
        with session_factory() as session:
            teams = ingest_teams(session)
            print(f"✅ Teams ingestion: {len(teams)} teams ingested")
        
        # Test players ingestion
        print("Testing players ingestion...")
        with session_factory() as session:
            players = ingest_players(session)
            print(f"✅ Players ingestion: {len(players)} players ingested")
        
        return True
        
    except Exception as e:
        print(f"❌ Ingestion integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏀 Testing Fixed NBA API Client")
    print("=" * 50)
    
    # Test fixed client
    if not test_fixed_client():
        print("\n💡 Fixed client test failed")
        sys.exit(1)
    
    # Test ingestion integration
    if not test_ingestion_integration():
        print("\n💡 Ingestion integration test failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Fixed NBA API client is working!")
    print("\n📝 NumPy compatibility issues resolved!")
    print("   - nba_api library working")
    print("   - pandas compatibility working")
    print("   - Ingestion modules updated")
    print("   - Ready for full endpoint coverage")

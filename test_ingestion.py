#!/usr/bin/env python3
"""
Test script for NBA ingestion modules with new API client
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_teams_ingestion():
    """Test teams ingestion"""
    try:
        from nba.ingest.teams_ingest import ingest_teams
        from nba.db.session import get_session_factory
        
        print("Testing teams ingestion...")
        teams = ingest_teams()
        print(f"✅ Teams ingestion successful: {len(teams)} teams ingested")
        
        # Get a fresh session to query the data
        session_factory = get_session_factory()
        with session_factory() as session:
            # Query a sample team
            sample_team = session.query(teams[0].__class__).first()
            if sample_team:
                print(f"   - Sample team: {sample_team.name} ({sample_team.abbreviation})")
        
        return True
        
    except Exception as e:
        print(f"❌ Teams ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_players_ingestion():
    """Test players ingestion"""
    try:
        from nba.ingest.players_ingest import ingest_players
        from nba.db.session import get_session_factory
        
        print("Testing players ingestion...")
        players = ingest_players()
        print(f"✅ Players ingestion successful: {len(players)} players ingested")
        
        # Get a fresh session to query the data
        session_factory = get_session_factory()
        with session_factory() as session:
            # Query a sample player
            sample_player = session.query(players[0].__class__).first()
            if sample_player:
                print(f"   - Sample player: {sample_player.name} ({sample_player.position})")
        
        return True
        
    except Exception as e:
        print(f"❌ Players ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_client_direct():
    """Test API client directly"""
    try:
        from nba.sources.nba_api_client import NBAAPIClient
        
        print("Testing API client directly...")
        client = NBAAPIClient()
        
        # Test teams
        teams = client.get_teams()
        print(f"✅ API client teams: {len(teams)} teams")
        
        # Test players
        players = client.get_players()
        print(f"✅ API client players: {len(players)} players")
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏀 Testing NBA Ingestion Modules")
    print("=" * 40)
    
    # Test API client directly first
    if not test_api_client_direct():
        print("\n💡 API client test failed")
        sys.exit(1)
    
    # Test teams ingestion
    if not test_teams_ingestion():
        print("\n💡 Teams ingestion failed")
        sys.exit(1)
    
    # Test players ingestion
    if not test_players_ingestion():
        print("\n💡 Players ingestion failed")
        sys.exit(1)
    
    print("\n🎉 All ingestion tests passed!")
    print("\n📝 Note: Some endpoints (games, stats) are temporarily disabled due to NumPy compatibility issues.")
    print("   - Teams and players ingestion is working")
    print("   - Database integration is working")

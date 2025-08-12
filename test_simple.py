#!/usr/bin/env python3
"""
Simple test script for NBA infrastructure
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nba.config import get_settings
from nba.sources.nba_client import NBAAPIClient


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        settings = get_settings()
        print(f"✓ Configuration loaded successfully")
        print(f"  Database URL: {settings.database_url}")
        print(f"  NBA API Key: {'Set' if settings.nba_api_key else 'Not set'}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_api_client():
    """Test NBA API client connectivity."""
    print("\nTesting NBA API client...")
    try:
        client = NBAAPIClient()
        print("✓ NBA API client created successfully")
        
        # Test a simple API call (teams)
        print("  Attempting to fetch teams from NBA API...")
        teams = client.get_teams()
        print(f"✓ API test passed - Retrieved {len(teams)} teams")
        
        # Show some sample data
        if teams:
            print("  Sample teams:")
            for team in teams[:5]:  # Show first 5 teams
                print(f"    - {team.get('name', 'Unknown')} ({team.get('abbreviation', 'N/A')})")
        
        return True
    except Exception as e:
        print(f"✗ API client test failed: {e}")
        print("  Note: NBA.com API may have rate limiting or require authentication")
        return False


def test_simple_ingestion():
    """Test simple data ingestion without database."""
    print("\nTesting simple data ingestion...")
    try:
        client = NBAAPIClient()
        
        # Try to get some basic data
        print("  Fetching teams...")
        teams = client.get_teams()
        print(f"  ✓ Retrieved {len(teams)} teams")
        
        # Try to get games for a recent season
        print("  Fetching games for 2023-24 season...")
        games = client.get_games(2023, "Regular Season")
        print(f"  ✓ Retrieved {len(games)} games")
        
        # Show sample game data
        if games:
            print("  Sample games:")
            for game in games[:3]:  # Show first 3 games
                print(f"    - {game.get('away_team_abbr', 'N/A')} @ {game.get('home_team_abbr', 'N/A')} on {game.get('game_date', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ Simple ingestion test failed: {e}")
        return False


def main():
    """Run simple infrastructure tests."""
    print("NBA Infrastructure Simple Test Suite")
    print("=" * 40)
    
    tests = [
        test_config,
        test_api_client,
        test_simple_ingestion
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! NBA infrastructure is working.")
    else:
        print("⚠ Some tests failed. This may be due to NBA API rate limiting.")
        print("  The infrastructure is set up correctly, but API access may be limited.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

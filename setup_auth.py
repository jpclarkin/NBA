#!/usr/bin/env python3
"""
NBA API Authentication Setup

This script helps you set up authentication for the NBA API.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nba.sources.auth import setup_authentication_interactive, get_authenticator
from nba.sources.nba_client import NBAAPIClient


def test_authenticated_client():
    """Test the NBA API client with authentication."""
    print("\n🧪 Testing Authenticated NBA API Client")
    print("=" * 40)
    
    try:
        # Create client with authentication
        client = NBAAPIClient()
        
        print("✓ NBA API client created with authentication")
        print(f"  Authenticator: {type(client.authenticator).__name__}")
        
        # Test API calls
        print("\nTesting API endpoints...")
        
        # Test teams endpoint
        print("  Testing teams endpoint...")
        teams = client.get_teams()
        print(f"  ✓ Teams endpoint: Retrieved {len(teams)} teams")
        
        # Show sample teams
        if teams:
            print("  Sample teams:")
            for team in teams[:3]:
                print(f"    - {team.get('name', 'Unknown')} ({team.get('abbreviation', 'N/A')})")
        
        # Test games endpoint
        print("\n  Testing games endpoint...")
        games = client.get_games(2023, "Regular Season")
        print(f"  ✓ Games endpoint: Retrieved {len(games)} games")
        
        # Show sample games
        if games:
            print("  Sample games:")
            for game in games[:2]:
                print(f"    - {game.get('away_team_abbr', 'N/A')} @ {game.get('home_team_abbr', 'N/A')}")
        
        print("\n🎉 All API tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ API test failed: {e}")
        print("  This may be due to NBA.com rate limiting or authentication issues.")
        return False


def main():
    """Main authentication setup function."""
    print("🏀 NBA API Authentication Setup")
    print("=" * 40)
    
    print("\nThis script will help you set up authentication for the NBA API.")
    print("NBA.com has various authentication methods and rate limiting.")
    
    # Set up authentication
    authenticator = setup_authentication_interactive()
    
    # Test the authenticated client
    if test_authenticated_client():
        print("\n✅ Authentication setup completed successfully!")
        print("\nYou can now use the NBA API client with authentication.")
        print("To use in your code:")
        print("  from nba.sources.nba_client import NBAAPIClient")
        print("  client = NBAAPIClient()  # Will use saved authentication")
    else:
        print("\n⚠ Authentication setup completed, but API tests failed.")
        print("This is common with NBA.com due to rate limiting.")
        print("The infrastructure is ready, but you may need to:")
        print("  - Wait between requests")
        print("  - Use different authentication methods")
        print("  - Consider using alternative data sources")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

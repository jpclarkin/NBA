#!/usr/bin/env python3
"""
Test script for NBA infrastructure

This script tests the basic functionality of the NBA data pipeline
including database initialization, API connectivity, and data ingestion.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nba.config import get_settings
from nba.db.session import create_all_tables, get_session_factory
from nba.sources.nba_client import NBAAPIClient
from nba.ingest.teams_ingest import ingest_teams
from nba.db.models import Team


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


def test_database():
    """Test database initialization and connectivity."""
    print("\nTesting database...")
    try:
        create_all_tables()
        print("✓ Database tables created successfully")
        
        # Test session creation
        session_factory = get_session_factory()
        session = session_factory()
        session.close()
        print("✓ Database session test passed")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_api_client():
    """Test NBA API client connectivity."""
    print("\nTesting NBA API client...")
    try:
        client = NBAAPIClient()
        print("✓ NBA API client created successfully")
        
        # Test a simple API call (teams)
        teams = client.get_teams()
        print(f"✓ API test passed - Retrieved {len(teams)} teams")
        return True
    except Exception as e:
        print(f"✗ API client test failed: {e}")
        return False


def test_teams_ingestion():
    """Test team data ingestion."""
    print("\nTesting team ingestion...")
    try:
        teams = ingest_teams()
        print(f"✓ Team ingestion successful - {len(teams)} teams ingested")
        
        # Verify teams in database
        session_factory = get_session_factory()
        session = session_factory()
        db_teams = session.query(Team).all()
        session.close()
        print(f"✓ Database verification - {len(db_teams)} teams in database")
        return True
    except Exception as e:
        print(f"✗ Team ingestion test failed: {e}")
        return False


def test_basic_queries():
    """Test basic database queries."""
    print("\nTesting basic queries...")
    try:
        session_factory = get_session_factory()
        session = session_factory()
        
        # Test team queries
        teams = session.query(Team).all()
        print(f"✓ Query test passed - {len(teams)} teams found")
        
        # Test filtering
        lakers = session.query(Team).filter(Team.abbreviation == "LAL").first()
        if lakers:
            print(f"✓ Filter test passed - Found Lakers: {lakers.name}")
        else:
            print("⚠ Filter test - Lakers not found (may need data ingestion)")
        
        session.close()
        return True
    except Exception as e:
        print(f"✗ Query test failed: {e}")
        return False


def main():
    """Run all infrastructure tests."""
    print("NBA Infrastructure Test Suite")
    print("=" * 40)
    
    tests = [
        test_config,
        test_database,
        test_api_client,
        test_teams_ingestion,
        test_basic_queries
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
        print("🎉 All tests passed! NBA infrastructure is ready to use.")
        return 0
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

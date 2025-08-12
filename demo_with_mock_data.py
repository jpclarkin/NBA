#!/usr/bin/env python3
"""
NBA Infrastructure Demo with Mock Data

This script demonstrates how the NBA infrastructure works by using mock data
to simulate the data ingestion and processing pipeline.
"""

import sys
from pathlib import Path
from datetime import datetime, date
import json

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nba.config import get_settings
from nba.db.session import create_all_tables, get_session_factory
from nba.db.models import Team, Game, Player, TeamStats


def create_mock_teams():
    """Create mock team data."""
    return [
        {
            "team_id": "1610612737",
            "name": "Atlanta Hawks",
            "abbreviation": "ATL",
            "city": "Atlanta",
            "state": "Georgia",
            "conference": "Eastern",
            "division": "Southeast"
        },
        {
            "team_id": "1610612738",
            "name": "Boston Celtics",
            "abbreviation": "BOS",
            "city": "Boston",
            "state": "Massachusetts",
            "conference": "Eastern",
            "division": "Atlantic"
        },
        {
            "team_id": "1610612747",
            "name": "Los Angeles Lakers",
            "abbreviation": "LAL",
            "city": "Los Angeles",
            "state": "California",
            "conference": "Western",
            "division": "Pacific"
        },
        {
            "team_id": "1610612744",
            "name": "Golden State Warriors",
            "abbreviation": "GSW",
            "city": "San Francisco",
            "state": "California",
            "conference": "Western",
            "division": "Pacific"
        }
    ]


def create_mock_games():
    """Create mock game data."""
    return [
        {
            "game_id": "0022300001",
            "game_date": "2023-10-24",
            "season": 2023,
            "season_type": "Regular Season",
            "home_team_abbr": "LAL",
            "away_team_abbr": "GSW",
            "home_score": 108,
            "away_score": 104,
            "home_win": True,
            "arena": "Crypto.com Arena",
            "attendance": 18997
        },
        {
            "game_id": "0022300002",
            "game_date": "2023-10-25",
            "season": 2023,
            "season_type": "Regular Season",
            "home_team_abbr": "BOS",
            "away_team_abbr": "ATL",
            "home_score": 112,
            "away_score": 98,
            "home_win": True,
            "arena": "TD Garden",
            "attendance": 19156
        }
    ]


def create_mock_players():
    """Create mock player data."""
    return [
        {
            "player_id": "2544",
            "name": "LeBron James",
            "first_name": "LeBron",
            "last_name": "James",
            "team_id": "1610612747",
            "position": "F",
            "height": "6-9",
            "weight": 250,
            "is_active": True,
            "jersey_number": "23"
        },
        {
            "player_id": "201939",
            "name": "Stephen Curry",
            "first_name": "Stephen",
            "last_name": "Curry",
            "team_id": "1610612744",
            "position": "G",
            "height": "6-3",
            "weight": 185,
            "is_active": True,
            "jersey_number": "30"
        }
    ]


def demo_database_operations():
    """Demonstrate database operations with mock data."""
    print("🏀 NBA Infrastructure Demo with Mock Data")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        create_all_tables()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"⚠ Database initialization: {e}")
        print("  (This is expected if tables already exist)")
    
    # Get session
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        # 2. Insert mock teams
        print("\n2. Inserting mock teams...")
        mock_teams = create_mock_teams()
        teams = []
        
        for team_data in mock_teams:
            team = Team(
                team_id=team_data["team_id"],
                name=team_data["name"],
                abbreviation=team_data["abbreviation"],
                city=team_data["city"],
                state=team_data["state"],
                conference=team_data["conference"],
                division=team_data["division"]
            )
            session.add(team)
            teams.append(team)
        
        session.commit()
        print(f"✓ Inserted {len(teams)} teams")
        
        # 3. Insert mock games
        print("\n3. Inserting mock games...")
        mock_games = create_mock_games()
        games = []
        
        for game_data in mock_games:
            # Find teams by abbreviation
            home_team = session.query(Team).filter(Team.abbreviation == game_data["home_team_abbr"]).first()
            away_team = session.query(Team).filter(Team.abbreviation == game_data["away_team_abbr"]).first()
            
            # Parse game date
            game_date = datetime.strptime(game_data["game_date"], "%Y-%m-%d").date()
            
            game = Game(
                id=int(game_data["game_id"]),
                game_date=game_date,
                season=game_data["season"],
                season_type=game_data["season_type"],
                home_team_id=home_team.id if home_team else None,
                away_team_id=away_team.id if away_team else None,
                home_team_abbr=game_data["home_team_abbr"],
                away_team_abbr=game_data["away_team_abbr"],
                home_score=game_data["home_score"],
                away_score=game_data["away_score"],
                home_win=game_data["home_win"],
                arena=game_data["arena"],
                attendance=game_data["attendance"]
            )
            session.add(game)
            games.append(game)
        
        session.commit()
        print(f"✓ Inserted {len(games)} games")
        
        # 4. Insert mock players
        print("\n4. Inserting mock players...")
        mock_players = create_mock_players()
        players = []
        
        for player_data in mock_players:
            # Find team by ID
            team = session.query(Team).filter(Team.team_id == player_data["team_id"]).first()
            
            player = Player(
                player_id=player_data["player_id"],
                name=player_data["name"],
                first_name=player_data["first_name"],
                last_name=player_data["last_name"],
                team_id=team.id if team else None,
                position=player_data["position"],
                height=player_data["height"],
                weight=player_data["weight"],
                is_active=player_data["is_active"],
                jersey_number=player_data["jersey_number"]
            )
            session.add(player)
            players.append(player)
        
        session.commit()
        print(f"✓ Inserted {len(players)} players")
        
        # 5. Query and display data
        print("\n5. Querying and displaying data...")
        
        # Get all teams
        all_teams = session.query(Team).all()
        print(f"  Teams in database: {len(all_teams)}")
        for team in all_teams:
            print(f"    - {team.name} ({team.abbreviation}) - {team.conference} Conference")
        
        # Get all games
        all_games = session.query(Game).all()
        print(f"\n  Games in database: {len(all_games)}")
        for game in all_games:
            print(f"    - {game.away_team_abbr} @ {game.home_team_abbr} - {game.home_score}-{game.away_score}")
        
        # Get all players
        all_players = session.query(Player).all()
        print(f"\n  Players in database: {len(all_players)}")
        for player in all_players:
            team_name = player.team.name if player.team else "No Team"
            print(f"    - {player.name} ({player.position}) - {team_name}")
        
        # 6. Demonstrate filtering
        print("\n6. Demonstrating filtering and queries...")
        
        # Find Lakers
        lakers = session.query(Team).filter(Team.abbreviation == "LAL").first()
        if lakers:
            print(f"  Found Lakers: {lakers.name} ({lakers.city}, {lakers.state})")
            
            # Find Lakers players
            lakers_players = session.query(Player).filter(Player.team_id == lakers.id).all()
            print(f"  Lakers players: {len(lakers_players)}")
            for player in lakers_players:
                print(f"    - {player.name} (#{player.jersey_number})")
        
        # Find games with high attendance
        high_attendance_games = session.query(Game).filter(Game.attendance > 18000).all()
        print(f"\n  Games with attendance > 18,000: {len(high_attendance_games)}")
        for game in high_attendance_games:
            print(f"    - {game.away_team_abbr} @ {game.home_team_abbr} - {game.attendance} fans")
        
        print("\n🎉 Demo completed successfully!")
        print("The NBA infrastructure is working correctly with:")
        print("  ✓ Database models and relationships")
        print("  ✓ Data insertion and querying")
        print("  ✓ Filtering and joins")
        print("  ✓ Proper data types and constraints")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def main():
    """Run the demo."""
    try:
        demo_database_operations()
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

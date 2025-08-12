"""
Database Models for NBA Data

This module defines SQLAlchemy models for NBA data including
games, teams, players, statistics, and other related data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Float, 
    Index, UniqueConstraint, Text, Column, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String(16), unique=True, index=True)  # NBA team ID
    name = Column(String(64), index=True)
    abbreviation = Column(String(8), unique=True, index=True)
    city = Column(String(64), nullable=True)
    state = Column(String(32), nullable=True)
    conference = Column(String(32), nullable=True, index=True)
    division = Column(String(32), nullable=True, index=True)
    arena = Column(String(128), nullable=True)
    arena_capacity = Column(Integer, nullable=True)
    founded = Column(Integer, nullable=True)
    primary_color = Column(String(32), nullable=True)
    secondary_color = Column(String(32), nullable=True)
    logo_url = Column(String(256), nullable=True)
    
    # Relationships
    team_stats = relationship("TeamStats", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id")
    away_games = relationship("Game", foreign_keys="Game.away_team_id")
    players = relationship("Player", back_populates="team")

    __table_args__ = (
        Index("ix_teams_conference", "conference"),
        Index("ix_teams_division", "division"),
    )

    def __repr__(self) -> str:
        return f"Team(id={self.id}, name={self.name}, abbreviation={self.abbreviation})"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)  # NBA game_id
    game_date = Column(Date, index=True)
    season = Column(Integer, index=True)
    season_type = Column(String(16), index=True)  # Regular Season, Playoffs, etc.
    game_type = Column(String(16), nullable=True)  # Regular, Playoff, All-Star, etc.
    
    # Team references
    home_team_id = Column(ForeignKey("teams.id"), nullable=True, index=True)
    away_team_id = Column(ForeignKey("teams.id"), nullable=True, index=True)
    home_team_abbr = Column(String(8), index=True)
    away_team_abbr = Column(String(8), index=True)
    
    # Game results
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_win = Column(Boolean, nullable=True)
    
    # Game metadata
    arena = Column(String(128), nullable=True)
    attendance = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    overtime = Column(Boolean, default=False)
    overtime_periods = Column(Integer, default=0)
    
    # Game context
    home_rest_days = Column(Integer, nullable=True)
    away_rest_days = Column(Integer, nullable=True)
    home_back_to_back = Column(Boolean, default=False)
    away_back_to_back = Column(Boolean, default=False)
    
    # Relationships
    game_stats = relationship("GameStats", back_populates="game", cascade="all, delete-orphan")
    player_stats = relationship("PlayerGameStats", back_populates="game", cascade="all, delete-orphan")
    betting_lines = relationship("BettingLine", back_populates="game", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_games_season_date", "season", "game_date"),
        Index("ix_games_home_team_id", "home_team_id"),
        Index("ix_games_away_team_id", "away_team_id"),
        Index("ix_games_home_team_abbr", "home_team_abbr"),
        Index("ix_games_away_team_abbr", "away_team_abbr"),
    )

    def __repr__(self) -> str:
        return f"Game(id={self.id}, {self.away_team_abbr}@{self.home_team_abbr}, {self.game_date})"


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(16), unique=True, index=True)  # NBA player ID
    name = Column(String(128), index=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    team_id = Column(ForeignKey("teams.id"), nullable=True, index=True)
    
    # Player details
    position = Column(String(8), nullable=True, index=True)
    height = Column(String(16), nullable=True)
    weight = Column(Integer, nullable=True)  # in pounds
    birth_date = Column(Date, nullable=True)
    birth_place = Column(String(128), nullable=True)
    college = Column(String(128), nullable=True)
    draft_year = Column(Integer, nullable=True)
    draft_round = Column(Integer, nullable=True)
    draft_number = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    jersey_number = Column(String(8), nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="players")
    game_stats = relationship("PlayerGameStats", back_populates="player", cascade="all, delete-orphan")
    season_stats = relationship("PlayerSeasonStats", back_populates="player", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_players_position", "position"),
        Index("ix_players_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"Player(id={self.id}, name={self.name}, position={self.position})"


class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(ForeignKey("teams.id"), nullable=False, index=True)
    season = Column(Integer, index=True)
    season_type = Column(String(16), index=True)
    
    # Basic stats
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_percentage = Column(Float, nullable=True)
    
    # Offensive stats
    points_per_game = Column(Float, nullable=True)
    field_goal_percentage = Column(Float, nullable=True)
    three_point_percentage = Column(Float, nullable=True)
    free_throw_percentage = Column(Float, nullable=True)
    offensive_rebounds_per_game = Column(Float, nullable=True)
    assists_per_game = Column(Float, nullable=True)
    turnovers_per_game = Column(Float, nullable=True)
    
    # Defensive stats
    defensive_rebounds_per_game = Column(Float, nullable=True)
    steals_per_game = Column(Float, nullable=True)
    blocks_per_game = Column(Float, nullable=True)
    personal_fouls_per_game = Column(Float, nullable=True)
    
    # Advanced stats
    pace = Column(Float, nullable=True)
    offensive_rating = Column(Float, nullable=True)
    defensive_rating = Column(Float, nullable=True)
    net_rating = Column(Float, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="team_stats")

    __table_args__ = (
        Index("ix_team_stats_team_season", "team_id", "season"),
        Index("ix_team_stats_season_type", "season", "season_type"),
    )

    def __repr__(self) -> str:
        return f"TeamStats(team_id={self.team_id}, season={self.season}, wins={self.wins}-{self.losses})"


class GameStats(Base):
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(ForeignKey("games.id"), nullable=False, index=True)
    team_id = Column(ForeignKey("teams.id"), nullable=False, index=True)
    is_home = Column(Boolean, index=True)
    
    # Basic stats
    points = Column(Integer, default=0)
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    field_goal_percentage = Column(Float, nullable=True)
    three_points_made = Column(Integer, default=0)
    three_points_attempted = Column(Integer, default=0)
    three_point_percentage = Column(Float, nullable=True)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)
    free_throw_percentage = Column(Float, nullable=True)
    
    # Rebounding
    offensive_rebounds = Column(Integer, default=0)
    defensive_rebounds = Column(Integer, default=0)
    total_rebounds = Column(Integer, default=0)
    
    # Other stats
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    
    # Advanced stats
    true_shooting_percentage = Column(Float, nullable=True)
    effective_field_goal_percentage = Column(Float, nullable=True)
    offensive_rebound_percentage = Column(Float, nullable=True)
    defensive_rebound_percentage = Column(Float, nullable=True)
    assist_percentage = Column(Float, nullable=True)
    turnover_percentage = Column(Float, nullable=True)
    
    # Relationships
    game = relationship("Game", back_populates="game_stats")

    __table_args__ = (
        Index("ix_game_stats_game_team", "game_id", "team_id"),
    )

    def __repr__(self) -> str:
        return f"GameStats(game_id={self.game_id}, team_id={self.team_id}, points={self.points})"


class PlayerGameStats(Base):
    __tablename__ = "player_game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(ForeignKey("games.id"), nullable=False, index=True)
    player_id = Column(ForeignKey("players.id"), nullable=False, index=True)
    team_id = Column(ForeignKey("teams.id"), nullable=False, index=True)
    
    # Game context
    started = Column(Boolean, default=False)
    minutes_played = Column(String(8), nullable=True)  # "MM:SS" format
    minutes_played_seconds = Column(Integer, nullable=True)
    
    # Basic stats
    points = Column(Integer, default=0)
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    field_goal_percentage = Column(Float, nullable=True)
    three_points_made = Column(Integer, default=0)
    three_points_attempted = Column(Integer, default=0)
    three_point_percentage = Column(Float, nullable=True)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)
    free_throw_percentage = Column(Float, nullable=True)
    
    # Rebounding
    offensive_rebounds = Column(Integer, default=0)
    defensive_rebounds = Column(Integer, default=0)
    total_rebounds = Column(Integer, default=0)
    
    # Other stats
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    
    # Advanced stats
    plus_minus = Column(Integer, nullable=True)
    true_shooting_percentage = Column(Float, nullable=True)
    effective_field_goal_percentage = Column(Float, nullable=True)
    offensive_rebound_percentage = Column(Float, nullable=True)
    defensive_rebound_percentage = Column(Float, nullable=True)
    assist_percentage = Column(Float, nullable=True)
    turnover_percentage = Column(Float, nullable=True)
    
    # Relationships
    game = relationship("Game", back_populates="player_stats")
    player = relationship("Player", back_populates="game_stats")

    __table_args__ = (
        Index("ix_player_game_stats_game_player", "game_id", "player_id"),
    )

    def __repr__(self) -> str:
        return f"PlayerGameStats(game_id={self.game_id}, player_id={self.player_id}, points={self.points})"


class PlayerSeasonStats(Base):
    __tablename__ = "player_season_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(ForeignKey("players.id"), nullable=False, index=True)
    team_id = Column(ForeignKey("teams.id"), nullable=False, index=True)
    season = Column(Integer, index=True)
    season_type = Column(String(16), index=True)
    
    # Games played
    games_played = Column(Integer, default=0)
    games_started = Column(Integer, default=0)
    
    # Minutes
    minutes_per_game = Column(Float, nullable=True)
    total_minutes = Column(Integer, nullable=True)
    
    # Basic stats (per game averages)
    points_per_game = Column(Float, nullable=True)
    rebounds_per_game = Column(Float, nullable=True)
    assists_per_game = Column(Float, nullable=True)
    steals_per_game = Column(Float, nullable=True)
    blocks_per_game = Column(Float, nullable=True)
    turnovers_per_game = Column(Float, nullable=True)
    personal_fouls_per_game = Column(Float, nullable=True)
    
    # Shooting percentages
    field_goal_percentage = Column(Float, nullable=True)
    three_point_percentage = Column(Float, nullable=True)
    free_throw_percentage = Column(Float, nullable=True)
    
    # Advanced stats
    true_shooting_percentage = Column(Float, nullable=True)
    effective_field_goal_percentage = Column(Float, nullable=True)
    offensive_rebound_percentage = Column(Float, nullable=True)
    defensive_rebound_percentage = Column(Float, nullable=True)
    assist_percentage = Column(Float, nullable=True)
    turnover_percentage = Column(Float, nullable=True)
    usage_percentage = Column(Float, nullable=True)
    player_efficiency_rating = Column(Float, nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="season_stats")

    __table_args__ = (
        Index("ix_player_season_stats_player_season", "player_id", "season"),
        Index("ix_player_season_stats_season_type", "season", "season_type"),
    )

    def __repr__(self) -> str:
        return f"PlayerSeasonStats(player_id={self.player_id}, season={self.season}, ppg={self.points_per_game})"


class BettingLine(Base):
    __tablename__ = "betting_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(ForeignKey("games.id"), nullable=False, index=True)
    
    # Line information
    home_spread = Column(Float, nullable=True)
    away_spread = Column(Float, nullable=True)
    total_points = Column(Float, nullable=True)
    home_moneyline = Column(Integer, nullable=True)
    away_moneyline = Column(Integer, nullable=True)
    
    # Results
    home_cover = Column(Boolean, nullable=True)
    away_cover = Column(Boolean, nullable=True)
    over_hit = Column(Boolean, nullable=True)
    under_hit = Column(Boolean, nullable=True)
    
    # Metadata
    sportsbook = Column(String(64), nullable=True)
    line_type = Column(String(32), nullable=True)  # opening, closing, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="betting_lines")

    __table_args__ = (
        Index("ix_betting_lines_game", "game_id"),
        Index("ix_betting_lines_sportsbook", "sportsbook"),
    )

    def __repr__(self) -> str:
        return f"BettingLine(game_id={self.game_id}, home_spread={self.home_spread}, total={self.total_points})"

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Time, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, nullable=False)
    season_id = Column(Integer, nullable=False)
    competition_name = Column(String, nullable=False)
    season_name = Column(String, nullable=False)
    country_name = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('competition_id', 'season_id', name='_comp_season_uc'),)

    matches = relationship("Match", back_populates="competition")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    lineups = relationship("Lineup", back_populates="team")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nickname = Column(String, nullable=True)

    lineups = relationship("Lineup", back_populates="player")
    events = relationship("Event", back_populates="player")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)  # StatsBomb match_id
    competition_id = Column(Integer, nullable=False)
    season_id = Column(Integer, nullable=False)
    match_date = Column(Date, nullable=False)
    kick_off = Column(Time, nullable=True)
    
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    match_status = Column(String, nullable=True)
    match_week = Column(Integer, nullable=True)
    competition_stage = Column(String, nullable=True)
    stadium = Column(String, nullable=True)
    referee = Column(String, nullable=True)

    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    
    # We link to competitions via foreign key composite or lookup. 
    # For MVP, link using manual relationship or filter. Let's add ForeignKey constraint:
    competition_db_id = Column(Integer, ForeignKey("competitions.id"), nullable=True)
    competition = relationship("Competition", back_populates="matches")
    
    lineups = relationship("Lineup", back_populates="match", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="match", cascade="all, delete-orphan")


class Lineup(Base):
    __tablename__ = "lineups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    jersey_number = Column(Integer, nullable=False)
    position_id = Column(Integer, nullable=True)
    position_name = Column(String, nullable=True)

    # Relationships
    match = relationship("Match", back_populates="lineups")
    team = relationship("Team", back_populates="lineups")
    player = relationship("Player", back_populates="lineups")

    __table_args__ = (UniqueConstraint('match_id', 'player_id', name='_match_player_uc'),)


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)  # UUID
    index = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    timestamp = Column(String, nullable=False)
    minute = Column(Integer, nullable=False)
    second = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # Pass, Shot, Carry, Pressure, etc.
    
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    
    # Pitch Coordinates (Standardized to StatsBomb 120x80)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    
    # Destination Coordinates (Pass, Shot, Carry, etc.)
    end_x = Column(Float, nullable=True)
    end_y = Column(Float, nullable=True)
    
    outcome = Column(String, nullable=True)  # Complete, Incomplete, Goal, Offside, etc.
    under_pressure = Column(Boolean, default=False)
    
    # Dynamic properties stored as JSON (e.g. shot body part, shot technique, pass length, etc.)
    detail_json = Column(JSON, nullable=True)

    # Relationships
    match = relationship("Match", back_populates="events")
    team = relationship("Team")
    player = relationship("Player", back_populates="events")

import json
import urllib.request
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import Competition, Team, Player, Match, Lineup, Event
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base URL for StatsBomb Open Data
STATS_BOMB_BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Competitions to ingest
# 1. 2018 FIFA World Cup: comp_id = 43, season_id = 3
# 2. 2018/2019 FA Women's Super League: comp_id = 37, season_id = 4
# 3. 2022 FIFA World Cup: comp_id = 43, season_id = 106
# 4. 2020/2021 La Liga: comp_id = 11, season_id = 90
# 5. 2015/2016 Premier League: comp_id = 2, season_id = 27
TARGET_COMPETITIONS = [
    {"competition_id": 43, "season_id": 3},
    {"competition_id": 37, "season_id": 4},
    {"competition_id": 43, "season_id": 106},
    {"competition_id": 11, "season_id": 90},
    {"competition_id": 2, "season_id": 27}
]

def fetch_json(url: str):
    """Fetch and parse JSON from a URL."""
    try:
        logger.info(f"Fetching: {url}")
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def ingest_competitions(db: Session):
    """Download and ingest competitions."""
    url = f"{STATS_BOMB_BASE_URL}/competitions.json"
    data = fetch_json(url)
    if not data:
        return []

    ingested = []
    for item in data:
        comp_id = item["competition_id"]
        season_id = item["season_id"]
        
        # Check if we care about this competition
        if not any(tc["competition_id"] == comp_id and tc["season_id"] == season_id for tc in TARGET_COMPETITIONS):
            continue
            
        # Check if already exists
        existing = db.query(Competition).filter_by(competition_id=comp_id, season_id=season_id).first()
        if not existing:
            comp = Competition(
                competition_id=comp_id,
                season_id=season_id,
                competition_name=item["competition_name"],
                season_name=item["season_name"],
                country_name=item["country_name"]
            )
            db.add(comp)
            db.flush()  # to get the db generated ID
            logger.info(f"Added Competition: {comp.competition_name} ({comp.season_name})")
            ingested.append(comp)
        else:
            ingested.append(existing)
    
    db.commit()
    return ingested

def ingest_teams_and_players(db: Session, match_id: int, home_team: dict, away_team: dict):
    """Ensure teams exist, and fetch lineup data to ensure players exist."""
    # Ensure Teams exist
    teams = []
    for team_data in [home_team, away_team]:
        team = db.query(Team).filter_by(id=team_data["id"]).first()
        if not team:
            team = Team(id=team_data["id"], name=team_data["name"])
            db.add(team)
            db.flush()
        teams.append(team)
    
    # Ingest Lineups (and Players) for this match
    lineups_url = f"{STATS_BOMB_BASE_URL}/lineups/{match_id}.json"
    lineup_data = fetch_json(lineups_url)
    if not lineup_data:
        db.commit()
        return
        
    for team_lineup in lineup_data:
        team_id = team_lineup["team_id"]
        for player_data in team_lineup["lineup"]:
            # Ensure player exists
            player_id = player_data["player_id"]
            player = db.query(Player).filter_by(id=player_id).first()
            if not player:
                player = Player(
                    id=player_id,
                    name=player_data["player_name"],
                    nickname=player_data.get("player_nickname")
                )
                db.add(player)
                db.flush()
                
            # Ensure lineup record exists
            lineup = db.query(Lineup).filter_by(match_id=match_id, player_id=player_id).first()
            if not lineup:
                # Get position info if available
                positions = player_data.get("positions", [])
                pos_id = None
                pos_name = None
                if positions:
                    # Use last/main position in statsbomb array
                    pos_id = positions[0].get("position_id")
                    pos_name = positions[0].get("position")
                    
                lineup = Lineup(
                    match_id=match_id,
                    team_id=team_id,
                    player_id=player_id,
                    jersey_number=player_data["jersey_number"],
                    position_id=pos_id,
                    position_name=pos_name
                )
                db.add(lineup)
    db.commit()

def ingest_matches(db: Session, competitions: list):
    """Download and ingest matches for each competition."""
    matches_list = []
    for comp in competitions:
        url = f"{STATS_BOMB_BASE_URL}/matches/{comp.competition_id}/{comp.season_id}.json"
        data = fetch_json(url)
        if not data:
            continue
            
        logger.info(f"Found {len(data)} matches for {comp.competition_name} ({comp.season_name})")
        
        # Limit to 5 matches per competition to keep runtime fast for MVP demo
        # If user wants full dataset they can configure this
        subset_data = data[:10]  # Increased to 10 matches for more robust model training
        
        for match_data in subset_data:
            match_id = match_data["match_id"]
            existing = db.query(Match).filter_by(id=match_id).first()
            
            home_team_info = {
                "id": match_data["home_team"]["home_team_id"],
                "name": match_data["home_team"]["home_team_name"]
            }
            away_team_info = {
                "id": match_data["away_team"]["away_team_id"],
                "name": match_data["away_team"]["away_team_name"]
            }
            
            # Ensure teams and players are in database first
            ingest_teams_and_players(db, match_id, home_team_info, away_team_info)
            
            if not existing:
                match = Match(
                    id=match_id,
                    competition_id=comp.competition_id,
                    season_id=comp.season_id,
                    competition_db_id=comp.id,
                    match_date=datetime.strptime(match_data["match_date"], "%Y-%m-%d").date(),
                    kick_off=datetime.strptime(match_data["kick_off"], "%H:%M:%S.%f").time() if match_data.get("kick_off") else None,
                    home_team_id=home_team_info["id"],
                    away_team_id=away_team_info["id"],
                    home_score=match_data["home_score"],
                    away_score=match_data["away_score"],
                    match_status=match_data.get("match_status"),
                    match_week=match_data.get("match_week"),
                    competition_stage=match_data.get("competition_stage", {}).get("name"),
                    stadium=match_data.get("stadium", {}).get("name") if match_data.get("stadium") else None,
                    referee=match_data.get("referee", {}).get("name") if match_data.get("referee") else None
                )
                db.add(match)
                db.flush()
                logger.info(f"Added Match {match_id}: {home_team_info['name']} vs {away_team_info['name']}")
                matches_list.append(match)
            else:
                matches_list.append(existing)
                
    db.commit()
    return matches_list

def ingest_events(db: Session, matches: list):
    """Download and ingest events for matches."""
    for match in matches:
        match_id = match.id
        
        # Check if events already exist for this match
        count = db.query(Event).filter_by(match_id=match_id).count()
        if count > 0:
            logger.info(f"Events already exist for Match {match_id}. Skipping event ingestion.")
            continue
            
        url = f"{STATS_BOMB_BASE_URL}/events/{match_id}.json"
        events_data = fetch_json(url)
        if not events_data:
            continue
            
        logger.info(f"Ingesting {len(events_data)} events for Match {match_id}...")
        
        db_events = []
        for index, item in enumerate(events_data):
            # Parse core details
            player_id = item.get("player", {}).get("id")
            team_id = item["team"]["id"]
            
            # Coordinates
            location = item.get("location")
            x = location[0] if location and len(location) >= 2 else None
            y = location[1] if location and len(location) >= 2 else None
            
            # Destination coordinates (Pass end, Shot end, etc.)
            end_x = None
            end_y = None
            outcome = None
            
            event_type = item["type"]["name"]
            detail = {}
            
            # Extract additional details based on event type
            if event_type == "Shot":
                shot = item.get("shot", {})
                end_location = shot.get("end_location", [])
                if len(end_location) >= 2:
                    end_x, end_y = end_location[0], end_location[1]
                outcome = shot.get("outcome", {}).get("name")
                
                # Shot specific features
                detail = {
                    "body_part": shot.get("body_part", {}).get("name"),
                    "technique": shot.get("technique", {}).get("name"),
                    "type": shot.get("type", {}).get("name"),
                    "first_touch": shot.get("first_touch", False),
                    "one_on_one": shot.get("one_on_one", False),
                    "open_goal": shot.get("open_goal", False),
                    "statsbomb_xg": shot.get("statsbomb_xg", 0.0)
                }
            elif event_type == "Pass":
                pass_info = item.get("pass", {})
                end_location = pass_info.get("end_location", [])
                if len(end_location) >= 2:
                    end_x, end_y = end_location[0], end_location[1]
                outcome = pass_info.get("outcome", {}).get("name") or "Complete"
                
                detail = {
                    "length": pass_info.get("length", 0.0),
                    "angle": pass_info.get("angle", 0.0),
                    "height": pass_info.get("height", {}).get("name"),
                    "body_part": pass_info.get("body_part", {}).get("name"),
                    "cross": pass_info.get("cross", False),
                    "assisted_shot_id": pass_info.get("assisted_shot_id"),
                    "switch": pass_info.get("switch", False)
                }
            elif event_type == "Carry":
                carry = item.get("carry", {})
                end_location = carry.get("end_location", [])
                if len(end_location) >= 2:
                    end_x, end_y = end_location[0], end_location[1]
                
            under_pressure = item.get("under_pressure", False)
            
            # Build database object
            ev = Event(
                id=item["id"],
                index=item["index"],
                period=item["period"],
                timestamp=item["timestamp"],
                minute=item["minute"],
                second=item["second"],
                type=event_type,
                match_id=match_id,
                team_id=team_id,
                player_id=player_id,
                x=x,
                y=y,
                end_x=end_x,
                end_y=end_y,
                outcome=outcome,
                under_pressure=under_pressure,
                detail_json=detail
            )
            db_events.append(ev)
            
        # Bulk save for speed
        db.bulk_save_objects(db_events)
        db.commit()
        logger.info(f"Ingested {len(db_events)} events for Match {match_id} successfully.")

def run_pipeline():
    """Main function to run the ETL pipeline."""
    db = SessionLocal()
    try:
        logger.info("Starting StatsBomb Ingestion ETL Pipeline...")
        # Make sure tables exist
        Base.metadata.create_all(bind=engine)
        
        comps = ingest_competitions(db)
        if not comps:
            logger.error("No competitions ingested. Exiting ETL.")
            return
            
        matches = ingest_matches(db, comps)
        if not matches:
            logger.warn("No matches ingested.")
            return
            
        ingest_events(db, matches)
        logger.info("ETL pipeline execution completed successfully!")
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_pipeline()

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Match, Player, Competition, Team
from app.schemas.schemas import ShotPredictionRequest, AssistantRequest
from app.services.xg_service import xg_service
from app.services.similarity_service import similarity_service
from app.services.analytics_service import analytics_service
from app.services.rag_service import rag_service
from ml.etl.ingest import run_pipeline
from ml.xg_model.train import train_and_evaluate
from ml.similarity.train_similarity import train_similarity_model

router = APIRouter()

# --- Competitions & Matches ---

@router.get("/competitions")
def get_competitions(db: Session = Depends(get_db)):
    """Fetch all competitions loaded in the database."""
    comps = db.query(Competition).all()
    if not comps:
        # Return fallback mock competitions for instant UI feedback
        return [
            {"id": 1, "competition_id": 37, "season_id": 4, "competition_name": "Premier League", "season_name": "2015/2016", "country_name": "England"},
            {"id": 2, "competition_id": 43, "season_id": 3, "competition_name": "FIFA World Cup", "season_name": "2018", "country_name": "International"}
        ]
    return comps

@router.get("/matches")
def get_matches(competition_id: Optional[int] = None, season_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get list of matches, optionally filtered by competition and season."""
    query = db.query(Match)
    if competition_id:
        query = query.filter(Match.competition_id == competition_id)
    if season_id:
        query = query.filter(Match.season_id == season_id)
    matches = query.all()
    
    if not matches:
        # Return fallback mock matches for instant UI feedback
        return [
            {
                "id": 3754058, "match_date": "2016-05-15", "home_score": 2, "away_score": 1, 
                "home_team": {"name": "Arsenal"}, "away_team": {"name": "Chelsea"},
                "stadium": "Emirates Stadium", "competition_id": 37, "season_id": 4
            },
            {
                "id": 3754059, "match_date": "2016-04-10", "home_score": 2, "away_score": 2,
                "home_team": {"name": "Manchester City"}, "away_team": {"name": "Liverpool"},
                "stadium": "Etihad Stadium", "competition_id": 37, "season_id": 4
            },
            {
                "id": 432204, "match_date": "2018-06-30", "home_score": 4, "away_score": 3,
                "home_team": {"name": "France"}, "away_team": {"name": "Argentina"},
                "stadium": "Kazan Arena", "competition_id": 43, "season_id": 3
            }
        ]
        
    # Format response nicely
    results = []
    for m in matches:
        results.append({
            "id": m.id,
            "match_date": m.match_date,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "home_team": {"name": db.query(Team.name).filter_by(id=m.home_team_id).scalar()},
            "away_team": {"name": db.query(Team.name).filter_by(id=m.away_team_id).scalar()},
            "stadium": m.stadium,
            "competition_id": m.competition_id,
            "season_id": m.season_id
        })
    return results

@router.get("/matches/{match_id}/stats")
def get_match_stats(match_id: int, db: Session = Depends(get_db)):
    """Retrieve full match possession, shot volume, and pass accuracy splits."""
    return analytics_service.get_match_stats(db, match_id)

@router.get("/matches/{match_id}/shot-map")
def get_match_shot_map(match_id: int, db: Session = Depends(get_db)):
    """Fetch shot coordinate coordinates and dynamic expected goals (xG)."""
    return analytics_service.get_shot_map(db, match_id)

@router.get("/matches/{match_id}/passing-network")
def get_match_passing_network(match_id: int, team_id: int, db: Session = Depends(get_db)):
    """Fetch nodes (player average position) and links (passing combinations)."""
    return analytics_service.get_passing_network(db, match_id, team_id)

@router.get("/matches/{match_id}/heatmap")
def get_match_heatmap(match_id: int, team_id: Optional[int] = None, player_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve touch coordinates for team/player visual heatmaps."""
    return analytics_service.get_touches_heatmap(db, match_id, team_id, player_id)

# --- xG Model API ---

@router.post("/predict/xg")
def predict_xg(shot: ShotPredictionRequest):
    """Predict the expected goal (xG) value for a shot with given properties."""
    xg = xg_service.predict_xg(
        x=shot.x,
        y=shot.y,
        body_part=shot.body_part,
        technique=shot.technique,
        shot_type=shot.shot_type,
        under_pressure=shot.under_pressure
    )
    return {"xg": xg}

# --- Player Similarity & Recruitment ---

@router.get("/players")
def get_players():
    """Fetch all players loaded in the similarity embedding database."""
    players = similarity_service.get_all_players()
    if not players:
        # Fast fallback
        return [
            {"player_id": 1, "player_name": "Bukayo Saka", "umap_x": 1.2, "umap_y": 3.4},
            {"player_id": 2, "player_name": "Lionel Messi", "umap_x": 1.5, "umap_y": 3.2},
            {"player_id": 11, "player_name": "Martin Odegaard", "umap_x": -0.8, "umap_y": 2.1},
            {"player_id": 26, "player_name": "Virgil van Dijk", "umap_x": -3.5, "umap_y": -4.2}
        ]
    return players

@router.get("/players/{player_id}/similar")
def get_similar_players(player_id: int, top_n: int = 3):
    """Find similar players based on multi-metric cosine distance."""
    result = similarity_service.find_similar_players(player_id, top_n)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# --- Coach AI Assistant ---

@router.post("/assistant/ask")
def ask_assistant(req: AssistantRequest, db: Session = Depends(get_db)):
    """Retrieve match information and respond to coaching queries with citations."""
    return rag_service.ask_assistant(req.query, db)

# --- MLOps & ETL Control ---

@router.post("/etl/run")
def trigger_etl(background_tasks: BackgroundTasks):
    """Trigger the StatsBomb data ingestion ETL pipeline asynchronously."""
    background_tasks.add_task(run_pipeline)
    return {"status": "ingestion_started", "message": "StatsBomb data ingestion running in the background."}

@router.post("/ml/train")
def trigger_training(background_tasks: BackgroundTasks):
    """Trigger retraining of both the xG model and player similarity embeddings."""
    def run_training():
        train_and_evaluate()
        train_similarity_model()
        # Reload services
        xg_service._load_model()
        similarity_service._load_model()
        
    background_tasks.add_task(run_training)
    return {"status": "training_started", "message": "Models training in the background."}

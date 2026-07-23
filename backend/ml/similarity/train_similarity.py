import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

from app.core.database import SessionLocal
from app.models.models import Player, Event, Lineup
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "goals_per_90", "shots_per_90", "shot_accuracy",
    "passes_per_90", "pass_completion_rate", "key_passes_per_90",
    "carries_per_90", "pressures_per_90", "tackles_per_90",
    "interceptions_per_90", "recoveries_per_90", "fouls_won_per_90"
]

def generate_synthetic_players() -> pd.DataFrame:
    """Generate realistic player features for 40-50 world class players for fallback."""
    logger.info("Generating synthetic player profiles for similarity training fallback...")
    np.random.seed(42)
    
    players_data = [
        # Forwards / Wingers
        {"id": 1, "name": "Bukayo Saka", "role": "Winger"},
        {"id": 2, "name": "Lionel Messi", "role": "Forward"},
        {"id": 3, "name": "Cristiano Ronaldo", "role": "Forward"},
        {"id": 4, "name": "Kylian Mbappe", "role": "Winger"},
        {"id": 5, "name": "Mohamed Salah", "role": "Winger"},
        {"id": 6, "name": "Erling Haaland", "role": "Striker"},
        {"id": 7, "name": "Harry Kane", "role": "Striker"},
        {"id": 8, "name": "Vinicius Junior", "role": "Winger"},
        {"id": 9, "name": "Son Heung-min", "role": "Winger"},
        {"id": 10, "name": "Neymar Jr", "role": "Winger"},
        
        # Midfielders
        {"id": 11, "name": "Martin Odegaard", "role": "AMidfielder"},
        {"id": 12, "name": "Kevin De Bruyne", "role": "AMidfielder"},
        {"id": 13, "name": "Luka Modric", "role": "CMidfielder"},
        {"id": 14, "name": "Declan Rice", "role": "DMidfielder"},
        {"id": 15, "name": "Rodri", "role": "DMidfielder"},
        {"id": 16, "name": "Jude Bellingham", "role": "AMidfielder"},
        {"id": 17, "name": "Bruno Fernandes", "role": "AMidfielder"},
        {"id": 18, "name": "Pedri", "role": "CMidfielder"},
        {"id": 19, "name": "Joshua Kimmich", "role": "DMidfielder"},
        {"id": 20, "name": "Toni Kroos", "role": "CMidfielder"},
        
        # Defensive Midfielders / Box-to-Box
        {"id": 21, "name": "Casemiro", "role": "DMidfielder"},
        {"id": 22, "name": "N'Golo Kante", "role": "DMidfielder"},
        {"id": 23, "name": "Federico Valverde", "role": "CMidfielder"},
        {"id": 24, "name": "Thomas Partey", "role": "DMidfielder"},
        {"id": 25, "name": "Alexis Mac Allister", "role": "CMidfielder"},
        
        # Defenders
        {"id": 26, "name": "Virgil van Dijk", "role": "Defender"},
        {"id": 27, "name": "William Saliba", "role": "Defender"},
        {"id": 28, "name": "Ruben Dias", "role": "Defender"},
        {"id": 29, "name": "John Stones", "role": "Defender"},
        {"id": 30, "name": "Alphonso Davies", "role": "Fullback"},
        {"id": 31, "name": "Trent Alexander-Arnold", "role": "Fullback"},
        {"id": 32, "name": "Kieran Trippier", "role": "Fullback"},
        {"id": 33, "name": "Achraf Hakimi", "role": "Fullback"},
        {"id": 34, "name": "Gabriel Magalhaes", "role": "Defender"},
        {"id": 35, "name": "Andrew Robertson", "role": "Fullback"}
    ]
    
    rows = []
    for p in players_data:
        role = p["role"]
        
        # Base stats dependent on role
        if role == "Striker":
            goals = np.random.uniform(0.6, 0.9)
            shots = np.random.uniform(3.5, 5.0)
            shot_acc = np.random.uniform(0.4, 0.55)
            passes = np.random.uniform(15.0, 25.0)
            pass_comp = np.random.uniform(0.7, 0.8)
            key_passes = np.random.uniform(0.8, 1.5)
            carries = np.random.uniform(10.0, 20.0)
            pressures = np.random.uniform(12.0, 18.0)
            tackles = np.random.uniform(0.2, 0.6)
            interceptions = np.random.uniform(0.1, 0.3)
            recoveries = np.random.uniform(1.5, 3.0)
            fouls_won = np.random.uniform(1.0, 2.5)
        elif role == "Winger" or role == "Forward":
            goals = np.random.uniform(0.4, 0.7)
            shots = np.random.uniform(2.5, 4.0)
            shot_acc = np.random.uniform(0.35, 0.5)
            passes = np.random.uniform(25.0, 45.0)
            pass_comp = np.random.uniform(0.75, 0.83)
            key_passes = np.random.uniform(1.8, 3.0)
            carries = np.random.uniform(25.0, 45.0)
            pressures = np.random.uniform(10.0, 16.0)
            tackles = np.random.uniform(0.5, 1.2)
            interceptions = np.random.uniform(0.2, 0.6)
            recoveries = np.random.uniform(2.5, 4.5)
            fouls_won = np.random.uniform(1.5, 3.5)
        elif role == "AMidfielder":
            goals = np.random.uniform(0.25, 0.45)
            shots = np.random.uniform(1.8, 3.0)
            shot_acc = np.random.uniform(0.3, 0.45)
            passes = np.random.uniform(50.0, 75.0)
            pass_comp = np.random.uniform(0.82, 0.88)
            key_passes = np.random.uniform(2.5, 4.0)
            carries = np.random.uniform(20.0, 35.0)
            pressures = np.random.uniform(14.0, 22.0)
            tackles = np.random.uniform(0.8, 1.8)
            interceptions = np.random.uniform(0.5, 1.2)
            recoveries = np.random.uniform(4.0, 6.5)
            fouls_won = np.random.uniform(1.0, 2.5)
        elif role == "CMidfielder":
            goals = np.random.uniform(0.1, 0.25)
            shots = np.random.uniform(1.0, 2.0)
            shot_acc = np.random.uniform(0.3, 0.4)
            passes = np.random.uniform(60.0, 85.0)
            pass_comp = np.random.uniform(0.85, 0.92)
            key_passes = np.random.uniform(1.2, 2.2)
            carries = np.random.uniform(15.0, 28.0)
            pressures = np.random.uniform(15.0, 25.0)
            tackles = np.random.uniform(1.5, 2.5)
            interceptions = np.random.uniform(0.8, 1.8)
            recoveries = np.random.uniform(5.5, 8.5)
            fouls_won = np.random.uniform(0.8, 2.0)
        elif role == "DMidfielder":
            goals = np.random.uniform(0.02, 0.12)
            shots = np.random.uniform(0.5, 1.2)
            shot_acc = np.random.uniform(0.2, 0.35)
            passes = np.random.uniform(65.0, 90.0)
            pass_comp = np.random.uniform(0.88, 0.94)
            key_passes = np.random.uniform(0.5, 1.2)
            carries = np.random.uniform(10.0, 22.0)
            pressures = np.random.uniform(16.0, 26.0)
            tackles = np.random.uniform(2.0, 3.5)
            interceptions = np.random.uniform(1.2, 2.5)
            recoveries = np.random.uniform(6.5, 9.5)
            fouls_won = np.random.uniform(0.5, 1.5)
        elif role == "Fullback":
            goals = np.random.uniform(0.02, 0.1)
            shots = np.random.uniform(0.4, 1.0)
            shot_acc = np.random.uniform(0.2, 0.35)
            passes = np.random.uniform(45.0, 70.0)
            pass_comp = np.random.uniform(0.78, 0.85)
            key_passes = np.random.uniform(1.0, 2.5)
            carries = np.random.uniform(15.0, 30.0)
            pressures = np.random.uniform(10.0, 18.0)
            tackles = np.random.uniform(1.8, 3.0)
            interceptions = np.random.uniform(1.0, 2.0)
            recoveries = np.random.uniform(4.5, 7.0)
            fouls_won = np.random.uniform(0.8, 1.8)
        else: # Central Defender
            goals = np.random.uniform(0.01, 0.08)
            shots = np.random.uniform(0.2, 0.6)
            shot_acc = np.random.uniform(0.2, 0.4)
            passes = np.random.uniform(50.0, 80.0)
            pass_comp = np.random.uniform(0.88, 0.95)
            key_passes = np.random.uniform(0.1, 0.5)
            carries = np.random.uniform(8.0, 18.0)
            pressures = np.random.uniform(6.0, 12.0)
            tackles = np.random.uniform(1.2, 2.2)
            interceptions = np.random.uniform(1.2, 2.2)
            recoveries = np.random.uniform(4.0, 6.0)
            fouls_won = np.random.uniform(0.3, 1.0)
            
        rows.append({
            "player_id": p["id"],
            "player_name": p["name"],
            "goals_per_90": round(goals, 3),
            "shots_per_90": round(shots, 3),
            "shot_accuracy": round(shot_acc, 3),
            "passes_per_90": round(passes, 3),
            "pass_completion_rate": round(pass_comp, 3),
            "key_passes_per_90": round(key_passes, 3),
            "carries_per_90": round(carries, 3),
            "pressures_per_90": round(pressures, 3),
            "tackles_per_90": round(tackles, 3),
            "interceptions_per_90": round(interceptions, 3),
            "recoveries_per_90": round(recoveries, 3),
            "fouls_won_per_90": round(fouls_won, 3)
        })
        
    return pd.DataFrame(rows)

def fetch_player_aggregates() -> pd.DataFrame:
    """Fetch all events and compile aggregated per-90 metrics for each player."""
    db = SessionLocal()
    try:
        # Check if we have players
        players = db.query(Player).all()
        if not players or len(players) < 10:
            logger.info("Insufficient players in database. Falling back to synthetic profiles.")
            return generate_synthetic_players()
            
        logger.info(f"Aggregating event stats for {len(players)} players...")
        
        # Calculate minutes played: count matches in which a player has events/lineup
        # For simplicity, approximate: each match is 90 mins
        player_matches = {}
        lineups = db.query(Lineup).all()
        for l in lineups:
            player_matches[l.player_id] = player_matches.get(l.player_id, 0) + 1
            
        records = []
        for player in players:
            matches_played = player_matches.get(player.id, 0)
            if matches_played == 0:
                continue
                
            minutes = matches_played * 90.0
            
            # Let's count key events for this player
            events = db.query(Event.type, Event.outcome, Event.under_pressure, Event.detail_json).filter_by(player_id=player.id).all()
            
            goals = 0
            shots = 0
            shots_on_target = 0
            passes = 0
            completed_passes = 0
            key_passes = 0
            carries = 0
            pressures = 0
            tackles = 0
            interceptions = 0
            recoveries = 0
            fouls_won = 0
            
            for ev_type, outcome, press, detail in events:
                detail = detail or {}
                if ev_type == "Shot":
                    shots += 1
                    if outcome == "Goal":
                        goals += 1
                    if outcome in ["Goal", "Saved", "Saved to Post", "Saved Off Target"]:
                        shots_on_target += 1
                elif ev_type == "Pass":
                    passes += 1
                    # In statsbomb events, pass outcome is None if complete, or a string if incomplete
                    if not outcome or outcome == "Complete":
                        completed_passes += 1
                    if detail.get("assisted_shot_id"):
                        key_passes += 1
                elif ev_type == "Carry":
                    carries += 1
                elif ev_type == "Pressure":
                    pressures += 1
                elif ev_type == "Foul Won":
                    fouls_won += 1
                elif ev_type == "Ball Recovery":
                    recoveries += 1
                elif ev_type == "Interception":
                    interceptions += 1
                elif ev_type in ["Tackle", "Duel"]:
                    # approximation
                    tackles += 1
                    
            # Compute per-90 metrics
            factor = 90.0 / minutes
            
            records.append({
                "player_id": player.id,
                "player_name": player.name,
                "goals_per_90": round(goals * factor, 3),
                "shots_per_90": round(shots * factor, 3),
                "shot_accuracy": round(shots_on_target / shots if shots > 0 else 0.0, 3),
                "passes_per_90": round(passes * factor, 3),
                "pass_completion_rate": round(completed_passes / passes if passes > 0 else 0.0, 3),
                "key_passes_per_90": round(key_passes * factor, 3),
                "carries_per_90": round(carries * factor, 3),
                "pressures_per_90": round(pressures * factor, 3),
                "tackles_per_90": round(tackles * factor, 3),
                "interceptions_per_90": round(interceptions * factor, 3),
                "recoveries_per_90": round(recoveries * factor, 3),
                "fouls_won_per_90": round(fouls_won * factor, 3)
            })
            
        df = pd.DataFrame(records)
        # Filter out players with less than 90 total minutes (e.g. sub players) to keep pool high quality
        # But if the pool is small, don't filter.
        if df.shape[0] < 5:
            return generate_synthetic_players()
            
        return df
    except Exception as e:
        logger.error(f"Error compiling aggregates: {e}. Falling back to synthetic players.")
        return generate_synthetic_players()
    finally:
        db.close()

def train_similarity_model():
    """Aggregate stats, scale, fit Nearest Neighbors, run UMAP reduction, and serialize."""
    df = fetch_player_aggregates()
    
    # Scale features
    X = df[FEATURE_COLUMNS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit Nearest Neighbors
    # Use cosine distance for similarity calculation
    nn_model = NearestNeighbors(n_neighbors=min(6, len(df)), metric="cosine")
    nn_model.fit(X_scaled)
    
    # Fit UMAP for 2D visualization representation
    umap_coords = None
    if HAS_UMAP:
        try:
            logger.info("Fitting UMAP embedding space...")
            # Set n_neighbors to a smaller value if dataset is small
            n_neighs = min(15, len(df) - 1)
            if n_neighs < 2:
                n_neighs = 2
            reducer = umap.UMAP(n_neighbors=n_neighs, min_dist=0.1, n_components=2, metric="cosine", random_state=42)
            umap_coords = reducer.fit_transform(X_scaled)
            logger.info("UMAP fitted successfully.")
        except Exception as e:
            logger.error(f"UMAP fitting failed: {e}. Using PCA fallback.")
            
    if umap_coords is None:
        # Simple PCA fallback if UMAP fails or is not present
        from sklearn.decomposition import PCA
        logger.info("Running PCA for 2D coords fallback...")
        pca = PCA(n_components=2, random_state=42)
        umap_coords = pca.fit_transform(X_scaled)
        
    df["umap_x"] = umap_coords[:, 0]
    df["umap_y"] = umap_coords[:, 1]
    
    # Save package
    payload = {
        "df": df,
        "scaler": scaler,
        "nn_model": nn_model,
        "features": FEATURE_COLUMNS,
        "trained_at": pd.Timestamp.now().isoformat()
    }
    
    model_path = settings.SIMILARITY_MODEL_PATH
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(payload, f)
        
    logger.info(f"Player Similarity Model saved to {model_path} with {len(df)} players indexed.")

if __name__ == "__main__":
    train_similarity_model()

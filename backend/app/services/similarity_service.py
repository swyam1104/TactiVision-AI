import os
import pickle
import logging
import numpy as np
import pandas as pd
from app.core.config import settings

logger = logging.getLogger(__name__)

class SimilarityService:
    def __init__(self):
        self.model_path = settings.SIMILARITY_MODEL_PATH
        self.model_data = None
        self._load_model()
        
    def _load_model(self):
        """Load similarity artifacts. If not found, try to run training to initialize."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model_data = pickle.load(f)
                logger.info(f"Player Similarity Model loaded successfully. {len(self.model_data['df'])} players indexed.")
            except Exception as e:
                logger.error(f"Error loading similarity model from {self.model_path}: {e}")
                self.model_data = None
        else:
            logger.warn(f"Similarity model file not found at {self.model_path}. Will trigger training.")
            self._trigger_training()
            
    def _trigger_training(self):
        """Train model in-process to create fallback dataset."""
        try:
            from backend.ml.similarity.train_similarity import train_similarity_model
            train_similarity_model()
            # Try reloading
            if os.path.exists(self.model_path):
                with open(self.model_path, "rb") as f:
                    self.model_data = pickle.load(f)
                logger.info("Successfully trained and loaded similarity model on startup.")
        except Exception as e:
            logger.error(f"Failed to auto-train similarity model: {e}")

    def get_all_players(self):
        """Get list of all indexed players."""
        if not self.model_data:
            return []
        df = self.model_data["df"]
        return df[["player_id", "player_name", "umap_x", "umap_y"]].to_dict(orient="records")

    def find_similar_players(self, player_id: int, top_n: int = 4) -> dict:
        """
        Find top_n similar players for player_id.
        Returns:
            Dictionary containing player info, similarity scores, radar comparison data,
            and explanation of overlap.
        """
        if not self.model_data:
            return {"error": "Similarity model not initialized."}
            
        df = self.model_data["df"]
        scaler = self.model_data["scaler"]
        nn_model = self.model_data["nn_model"]
        features = self.model_data["features"]
        
        # Locate target player
        target_row = df[df["player_id"] == player_id]
        if target_row.empty:
            # Try to match by name as a fallback
            target_row = df[df["player_name"].str.contains(str(player_id), case=False, na=False)]
            if target_row.empty:
                return {"error": f"Player with identifier {player_id} not found."}
        
        player_idx = target_row.index[0]
        player_name = target_row.iloc[0]["player_name"]
        
        # Extract scaled features
        X = df[features].values
        X_scaled = scaler.transform(X)
        
        # Query nearest neighbors
        # We query top_n + 1 because the player themselves will be the 0th neighbor (cosine distance 0)
        distances, indices = nn_model.kneighbors(X_scaled[player_idx].reshape(1, -1), n_neighbors=min(top_n + 1, len(df)))
        
        distances = distances[0]
        indices = indices[0]
        
        results = []
        for dist, idx in zip(distances, indices):
            if idx == player_idx:
                continue # Skip self
                
            neighbor = df.iloc[idx]
            sim_score = 1.0 - dist # Cosine similarity = 1 - Cosine distance
            
            # Generate feature-by-feature comparison
            radar_comparison = []
            for feat in features:
                # Get raw values
                target_val = float(target_row.iloc[0][feat])
                neighbor_val = float(neighbor[feat])
                
                # Get percentiles to normalize radar charts between 0 and 100
                target_pct = float((df[feat] <= target_val).mean() * 100)
                neighbor_pct = float((df[feat] <= neighbor_val).mean() * 100)
                
                radar_comparison.append({
                    "metric": feat.replace("_per_90", "").replace("_rate", "").replace("_", " ").title(),
                    "player_value": target_val,
                    "player_percentile": round(target_pct, 1),
                    "match_value": neighbor_val,
                    "match_percentile": round(neighbor_pct, 1)
                })
                
            # Explain why they are similar
            # Find the metrics that are closest in standard deviation space
            target_scaled = X_scaled[player_idx]
            neighbor_scaled = X_scaled[idx]
            differences = np.abs(target_scaled - neighbor_scaled)
            
            # Sort features by smallest difference
            sorted_feats_idx = np.argsort(differences)
            closest_feats = [features[i] for i in sorted_feats_idx[:3]]
            
            explanation_parts = []
            for feat in closest_feats:
                clean_name = feat.replace("_per_90", "").replace("_rate", "").replace("_", " ")
                target_val = float(target_row.iloc[0][feat])
                neighbor_val = float(neighbor[feat])
                
                if "rate" in feat or "accuracy" in feat:
                    explanation_parts.append(f"{clean_name} ({target_val*100:.1f}% vs {neighbor_val*100:.1f}%)")
                else:
                    explanation_parts.append(f"{clean_name} ({target_val:.2f} vs {neighbor_val:.2f} per 90)")
            
            explanation = f"Highly similar in: {', '.join(explanation_parts)}."
            
            results.append({
                "player_id": int(neighbor["player_id"]),
                "player_name": str(neighbor["player_name"]),
                "similarity_score": round(float(sim_score), 4),
                "radar_comparison": radar_comparison,
                "explanation": explanation,
                "umap_x": float(neighbor["umap_x"]),
                "umap_y": float(neighbor["umap_y"])
            })
            
        return {
            "player_id": int(target_row.iloc[0]["player_id"]),
            "player_name": player_name,
            "umap_x": float(target_row.iloc[0]["umap_x"]),
            "umap_y": float(target_row.iloc[0]["umap_y"]),
            "similar_players": results
        }

similarity_service = SimilarityService()

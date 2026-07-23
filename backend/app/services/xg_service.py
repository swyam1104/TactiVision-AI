import os
import pickle
import logging
import numpy as np
from app.core.config import settings
from backend.ml.xg_model.features import extract_shot_features

logger = logging.getLogger(__name__)

class XGService:
    def __init__(self):
        self.model_path = settings.XG_MODEL_PATH
        self.model_data = None
        self._load_model()
        
    def _load_model(self):
        """Load the trained xG model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model_data = pickle.load(f)
                logger.info(f"xG Model loaded successfully: {self.model_data.get('model_type')} (AUC: {self.model_data.get('auc', 0.0):.4f})")
            except Exception as e:
                logger.error(f"Error loading xG model from {self.model_path}: {e}")
                self.model_data = None
        else:
            logger.warn(f"xG model file not found at {self.model_path}. Using mathematical fallback.")
            self.model_data = None

    def predict_xg(self, x: float, y: float, body_part: str = "Foot", technique: str = "Normal", shot_type: str = "Open Play", under_pressure: bool = False) -> float:
        """
        Predict expected goal (xG) for a shot.
        
        Args:
            x, y: Pitch coordinates (0 to 120, 0 to 80)
            body_part: "Foot", "Head", "Other"
            technique: "Normal", "Volley", "Half Volley", "Lob"
            shot_type: "Open Play", "Penalty", "Free Kick"
            under_pressure: boolean indicating if player was under pressure
        """
        # Penalties have a fixed standard xG of 0.76 in analytics
        if shot_type.lower() == "penalty":
            return 0.76

        # Extract features
        shot_dict = {
            "x": x,
            "y": y,
            "under_pressure": under_pressure,
            "detail_json": {
                "body_part": body_part,
                "technique": technique,
                "type": shot_type
            }
        }
        features = extract_shot_features(shot_dict)
        
        # If model is loaded, use it
        if self.model_data:
            try:
                model = self.model_data["model"]
                feature_names = self.model_data["features"]
                
                # Order the features correctly
                X_vals = [[features[name] for name in feature_names]]
                
                # Predict probability
                prob = float(model.predict_proba(X_vals)[0, 1])
                return round(prob, 3)
            except Exception as e:
                logger.error(f"Error using xG model for prediction: {e}. Using mathematical fallback.")
                
        # Heuristic/Mathematical fallback (Logistic Regression coefficients from open data benchmark)
        # logit = 0.5 - 0.11 * distance + 1.6 * angle - 0.7 * is_header - 0.4 * under_pressure - 0.3 * is_volley
        distance = features["distance"]
        angle = features["angle"]
        is_header = features["is_header"]
        under_press = features["under_pressure"]
        is_volley = features["is_volley"]
        
        logit = 0.5 - 0.11 * distance + 1.6 * angle - 0.7 * is_header - 0.4 * under_press - 0.3 * is_volley
        prob = 1.0 / (1.0 + np.exp(-logit))
        
        return round(float(prob), 3)

xg_service = XGService()

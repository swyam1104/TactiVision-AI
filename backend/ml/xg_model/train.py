import os
import pickle
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_auc_score, brier_score_loss, classification_report
import xgboost as xgb

from app.core.database import SessionLocal
from app.models.models import Event
from backend.ml.xg_model.features import extract_shot_features

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def generate_synthetic_shots(n_samples: int = 1500) -> pd.DataFrame:
    """Generate realistic synthetic shots for model training fallback."""
    logger.info(f"Generating {n_samples} synthetic shot records for training...")
    np.random.seed(42)
    
    x = np.random.uniform(85.0, 119.0, n_samples)
    y = np.random.uniform(20.0, 60.0, n_samples)
    under_pressure = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    is_header = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])
    is_volley = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    is_free_kick = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
    is_penalty = np.random.choice([0, 1], size=n_samples, p=[0.98, 0.02])
    
    # Calculate distance and angle
    distance = np.sqrt((120.0 - x)**2 + (40.0 - y)**2)
    
    # Visible goal angle
    dx = 120.0 - x
    v_a_y = 36.0 - y
    v_b_y = 44.0 - y
    dot = dx*dx + v_a_y*v_b_y
    norm_a = np.sqrt(dx*dx + v_a_y*v_a_y)
    norm_b = np.sqrt(dx*dx + v_b_y*v_b_y)
    angle = np.arccos(np.clip(dot / (norm_a * norm_b), -1.0, 1.0))
    
    # Define underlying probability structure
    # Goals are easier when close, wide angle, foot shot, no pressure, etc.
    logits = (
        0.5 
        - 0.12 * distance 
        + 1.8 * angle 
        - 0.6 * is_header 
        - 0.4 * under_pressure 
        - 0.3 * is_volley
    )
    
    # Penalties have fixed high rate
    logits[is_penalty == 1] = 1.2
    
    prob = 1.0 / (1.0 + np.exp(-logits))
    # Sample outcomes
    outcome = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "distance": distance,
        "angle": angle,
        "is_header": is_header,
        "is_volley": is_volley,
        "is_free_kick": is_free_kick,
        "is_penalty": is_penalty,
        "under_pressure": under_pressure,
        "is_goal": outcome
    })
    return df

def fetch_data_from_db() -> pd.DataFrame:
    """Fetch shot events from Postgres and build a dataframe."""
    db = SessionLocal()
    try:
        shots = db.query(Event).filter(Event.type == "Shot").all()
        if not shots or len(shots) < 100:
            logger.info("Insufficient shots in database. Falling back to synthetic data.")
            return generate_synthetic_shots()
            
        logger.info(f"Loaded {len(shots)} shots from database.")
        
        records = []
        for shot in shots:
            feat = extract_shot_features({
                "x": shot.x,
                "y": shot.y,
                "under_pressure": shot.under_pressure,
                "detail_json": shot.detail_json
            })
            
            # Map outcome to target
            is_goal = 1 if shot.outcome == "Goal" else 0
            feat["is_goal"] = is_goal
            records.append(feat)
            
        return pd.DataFrame(records)
    except Exception as e:
        logger.error(f"Failed to fetch data from DB: {e}. Using synthetic data.")
        return generate_synthetic_shots()
    finally:
        db.close()

def train_and_evaluate():
    """Train models, evaluate performance, and serialize the best one."""
    df = fetch_data_from_db()
    
    features = ["distance", "angle", "is_header", "is_volley", "is_free_kick", "is_penalty", "under_pressure"]
    X = df[features]
    y = df["is_goal"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    logger.info(f"Training set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")
    
    # 1. Logistic Regression
    lr_model = LogisticRegression(class_weight="balanced", random_state=42)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict_proba(X_test)[:, 1]
    lr_auc = roc_auc_score(y_test, lr_preds)
    lr_brier = brier_score_loss(y_test, lr_preds)
    
    logger.info(f"Logistic Regression -> ROC-AUC: {lr_auc:.4f}, Brier Loss: {lr_brier:.4f}")
    
    # 2. XGBoost
    # Compute class weight for scale_pos_weight
    neg_count = sum(y_train == 0)
    pos_count = sum(y_train == 1)
    scale_weight = neg_count / pos_count if pos_count > 0 else 1.0
    
    xgb_model = xgb.XGBClassifier(
        max_depth=3,
        learning_rate=0.05,
        n_estimators=100,
        scale_pos_weight=scale_weight,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict_proba(X_test)[:, 1]
    xgb_auc = roc_auc_score(y_test, xgb_preds)
    xgb_brier = brier_score_loss(y_test, xgb_preds)
    
    logger.info(f"XGBoost Classifier   -> ROC-AUC: {xgb_auc:.4f}, Brier Loss: {xgb_brier:.4f}")
    
    # Select best model
    if xgb_auc > lr_auc:
        best_model = xgb_model
        best_type = "xgboost"
        best_auc = xgb_auc
        best_preds = xgb_preds
    else:
        best_model = lr_model
        best_type = "logistic_regression"
        best_auc = lr_auc
        best_preds = lr_preds
        
    logger.info(f"Selected Best Model: {best_type} with ROC-AUC {best_auc:.4f}")
    
    # Save the model
    model_payload = {
        "model": best_model,
        "model_type": best_type,
        "features": features,
        "auc": float(best_auc),
        "trained_at": datetime.now().isoformat()
    }
    
    model_path = settings.XG_MODEL_PATH
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model_payload, f)
        
    logger.info(f"Model saved to {model_path}")
    
    # Print classification report
    y_pred_bin = (best_preds >= 0.5).astype(int)
    logger.info("\n" + classification_report(y_test, y_pred_bin))

if __name__ == "__main__":
    train_and_evaluate()

import numpy as np

def calculate_distance(x: float, y: float) -> float:
    """Calculate distance from shot location to center of the goal (120, 40)."""
    if x is None or y is None:
        return 20.0  # default average distance
    return float(np.sqrt((120.0 - x) ** 2 + (40.0 - y) ** 2))

def calculate_angle(x: float, y: float) -> float:
    """
    Calculate the visible angle to the goal (goalposts at (120, 36) and (120, 44)).
    Returns the angle in radians.
    """
    if x is None or y is None:
        return 0.3  # default average angle
    
    # Avoid division by zero if shot is exactly on the goal line
    dx = 120.0 - x
    if dx <= 0.05:
        dx = 0.05
        
    # Vectors to goal posts
    v_a = np.array([dx, 36.0 - y])
    v_b = np.array([dx, 44.0 - y])
    
    # Dot product
    dot = np.dot(v_a, v_b)
    norm_a = np.linalg.norm(v_a)
    norm_b = np.linalg.norm(v_b)
    
    cos_theta = dot / (norm_a * norm_b)
    # Clip to avoid floating point errors out of range [-1, 1]
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    return float(np.arccos(cos_theta))

def extract_shot_features(event_dict: dict) -> dict:
    """
    Extract features from a raw database event record dictionary or details.
    """
    x = event_dict.get("x")
    y = event_dict.get("y")
    under_pressure = event_dict.get("under_pressure", False)
    
    detail = event_dict.get("detail_json") or {}
    body_part = detail.get("body_part", "Foot")
    technique = detail.get("technique", "Normal")
    shot_type = detail.get("type", "Open Play")
    
    is_header = 1 if body_part == "Head" else 0
    is_volley = 1 if technique in ["Volley", "Half Volley"] else 0
    is_free_kick = 1 if shot_type == "Free Kick" else 0
    is_penalty = 1 if shot_type == "Penalty" else 0
    
    dist = calculate_distance(x, y)
    angle = calculate_angle(x, y)
    
    return {
        "distance": dist,
        "angle": angle,
        "is_header": is_header,
        "is_volley": is_volley,
        "is_free_kick": is_free_kick,
        "is_penalty": is_penalty,
        "under_pressure": 1 if under_pressure else 0
    }
